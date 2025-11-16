# Week 5: Real-World System Designs

## Overview
This week focuses on designing complete, production-ready systems that power some of the world's most popular applications. We'll explore how to design scalable, fault-tolerant systems that handle millions (or billions) of users.

## Learning Objectives
By the end of this week, you will be able to:
- Design complex real-world systems from scratch
- Make informed trade-offs between consistency, availability, and partition tolerance
- Estimate capacity and scale requirements for large-scale systems
- Apply design patterns to solve real-world problems
- Articulate design decisions clearly in interviews

## Topics Covered

### 1. WhatsApp Architecture
**Location**: [examples/week5/whatsapp/design.md](./examples/week5/whatsapp/design.md)

A messaging platform handling 100B+ messages daily across 2B+ users.

**Key Concepts**:
- Real-time message delivery using WebSockets
- Presence service for online/offline status
- Media storage and delivery
- Group messaging at scale
- End-to-end encryption considerations

**Technologies Explored**:
- WebSockets for persistent connections
- Apache Kafka for message queuing
- Cassandra for message storage
- Redis for caching and presence
- CDN for media delivery

**Scalability Challenges**:
- Handling billions of concurrent connections
- Message ordering and delivery guarantees
- Cross-datacenter synchronization
- Mobile-first optimization

---

### 2. YouTube Architecture
**Location**: [examples/week5/youtube/design.md](./examples/week5/youtube/design.md)

A video platform serving 1B+ hours of video daily.

**Key Concepts**:
- Video upload and transcoding pipeline
- Adaptive bitrate streaming
- Content Delivery Network (CDN) architecture
- Recommendation engine
- View count aggregation at scale

**Technologies Explored**:
- Distributed file systems (GFS/HDFS)
- Video transcoding with FFmpeg
- HLS/DASH for streaming
- Machine Learning for recommendations
- BigTable/Bigtable for metadata

**Scalability Challenges**:
- Storing petabytes of video data
- Global content distribution
- Real-time view count updates
- Personalized recommendations for billions

---

### 3. Uber Architecture
**Location**: [examples/week5/uber/design.md](./examples/week5/uber/design.md)

A ride-sharing platform matching drivers and riders in real-time.

**Key Concepts**:
- Real-time location tracking
- Geospatial indexing (QuadTree, S2)
- Ride matching algorithm
- Dynamic pricing (surge)
- ETA calculation

**Technologies Explored**:
- WebSockets for real-time updates
- Redis with Geospatial indexes
- PostgreSQL with PostGIS
- Kafka for event streaming
- Machine Learning for pricing and ETA

**Scalability Challenges**:
- Processing millions of location updates/second
- Sub-second ride matching
- Global availability across cities
- Handling peak demand (surge)

---

### 4. Stock Trading Platform Architecture
**Location**: [examples/week5/stock_trading/design.md](./examples/week5/stock_trading/design.md)

A high-frequency trading platform requiring ultra-low latency.

**Key Concepts**:
- Order matching engine
- Real-time price feeds
- Low-latency requirements (microseconds)
- Risk management and circuit breakers
- Audit and compliance

**Technologies Explored**:
- In-memory data structures
- LMAX Disruptor pattern
- Event sourcing
- FPGA for order matching
- Time-series databases

**Scalability Challenges**:
- Processing millions of orders/second
- Maintaining order fairness (FIFO)
- Ensuring data consistency
- Meeting regulatory requirements

---

### 5. Interview Preparation Guide
**Location**: [examples/week5/interview_guide.md](./examples/week5/interview_guide.md)

A comprehensive guide to acing system design interviews.

**Contents**:
- 100+ common system design questions
- Structured framework (RADIO)
- Capacity estimation templates
- Trade-off discussions
- Company-specific tips (FAANG+)

---

## Week 5 Learning Path

### Day 1-2: WhatsApp & YouTube
- Study WhatsApp design focusing on real-time messaging
- Understand YouTube's video pipeline and CDN architecture
- Compare trade-offs between consistency and availability
- Practice: Design a simplified messaging app

