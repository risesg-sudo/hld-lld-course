# When to Use NoSQL Databases

## Massive Scale and High Throughput

Use NoSQL when you need to handle billions of records and millions of operations per second.

### Social Media Platforms

**Twitter - Cassandra for Tweets**
- 500 million tweets per day
- Billions of timeline reads
- Distributed across data centers worldwide

```javascript
// Tweet stored as document
{
    "tweet_id": "1234567890",
    "user_id": "user_alice",
    "text": "NoSQL scales horizontally!",
    "created_at": "2024-01-20T10:30:00Z",
    "likes_count": 0,
    "retweets_count": 0
}

// Sharded by tweet_id across 100s of nodes
// Each node handles a portion of the data
// Linear scalability: add nodes = add capacity
```

### IoT and Sensor Data

Millions of devices sending data every second.

```javascript
// Sensor reading - Time-series data
{
    "sensor_id": "sensor_789",
    "timestamp": "2024-01-20T10:30:00.123Z",
    "temperature": 22.5,
    "humidity": 45.2,
    "pressure": 1013.25
}

// Cassandra partition by sensor_id + time bucket
// Efficient time-range queries
// Automatic data expiration with TTL
```

## Flexible or Evolving Schema

Use NoSQL when your data structure changes frequently or varies between records.

### Product Catalogs

Different product types have different attributes.

```javascript
// Electronics product
{
    "_id": "prod_123",
    "name": "Laptop",
    "category": "electronics",
    "brand": "TechCorp",
    "specs": {
        "cpu": "Intel i7",
        "ram": "16GB",
        "storage": "512GB SSD"
    },
    "warranty_years": 2
}

// Clothing product - completely different structure
{
    "_id": "prod_456",
    "name": "T-Shirt",
    "category": "clothing",
    "sizes": ["S", "M", "L", "XL"],
    "colors": ["red", "blue", "black"],
    "material": "100% cotton",
    "care_instructions": "Machine wash cold"
}

// Both in same MongoDB collection, no schema migration needed
```

### User Profiles with Custom Fields

Users can have different attributes based on account type.

```javascript
// Basic user
{
    "user_id": "user_123",
    "name": "Alice",
    "email": "alice@email.com",
    "created_at": "2024-01-15"
}

// Premium user with extra fields
{
    "user_id": "user_456",
    "name": "Bob",
    "email": "bob@email.com",
    "created_at": "2024-01-16",
    "premium_since": "2024-01-20",
    "subscription_tier": "gold",
    "billing": {
        "method": "credit_card",
        "next_billing_date": "2024-02-20"
    }
}
```

## High Availability Requirements

Use NoSQL when system must stay available even during failures.

### E-commerce Shopping Cart (DynamoDB)

Cart must always be accessible, even with slight inconsistency.

```javascript
// Cart stored in DynamoDB
{
    "user_id": "user_123",  // Partition key
    "items": [
        {"product_id": "prod_789", "quantity": 2, "price": 99.99},
        {"product_id": "prod_456", "quantity": 1, "price": 149.99}
    ],
    "last_updated": "2024-01-20T10:30:00Z"
}

// Multi-region replication
// US-East: User adds item → writes to local region
// US-West: Item appears in 10-50ms (replication lag)
// If US-East fails → US-West serves requests
```

Eventual consistency acceptable here:
- Showing 2 items vs 3 items for 50ms is okay
- Better than cart being unavailable

### Session Storage (Redis)

User sessions must be fast and always available.

```bash
# Session stored in Redis
SET session:xyz123 '{"user_id": 456, "login_time": "...", "cart": [...]}'
EXPIRE session:xyz123 3600  # Auto-delete after 1 hour

# Redis replication:
# Master handles writes
# Replicas handle reads
# If master fails, replica promoted
```

## Real-Time Analytics

Use NoSQL for collecting and querying high-velocity data.

### Application Metrics (InfluxDB - Time Series)

```javascript
// Metric point
{
    "measurement": "api_response_time",
    "tags": {
        "endpoint": "/api/users",
        "region": "us-east-1",
        "status_code": "200"
    },
    "fields": {
        "duration_ms": 45.2
    },
    "timestamp": "2024-01-20T10:30:00.123Z"
}

// Query: Average response time per endpoint, last hour
SELECT MEAN(duration_ms)
FROM api_response_time
WHERE time > now() - 1h
GROUP BY endpoint
```

### User Activity Tracking

```javascript
// Activity event
{
    "event_id": "evt_123",
    "user_id": "user_456",
    "event_type": "page_view",
    "page": "/products/laptop",
    "timestamp": "2024-01-20T10:30:00Z",
    "metadata": {
        "referrer": "https://google.com",
        "device": "mobile",
        "session_id": "sess_789"
    }
}

// Store in Cassandra
// Query patterns:
// - Events by user_id + time_range
// - Events by event_type + time_range
// Billions of events, fast writes, efficient range queries
```

