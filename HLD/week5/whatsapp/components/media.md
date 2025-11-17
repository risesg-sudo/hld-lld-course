# WhatsApp: Media Service

## The Media Challenge

Text messages are tiny (100 bytes), but media files are massive (500 KB average). When users share 5 billion media files daily, we're looking at 2.5 petabytes of data per day. Storing and delivering this efficiently is a completely different problem than text messaging.

The challenges:
- Uploading through application servers wastes bandwidth and CPU
- Storing in a database is prohibitively expensive
- Global delivery requires content distribution
- Mobile networks are slow and unreliable

## Design Philosophy

**Direct Upload**: Clients upload directly to object storage, bypassing application servers

**Separate Storage**: Media files live in cheap object storage (S3), not in the database

**Lazy Processing**: Generate thumbnails and compressions only when needed

**CDN Distribution**: Popular media cached at edge locations globally

## Upload Flow

### Traditional Approach (What We Don't Do)

```
Client → API Server → S3
Problems:
- API server bandwidth wasted (passes through 2.5 PB/day)
- Server CPU used for upload handling
- Doesn't scale well
```

### Our Approach: Pre-Signed URLs

```
┌────────┐         ┌──────────────┐         ┌─────┐         ┌──────────┐
│ Client │         │Media Service │         │  S3 │         │Cassandra │
└───┬────┘         └──────┬───────┘         └──┬──┘         └────┬─────┘
    │                     │                    │                  │
    ├─1. Request upload──►│                    │                  │
    │                     │                    │                  │
    │                     ├─2. Generate ID─────┤                  │
    │                     │                    │                  │
    │                     ├─3. Create presigned URL                │
    │                     │                    │                  │
    │◄─4. Return URL──────┤                    │                  │
    │  (expires in 5 min) │                    │                  │
    │                     │                    │                  │
    ├─5. Upload directly─────────────────────►│                  │
    │   (bypasses server)                     │                  │
    │                     │                    │                  │
    │◄─6. Upload complete─┼────────────────────┤                  │
    │                     │                    │                  │
    ├─7. Confirm upload───►│                    │                  │
    │                     │                    │                  │
    │                     ├─8. Store metadata──┼─────────────────►│
    │                     │                    │                  │
    │◄─9. Return media ID─┤                    │                  │
```

### Implementation

**Step 1: Request Upload URL**

```python
async def request_upload_url(user_id, file_type, file_size):
    # 1. Validate
    if file_size > 100 * 1024 * 1024:  # 100 MB limit
        raise ValueError("File too large")

    if file_type not in ['image/jpeg', 'image/png', 'video/mp4', 'application/pdf']:
        raise ValueError("Unsupported file type")

    # 2. Generate unique media ID
    media_id = generate_media_id()  # UUID or Snowflake ID

    # 3. Generate S3 key
    # Structure: uploads/{year}/{month}/{media_id}.{ext}
    s3_key = f"uploads/{now().year}/{now().month}/{media_id}.{get_extension(file_type)}"

    # 4. Generate pre-signed URL (expires in 5 minutes)
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': 'whatsapp-media',
            'Key': s3_key,
            'ContentType': file_type
        },
        ExpiresIn=300  # 5 minutes
    )

    # 5. Store pending upload in Redis
    await redis.setex(
        f'upload:pending:{media_id}',
        300,  # 5 minute TTL
        json.dumps({
            'user_id': user_id,
            's3_key': s3_key,
            'file_type': file_type,
            'file_size': file_size
        })
    )

    return {
        'media_id': media_id,
        'upload_url': presigned_url,
        'expires_in': 300
    }
```

**Why pre-signed URLs?**

The URL grants temporary upload permission. The client can upload directly to S3 without giving them AWS credentials. The URL expires after 5 minutes, limiting security exposure.

**Step 2: Confirm Upload**

After the client uploads, they confirm with the server:

