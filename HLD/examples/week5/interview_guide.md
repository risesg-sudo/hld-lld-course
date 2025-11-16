# System Design Interview Guide

## Table of Contents
1. [Interview Framework (RADIO)](#interview-framework-radio)
2. [Capacity Estimation Templates](#capacity-estimation-templates)
3. [100+ System Design Questions](#100-system-design-questions)
4. [How to Discuss Trade-offs](#how-to-discuss-trade-offs)
5. [Company-Specific Tips](#company-specific-tips)
6. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
7. [Sample Interview Walkthrough](#sample-interview-walkthrough)

---

## Interview Framework (RADIO)

Use the **RADIO** framework for every system design interview:

### R - Requirements (5-10 minutes)

**Goal**: Understand what you're building

**Questions to Ask**:
1. **Users**: How many users? DAU vs MAU?
2. **Scale**: How many requests/second? Data volume?
3. **Features**: What are the core features? What's out of scope?
4. **Platform**: Mobile, web, both?
5. **Performance**: Latency requirements? Availability?
6. **Constraints**: Budget? Timeline? Team size?

**Categorize Requirements**:
- **Functional**: What the system does (features)
- **Non-Functional**: How the system performs (scalability, latency, etc.)

**Example** (Design Twitter):
```
Interviewer: "Design Twitter"

You: "Let me clarify the requirements:
- Should users be able to post tweets, follow users, and view timeline?
- What's the scale? How many users and tweets per day?
- Do we need to support media (images, videos)?
- What about search, trending, notifications?
- What are the latency requirements for timeline load?
- Should we focus on read-heavy or write-heavy optimization?"

Functional Requirements:
✓ Post tweets (280 chars)
✓ Follow/unfollow users
✓ View home timeline (tweets from followed users)
✓ View user profile

Non-Functional Requirements:
✓ 500M users, 100M DAU
✓ Read-heavy (100:1 read/write ratio)
✓ Timeline load < 200ms
✓ High availability (99.9%)
✓ Eventual consistency acceptable
```

### A - Architecture (10-15 minutes)

**Goal**: Draw high-level design with boxes and arrows

**Components to Include**:
1. **Clients**: Web, mobile, desktop
2. **Load Balancer**: Distribute traffic
3. **Application Servers**: Business logic
4. **Databases**: Storage (SQL, NoSQL)
5. **Cache**: Redis, Memcached
6. **Message Queue**: Kafka, RabbitMQ
7. **CDN**: Static content delivery
8. **Object Storage**: S3 for media files

**Flow**:
1. Draw client → load balancer → servers
2. Add databases and cache
3. Add supporting services (queues, CDN, etc.)
4. Show data flow with arrows
5. Explain briefly what each component does

**Example** (Twitter Architecture):
```
┌──────────┐
│  Client  │
└─────┬────┘
      │
      ▼
┌──────────────┐
│Load Balancer │
└──────┬───────┘
       │
   ┌───┴───┐
   ▼       ▼
┌─────┐ ┌─────┐
│ API │ │ API │
│Srvr │ │Srvr │
└──┬──┘ └──┬──┘
   │       │
   └───┬───┘
       │
   ┌───┴────┬─────────┬─────────┐
   ▼        ▼         ▼         ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Redis │ │MySQL │ │Kafka │ │  S3  │
│Cache │ │ User │ │Queue │ │Media │
└──────┘ └──────┘ └──────┘ └──────┘
```

### D - Deep Dive (15-20 minutes)

**Goal**: Drill into 2-3 components in detail

**Interviewer will guide** which components to discuss. Common deep dives:
1. **Database Schema**: Tables, indexes, relationships
2. **API Design**: Endpoints, request/response formats
3. **Scalability**: How to handle 10x, 100x growth
4. **Caching Strategy**: What to cache, invalidation
5. **Specific Algorithm**: Newsfeed ranking, recommendation, etc.

**Be Ready to Discuss**:
- Data models (SQL schema, NoSQL documents)
- API endpoints (REST, GraphQL, gRPC)
- Algorithms (ranking, matching, searching)
- Scaling strategies (sharding, replication, caching)

**Example** (Twitter Timeline Generation):
```python
# Approach 1: Fan-out on write (Write-heavy)
def post_tweet(user_id, tweet):
    tweet_id = generate_id()
    save_tweet(tweet_id, user_id, tweet)

    # Get all followers
    followers = get_followers(user_id)

    # Write to each follower's timeline (fan-out)
    for follower in followers:
        timeline_cache.add(follower, tweet_id)

# Approach 2: Fan-out on read (Read-heavy)
def get_timeline(user_id):
    # Get all followed users
    following = get_following(user_id)

    # Fetch recent tweets from each
    tweets = []
    for followed_user in following:
        tweets.extend(get_recent_tweets(followed_user, limit=100))

    # Merge and sort by time
    return sorted(tweets, key=lambda t: t.timestamp, reverse=True)[:50]

# Hybrid approach (best for Twitter):
# - Fan-out on write for most users
# - Fan-out on read for celebrities (too many followers)
```

### I - Issues & Bottlenecks (5-10 minutes)

**Goal**: Identify potential problems and solutions

**Common Bottlenecks**:
1. **Database**: Write/read bottleneck, hot partitions
2. **Network**: Bandwidth, latency
3. **Single Point of Failure**: One component crashes → system down
4. **Race Conditions**: Concurrent updates to same data
5. **Memory**: Cache overflow, memory leaks

**For Each Bottleneck**:
- Identify the issue
- Explain impact
- Propose solution(s)

**Example** (Twitter Bottlenecks):
```
1. Celebrity Problem (Lady Gaga with 100M followers)
   - Issue: Fan-out on write → 100M timeline writes per tweet
   - Impact: Slow tweet posting, DB overload
   - Solution: Fan-out on read for celebrities, hybrid approach

2. Timeline Generation Latency
   - Issue: Fetching from 1000 followed users is slow
   - Impact: Timeline load > 1 second
   - Solution: Pre-compute timelines, cache aggressively

3. Database Write Hotspot
   - Issue: All tweets to one DB shard (if sharded by user_id)
   - Impact: One shard overloaded
   - Solution: Shard by tweet_id (better distribution)

4. Cache Invalidation
   - Issue: User unfollows → need to remove tweets from cache
   - Impact: Stale data, cache inconsistency
   - Solution: Lazy invalidation, TTL-based expiry
```

### O - Optimizations & Extensions (5 minutes)

**Goal**: Suggest improvements and future enhancements

**Optimizations**:
- **Performance**: CDN, caching, indexing, denormalization
- **Cost**: Tiered storage, compression, deduplication
- **Reliability**: Replication, failover, circuit breakers
- **Monitoring**: Metrics, alerts, dashboards

**Extensions** (if time permits):
- Additional features
- Advanced use cases
- Alternative approaches

**Example** (Twitter Optimizations):
```
Performance:
- CDN for profile images, media
- Read replicas for database (10+)
- GraphQL for mobile (reduce bandwidth)

Cost:
- Compress old tweets (after 30 days)
- Archive inactive users (no login in 1 year)
- Tiered storage (hot/warm/cold)

Reliability:
- Multi-region deployment
- Automatic failover
- Rate limiting (prevent spam)

Extensions:
- Trending topics (aggregation + ML)
- Recommendations (collaborative filtering)
- Spaces (live audio rooms)
- Monetization (Super Follows)
```

---

## Capacity Estimation Templates

### Template 1: Traffic Estimation

```
Given:
- Daily Active Users (DAU) = X
- Actions per user per day = Y

Calculations:
1. Requests per day = DAU × Y
2. Requests per second (RPS) = Requests per day / 86,400
3. Peak RPS = Average RPS × Peak factor (2-5x)

Example (YouTube):
- DAU = 500M
- Videos watched = 5 per day

RPS = 500M × 5 / 86,400 = 28,935 requests/sec
Peak = 28,935 × 3 = 86,805 requests/sec
```

### Template 2: Storage Estimation

```
Given:
- Number of entities = X
- Size per entity = Y bytes
- Retention period = Z days/years

Calculations:
1. Total storage = X × Y
2. With retention = (X per day × Z days)
3. With replication = Total × Replication factor (3x)

Example (Twitter):
- Tweets per day = 500M
- Size per tweet = 300 bytes (avg)
- Retention = 5 years

Daily storage = 500M × 300 bytes = 150 GB/day
5-year storage = 150 GB × 365 × 5 = 274 TB
With replication (3x) = 822 TB
```

### Template 3: Bandwidth Estimation

```
Given:
- Requests per second = X
- Request size = Y bytes
- Response size = Z bytes

Calculations:
1. Incoming bandwidth = X × Y
2. Outgoing bandwidth = X × Z
3. Total bandwidth = Incoming + Outgoing

Example (Image Upload Service):
- Uploads = 1,000/sec
- Image size = 2 MB

Incoming = 1,000 × 2 MB = 2 GB/sec = 16 Gbps
```

### Template 4: Cache Size Estimation

```
Given:
- Total data = X
- Hot data percentage = Y% (typically 20%)

Calculation:
Cache size = X × Y%

Example (Netflix):
- Total videos = 100 PB
- Hot videos (80-20 rule) = 20%

Cache needed = 100 PB × 20% = 20 PB (distributed globally)
```

### Quick Reference Numbers

**Latency**:
- L1 cache: 0.5 ns
- L2 cache: 7 ns
- RAM: 100 ns
- SSD: 150 μs
- HDD: 10 ms
- Network (same datacenter): 0.5 ms
- Network (cross-region): 50 ms

**Throughput**:
- SSD: 500 MB/sec
- HDD: 100 MB/sec
- Network (1 Gbps): 125 MB/sec
- Network (10 Gbps): 1.25 GB/sec

**Powers of 2**:
- 2^10 = 1K (thousand)
- 2^20 = 1M (million)
- 2^30 = 1B (billion)
- 2^40 = 1T (trillion)

**Time**:
- 1 day = 86,400 seconds (~100K)
- 1 month = 2.6M seconds (~2.5M)
- 1 year = 31.5M seconds (~30M)

---

## 100+ System Design Questions

### Beginner Level (1-2 years experience)

**Basic Systems**:
1. Design a URL shortener (bit.ly)
2. Design a pastebin (pastebin.com)
3. Design a key-value store (Redis)
4. Design a rate limiter
5. Design a unique ID generator
6. Design a web crawler
7. Design a autocomplete/typeahead system
8. Design a notification service
9. Design a metrics/monitoring system
10. Design a distributed cache

**Social Features**:
11. Design a comments system
12. Design a like/vote counter
13. Design a leaderboard
14. Design a trending topics system
15. Design a hashtag system

**Content Systems**:
16. Design a blog platform (Medium)
17. Design a photo sharing app (Instagram - basic)
18. Design a Q&A platform (StackOverflow - basic)
19. Design a bookmarking service (Pocket)
20. Design a file sharing service (Dropbox - basic)

### Intermediate Level (3-5 years experience)

**Social Media**:
21. Design Twitter
22. Design Facebook Newsfeed
23. Design Instagram
24. Design LinkedIn
25. Design Reddit
26. Design TikTok
27. Design Pinterest
28. Design Snapchat
29. Design Discord
30. Design Clubhouse (audio rooms)

**Messaging & Communication**:
31. Design WhatsApp
32. Design Facebook Messenger
33. Design Slack
34. Design Zoom (video conferencing)
35. Design Telegram
36. Design a group chat system
37. Design a notification system at scale

**E-commerce & Marketplace**:
38. Design Amazon
39. Design eBay
40. Design Airbnb
41. Design DoorDash/Uber Eats
42. Design Shopify
43. Design a flash sale system
44. Design a coupon system
45. Design a recommendation engine

**Media & Entertainment**:
46. Design YouTube
47. Design Netflix
48. Design Spotify
49. Design Twitch
50. Design a podcast platform
51. Design a live streaming service
52. Design a music streaming service

**Productivity & Collaboration**:
53. Design Google Drive
54. Design Google Docs (collaborative editing)
55. Design Trello (kanban board)
56. Design Notion
57. Design a calendar system (Google Calendar)
58. Design a task management system
59. Design a wiki system (Confluence)

**Search & Discovery**:
60. Design Google Search
61. Design Yelp
62. Design a proximity service
63. Design an autocomplete system
64. Design a spell checker
65. Design a search ranking system

### Advanced Level (5+ years experience)

**Ride Sharing & Maps**:
66. Design Uber
67. Design Lyft
68. Design Google Maps
69. Design a real-time location tracking system
70. Design a route optimization system
71. Design a geofencing system
72. Design a parking spot finder

**Financial Systems**:
73. Design a payment system (PayPal)
74. Design a stock trading platform
75. Design a cryptocurrency exchange
76. Design a digital wallet
77. Design a fraud detection system
78. Design a credit card transaction system
79. Design Venmo/CashApp

**Gaming & Real-time**:
80. Design a multiplayer game backend
81. Design a leaderboard for games
82. Design a matchmaking system
83. Design a real-time analytics system
84. Design a live scoreboard
85. Design an online chess platform

**Distributed Systems**:
86. Design a distributed lock
87. Design a distributed task scheduler
88. Design a distributed file system (HDFS)
89. Design a distributed database
90. Design a consensus system (Raft/Paxos)
91. Design a message queue (Kafka)
92. Design a service discovery system

**Advanced Platforms**:
93. Design GitHub
94. Design StackOverflow
95. Design Quora
96. Design a code review system
97. Design a CI/CD pipeline
98. Design a feature flag system
99. Design an A/B testing platform
100. Design a load balancer

**Infrastructure & Monitoring**:
101. Design a logging system (Splunk)
102. Design a metrics system (Prometheus)
103. Design a distributed tracing system (Jaeger)
104. Design an alerting system
105. Design a CDN
106. Design an API gateway
107. Design a rate limiting system
108. Design a circuit breaker

**AI/ML Systems**:
109. Design a recommendation system
110. Design a search ranking system
111. Design a spam detection system
112. Design an image recognition system
113. Design a chatbot platform
114. Design a voice assistant (Alexa)

**Additional Complex Systems**:
115. Design Ticketmaster (ticket booking)
116. Design a hotel reservation system
117. Design an airline reservation system
118. Design a library management system
119. Design a parking lot system
120. Design an elevator system

---

## How to Discuss Trade-offs

Every design decision has trade-offs. **Always articulate both sides**:

### Framework for Trade-offs

```
When choosing between X and Y:

Approach X:
✓ Pros: [advantages]
✗ Cons: [disadvantages]
Use case: [when to use]

Approach Y:
✓ Pros: [advantages]
✗ Cons: [disadvantages]
Use case: [when to use]

My Choice: [X/Y] because [reasoning based on requirements]
```

### Common Trade-off Scenarios

#### 1. SQL vs NoSQL

**SQL (PostgreSQL, MySQL)**:
- ✓ ACID guarantees (consistency)
- ✓ Complex queries (JOINs)
- ✓ Data integrity (foreign keys)
- ✗ Harder to scale horizontally
- ✗ Schema changes can be painful
- **Use**: Financial systems, structured data, complex relationships

**NoSQL (MongoDB, Cassandra)**:
- ✓ Horizontal scalability
- ✓ Flexible schema
- ✓ High write throughput
- ✗ No ACID (eventual consistency)
- ✗ Limited query capabilities
- **Use**: Social media, IoT, high-scale writes

**Discussion**:
"For Twitter, I'd use SQL for user profiles (structured, relationships) and NoSQL (Cassandra) for tweets (high volume, simple queries)."

#### 2. Normalization vs Denormalization

**Normalized**:
- ✓ No data duplication (save storage)
- ✓ Data consistency
- ✓ Easy updates
- ✗ Slower reads (JOINs)
- **Use**: Write-heavy systems

**Denormalized**:
- ✓ Faster reads (no JOINs)
- ✓ Simple queries
- ✗ Data duplication (more storage)
- ✗ Update complexity (multiple places)
- **Use**: Read-heavy systems (YouTube metadata)

**Discussion**:
"YouTube is 100:1 read/write. I'd denormalize video metadata (include channel name in video table) for faster reads, accepting storage cost."

#### 3. Consistency vs Availability (CAP Theorem)

**Strong Consistency**:
- ✓ All reads see latest write
- ✓ Simple reasoning
- ✗ Slower (coordination overhead)
- ✗ Less available during partition
- **Use**: Banks, stock trading

**Eventual Consistency**:
- ✓ Higher availability
- ✓ Lower latency
- ✗ Reads may return stale data
- ✗ Complex conflict resolution
- **Use**: Social media, analytics

**Discussion**:
"For Instagram likes, eventual consistency is fine. If count is 100 vs 101, user doesn't care. But for bank balance, we need strong consistency."

#### 4. Synchronous vs Asynchronous

**Synchronous**:
- ✓ Immediate feedback
- ✓ Simple error handling
- ✗ Slower (blocking)
- ✗ Tight coupling
- **Use**: Payment processing, order placement

**Asynchronous**:
- ✓ Better throughput
- ✓ Resilience (queue buffers)
- ✗ Complex error handling
- ✗ No immediate confirmation
- **Use**: Email sending, video transcoding

**Discussion**:
"For video upload on YouTube, I'd acknowledge upload immediately (sync) but transcode asynchronously. User doesn't need to wait for transcoding."

#### 5. Push vs Pull

**Push (Server pushes updates)**:
- ✓ Real-time updates
- ✓ Low latency
- ✗ Server maintains connections
- ✗ Scalability challenges
- **Use**: Chat (WhatsApp), live scores

**Pull (Client polls server)**:
- ✓ Simple server (stateless)
- ✓ Easier to scale
- ✗ Higher latency (poll interval)
- ✗ Wasted requests (polling when no updates)
- **Use**: Email, less time-sensitive

**Discussion**:
"For WhatsApp, push via WebSockets for real-time delivery. For email, pull is fine (check every 5 minutes)."

#### 6. Horizontal vs Vertical Scaling

**Horizontal (Add more servers)**:
- ✓ Linear scaling
- ✓ Fault tolerance
- ✓ Cost-effective (commodity hardware)
- ✗ Complex (load balancing, data partitioning)
- **Use**: Web servers, stateless services

**Vertical (Bigger server)**:
- ✓ Simple (no distributed complexity)
- ✓ No network overhead
- ✗ Limited (hardware ceiling)
- ✗ Single point of failure
- **Use**: Databases (until limits reached)

**Discussion**:
"Start vertical for simplicity. Once hitting limits (16-core, 256GB RAM), go horizontal. Most modern systems are horizontal."

---

## Company-Specific Tips

### Google

**Focus**:
- Scalability (billions of users)
- Efficiency (cost optimization)
- Innovation (novel approaches)

**Common Questions**:
- Design Google Search
- Design YouTube
- Design Gmail
- Design Google Maps
- Design Google Drive

**Tips**:
- Emphasize distributed systems
- Discuss data center efficiency
- Mention Google tech (Bigtable, Spanner, etc.)
- Focus on algorithms (PageRank, etc.)

### Facebook/Meta

**Focus**:
- Social graphs
- Real-time updates
- Newsfeed ranking
- Mobile-first

**Common Questions**:
- Design Facebook Newsfeed
- Design Instagram
- Design WhatsApp
- Design Messenger
- Design Facebook Groups

**Tips**:
- Discuss graph databases (TAO)
- Fan-out strategies
- Edge computing (mobile optimization)
- A/B testing for ranking

### Amazon

**Focus**:
- E-commerce
- Reliability (orders can't fail)
- Operational excellence
- Leadership principles

**Common Questions**:
- Design Amazon.com
- Design Prime Video
- Design AWS S3
- Design DynamoDB
- Design a recommendation engine

**Tips**:
- Discuss inventory management
- Payment reliability (retries, idempotency)
- Distributed systems (AWS services)
- Cost optimization

### Netflix

**Focus**:
- Video streaming
- CDN architecture
- Personalization
- Chaos engineering

**Common Questions**:
- Design Netflix
- Design a CDN
- Design a recommendation system
- Design video encoding pipeline

**Tips**:
- Discuss adaptive streaming (ABR)
- CDN strategies (multi-tier caching)
- A/B testing at scale
- Chaos Monkey (resilience)

### Uber/Lyft

**Focus**:
- Real-time systems
- Geospatial indexing
- Matching algorithms
- Mobile-first

**Common Questions**:
- Design Uber
- Design UberEats
- Design real-time location tracking
- Design surge pricing

**Tips**:
- Geospatial data structures (QuadTree, S2)
- Real-time updates (WebSockets)
- Event-driven architecture (Kafka)
- Mobile optimization (low bandwidth)

### Twitter

**Focus**:
- Real-time
- High read/write ratio
- Trending algorithms
- API design

**Common Questions**:
- Design Twitter
- Design trending topics
- Design Twitter timeline
- Design search

**Tips**:
- Fan-out strategies
- Celebrity problem (hybrid approach)
- Real-time analytics
- Spam/abuse prevention

### Airbnb

**Focus**:
- Search & discovery
- Booking systems
- Payment reliability
- Two-sided marketplace

**Common Questions**:
- Design Airbnb
- Design search ranking
- Design booking system
- Design payment processing

**Tips**:
- Elasticsearch for search
- Double-booking prevention
- Payment idempotency
- Review/rating system

---

## Common Mistakes to Avoid

### 1. Jumping to Solution Too Quickly

**Mistake**:
```
Interviewer: "Design Twitter"
You: "I'll use PostgreSQL for users, Redis for cache, Kafka for..."
```

**Correct**:
```
Interviewer: "Design Twitter"
You: "Let me clarify requirements first. How many users?
     What features are in scope? Read/write ratio?"
```

**Why**: Requirements drive design. Same problem has different solutions at different scales.

### 2. Over-Engineering for Small Scale

**Mistake** (for 1000 users):
```
"I'll use Kafka for messaging, Cassandra for storage,
Redis cluster with 10 shards, Kubernetes for orchestration..."
```

**Correct**:
```
"For 1000 users, a single PostgreSQL instance and basic
caching with Redis would suffice. We can scale later."
```

**Why**: Simple is better. Don't use distributed systems for 1000 users.

### 3. Under-Engineering for Large Scale

**Mistake** (for 1 billion users):
```
"A single MySQL database should handle it."
```

**Correct**:
```
"We need to shard the database, use read replicas,
implement caching, and consider NoSQL for some use cases."
```

**Why**: Single database can't handle billions of users.

### 4. Not Discussing Trade-offs

**Mistake**:
```
"I'll use NoSQL because it's scalable."
```

**Correct**:
```
"NoSQL provides better horizontal scalability and flexibility,
but we lose ACID guarantees and complex queries. For this
use case (high writes, simple queries), the trade-off is worth it."
```

**Why**: Shows critical thinking and understanding of trade-offs.

### 5. Ignoring Non-Functional Requirements

**Mistake**: Only discussing features, ignoring latency/availability

**Correct**: Address scalability, latency, availability, consistency explicitly

### 6. Poor Communication

**Mistake**:
- Long silence while thinking
- Mumbling or unclear speech
- Not checking if interviewer follows

**Correct**:
- Think out loud
- Draw diagrams
- Ask "Does this make sense?" periodically

### 7. Not Asking Questions

**Mistake**: Making assumptions without asking

**Correct**: "Should I assume X, or would you like me to consider Y?"

### 8. Focusing Only on Happy Path

**Mistake**: Not discussing failures, edge cases

**Correct**: Discuss failures, retries, monitoring, alerts

### 9. Being Too Rigid

**Mistake**: Defending your design when interviewer challenges

**Correct**: "That's a good point. Let me reconsider..."

### 10. Not Managing Time

**Mistake**: Spending 30 minutes on requirements, rushing the rest

**Correct**: Follow RADIO framework timing (see above)

---

## Sample Interview Walkthrough

**Question**: Design a URL shortener (like bit.ly)

### Phase 1: Requirements (5 min)

**You**: "Let me clarify the requirements:
1. Users can submit a long URL and get a short URL?
2. When accessing the short URL, redirect to the original?
3. What's the scale? How many URLs shortened per day?
4. Do we need analytics (click tracking)?
5. Custom short URLs allowed?
6. Expiration of links?
7. Any rate limiting required?"

**Interviewer**: "Yes to 1 and 2. Let's say 100M URLs created per day, 1B redirects. Analytics would be nice but not critical. No custom URLs. Links don't expire. Yes, rate limit to prevent abuse."

**You**: "Got it. So:

**Functional**:
- Shorten URL
- Redirect short → long
- Basic analytics (click count)

**Non-Functional**:
- 100M writes/day
- 1B reads/day (10:1 read/write ratio)
- Low latency redirects (< 100ms)
- High availability (99.9%)
- Rate limiting"

### Phase 2: High-Level Architecture (10 min)

**You**: "Let me draw the high-level architecture:

```
Client
   │
   ▼
Load Balancer
   │
   ├──────────┬──────────┐
   ▼          ▼          ▼
 API       API        API
Server    Server    Server
   │
   ├─────┬─────┬─────┐
   ▼     ▼     ▼     ▼
 Cache  DB   Queue  S3
(Redis) (PG) (Kafka)(Analytics)
```

**Flow for shortening**:
1. Client sends long URL to API
2. API generates short code
3. Store mapping in database
4. Return short URL to client

**Flow for redirect**:
1. Client accesses short URL
2. API looks up in cache (Redis)
3. If miss, query database
4. Redirect to long URL
5. Increment click count (async via Kafka)

**Interviewer**: "How do you generate the short code?"

**You**: "Good question. I have two approaches:

**Approach 1: Hash-based**
- Hash the long URL (MD5, SHA256)
- Take first 6-7 characters
- Pros: Deterministic (same URL → same short code)
- Cons: Collision handling needed

**Approach 2: Counter-based**
- Auto-incrementing counter
- Encode to base62 (a-z, A-Z, 0-9)
- Counter 1 → 'b', 125 → 'cb', etc.
- Pros: No collisions, short codes
- Cons: Predictable, need distributed counter

I'd go with **base62 encoding** for simplicity and guaranteed uniqueness."

### Phase 3: Deep Dive (15 min)

**Interviewer**: "Show me the database schema and API."

**You**: "Sure.

**Database Schema (PostgreSQL)**:
```sql
CREATE TABLE urls (
  id BIGSERIAL PRIMARY KEY,
  short_code VARCHAR(7) UNIQUE NOT NULL,
  long_url TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  click_count BIGINT DEFAULT 0,
  INDEX idx_short_code (short_code)
);
```

**API Design**:

```http
POST /api/v1/shorten
Content-Type: application/json

Request:
{
  "long_url": "https://example.com/very/long/url"
}

Response: 201 Created
{
  "short_url": "https://bit.ly/abc123",
  "short_code": "abc123"
}

---

GET /{short_code}
→ 301 Redirect to long_url
```

**Interviewer**: "How do you handle 1B redirects per day?"

**You**: "That's ~11,500 redirects/sec, peak 3x = 35K/sec. Strategies:

1. **Aggressive Caching** (Redis):
   - Cache all short_code → long_url mappings
   - 100M URLs × 100 bytes = 10 GB (fits in memory)
   - Cache hit ratio: 95%+
   - TTL: None (URLs don't change)

2. **Read Replicas**:
   - 10 read replicas for DB queries
   - 5% cache misses = 575/sec to DB (easily handled)

3. **CDN**:
   - Popular short URLs cached at edge
   - Reduces load on origin

**Caching Strategy**:
```python
def redirect(short_code):
    # Try cache first
    long_url = redis.get(f"short:{short_code}")

    if not long_url:
        # Cache miss, query DB
        long_url = db.query(
            "SELECT long_url FROM urls WHERE short_code = ?",
            short_code
        )

        if long_url:
            # Cache for future requests
            redis.set(f"short:{short_code}", long_url)
        else:
            return 404  # Not found

    # Increment click count (async)
    kafka.publish("clicks", {
        "short_code": short_code,
        "timestamp": now()
    })

    return redirect(long_url, status=301)
```"

**Interviewer**: "What about the distributed counter for generating IDs?"

**You**: "Great question. Options:

**Option 1: Database Auto-increment**
- Simple, but single point of contention
- Won't scale to 100M/day

**Option 2: UUID**
- Unique, distributed
- But too long for short URL

**Option 3: Snowflake ID** (my choice)
```
64-bit ID:
┌────────────────────┬──────┬──────┬────────────┐
│   Timestamp (41)   │DC(5) │Srv(5)│ Sequence(12)│
└────────────────────┴──────┴──────┴────────────┘

- Timestamp: milliseconds since epoch (41 bits)
- Datacenter ID: 5 bits (32 datacenters)
- Server ID: 5 bits (32 servers per DC)
- Sequence: 12 bits (4096 IDs per ms per server)

Benefits:
- Distributed (each server generates independently)
- No coordination needed
- Sortable by time
- Throughput: 4096 IDs/ms/server = 4M/sec/server
```

Then encode to base62 for short code."

### Phase 4: Bottlenecks (5 min)

**Interviewer**: "What are potential bottlenecks?"

**You**:

**1. Database Write Bottleneck**
- 100M writes/day = 1,157/sec (manageable)
- Solution: Batch writes, use SSD, shard if needed

**2. Cache Invalidation**
- If we update long_url, cache is stale
- Solution: Invalidate cache on update, or don't allow edits

**3. Hot Short URLs**
- One viral link → millions of redirects
- Solution: CDN caching, multi-tier cache

**4. ID Generator Failure**
- If Snowflake server crashes, can't generate IDs
- Solution: Multiple servers, failover

**5. Rate Limiting**
- Prevent abuse (1M shortens from one IP)
- Solution: Rate limit by IP (100 requests/hour)

### Phase 5: Optimizations (3 min)

**You**: "Possible optimizations:

**Performance**:
- Pre-warm cache on startup
- Use CDN for static pages
- Async click counting (don't block redirect)

**Cost**:
- Compress analytics data
- Archive old links (> 1 year inactive)

**Reliability**:
- Multi-region deployment
- Database replication
- Monitor cache hit rate

**Extensions** (if time):
- Custom short codes (if not taken)
- Link expiration
- QR code generation
- Analytics dashboard (clicks over time, geography)"

**Interviewer**: "Great! Any questions for me?"

**You**: "Yes, what would be the next steps in the process?"

---

## Additional Resources

### Books
1. **"Designing Data-Intensive Applications"** by Martin Kleppmann (Bible of system design)
2. **"System Design Interview" Vol 1 & 2** by Alex Xu (Interview-focused)
3. **"Web Scalability for Startup Engineers"** by Artur Ejsmont

### Online Courses
1. **Grokking the System Design Interview** (educative.io)
2. **System Design Primer** (GitHub repo by donnemartin)
3. **Gaurav Sen's YouTube** (excellent explanations)

### Practice Platforms
1. **Pramp** (mock interviews with peers)
2. **interviewing.io** (anonymous interviews)
3. **Exponent** (system design practice)

### Blogs to Follow
1. **High Scalability** (highscalability.com)
2. **Netflix Tech Blog**
3. **Uber Engineering Blog**
4. **Airbnb Engineering Blog**
5. **LinkedIn Engineering Blog**

### Key Concepts to Master
- CAP Theorem
- Consistent Hashing
- Bloom Filters
- Load Balancing
- Caching Strategies
- Database Sharding
- Replication (Master-Slave, Multi-Master)
- Message Queues
- Microservices
- API Design (REST, GraphQL, gRPC)

---

## Final Tips

1. **Practice**: Do 20-30 system design problems before interview
2. **Communicate**: Think out loud, draw diagrams
3. **Ask Questions**: Clarify requirements, don't assume
4. **Trade-offs**: Always discuss pros/cons of choices
5. **Be Flexible**: Adapt based on interviewer feedback
6. **Stay Calm**: It's okay to pause and think
7. **Mock Interviews**: Practice with friends/peers
8. **Study Real Systems**: Read engineering blogs, understand actual architectures
9. **Time Management**: Don't spend too long on one section
10. **Be Honest**: Say "I don't know" if you don't, then think through it

**Remember**: The interview is a **conversation**, not an exam. The interviewer wants to see how you think, not just the final answer. Good luck!