## Caching Layer

Use key-value NoSQL (Redis, Memcached) for caching.

### Database Query Caching

```python
def get_user(user_id):
    # Try cache first
    cache_key = f"user:{user_id}"
    cached = redis.get(cache_key)

    if cached:
        return json.loads(cached)

    # Cache miss - query database
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)

    # Store in cache (expire in 1 hour)
    redis.setex(cache_key, 3600, json.dumps(user))

    return user
```

### API Response Caching

```javascript
// Cache expensive computation
{
    "key": "recommendations:user_123",
    "value": [
        {"product_id": "prod_1", "score": 0.95},
        {"product_id": "prod_2", "score": 0.89},
        ...
    ],
    "ttl": 300  // 5 minutes
}
```

## Graph Relationships

Use graph databases for highly connected data.

### Social Network Friend Recommendations

```cypher
// Neo4j query: Find friend recommendations
// (Friends of friends who aren't already friends)
MATCH (me:User {user_id: 'user_123'})-[:FRIENDS_WITH]->(friend)
      -[:FRIENDS_WITH]->(foaf)
WHERE NOT (me)-[:FRIENDS_WITH]->(foaf)
    AND me <> foaf
RETURN foaf.name, COUNT(*) as mutual_friends
ORDER BY mutual_friends DESC
LIMIT 10
```

This query is very efficient in graph DB, but would require complex JOINs in SQL.

### Fraud Detection

```cypher
// Find suspicious patterns
MATCH (user:User)-[:MADE_TRANSACTION]->(txn:Transaction)
      -[:TO_ACCOUNT]->(account:Account)
WHERE txn.amount > 10000
    AND txn.timestamp > datetime() - duration('PT1H')
WITH user, COUNT(txn) as txn_count
WHERE txn_count > 5
RETURN user.user_id, txn_count
```

## Content Management Systems

Use document databases for flexible content structures.

### Blog Platform (MongoDB)

```javascript
// Article with nested comments
{
    "_id": "article_123",
    "title": "Guide to NoSQL Databases",
    "author": {
        "user_id": "user_456",
        "name": "Alice",
        "avatar_url": "https://..."
    },
    "content": "NoSQL databases come in several types...",
    "tags": ["database", "nosql", "tutorial"],
    "published_at": "2024-01-20T09:00:00Z",
    "comments": [
        {
            "comment_id": "cmt_1",
            "user_id": "user_789",
            "text": "Great article!",
            "timestamp": "2024-01-20T10:00:00Z",
            "replies": [
                {
                    "user_id": "user_456",
                    "text": "Thank you!",
                    "timestamp": "2024-01-20T10:30:00Z"
                }
            ]
        }
    ],
    "stats": {
        "views": 1523,
        "likes": 89
    }
}

// Single query gets entire article with comments
// No JOINs needed
// Easy to add new fields (e.g., "featured": true)
```

## When NOT to Use NoSQL

### Avoid NoSQL When:

**1. Complex Transactions Required**
Multi-document ACID transactions are limited or unavailable.

```javascript
// This is hard in NoSQL:
BEGIN TRANSACTION
    Deduct inventory
    Create order
    Process payment
    Update user points
COMMIT
```

Use SQL instead for financial transactions, order processing with inventory.

**2. Complex Joins are Common**

```sql
-- This query is natural in SQL:
SELECT c.name, COUNT(o.order_id), SUM(o.total)
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE p.category = 'electronics'
GROUP BY c.name;

-- In NoSQL: Must denormalize OR do application-level joins
```

**3. Data is Highly Relational**

If everything is connected and you frequently query across relationships:
- Use SQL for better query efficiency
- Or use Graph DB if relationships are the focus

**4. Strong Consistency is Critical**

Banking, healthcare, inventory management:
- Cannot tolerate stale reads
- Need ACID guarantees
- SQL is better fit

## Decision Framework

Use NoSQL if you answer "yes" to most of these:

- [ ] Need horizontal scalability across data centers?
- [ ] Handle millions of operations per second?
- [ ] Schema evolves frequently?
- [ ] Data is semi-structured or unstructured?
- [ ] Eventual consistency is acceptable?
- [ ] Simple query patterns (key-based lookups)?
- [ ] Availability more important than consistency?

## Real-World Examples

### Netflix - Cassandra
- User viewing history
- Billions of events per day
- Multi-region deployment
- High availability required

### Discord - Cassandra
- Message storage
- Millions of messages per second
- Partitioned by channel_id
- 99.99% uptime requirement

### Uber - Multiple NoSQL DBs
- Redis: Session storage, caching
- Cassandra: Trip data, analytics
- DynamoDB: Real-time operations
- MongoDB: Operational data

### Instagram - Cassandra
- User feed storage
- Photo metadata
- Billions of rows
- Horizontal scaling across regions
