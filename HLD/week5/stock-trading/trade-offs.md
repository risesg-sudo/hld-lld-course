# Stock Trading: Design Trade-offs

## Key Trade-offs

**Latency vs Throughput**

Single-threaded matching: Low latency (no locks) but limited throughput (1 core)

Solution: Shard by symbol. AAPL on engine 1, GOOGL on engine 2, etc.

**Consistency vs Availability**

Strong consistency required (no duplicate trades). This sacrifices some availability.

Acceptable because: Trading hours are limited (6.5 hours/day). Downtime outside hours is tolerable. During hours, hot standby provides fast failover.

**Sync vs Async Persistence**

Choice: Sync to event log (memory-mapped file), async to database

Why? Event log provides durability (replayed on restart). Database persistence can lag without data loss.

**Bare Metal vs Cloud**

Choice: Bare metal for matching engines

Why? Predictable latency (no noisy neighbors), kernel bypass possible, CPU pinning.

Trade-off: Less flexible, higher operational burden.

## Bottlenecks and Solutions

**Matching Engine Throughput**: 100K orders/sec per engine

Solution: Horizontal scaling by symbol sharding. 10 engines = 1M orders/sec total.

**Market Data Fan-out**: 1M clients × 100K updates/sec = impossible

Solution: Conflation (aggregate over 100ms), subscription model (clients choose symbols), multicast (one message to many clients).

**Flash Crash Scenario**: Algorithmic cascade causes extreme volatility

Solution: Circuit breakers (halt trading if 7% drop), limit up/down (max price move), kill switch.

## Why This Design Works

**Event sourcing provides audit trail**: Every event logged, can replay for debugging/compliance.

**Single-threaded eliminates race conditions**: Deterministic, no locks needed.

**Hardware optimization**: Bare metal, CPU pinning, kernel bypass achieve microsecond latencies.

**Horizontal scaling**: Shard by symbol to scale beyond single engine limits.
