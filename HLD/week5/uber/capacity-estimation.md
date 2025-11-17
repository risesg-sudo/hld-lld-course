# Uber: Capacity Estimation

## Scale Assumptions

- Daily rides: 15 million
- Active drivers: 1 million
- Active riders: 20 million DAU
- Average ride: 20 minutes
- Location update frequency: 4 seconds (drivers)

## Traffic Estimates

**Ride requests**: 15M/day = 174 req/sec (avg), 522 req/sec (peak 3x)

**Location updates**:
- Active drivers: 1M / 4 sec = 250K updates/sec
- During rides (more frequent): 70K updates/sec
- Total: 320K driver location updates/sec

**Read requests** (rider tracking driver): 70K req/sec

## Storage Estimates

**Location data** (30 day retention):
- 31.3B updates/day × 50 bytes = 1.56 TB/day
- With replication: 140 TB/month

**Ride data** (5 year retention):
- 15M rides/day × 1 KB = 15 GB/day
- 5 years with replication: 82.5 TB

## Bandwidth

**Incoming**: 18 MB/sec (location updates)
**Outgoing**: 87 MB/sec (location queries, rider tracking)

## Key Insights

**Location updates dominate load**: 320K writes/sec requires write-optimized database (Cassandra).

**Geospatial queries are critical path**: Must be sub-100ms for good UX. Requires specialized indexing (Redis Geospatial, QuadTree).

**Real-time nature drives WebSocket use**: Polling would waste bandwidth and increase latency.
