# HLD Week 2: Scaling, Caching, and Distributed Systems

This week covers strategies for building scalable, high-performance distributed systems.

## Directory Structure

```
week2/
├── fundamentals/
│   ├── latency-throughput/
│   │   └── concept.md - Understanding performance metrics
│   │
│   ├── consistency-availability/
│   │   └── concept.md - Distributed system guarantees
│   │
│   └── cap-theorem/
│       ├── concept.md - CAP theorem explained
│       ├── example.py - CP vs AP system simulation
│       └── dry_run.md - Partition scenario walkthrough
│
├── load-balancing/
│   ├── round-robin/
│   │   ├── concept.md - Sequential distribution
│   │   ├── example.py - Round-robin implementation
│   │   └── dry_run.md - Request distribution trace
│   │
│   ├── least-connections/
│   │   ├── concept.md - Load-aware balancing
│   │   ├── example.py - Least connections algorithm
│   │   └── dry_run.md - Connection tracking trace
│   │
│   └── consistent-hashing/
│       ├── concept.md - Distributed caching strategy
│       ├── example.py - Consistent hash ring
│       └── dry_run.md - Server addition/removal trace
│
├── caching/
│   ├── strategies/
│   │   ├── cache-aside/
│   │   │   ├── concept.md - Lazy loading pattern
│   │   │   ├── example.py - Cache-aside implementation
│   │   │   └── dry_run.md - Cache miss/hit scenarios
│   │   │
│   │   └── write-through/
│   │       ├── concept.md - Synchronous write pattern
│   │       ├── example.py - Write-through implementation
│   │       └── dry_run.md - Write operation trace
│   │
│   └── eviction/
│       ├── lru/
│       │   ├── concept.md - Least Recently Used policy
│       │   ├── example.py - LRU cache with HashMap + DLL
│       │   └── dry_run.md - Eviction trace with operations
│       │
│       └── lfu/
│           ├── concept.md - Least Frequently Used policy
│           ├── example.py - LFU cache implementation
│           └── dry_run.md - Frequency tracking trace
│
└── messaging/
    ├── pubsub/
    │   ├── concept.md - Publish-subscribe pattern
    │   ├── example.py - Simple pub/sub system
    │   └── dry_run.md - Message flow trace
    │
    └── kafka/
        ├── concept.md - Distributed streaming platform
        ├── example.py - Kafka producer/consumer
        └── dry_run.md - Partition and offset management
```

## Learning Path

### 1. Performance Fundamentals

**Latency vs Throughput**:
- Read: `fundamentals/latency-throughput/concept.md`
- Understand: The trade-offs between these two metrics
- Know: Latency numbers every programmer should know

**Consistency and Availability**:
- Read: `fundamentals/consistency-availability/concept.md`
- Learn: Strong vs eventual consistency models
- Understand: Availability metrics (nines)

**CAP Theorem**:
- Read: `fundamentals/cap-theorem/concept.md`
- Practice: `fundamentals/cap-theorem/example.py`
- Decision: When to choose CP vs AP systems

### 2. Load Balancing

Learn how to distribute traffic across multiple servers.

**Round Robin**:
- Simple, fair distribution
- Best for: Equal servers, stateless applications
- Implement: `load-balancing/round-robin/example.py`

**Least Connections**:
- Load-aware routing
- Best for: Long-lived connections, varying request times
- Implement: `load-balancing/least-connections/example.py`

**Consistent Hashing**:
- Minimal redistribution on server changes
- Best for: Distributed caching, sharding
- Implement: `load-balancing/consistent-hashing/example.py`

### 3. Caching Strategies

**Cache-Aside** (Lazy Loading):
- Application manages cache explicitly
- Most common pattern
- Example: `caching/strategies/cache-aside/example.py`

**Write-Through**:
- Synchronous writes to cache and database
- Strong consistency
- Example: `caching/strategies/write-through/example.py`

### 4. Cache Eviction Policies

**LRU (Least Recently Used)**:
- Evict oldest accessed item
- O(1) operations with HashMap + Doubly Linked List
- Example: `caching/eviction/lru/example.py`

**LFU (Least Frequently Used)**:
- Evict least accessed item
- Better for frequency-based patterns
- Example: `caching/eviction/lfu/example.py`

### 5. Message Systems

**Pub/Sub Pattern**:
- Decoupled publishers and subscribers
- Scalable message distribution
- Example: `messaging/pubsub/example.py`

**Apache Kafka**:
- Distributed streaming platform
- High throughput, durable, scalable
- Example: `messaging/kafka/example.py`

## Quick Reference

### Load Balancer Algorithm Selection

| Algorithm | Complexity | Use When |
|-----------|-----------|----------|
| Round Robin | O(1) | Equal servers, stateless |
| Weighted RR | O(1) | Different server capacities |
| Least Connections | O(n) | Long connections, varying duration |
| IP Hash | O(1) | Session persistence needed |
| Consistent Hash | O(log n) | Dynamic server pool, caching |

