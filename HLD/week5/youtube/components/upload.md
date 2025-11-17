# YouTube: Video Upload Pipeline

## The Upload Challenge

Traditional approach: client uploads to server, server processes and stores. This doesn't scale when handling 50 GB video files at 50 uploads/second. We need a better approach.

## Pre-Signed URL Approach

**Flow**:
1. Client requests upload URL
2. Server generates pre-signed URL (S3/GCS)
3. Client uploads directly to storage
4. Client confirms upload completion
5. Server queues transcoding job

**Why?** Bypasses application servers for data transfer. Servers only coordinate, storage handles heavy lifting.

## Multipart Upload

For large files, split into chunks:
```javascript
// Client side
async function uploadLargeVideo(file) {
  const chunkSize = 5 * 1024 * 1024; // 5 MB chunks
  const chunks = Math.ceil(file.size / chunkSize);
  
  // 1. Initiate multipart upload
  const uploadId = await initiateUpload(file.name);
  
  // 2. Upload chunks in parallel
  const uploadPromises = [];
  for (let i = 0; i < chunks; i++) {
    const chunk = file.slice(i * chunkSize, (i + 1) * chunkSize);
    uploadPromises.push(uploadChunk(uploadId, i, chunk));
  }
  
  await Promise.all(uploadPromises);
  
  // 3. Complete multipart upload
  await completeUpload(uploadId);
}
```

**Benefits**: Parallel upload (faster), resumable (retry failed chunks), progress tracking.

## Upload Service Implementation

```python
async def request_upload_url(user_id, video_name, file_size):
    # 1. Validate
    if file_size > 256 * 1024**3:  # 256 GB limit
        raise ValueError("File too large")
    
    # 2. Generate video ID
    video_id = generate_id()
    
    # 3. Create GCS key
    gcs_key = f"uploads/{datetime.now().year}/{datetime.now().month}/{video_id}"
    
    # 4. Generate pre-signed URL (expires in 24 hours)
    signed_url = gcs_client.generate_upload_url(
        bucket='youtube-uploads',
        key=gcs_key,
        expires_in=86400
    )
    
    # 5. Store pending upload in database
    await db.execute("""
        INSERT INTO video_uploads (video_id, user_id, gcs_key, status)
        VALUES (?, ?, ?, 'pending')
    """, (video_id, user_id, gcs_key))
    
    return {'video_id': video_id, 'upload_url': signed_url}
```

## Confirming Upload

```python
async def confirm_upload(video_id, metadata):
    # 1. Verify file exists in GCS
    video = await db.get_video_upload(video_id)
    exists = await gcs_client.object_exists(video['gcs_key'])
    if not exists:
        raise ValueError("Upload not found")
    
    # 2. Update metadata
    await db.execute("""
        UPDATE video_uploads
        SET title = ?, description = ?, status = 'uploaded'
        WHERE video_id = ?
    """, (metadata['title'], metadata['description'], video_id))
    
    # 3. Queue transcoding job
    await kafka.send('video.transcoding.queue', {
        'video_id': video_id,
        'gcs_key': video['gcs_key'],
        'priority': 'normal'
    })
    
    return {'video_id': video_id, 'status': 'processing'}
```

## Resumable Uploads

Handle network failures gracefully:
```python
# Client tracking uploaded chunks
uploaded_chunks = set()

async def upload_chunk_with_retry(chunk_num, data):
    if chunk_num in uploaded_chunks:
        return  # Already uploaded
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await upload_chunk(chunk_num, data)
            uploaded_chunks.add(chunk_num)
            return
        except NetworkError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Why This Design Works

**Pre-signed URLs eliminate server bottleneck**: Servers don't handle data transfer.

**Multipart enables parallelism**: Multiple chunks upload simultaneously.

**Resumable uploads handle failures**: Network issues don't require full re-upload.

**Async confirmation decouples upload from processing**: Users get fast feedback.
