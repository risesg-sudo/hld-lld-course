# System Design Interview: Common Questions by Difficulty

## Beginner Level (1-2 years experience)

**Simple Systems**:
1. URL Shortener (bit.ly)
2. Pastebin
3. Key-Value Store (Redis-like)
4. Rate Limiter
5. Unique ID Generator
6. Web Crawler
7. Autocomplete/Typeahead
8. Notification Service

**Why these are beginner**:
- Single primary function
- Limited components
- Straightforward scaling patterns
- Good for learning fundamentals

**Focus Areas**:
- Database choice (SQL vs NoSQL)
- Caching strategies
- API design
- Basic scalability (sharding, replication)

**Example: URL Shortener**
```
Core challenge: Generate unique short codes, store mappings
Key decisions: Base62 encoding vs hashing, database choice, caching
Scale: Millions of URLs, read-heavy workload
```

## Intermediate Level (3-5 years experience)

**Social Media**:
1. Twitter
2. Facebook Newsfeed
3. Instagram
4. Reddit
5. TikTok

**Messaging**:
1. WhatsApp
2. Slack
3. Discord

**E-commerce**:
1. Amazon
2. Airbnb
3. DoorDash/Uber Eats

**Media**:
1. YouTube
2. Netflix
3. Spotify
4. Twitch

**Why these are intermediate**:
- Multiple interconnected features
- Complex data models
- Various trade-offs to consider
- Real-world scaling challenges

**Focus Areas**:
- Fan-out strategies (write vs read)
- Real-time updates (WebSockets, long polling)
- Recommendation engines
- CDN strategies
- Polyglot persistence

**Example: Twitter**
```
Core challenges: Newsfeed generation, celebrity problem, real-time updates
Key decisions: Fan-out write vs read, timeline caching, trending topics
Scale: 500M users, 500M tweets/day, read-heavy (100:1)
Trade-offs: Fan-out write (fast reads) vs fan-out read (less storage)
```

## Advanced Level (5+ years experience)

**Real-Time Location**:
1. Uber/Lyft
2. Google Maps
3. Real-time location tracking

**Financial**:
1. Stock Trading Platform
2. PayPal/Payment System
3. Cryptocurrency Exchange
4. Fraud Detection

**Distributed Systems**:
1. Distributed Lock
2. Distributed Task Scheduler
3. Distributed File System (HDFS)
4. Message Queue (Kafka)
5. Service Discovery

**Infrastructure**:
1. Load Balancer
2. API Gateway
3. CDN
4. Monitoring System (Prometheus)
5. Logging System (Splunk)

**Why these are advanced**:
- Ultra-low latency requirements (microseconds)
- Complex distributed coordination
- Strong consistency requirements
- Geographic distribution challenges
- Specialized data structures (QuadTree, S2, Merkle Trees)

**Focus Areas**:
- Geospatial indexing
- Consensus algorithms (Raft, Paxos)
- Event sourcing
- Hardware optimization (bare metal, kernel bypass)
- CAP theorem trade-offs
- Multi-region deployment

**Example: Stock Trading Platform**
```
Core challenges: Sub-millisecond latency, FIFO fairness, strong consistency
Key decisions: Single-threaded matching, event sourcing, hardware optimization
Scale: 100K orders/sec, microsecond latency requirements
Trade-offs: Latency vs throughput, bare metal vs cloud, sync vs async
Unique aspects: Regulatory compliance, deterministic execution, no data loss
```

## How to Approach Based on Difficulty

**Beginner**:
- Focus on fundamentals
- Simple, clear architecture
- Explain basic scaling (vertical → horizontal)
- Don't over-complicate

**Intermediate**:
- Discuss trade-offs extensively
- Multiple database types
- Caching strategies
- Real-world considerations (cost, operations)

**Advanced**:
- Extreme optimization techniques
- Distributed systems theory
- Hardware-level considerations
- Regulatory/compliance aspects
- Multi-region deployment

## Practice Strategy

**Week 1-2**: Master 10 beginner questions
**Week 3-4**: Master 10 intermediate questions
**Week 5-6**: Master 5 advanced questions
**Week 7+**: Mock interviews, iterate based on feedback

**Practice Method**:
1. Set 45-minute timer
2. Go through RADIO framework
3. Record yourself or write solution
4. Compare to reference architectures
5. Note gaps in knowledge
6. Repeat until confident
