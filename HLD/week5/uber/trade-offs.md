# Uber: Design Trade-offs

## Key Trade-offs

**Redis vs PostgreSQL for Driver Status**

Choice: Redis for active status, PostgreSQL as source of truth

Why? Redis provides sub-millisecond lookups needed for matching. PostgreSQL persists data for consistency.

Trade-off: Potential inconsistency if Redis and PostgreSQL diverge.

Mitigation: Redis has short TTL (60s), periodically refreshed from PostgreSQL.

**Fan-out on Write vs Read (Location Updates)**

Choice: Write to Redis (fast lookup), async write to Cassandra (history)

Why? Matching requires fast reads. History is queried infrequently.

Trade-off: Write amplification (write to Redis + Cassandra).

**GEORADIUS vs QuadTree**

Choice: Redis GEORADIUS for most cities

Why? Simpler to implement and operate. Good enough for most densities.

When to use QuadTree? Extremely dense cities (Mumbai, Tokyo) where GEORADIUS becomes slow.

## Scalability Bottlenecks

**Hot Spot Problem**: Concert ends, 50K riders request simultaneously in 1km area.

Solution: Priority queue, batch matching, suggest alternatives (walk to less congested area).

**Location Update Storm**: 1M drivers × 1 update/4 sec = 250K writes/sec.

Solution: Cassandra handles write volume. Batch writes reduce latency.

**Double-Booking Race Condition**: Two riders claim same driver.

Solution: Atomic PostgreSQL transaction with optimistic locking.

## Why This Design Scales

**Regional deployment**: Each city has dedicated cluster, no cross-city coordination needed.

**Geospatial indexing**: Redis GEORADIUS enables sub-100ms nearby driver queries.

**Event-driven**: Kafka decouples components, enables backpressure handling.

**Async processing**: Location history, analytics processed asynchronously.
