# WhatsApp: Capacity Estimation

## Why Capacity Estimation Matters

Before designing any large-scale system, we must understand the magnitude of the problem. Capacity estimation helps us:
- Choose appropriate technologies (SQL vs NoSQL, single server vs distributed)
- Plan infrastructure costs and budget
- Identify potential bottlenecks early
- Make informed trade-offs between consistency, availability, and performance

## Base Assumptions

Let's establish our assumptions based on WhatsApp's scale:

**User Metrics**
- Total users: 2 billion
- Daily active users (DAU): 1 billion (50% engagement rate)
- Messages per user per day: 50
- Group messages: 20% of total messages
- Media messages: 10% of total messages

**Message Characteristics**
- Average text message size: 100 bytes
- Average media file size: 500 KB
- Concurrent connections at peak: 100 million

**Why these numbers?** They align with published WhatsApp statistics and represent realistic usage patterns across diverse user bases.

## Traffic Estimation

### Daily Message Volume

```
Total messages per day = DAU × messages per user
                       = 1 billion × 50
                       = 50 billion messages/day
```

This is a staggering number, but it's manageable when distributed across 24 hours and multiple datacenters.

### Messages Per Second

```
Average rate = 50 billion / 86,400 seconds
             = 578,703 messages/second
             ≈ 580,000 messages/second
```

```
Peak rate (3x average, during morning/evening hours)
         = 580,000 × 3
         = 1,740,000 messages/second
```

Why 3x peak factor? User activity is not uniform. Morning (people waking up) and evening (after work) see concentrated activity. We must design for peak load, not average.

### Read vs Write Ratio

Unlike social media platforms, messaging is relatively balanced:
- Writes: Sending messages
- Reads: Receiving messages, viewing history

For one-on-one chats: roughly 1:1 (one person writes, one person reads)
For group chats: 1:N (one person writes, N people read)

With 20% group messages (average 10 members), the effective read multiplier is:
```
Read multiplier = 0.8 × 1 + 0.2 × 10 = 2.8
```

So for every write, we have approximately 2.8 reads.

## Data Generation

### Text Messages

```
Text messages per day = 50 billion × 0.9 (90% are text)
                      = 45 billion messages/day

Data volume = 45 billion × 100 bytes
            = 4.5 TB/day of text data
```

This is quite manageable for modern distributed databases.

### Media Messages

```
Media messages per day = 50 billion × 0.1 (10% contain media)
                       = 5 billion media messages/day

Data volume = 5 billion × 500 KB
            = 2.5 PB/day of media data
```

This is where the real storage challenge lies. Media dominates our storage requirements by three orders of magnitude.

## Storage Requirements

### Message Storage (5-Year Retention)

**Text Messages**
```
Daily: 4.5 TB
Yearly: 4.5 TB × 365 = 1.64 PB
5-Year: 1.64 PB × 5 = 8.2 PB

With 3x replication: 24.6 PB
```

**Media Files**
```
Daily: 2.5 PB
Yearly: 2.5 PB × 365 = 912 PB ≈ 0.9 EB
5-Year: 4.5 EB (exabytes)

With 3x replication: 13.5 EB
```

Why 3x replication? To ensure durability and availability. If one datacenter fails, we have two copies elsewhere. This is the standard approach for critical data.

### Metadata Storage

```
User profiles: 2 billion users × 1 KB = 2 TB
Groups: 100 million groups × 10 KB = 1 TB
Total metadata: ~3 TB
```

Metadata storage is negligible compared to messages and media.

## Bandwidth Requirements

### Incoming Traffic (Uploads)

```
Text: 4.5 TB/day / 86,400 seconds = 52 MB/s
Media: 2.5 PB/day / 86,400 seconds = 28.9 GB/s
Total incoming: ~29 GB/s
```

Peak (3x): 87 GB/s

### Outgoing Traffic (Downloads)

Remember our 2.8x read multiplier:

```
Outgoing = Incoming × 2.8
         = 29 GB/s × 2.8
         = 81 GB/s

Peak (3x): 243 GB/s
```

This massive bandwidth requirement is why WhatsApp uses CDNs extensively for media delivery.

## Memory Requirements for Caching

What should we cache?

**Active User Data**
```
Concurrent users: 100 million
Data per user: 10 KB (profile, settings, session)
Total: 100 million × 10 KB = 1 TB
```

**Recent Messages**
```
Cache last 10 messages per conversation
100 million users × 10 messages × 100 bytes = 100 GB
```

**Presence Information**
```
100 million users × 100 bytes (status, last seen) = 10 GB
```

**Total cache requirement: ~1.1 TB**

This is distributed across many cache servers globally, so per-server memory requirements are reasonable.

## Server Estimation

### WebSocket Servers

Each server can handle approximately 50,000 concurrent connections (limited by file descriptors and memory).

```
Required servers = 100 million connections / 50,000
                 = 2,000 WebSocket servers
```

With redundancy and geographic distribution: ~2,500 servers

### Message Processing Servers

Each server can process approximately 10,000 messages/second.

```
Required servers = 1.74 million (peak) / 10,000
                 = 174 servers
```

With redundancy: ~250 servers

### Why These Numbers?

50,000 connections per server is achievable with:
- Optimized WebSocket libraries
- Increased file descriptor limits (ulimit -n)
- Efficient memory management (10-20 KB per connection)
- Modern multi-core servers

10,000 messages/second per server assumes:
- Lightweight processing (validation, routing)
- Async I/O operations
- Database operations handled separately

## Key Insights from Estimation

1. **Media dominates storage**: 13.5 EB vs 24.6 PB for text (560x larger)
   - This drives our decision to use object storage (S3) for media
   - Aggressive compression and tiered storage are essential

2. **Bandwidth is the real challenge**: 243 GB/s peak
   - CDN is not optional, it's essential
   - Direct client-to-storage uploads reduce server load

3. **Caching is crucial**: 1.1 TB cache reduces database load dramatically
   - Redis cluster can handle this across multiple nodes
   - Cache hit rate > 90% makes the system performant

4. **Horizontal scaling is necessary**: No single server can handle the load
   - 2,500+ servers distributed globally
   - Stateless design enables scaling

These estimates guide every architectural decision we make in the following sections.
