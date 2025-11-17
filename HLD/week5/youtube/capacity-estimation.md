# YouTube: Capacity Estimation

## Traffic Estimates

**Video Views**:
- Daily active users: 500 million
- Videos per user: 5
- Total views/day: 2.5 billion
- Views/second (avg): 28,935 views/sec
- Peak (5x): 145,000 views/sec

**Video Uploads**:
- Upload rate: 500 hours/minute
- Average video: 10 minutes
- Videos/second: 50 uploads/sec

## Storage Estimates

**Raw Upload Storage (1 year)**:
- Daily uploads: 720,000 hours/day
- At 50 MB/minute: 2.16 PB/day
- Yearly: 788 PB/year

**Multiple Formats** (7 resolutions):
- Multiplier: 4x average (compression varies by resolution)
- Total with formats: 3.15 EB/year

**Why 4x?** Higher resolutions use better compression. 4K doesn't take 16x space of 240p due to efficient codecs like H.265.

## Bandwidth Estimates

**Incoming** (uploads): 50 videos/sec × 50 MB = 2.5 GB/sec = 20 Gbps

**Outgoing** (streaming):
- Concurrent viewers: 4.8 million (based on 10 min avg watch time)
- Average bitrate: 2 Mbps (adaptive, varies by quality)
- Bandwidth: 4.8M × 2 Mbps = 9.6 Tbps
- Peak (5x): 48 Tbps

**CDN is essential**: This bandwidth cannot come from origin servers. With 95% CDN cache hit:
- Origin bandwidth: 480 Gbps (manageable)
- CDN serves 45.6 Tbps from edge

## Key Insights

**Media dominates everything**: 3.15 EB/year storage growth dwarfs all other data.

**CDN is not optional**: 95%+ cache hit rate reduces origin bandwidth by 20x.

**Transcoding is CPU-intensive**: 50 videos/sec × 70 min transcoding (all formats) = 3,500 concurrent transcodes needed.