```python
async def confirm_upload(user_id, media_id):
    # 1. Check pending upload
    pending = await redis.get(f'upload:pending:{media_id}')
    if not pending:
        raise ValueError("Upload not found or expired")

    pending_data = json.loads(pending)

    # 2. Verify ownership
    if pending_data['user_id'] != user_id:
        raise PermissionError("Not your upload")

    # 3. Verify file exists in S3
    exists = await s3_client.head_object(
        Bucket='whatsapp-media',
        Key=pending_data['s3_key']
    )
    if not exists:
        raise ValueError("File not found in storage")

    # 4. Store metadata in Cassandra
    await cassandra.execute("""
        INSERT INTO media (
            media_id, uploader_id, s3_key, file_type, file_size,
            uploaded_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        media_id, user_id, pending_data['s3_key'],
        pending_data['file_type'], pending_data['file_size'],
        now(), 'uploaded'
    ))

    # 5. Queue for processing (thumbnails, compression)
    await kafka.send('media.processing', {
        'media_id': media_id,
        's3_key': pending_data['s3_key'],
        'file_type': pending_data['file_type']
    })

    # 6. Clean up pending upload
    await redis.delete(f'upload:pending:{media_id}')

    return {
        'media_id': media_id,
        'status': 'processing'
    }
```

## Download Flow

```python
async def get_media_url(viewer_id, media_id):
    # 1. Fetch metadata
    media = await cassandra.execute(
        "SELECT * FROM media WHERE media_id = ?",
        (media_id,)
    )

    if not media:
        raise NotFoundError("Media not found")

    # 2. Check permissions (is viewer allowed to access?)
    # (Simplified - in reality, check message access)
    if not await can_access_media(viewer_id, media_id):
        raise PermissionError("Access denied")

    # 3. Generate CDN URL or pre-signed URL
    if media['file_type'].startswith('image'):
        # Serve through CDN for images
        cdn_url = f"https://cdn.whatsapp.com/{media['s3_key']}"
        return {
            'url': cdn_url,
            'thumbnail_url': cdn_url.replace('.jpg', '_thumb.jpg')
        }
    else:
        # Generate temporary download URL for other files
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': 'whatsapp-media',
                'Key': media['s3_key']
            },
            ExpiresIn=3600  # 1 hour
        )
        return {'url': download_url}
```

## Media Processing

After upload, we process media in the background:

```python
class MediaProcessor:
    async def process_media(self, media_id, s3_key, file_type):
        if file_type.startswith('image'):
            await self.process_image(media_id, s3_key)
        elif file_type.startswith('video'):
            await self.process_video(media_id, s3_key)

    async def process_image(self, media_id, s3_key):
        # 1. Download from S3
        image_data = await s3_client.get_object(
            Bucket='whatsapp-media',
            Key=s3_key
        )

        # 2. Generate thumbnail (200x200)
        thumbnail = create_thumbnail(image_data, size=(200, 200))

        # 3. Compress full image (reduce quality to 85%)
        compressed = compress_image(image_data, quality=85)

        # 4. Upload processed versions
        thumbnail_key = s3_key.replace('.jpg', '_thumb.jpg')
        compressed_key = s3_key.replace('.jpg', '_compressed.jpg')

        await s3_client.put_object(
            Bucket='whatsapp-media',
            Key=thumbnail_key,
            Body=thumbnail
        )

        await s3_client.put_object(
            Bucket='whatsapp-media',
            Key=compressed_key,
            Body=compressed
        )

        # 5. Update metadata
        await cassandra.execute("""
            UPDATE media
            SET thumbnail_url = ?, compressed_url = ?, status = 'ready'
            WHERE media_id = ?
        """, (thumbnail_key, compressed_key, media_id))
```

Why lazy processing?

Not all uploaded media is viewed. Processing on demand or in background saves CPU when files are never accessed.

## Storage Strategy

### Tiered Storage

Not all media needs to be instantly accessible:

**Hot Tier (S3 Standard)**: Last 30 days
- Frequently accessed
- Low latency required
- Higher cost

**Warm Tier (S3 IA - Infrequent Access)**: 30 days - 1 year
- Occasionally accessed
- Slightly higher latency acceptable
- 50% cheaper than standard

**Cold Tier (S3 Glacier)**: > 1 year
- Rarely accessed
- Minutes to hours retrieval time
- 90% cheaper than standard

```python
async def apply_lifecycle_policy():
    """Run daily to transition media to appropriate tiers"""
    # S3 lifecycle policy (configured once)
    lifecycle_policy = {
        'Rules': [
            {
                'Id': 'Move to IA after 30 days',
                'Status': 'Enabled',
                'Transitions': [{
                    'Days': 30,
                    'StorageClass': 'STANDARD_IA'
                }]
            },
            {
                'Id': 'Move to Glacier after 365 days',
                'Status': 'Enabled',
                'Transitions': [{
                    'Days': 365,
                    'StorageClass': 'GLACIER'
                }]
            }
        ]
    }
```