### Day 3-4: Uber & Stock Trading Platform
- Learn geospatial indexing for location-based services
- Understand low-latency requirements for trading
- Study event-driven architectures
- Practice: Design a food delivery app

### Day 5-7: Interview Preparation
- Review all 4 system designs
- Practice the RADIO framework
- Solve 10+ system design questions
- Mock interview with peers

---

## Common Patterns Across Systems

### 1. Scalability Patterns
- **Horizontal Scaling**: Add more servers (all systems)
- **Database Sharding**: Partition data across databases
- **Caching**: Redis/Memcached for hot data
- **CDN**: Global content distribution
- **Load Balancing**: Distribute traffic evenly

### 2. Reliability Patterns
- **Replication**: Data redundancy (master-slave, multi-master)
- **Failover**: Automatic recovery from failures
- **Circuit Breaker**: Prevent cascade failures
- **Retry with Exponential Backoff**: Handle transient failures
- **Health Checks**: Monitor service health

### 3. Performance Patterns
- **Connection Pooling**: Reuse database connections
- **Asynchronous Processing**: Background jobs for heavy tasks
- **Batch Processing**: Group operations for efficiency
- **Denormalization**: Trade storage for speed
- **Indexing**: Speed up data retrieval

### 4. Data Patterns
- **Event Sourcing**: Store state changes as events
- **CQRS**: Separate read and write models
- **Saga Pattern**: Distributed transactions
- **Change Data Capture (CDC)**: Track database changes
- **Data Partitioning**: Shard data by key ranges

---

## Capacity Estimation Framework

### Step 1: Understand Scale
```
Daily Active Users (DAU)
Monthly Active Users (MAU)
Peak concurrent users
Growth rate
```

### Step 2: Calculate Traffic
```
Requests per second (RPS) = DAU × Actions per user / 86400
Peak RPS = Average RPS × Peak factor (2-5x)
```

### Step 3: Storage Estimation
```
Data per user
Retention period
Replication factor
Total storage = Users × Data per user × Retention × Replication
```

### Step 4: Bandwidth Estimation
```
Incoming = Writes × Average request size × RPS
Outgoing = Reads × Average response size × RPS
```

### Step 5: Memory/Cache Estimation
```
Cache size = Hot data percentage × Total data
Follow 80-20 rule (20% data = 80% traffic)
```

---

## Technology Decision Matrix

| Requirement | Technology Options | Best For |
|-------------|-------------------|----------|
| **Real-time Communication** | WebSockets, SSE, Long Polling | WhatsApp, Uber live tracking |
| **Message Queue** | Kafka, RabbitMQ, SQS | Asynchronous processing |
| **Database (SQL)** | PostgreSQL, MySQL | Structured data, ACID |
| **Database (NoSQL)** | Cassandra, MongoDB, DynamoDB | High write throughput |
| **Caching** | Redis, Memcached | Session, hot data |
| **Search** | Elasticsearch, Solr | Full-text search |
| **File Storage** | S3, GCS, HDFS | Media, documents |
| **CDN** | CloudFlare, Akamai, CloudFront | Static content, videos |
| **Load Balancer** | Nginx, HAProxy, AWS ALB | Traffic distribution |
| **Monitoring** | Prometheus, Grafana, Datadog | Metrics, alerts |

---

## Trade-offs Discussion Framework

When discussing any design decision, consider:

### 1. Consistency vs Availability (CAP Theorem)
- **Strong Consistency**: All nodes see same data (banks, trading)
- **Eventual Consistency**: Data propagates eventually (social media)
- **Choose based on**: Business requirements, user expectations

### 2. Latency vs Throughput
- **Low Latency**: Fast response time (gaming, trading)
- **High Throughput**: Many requests/second (analytics)
- **Trade-off**: More complex to optimize both

