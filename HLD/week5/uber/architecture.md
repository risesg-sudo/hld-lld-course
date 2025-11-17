# Uber: High-Level Architecture

## System Components

```
┌────────┐
│ Client │
└────┬───┘
     │
     ▼
┌─────────────┐
│Load Balancer│
└──────┬──────┘
       │
   ┌───┴────┬──────────┬─────────┐
   ▼        ▼          ▼         ▼
┌───────┐┌────────┐┌────────┐┌────────┐
│ Ride  ││Location││Pricing ││Payment │
│Service││Service ││Service ││Service │
└───┬───┘└───┬────┘└────┬───┘└────┬───┘
    │        │           │         │
    └────┬───┴───────┬───┴─────┬───┘
         │           │         │
         ▼           ▼         ▼
    ┌────────────────────────────┐
    │       Kafka Event Bus      │
    └─────────┬──────────────────┘
              │
    ┌─────────┼──────────┬────────┐
    ▼         ▼          ▼        ▼
┌────────┐┌────────┐┌────────┐┌────────┐
│ Redis  ││Postgres││Cassandra│Kafka   │
│(Geo)   ││(Rides) ││(Location)Stream │
└────────┘└────────┘└────────┘└────────┘
```

## Component Responsibilities

**Location Service**: Track driver/rider locations, perform geospatial queries (nearby drivers).

**Ride Service**: Handle ride lifecycle (request → match → start → complete).

**Matching Engine**: Find best available driver for rider request.

**Pricing Service**: Calculate fares, surge pricing based on supply/demand.

**Payment Service**: Process payments via Stripe/Braintree.

**Notification Service**: Push notifications (driver matched, driver arrived, etc.).

## Key Design Decisions

**Redis Geospatial for active locations**: Sub-millisecond geospatial queries, auto-expiry via TTL.

**Cassandra for location history**: High write throughput for 320K updates/sec.

**PostgreSQL for transactional data**: Rides, users require ACID guarantees.

**Kafka for events**: Decouple components, enable replay, audit trail.

**WebSockets for real-time**: Push location updates to clients instantly.

## Why This Architecture

**Geospatial optimization**: Redis GEORADIUS handles "find drivers within 5km" in <10ms.

**Write scalability**: Cassandra handles massive location update volume.

**Event-driven**: Kafka enables async processing and service decoupling.

**Regional deployment**: Each city/region has dedicated deployment for low latency.
