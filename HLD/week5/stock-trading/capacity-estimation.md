# Stock Trading: Capacity Estimation

## Assumptions

- Active users: 1 million traders
- Orders per user per day: 10
- Trading hours: 6.5 hours/day
- Peak to average ratio: 10x
- Order to trade ratio: 5:1 (20% of orders execute)

## Traffic Estimates

**Orders**: 10M/day = 427/sec avg, 4,270/sec peak

**Trades**: 2M/day = 85/sec avg, 850/sec peak

**Market Data Updates**: 10K securities × 10 updates/sec = 100K updates/sec

Note: HFT firms can generate millions of orders/sec. We design for 100K orders/sec peak to handle institutional + HFT traffic.

## Storage Estimates

**Orders** (1 year): 10M/day × 200 bytes = 2 GB/day = 500 GB/year (with audit: 5 TB)

**Trades** (7 years, regulatory): 2M/day × 300 bytes = 600 MB/day = 1 TB for 7 years (with audit: 10 TB)

**Market Data** (tick data, 1 year): 100K updates/sec × 50 bytes = 5 MB/sec = 117 GB/day = 29 TB/year

## Latency Budget (1ms total)

- Network (client to gateway): 200μs
- Gateway processing: 50μs
- Order validation: 100μs
- Matching engine: 500μs
- Trade confirmation: 100μs
- Response network: 50μs
Total: 1000μs = 1ms

## Key Insights

**Latency is king**: Every microsecond counts. This drives hardware choices (bare metal, kernel bypass), algorithms (lock-free), and architecture (single-threaded matching).

**Determinism required**: Regulatory compliance requires exact replay capability. Event sourcing is essential.

**High availability critical**: Downtime during trading hours is unacceptable. Hot standby and fast failover required.
