# NoSQL Databases - Core Concepts

## What Problem Do NoSQL Databases Solve?

Imagine you're building a social media platform like Twitter. You need to store millions of tweets per day, handle massive read traffic, and scale horizontally across data centers worldwide. The structure of tweets is flexible (text, images, videos, polls), and you can tolerate showing slightly stale like counts. Traditional SQL databases struggle with this scale and flexibility.

NoSQL databases sacrifice some guarantees (like strong consistency and complex JOINs) to gain horizontal scalability, flexibility, and performance at massive scale.

## The Name "NoSQL"

Originally meant "No SQL", now commonly interpreted as "Not Only SQL":
- Not a replacement for SQL databases
- Different tool for different use cases
- Many systems use both (polyglot persistence)

## Core Principles

### Schema Flexibility
Structure can evolve without database migrations.

```javascript
// Document 1
{
    "user_id": "user123",
    "name": "Alice",
    "email": "alice@email.com"
}

// Document 2 - different fields
{
    "user_id": "user456",
    "name": "Bob",
    "email": "bob@email.com",
    "avatar_url": "https://...",
    "verified": true,
    "followers_count": 1000
}
```

Both documents can coexist in the same collection without schema changes.

### Horizontal Scalability
Built to scale across multiple servers (sharding).

```
User Data Distributed Across Nodes:
Node 1: users 1-1M
Node 2: users 1M-2M
Node 3: users 2M-3M
```

Add more nodes to handle more data and traffic.

### BASE Model Over ACID
Prioritizes availability and partition tolerance over strong consistency.

- Basically Available: System responds to requests
- Soft State: State may change without input (replication lag)
- Eventual Consistency: System becomes consistent over time

## Types of NoSQL Databases

### 1. Document Stores

Store data as JSON-like documents.

**Examples:** MongoDB, CouchDB, Amazon DocumentDB

**Structure:**
```javascript
{
    "_id": "post_123",
    "title": "Introduction to NoSQL",
    "author": {
        "user_id": "user_456",
        "name": "Alice"
    },
    "content": "NoSQL databases are...",
    "tags": ["database", "nosql", "scalability"],
    "comments": [
        {
            "user_id": "user_789",
            "text": "Great article!",
            "timestamp": "2024-01-20T10:30:00Z"
        }
    ],
    "created_at": "2024-01-20T09:00:00Z",
    "likes_count": 42
}
```

**Characteristics:**
- Rich query capabilities (by field, nested field, array elements)
- Indexes on any field
- Good for hierarchical data
- Natural fit for JSON APIs

**When to Use:**
- Content management systems
- User profiles
- Product catalogs
- Real-time analytics

### 2. Key-Value Stores

Simplest NoSQL model. Each item has a key and a value (blob).

**Examples:** Redis, Amazon DynamoDB, Riak

**Structure:**
```
Key: "session:abc123"
Value: {"user_id": 456, "login_time": "2024-01-20T10:00:00Z", "cart": [...]}

Key: "user:456:profile"
Value: {"name": "Alice", "email": "alice@email.com", ...}

Key: "cache:product:789"
Value: {"name": "Laptop", "price": 999.99, ...}
```

**Characteristics:**
- Extremely fast lookups: O(1)
- Simple API: GET, PUT, DELETE
- No complex queries (only key-based access)
- Often held in memory for performance

**When to Use:**
- Session storage
- Caching layer
- Real-time recommendations
- Shopping carts
- Leaderboards

### 3. Column-Family Stores (Wide-Column)

Store data in column families rather than rows.

**Examples:** Apache Cassandra, HBase, ScyllaDB

**Structure:**
```
Row Key: user_123
Column Family: profile
    name: "Alice"
    email: "alice@email.com"
    created: "2024-01-15"

Column Family: activity
    last_login: "2024-01-20T10:00:00Z"
    post_count: 42
    follower_count: 1000
```

**Characteristics:**
- Optimized for write-heavy workloads
- Excellent horizontal scaling
- Good for time-series data
- Sparse columns (not all rows have all columns)

**When to Use:**
- Time-series data (metrics, logs, events)
- IoT sensor data
- Message history
- Analytics on large datasets

### 4. Graph Databases

Store data as nodes and edges (relationships).

**Examples:** Neo4j, Amazon Neptune, ArangoDB

**Structure:**
```
Nodes:
- (Alice:User {name: "Alice", email: "alice@email.com"})
- (Bob:User {name: "Bob"})
- (JavaScript:Skill {level: "expert"})

Edges:
- (Alice)-[:FOLLOWS]->(Bob)
- (Bob)-[:FOLLOWS]->(Alice)
- (Alice)-[:HAS_SKILL]->(JavaScript)
```

**Characteristics:**
- Optimized for relationship traversal
- Native graph queries (Cypher, Gremlin)
- Efficient for connected data
- Avoids expensive JOINs

**When to Use:**
- Social networks (friends, followers)
- Recommendation engines
- Fraud detection (pattern recognition)
- Knowledge graphs
- Network topology

