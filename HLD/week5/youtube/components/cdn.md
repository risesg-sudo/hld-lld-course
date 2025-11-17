# YouTube: CDN Strategy

## Why CDN is Essential

Without CDN, origin servers must serve 48 Tbps peak bandwidth. This is physically impossible and economically infeasible.

With 95% CDN cache hit rate:
- CDN serves: 45.6 Tbps (from edge caches)
- Origin serves: 2.4 Tbps (cache misses only)

This 20x reduction makes the system feasible.

## Multi-Tier Caching

```
User
 │
 ▼
Edge PoP (200+ locations) ─────► 95% hit rate
 │ (cache miss)
 ▼
Regional Cache (origin shield) ─► 99% hit rate
 │ (cache miss)
 ▼
Origin (GCS)
```

**Edge PoP**: Closest to user (10-50ms latency)
**Regional Cache**: Reduces load on origin
**Origin**: Only hit for new/unpopular videos

## Cache Strategy

**Video segments**: Cache aggressively (immutable)
```
Cache-Control: public, max-age=31536000, immutable
```

**Manifests**: Short cache (content changes)
```
Cache-Control: public, max-age=60
```

## Cache Warming

For popular videos (trending, new uploads from big channels):
```python
async def warm_cache(video_id):
    # Pre-fetch to major edge locations
    locations = ['us-east', 'us-west', 'eu-west', 'asia-east']
    
    for location in locations:
        await cdn_api.prefetch(
            video_id=video_id,
            location=location,
            files=['manifest', '720p/*', '1080p/*']  # Most common qualities
        )
```

This ensures popular videos are cached before users request them.

## Why 95%+ Hit Rate is Achievable

**Power law distribution**: 20% of videos account for 80% of views. These stay cached.

**Repeat views**: Same video watched by many users. First user caches, rest hit cache.

**Long-tail rarely accessed**: Videos with 100 views don't stay in cache, but don't matter for bandwidth.