This automatically reduces storage costs as media ages.

## CDN Strategy

### Why CDN for Media?

**Bandwidth Savings**: 90%+ of media views are repeat views (same image shared in group, viewed by multiple people)

**Global Distribution**: Users in India don't need to fetch from US servers

**Reduced Latency**: Edge caches serve media in milliseconds

### CDN Configuration

```nginx
# CloudFront distribution config
cache_behavior {
  path_pattern = "/media/*"
  target_origin = "whatsapp-media.s3.amazonaws.com"

  # Cache for 30 days (media URLs don't change)
  min_ttl = 2592000
  default_ttl = 2592000
  max_ttl = 2592000

  # Compress responses
  compress = true

  # Forward only necessary headers
  forward_headers = ["Authorization"]
}
```

### Cache Invalidation

What if media needs to be deleted (user removes it)?

```python
async def delete_media(media_id):
    # 1. Mark as deleted in database
    await cassandra.execute(
        "UPDATE media SET status = 'deleted' WHERE media_id = ?",
        (media_id,)
    )

    # 2. Delete from S3 (actual deletion)
    media = await get_media(media_id)
    await s3_client.delete_object(
        Bucket='whatsapp-media',
        Key=media['s3_key']
    )

    # 3. Invalidate CDN cache
    await cloudfront.create_invalidation(
        DistributionId='DISTRIBUTION_ID',
        InvalidationBatch={
            'Paths': [f"/media/{media_id}*"],
            'CallerReference': str(uuid.uuid4())
        }
    )
```

## Optimizations

### Client-Side Compression

Before uploading, mobile clients compress images:

```javascript
// Client-side (mobile)
async function uploadImage(file) {
  // 1. Compress image before upload
  const compressed = await compressImage(file, {
    maxWidth: 1920,
    maxHeight: 1920,
    quality: 0.8
  });

  // 2. Upload compressed version
  const uploadUrl = await requestUploadUrl();
  await uploadToS3(uploadUrl, compressed);
}
```

This reduces bandwidth by 70-80%, especially important on mobile networks.

### Progressive JPEG

Encode images as progressive JPEG:
- Displays low-quality version immediately
- Refines as more data loads
- Better user experience on slow networks

### Video Compression

For videos, use modern codecs:
- H.265/HEVC: 50% smaller than H.264
- VP9: Good compression, royalty-free
- Trade-off: More CPU for encoding

## Security Considerations

### Access Control

```python
async def can_access_media(user_id, media_id):
    # Check if user has access to any message containing this media
    message = await cassandra.execute("""
        SELECT sender_id, recipient_id FROM messages
        WHERE media_id = ?
        LIMIT 1
    """, (media_id,))

    if not message:
        return False

    # User must be sender or recipient
    return user_id in [message['sender_id'], message['recipient_id']]
```

### Encryption

Media files can be encrypted at rest:

```python
# S3 server-side encryption
await s3_client.put_object(
    Bucket='whatsapp-media',
    Key=s3_key,
    Body=file_data,
    ServerSideEncryption='AES256'
)
```

For end-to-end encryption (E2EE):
- Encrypt on client before upload
- Server stores encrypted blob
- Only recipient's client can decrypt

## Performance Characteristics

**Upload**:
- Direct to S3: 100 MB file uploads in 10-30 seconds (depending on network)
- No server bandwidth consumed

**Download**:
- CDN cache hit: 50-200ms globally
- CDN cache miss: 200-500ms (origin fetch)
- 95%+ cache hit rate

**Storage Cost**:
- S3 Standard: $0.023 per GB/month
- 2.5 PB/day × 30 days = 75 PB/month
- Cost: 75 PB × $0.023/GB = $1.7M/month
- With tiered storage: ~$800K/month (50% savings)

**Bandwidth Cost**:
- Without CDN: 81 GB/s × $0.09/GB = massive cost
- With CDN (95% cache hit): 95% savings

## Why This Design Works

**Direct uploads eliminate server bottleneck**: Clients upload directly to S3, servers only coordinate

**Pre-signed URLs maintain security**: Temporary, scoped permissions without exposing credentials

**CDN dramatically reduces bandwidth costs**: 95%+ cache hit rate = 95% bandwidth savings

**Tiered storage reduces costs**: Old media automatically moved to cheaper storage

**Lazy processing optimizes resources**: Don't process media that's never viewed

This architecture handles petabytes of media uploads daily while keeping costs reasonable and maintaining fast global access.