## How NoSQL Databases Achieve Scale

### Sharding (Horizontal Partitioning)

Data split across multiple servers automatically.

```
Hash-Based Sharding:
hash(user_id) % num_shards = shard_number

user_123 → hash → shard 0
user_456 → hash → shard 1
user_789 → hash → shard 2
```

### Replication

Data copied to multiple nodes for redundancy and availability.

```
Write to Primary:
User creates post → Write to Node 1

Replicate to Secondaries:
Node 1 → replicate → Node 2
      → replicate → Node 3

Read from Any:
User views post → Read from Node 1, 2, or 3
```

### Eventual Consistency

Replicas may temporarily diverge but converge over time.

```
Time: T0
Node 1: likes = 100
Node 2: likes = 100
Node 3: likes = 100

Time: T1 (User likes post, writes to Node 1)
Node 1: likes = 101
Node 2: likes = 100  (not yet replicated)
Node 3: likes = 100  (not yet replicated)

Time: T2 (Replication completes)
Node 1: likes = 101
Node 2: likes = 101
Node 3: likes = 101
```

## CAP Theorem

NoSQL databases must choose two of three:
- Consistency (all nodes see same data)
- Availability (system responds to requests)
- Partition Tolerance (system works despite network failures)

**CP Systems:** MongoDB, HBase
- Prioritize consistency and partition tolerance
- May become unavailable during network partitions

**AP Systems:** Cassandra, DynamoDB
- Prioritize availability and partition tolerance
- May return stale data during network partitions

## Data Modeling in NoSQL

### Denormalization

Duplicate data to avoid lookups across partitions.

**SQL Normalized:**
```sql
users table: user_id, name, email
posts table: post_id, user_id, content
```

**NoSQL Denormalized:**
```javascript
{
    "_id": "post_123",
    "content": "Hello world!",
    "author": {
        "user_id": "user_456",
        "name": "Alice",      // Duplicated from user document
        "avatar_url": "..."    // Duplicated from user document
    }
}
```

**Trade-off:**
- Faster reads (no JOIN needed)
- Slower updates (must update all copies)
- More storage (data duplicated)

### Embedding vs Referencing

**Embedding (Denormalized):**
```javascript
{
    "_id": "user_123",
    "name": "Alice",
    "posts": [
        {"post_id": "post_1", "content": "First post"},
        {"post_id": "post_2", "content": "Second post"}
    ]
}
```

**Referencing (Normalized):**
```javascript
User:
{
    "_id": "user_123",
    "name": "Alice",
    "post_ids": ["post_1", "post_2"]
}

Posts:
{"_id": "post_1", "content": "First post"}
{"_id": "post_2", "content": "Second post"}
```

## Indexing in NoSQL

### Primary Key / Partition Key
Always indexed for fast lookups.

```javascript
// MongoDB
db.users.find({"_id": "user_123"})  // Instant lookup via primary key

// DynamoDB
GetItem({"user_id": "user_123"})  // Partition key lookup
```

### Secondary Indexes
Create indexes on frequently queried fields.

```javascript
// Index on email
db.users.createIndex({"email": 1})
db.users.find({"email": "alice@email.com"})  // Uses index
```

### Composite Indexes
```javascript
// Index on multiple fields
db.posts.createIndex({"author_id": 1, "created_at": -1})

// Efficient query:
db.posts.find({"author_id": "user_123"}).sort({"created_at": -1})
```

## Query Patterns

### MongoDB Example
```javascript
// Find users in a city with age > 25
db.users.find({
    "city": "New York",
    "age": { "$gt": 25 }
})

// Aggregation pipeline
db.orders.aggregate([
    { "$match": { "status": "completed" } },
    { "$group": {
        "_id": "$user_id",
        "total_spent": { "$sum": "$amount" }
    }},
    { "$sort": { "total_spent": -1 } },
    { "$limit": 10 }
])
```

### Cassandra Example (CQL)
```sql
-- Time-series query
SELECT * FROM sensor_data
WHERE sensor_id = 'sensor_123'
    AND timestamp >= '2024-01-01'
    AND timestamp < '2024-02-01'
ORDER BY timestamp DESC;
```

### Redis Example
```bash
# Set value
SET session:abc123 '{"user_id": 456, "login_time": "..."}'

# Get value
GET session:abc123

# Set with expiry
SETEX cache:product:789 3600 '{"name": "Laptop", ...}'
```

## Trade-offs

### What You Gain
- Horizontal scalability (add more servers)
- Schema flexibility (evolve structure easily)
- High performance for simple queries
- Better availability (AP systems)
- Natural fit for semi-structured data

### What You Sacrifice
- Complex JOINs (must denormalize or do application-level joins)
- Strong consistency (eventual consistency in many cases)
- ACID transactions across documents (limited support)
- Standardization (each NoSQL DB has different query language)
- Mature tooling (compared to SQL)
