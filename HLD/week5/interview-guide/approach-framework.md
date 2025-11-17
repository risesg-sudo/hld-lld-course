# System Design Interview: Approach Framework

## The RADIO Framework

Use this structured approach for every system design interview:

### R - Requirements (5-10 minutes)

**Goal**: Understand what you're building before proposing solutions.

**Questions to Ask**:
- Scale: How many users? DAU vs MAU?
- Features: What are core features? What's out of scope?
- Performance: Latency requirements? Availability target?
- Platform: Mobile, web, both?
- Constraints: Budget? Timeline? Team size?

**Why this matters**: Same problem has different solutions at 1K vs 1B users. Requirements drive every design decision.

**Example**:
```
Interviewer: "Design Twitter"

You: "Let me clarify requirements:
- Scale: How many users and tweets per day?
- Features: Post tweets, follow, timeline. Search? Trending? DMs?
- Latency: What's acceptable timeline load time?
- Should we optimize for read-heavy or write-heavy?"
```

**Categorize Requirements**:
- Functional: What the system does
- Non-Functional: How well it performs (scalability, latency, availability)

### A - Architecture (10-15 minutes)

**Goal**: Draw high-level design with boxes and arrows.

**Components to Include**:
1. Clients (web, mobile)
2. Load balancer
3. Application servers
4. Databases (SQL/NoSQL)
5. Cache (Redis, Memcached)
6. Message queue (Kafka, RabbitMQ)
7. CDN (for static content)
8. Object storage (S3 for media)

**Best Practices**:
- Start simple, add complexity only when needed
- Label arrows with data flow
- Explain what each component does
- Call out technology choices (PostgreSQL vs Cassandra, etc.)

### D - Deep Dive (15-20 minutes)

**Interviewer will guide** which components to explore. Common deep dives:

**Database Schema**:
```sql
CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  username VARCHAR(50),
  created_at TIMESTAMP
);
```

**API Design**:
```http
POST /api/v1/tweets
{
  "content": "Hello world",
  "user_id": "123"
}
```

**Algorithms**: Newsfeed ranking, recommendation, matching

**Scaling Strategies**: Sharding, replication, caching

**Be Ready to Code**: Pseudocode for critical algorithms

### I - Issues & Bottlenecks (5-10 minutes)

**Goal**: Identify problems and propose solutions.

**Common Bottlenecks**:
- Database: Write/read bottleneck, hot partitions
- Single point of failure
- Race conditions
- Cache invalidation
- Memory limits

**For Each Bottleneck**:
1. Identify the issue
2. Explain impact
3. Propose solution(s)

**Example**:
```
Issue: Celebrity with 100M followers posts tweet
Impact: Fan-out write creates 100M timeline writes → database overload
Solution: Hybrid approach - fan-out for normal users, on-demand load for celebrities
```

### O - Optimizations (5 minutes)

**Goal**: Suggest improvements and future enhancements.

**Categories**:
- Performance: CDN, caching, indexing, denormalization
- Cost: Tiered storage, compression, deduplication
- Reliability: Replication, failover, circuit breakers
- Monitoring: Metrics, alerts, dashboards

**Extensions**: Additional features, alternative approaches

## Interview Tips

**Think Out Loud**: Explain your reasoning as you design.

**Ask Questions**: Don't assume - clarify ambiguities.

**Discuss Trade-offs**: Every decision has pros/cons. Articulate both.

**Be Flexible**: If interviewer challenges your design, reconsider. Don't be defensive.

**Manage Time**: Don't spend 30 minutes on requirements. Follow RADIO timing.

**Draw Diagrams**: Visual communication is key in system design.

**Acknowledge Limitations**: "I don't know" is better than making up answers.

## Common Mistakes to Avoid

**Jumping to solution**: Clarify requirements first.

**Over-engineering**: Don't use Kafka for 100 users.

**Under-engineering**: Don't use single MySQL for 1B users.

**Not discussing trade-offs**: Always explain why you chose X over Y.

**Ignoring non-functional requirements**: Scalability, latency, availability matter.

**Poor communication**: Long silences, unclear explanations.

**Not asking questions**: Making assumptions instead of clarifying.

**Focusing only on happy path**: Discuss failures, edge cases.

**Being rigid**: Accept feedback, adapt design.

**Not managing time**: Rushing through critical sections.