### 3. SQL vs NoSQL
- **SQL**: ACID, complex queries, relations
- **NoSQL**: Scalability, flexibility, high throughput
- **Choose based on**: Data structure, scale, query patterns

### 4. Synchronous vs Asynchronous
- **Sync**: Immediate response, simpler logic
- **Async**: Better throughput, resilience, complexity
- **Choose based on**: User expectations, system coupling

### 5. Normalization vs Denormalization
- **Normalized**: Less storage, data integrity
- **Denormalized**: Faster reads, more storage
- **Choose based on**: Read/write ratio, query patterns

---

## Interview Best Practices

### 1. Clarify Requirements (5 min)
- Ask about users, scale, features
- Functional vs non-functional requirements
- Constraints (budget, time, team size)

### 2. High-Level Design (10-15 min)
- Draw boxes and arrows
- Identify major components
- Explain data flow
- Discuss APIs

### 3. Deep Dive (15-20 min)
- Scale estimation
- Database schema
- Component details
- Bottlenecks and solutions

### 4. Wrap Up (5 min)
- Monitoring and maintenance
- Future enhancements
- Trade-offs summary
- Questions for interviewer

### Common Mistakes to Avoid
- Jumping to solution without clarifying
- Over-engineering for small scale
- Under-estimating at large scale
- Ignoring non-functional requirements
- Not discussing trade-offs
- Poor communication

---

## Practice Problems

### Beginner Level
1. Design a URL shortener (bit.ly)
2. Design a pastebin (pastebin.com)
3. Design a rate limiter
4. Design a notification service

### Intermediate Level
5. Design Instagram
6. Design Twitter
7. Design a web crawler
8. Design a typeahead/autocomplete
9. Design a proximity service (Yelp)
10. Design a ride-sharing service (Uber)

### Advanced Level
11. Design Netflix
12. Design a distributed cache
13. Design a search engine (Google)
14. Design a chat application (WhatsApp)
15. Design a stock exchange

---

## Additional Resources

### Books
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "System Design Interview" by Alex Xu (Volume 1 & 2)
- "Web Scalability for Startup Engineers" by Artur Ejsmont

### Online Resources
- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [High Scalability Blog](http://highscalability.com/)
- Engineering blogs: Netflix, Uber, Airbnb, LinkedIn

### Video Resources
- Gaurav Sen's System Design playlist
- Tech Dummies Narendra L
- InfoQ presentations on architecture

---

## Weekly Assignment

### Part 1: Individual Designs
Design each of the following systems (written + diagrams):
1. WhatsApp messaging system
2. YouTube video platform
3. Uber ride-sharing
4. Stock trading platform

### Part 2: Comparative Analysis
Write a 2-page analysis comparing:
- Database choices across systems
- Consistency requirements
- Scalability strategies
- Technology stack decisions

### Part 3: Mock Interview
- Record yourself designing a system (30 min)
- Get feedback from peers or mentors
- Identify areas for improvement

### Submission Format
```
week5_submission/
├── whatsapp_design.md
├── youtube_design.md
├── uber_design.md
├── trading_platform_design.md
├── comparative_analysis.md
└── mock_interview_recording.mp4
```

---

## Next Steps

After completing Week 5:
1. Review all 5 weeks of HLD content
2. Practice 20+ system design problems
3. Participate in mock interviews
4. Study company-specific architectures
5. Read engineering blogs regularly

**Pro Tip**: The best way to learn system design is to actually build systems. Try implementing simplified versions of these designs!

---

## Summary

Week 5 brings together everything learned in previous weeks:
- **Week 1**: Fundamentals (scaling, databases, caching)
- **Week 2**: Components (load balancers, CDN, message queues)
- **Week 3**: Data design (SQL vs NoSQL, sharding, replication)
- **Week 4**: Advanced patterns (microservices, distributed systems)
- **Week 5**: Real-world applications (WhatsApp, YouTube, Uber, Trading)

You're now equipped to design any large-scale system and ace system design interviews!
