# YouTube: Design Trade-offs

## Key Trade-offs

**Storage vs Cost**: Storing 7 formats multiplies storage by 4x. Trade-off: Higher storage cost for better user experience (adaptive quality).

**Why worth it?** User experience drives engagement. Buffering videos loses viewers.

**Transcoding Speed vs Quality**: Fast presets produce larger files. Slow presets compress better.

**YouTube's choice**: Medium preset. Balance between transcode time (important for upload-to-watch delay) and file size (affects storage/bandwidth costs).

**Consistency vs Availability**: View counts use eventual consistency. Multiple writes might conflict, but exact count doesn't matter.

**Why acceptable?** Difference between 1,000,001 and 1,000,003 views is meaningless to users. Strong consistency not worth the performance cost.

**Pre-computation vs Real-time**: Recommendations pre-computed overnight vs computed on-demand.

**Trade-off**: Pre-computed recommendations are slightly stale but serve quickly. Real-time would be fresh but too expensive.

**Mitigation**: Adjust pre-computed recommendations with recent signals (last hour of activity).

## Scalability Bottlenecks

**Transcoding throughput**: 50 videos/sec × 70 min processing = 3,500 concurrent jobs. Solution: Massive parallel worker pool with GPU acceleration.

**Storage growth**: 3.15 EB/year is expensive. Solution: Tiered storage (hot/warm/cold based on access patterns), compression, deduplication.

**Recommendation computation**: Can't compute for 2.5B users in real-time. Solution: Batch pre-compute, cache results, real-time adjustment for fresh signals.

**Global bandwidth**: 48 Tbps impossible from origin. Solution: CDN with 95% cache hit rate reduces origin bandwidth 20x.

## Why This Design Scales

**Async everything**: Upload separate from transcode, transcode separate from serving.

**CDN-first**: Edge caching handles 95% of traffic.

**Polyglot persistence**: Right database for each workload.

**Horizontal scaling**: All components scale by adding more instances.

**Pre-computation where possible**: Batch expensive operations (recommendations, thumbnails), serve from cache.