### Caching Strategy Selection

| Strategy | Write Latency | Read Latency | Consistency | Use When |
|----------|--------------|--------------|-------------|----------|
| Cache-Aside | Low (DB only) | Medium (miss penalty) | Eventual | Read-heavy |
| Write-Through | High (2 writes) | Low | Strong | Consistency critical |
| Write-Back | Very Low | Low | Eventual | Write-heavy |
| Write-Around | Low (DB only) | High (miss likely) | Strong | Write-once-read-rarely |

### Eviction Policy Selection

| Policy | Best For | Complexity |
|--------|----------|------------|
| LRU | Temporal locality, general purpose | O(1) |
| LFU | Frequency patterns, content popularity | O(1) or O(log n) |
| FIFO | Simple buffers, streaming | O(1) |
| TTL | Time-sensitive data | O(1) |
| ARC | Adaptive workloads | High |

### CAP Theorem Decision

**Choose CP (Consistency + Partition Tolerance)**:
- Banking transactions
- Inventory management
- Critical data integrity
- Examples: MongoDB, HBase, Redis (sync)

**Choose AP (Availability + Partition Tolerance)**:
- Social media
- Shopping carts
- Product catalogs
- Examples: Cassandra, DynamoDB, DNS

## Hands-On Exercises

1. **Implement LRU Cache**: Build from scratch with HashMap and Doubly Linked List
2. **Load Balancer Comparison**: Measure distribution for different algorithms
3. **Cache Performance**: Test hit rates with different eviction policies
4. **CAP Trade-offs**: Simulate network partition and observe behavior
5. **Pub/Sub System**: Build a simple message broker

## Common Patterns

### Scaling Pattern

```
Start: Monolith on single server
   ↓
Step 1: Vertical scaling (bigger server)
   ↓
Step 2: Add caching layer (Redis)
   ↓
Step 3: Horizontal scaling + load balancer
   ↓
Step 4: Database read replicas
   ↓
Step 5: Microservices (if needed)
```

### Caching Layers

```
Client
  ↓
CDN (static assets)
  ↓
Application Cache (Redis)
  ↓
Database Query Cache
  ↓
Database
```

## Interview Questions

### Fundamental Concepts

1. Explain latency vs throughput with examples
2. What is the CAP theorem? Give examples of CP and AP systems
3. Difference between strong and eventual consistency?
4. What are the five nines of availability?

### Load Balancing

5. When would you use Round Robin vs Least Connections?
6. How does consistent hashing work?
7. Explain Layer 4 vs Layer 7 load balancing
8. How do you handle server failures in load balancing?

### Caching

9. Compare cache-aside and write-through strategies
10. How does LRU cache achieve O(1) operations?
11. When would you use LFU over LRU?
12. How do you handle cache invalidation?

### Distributed Systems

13. Design a scalable notification system
14. How would you scale a database?
15. Kafka vs RabbitMQ - when to use each?
16. How do you ensure message delivery in distributed systems?

## Calculation Examples

### Cache Size Estimation

```
Active users: 1M
Data per user: 10KB
Cache size: 1M × 10KB = 10GB
With 80% hit rate: ~8GB frequently accessed
Redis server: 16GB recommended (headroom for growth)
```

### Throughput Calculation

```
Server capacity: 1000 requests/sec
Load balancer: 3 servers
Total capacity: 3000 requests/sec
With 70% utilization target: 2100 sustained requests/sec
```

### Availability Calculation

```
Availability = (Total Time - Downtime) / Total Time
99.9% = 8.76 hours downtime/year
99.99% = 52.6 minutes downtime/year
99.999% = 5.26 minutes downtime/year
```

## Performance Numbers to Remember

```
L1 cache reference: 0.5 ns
L2 cache reference: 7 ns
Main memory reference: 100 ns
Read 1 MB from memory: 250,000 ns (250 μs)
Read 1 MB from SSD: 1,000,000 ns (1 ms)
Disk seek: 10,000,000 ns (10 ms)
Read 1 MB from disk: 20,000,000 ns (20 ms)
Send packet CA->Netherlands->CA: 150,000,000 ns (150 ms)
```

## Next Steps

After Week 2, you should understand:
- How to scale applications horizontally and vertically
- When to use different load balancing algorithms
- How to implement and choose caching strategies
- CAP theorem implications for distributed systems
- Message queues and event-driven architectures

Continue to Week 3 to learn about databases, sharding, and data modeling.

## Resources

Run examples:
```bash
# LRU Cache
python week2/caching/eviction/lru/example.py

# Load Balancer
python week2/load-balancing/round-robin/example.py

# CAP Theorem Demo
python week2/fundamentals/cap-theorem/example.py
```

Each example includes:
- Implementation with detailed comments
- Dry run showing step-by-step execution
- Performance analysis
- Trade-offs discussion
- Real-world use cases
