# Week 3: Storage & Databases - High Level Design

## Table of Contents
1. [SQL vs NoSQL Databases](#sql-vs-nosql-databases)
2. [Database Migration Strategies](#database-migration-strategies)
3. [Indexing](#indexing)
4. [Database Replication](#database-replication)
5. [Database Sharding](#database-sharding)
6. [Consistent Hashing](#consistent-hashing)
7. [ACID Properties](#acid-properties)
8. [BASE Model](#base-model)
9. [Real-World Examples](#real-world-examples)
10. [Best Practices](#best-practices)

---

## SQL vs NoSQL Databases

### SQL Databases (Relational)

**Characteristics:**
- **Structured data** with predefined schema
- **ACID compliance** (Atomicity, Consistency, Isolation, Durability)
- **Relational model** with tables, rows, and columns
- **SQL** (Structured Query Language) for queries
- **Strong consistency** guarantees
- **Vertical scaling** traditionally preferred

**Popular SQL Databases:**
- PostgreSQL
- MySQL
- Oracle Database
- Microsoft SQL Server
- MariaDB

**Use Cases:**
- Financial applications (banking, trading)
- E-commerce platforms (order management)
- ERP/CRM systems
- Applications requiring complex joins
- Systems requiring strong consistency

**Pros:**
- ACID compliance ensures data integrity
- Mature ecosystem and tooling
- Complex query capabilities (JOINs, aggregations)
- Standardized query language (SQL)
- Good for structured data with relationships

**Cons:**
- Schema changes can be difficult
- Vertical scaling has limits
- Can be slower for massive scale
- Less flexible for semi-structured data

### NoSQL Databases (Non-Relational)

**Types of NoSQL Databases:**

#### 1. Document Stores
- **Examples:** MongoDB, CouchDB, DocumentDB
- **Data Model:** JSON/BSON documents
- **Use Cases:** Content management, user profiles, catalogs
- **Schema:** Flexible, schema-less

#### 2. Key-Value Stores
- **Examples:** Redis, DynamoDB, Riak
- **Data Model:** Simple key-value pairs
- **Use Cases:** Caching, session management, real-time analytics
- **Performance:** Extremely fast for simple lookups

#### 3. Column-Family Stores
- **Examples:** Cassandra, HBase, ScyllaDB
- **Data Model:** Column families (wide columns)
- **Use Cases:** Time-series data, IoT data, analytics
- **Scalability:** Excellent horizontal scaling

#### 4. Graph Databases
- **Examples:** Neo4j, Amazon Neptune, ArangoDB
- **Data Model:** Nodes and edges (relationships)
- **Use Cases:** Social networks, recommendation engines, fraud detection
- **Strength:** Relationship traversal queries

**NoSQL Characteristics:**
- **Schema flexibility** or schema-less design
- **Horizontal scalability** (distributed architecture)
- **BASE properties** (eventual consistency)
- **High performance** for specific use cases
- **Partition tolerance** in CAP theorem

**Use Cases:**
- Real-time analytics
- Social media platforms
- IoT and sensor data
- Content delivery networks
- Gaming leaderboards
- Session stores

**Pros:**
- Horizontal scaling is easier
- Flexible schema (adapt to changing requirements)
- High performance for specific operations
- Better for unstructured/semi-structured data
- Built for distributed systems

**Cons:**
- Eventual consistency (not always)
- Limited query capabilities (no complex JOINs)
- Less mature tooling in some cases
- Learning curve for different query languages
- May sacrifice ACID guarantees

### Decision Matrix

| Factor | SQL | NoSQL |
|--------|-----|-------|
| Data Structure | Structured, relational | Unstructured, semi-structured |
| Schema | Fixed, predefined | Flexible, dynamic |
| Scaling | Vertical (primary) | Horizontal (native) |
| Consistency | Strong (ACID) | Eventual (BASE) |
| Transactions | Multi-row, complex | Limited (improving) |
| Query Complexity | High (JOINs, aggregations) | Lower (key-based) |
| Use Case | Financial, ERP, complex relationships | Big data, real-time, flexible schema |

---

## Database Migration Strategies

Database migration is critical for evolving systems without downtime.

### 1. Zero-Downtime Migration

**Dual-Write Pattern:**
```
Application
    ↓
Write to Old DB ← Primary
    ↓
Write to New DB ← Shadow (verify)
```

**Steps:**
1. Deploy dual-write code
2. Backfill historical data to new DB
3. Verify data consistency
4. Switch reads to new DB
5. Monitor and validate
6. Deprecate old DB writes
7. Decommission old DB

**Benefits:**
- No downtime
- Easy rollback
- Gradual validation

**Challenges:**
- Temporary complexity
- Data consistency management
- Resource overhead

### 2. Blue-Green Deployment

**Architecture:**
```
Load Balancer
    ↓
    ├─→ Blue (Current) → Old DB
    └─→ Green (New) → New DB
```

**Process:**
1. Set up Green environment with new DB
2. Migrate data to new DB
3. Route small % of traffic to Green
4. Monitor and validate
5. Gradually increase traffic to Green
6. Switch 100% to Green
7. Keep Blue as fallback

### 3. Strangler Fig Pattern

**Concept:** Gradually migrate portions of the application

```
Old System (Monolith)
    ↓
Proxy/Router
    ↓
    ├─→ New Service 1 → New DB 1
    ├─→ New Service 2 → New DB 2
    └─→ Old System → Old DB (shrinking)
```

**Use Cases:**
- Monolith to microservices
- Legacy system modernization

### 4. Change Data Capture (CDC)

**Tools:** Debezium, AWS DMS, Oracle GoldenGate

**Flow:**
```
Old DB → CDC Tool → Event Stream → New DB
```

**Benefits:**
- Real-time synchronization
- Minimal impact on source DB
- Event-driven architecture

### 5. Schema Migration Best Practices

**Backward Compatible Changes:**
- Add new columns (nullable or with defaults)
- Add new tables
- Add new indexes

**Backward Incompatible Changes (require coordination):**
- Rename columns (use multi-phase migration)
- Delete columns (deprecate first, then remove)
- Change data types (create new column, migrate, remove old)

**Multi-Phase Column Rename:**
```sql
-- Phase 1: Add new column
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);
UPDATE users SET email_address = email;

-- Phase 2: Deploy code reading from both
-- Application code: user.email_address || user.email

-- Phase 3: Verify and remove old column
ALTER TABLE users DROP COLUMN email;
```

---

## Indexing

Indexes are data structures that improve query performance by reducing disk I/O.

### 1. B-Tree Indexes

**Structure:**
- Balanced tree structure
- Sorted order maintained
- Logarithmic search time: O(log n)
- Most common index type

**Characteristics:**
```
           [50]
          /    \
      [25]      [75]
     /   \      /   \
  [10] [35]  [60] [90]
```

**Best For:**
- Range queries (>, <, BETWEEN)
- Sorting (ORDER BY)
- Exact matches (=)
- Prefix searches (LIKE 'abc%')

**Example:**
```sql
-- B-Tree index on email
CREATE INDEX idx_users_email ON users(email);

-- Efficient queries:
SELECT * FROM users WHERE email = 'user@example.com';
SELECT * FROM users WHERE email > 'a' AND email < 'c';
SELECT * FROM users ORDER BY email;
```

**Pros:**
- Good for range queries
- Maintains sort order
- Well-balanced performance
- Supports composite indexes

**Cons:**
- Slower inserts/updates (rebalancing)
- More storage overhead
- Not optimal for equality-only queries

### 2. Hash Indexes

**Structure:**
- Hash table: key → bucket → value
- O(1) lookup for exact matches
- No ordering maintained

**Characteristics:**
```
Hash(key) → Bucket → Row Location
Hash("user@example.com") → 42 → Disk Location
```

**Best For:**
- Exact equality matches (=)
- High-cardinality columns
- In-memory databases

**Example:**
```sql
-- Hash index on user_id
CREATE INDEX idx_users_id USING HASH ON users(user_id);

-- Efficient:
SELECT * FROM users WHERE user_id = 12345;

-- NOT efficient (can't use hash index):
SELECT * FROM users WHERE user_id > 12345;
SELECT * FROM users ORDER BY user_id;
```

**Pros:**
- Very fast for equality lookups
- Constant time O(1) access
- Compact storage

**Cons:**
- No range query support
- No sorting support
- Hash collisions
- Not supported in all databases

### 3. Bitmap Indexes

**Structure:**
- Bit array for each distinct value
- Each bit represents a row
- Efficient for low-cardinality columns

**Characteristics:**
```
Column: Status
Value "active":   [1, 0, 1, 1, 0, 1, 0, ...]
Value "inactive": [0, 1, 0, 0, 1, 0, 1, ...]
Value "deleted":  [0, 0, 0, 0, 0, 0, 0, ...]
```

**Best For:**
- Low-cardinality columns (few distinct values)
- Data warehouses / OLAP
- Complex boolean queries (AND, OR, NOT)
- Read-heavy workloads

**Example:**
```sql
-- Bitmap index on gender
CREATE BITMAP INDEX idx_users_gender ON users(gender);

-- Very efficient with bitmap:
SELECT * FROM users WHERE gender = 'F' AND status = 'active';
-- Uses bitwise AND: [gender bitmap] & [status bitmap]
```

**Pros:**
- Extremely space-efficient for low cardinality
- Fast for complex boolean queries
- Excellent compression
- Great for analytics

**Cons:**
- Poor for high-cardinality columns
- Slow updates (entire bitmap changes)
- Not suitable for OLTP
- Lock contention on updates

### 4. Composite Indexes

**Definition:** Index on multiple columns

```sql
CREATE INDEX idx_users_city_age ON users(city, age);
```

**Index Column Order Matters:**
- Left-to-right usage
- `(city, age)` ≠ `(age, city)`

**Efficient Queries:**
```sql
-- Uses index (left-most prefix):
SELECT * FROM users WHERE city = 'NYC';
SELECT * FROM users WHERE city = 'NYC' AND age > 25;

-- Does NOT use index efficiently:
SELECT * FROM users WHERE age > 25;
```

### 5. Covering Indexes

**Definition:** Index contains all columns needed for a query

```sql
CREATE INDEX idx_users_cover ON users(email, name, age);

-- Covered query (no table lookup needed):
SELECT name, age FROM users WHERE email = 'user@example.com';
```

**Benefits:**
- No need to access table data
- Faster query execution
- Reduced I/O

### Index Best Practices

1. **Index Selectivity:** High selectivity = better performance
   - Good: user_id, email (unique values)
   - Poor: boolean flags, gender (few distinct values)

2. **Monitor Index Usage:**
   ```sql
   -- PostgreSQL: Check unused indexes
   SELECT schemaname, tablename, indexname, idx_scan
   FROM pg_stat_user_indexes
   WHERE idx_scan = 0;
   ```

3. **Avoid Over-Indexing:**
   - Each index costs storage
   - Slows down writes (INSERT, UPDATE, DELETE)
   - Balance read vs write performance

4. **Choose Index Type Based on Query Patterns:**
   - Equality lookups → Hash
   - Range queries → B-Tree
   - Low-cardinality analytics → Bitmap
   - Full-text search → GIN/Full-text indexes

---

## Database Replication

Replication creates copies of data across multiple database servers.

### Benefits of Replication

1. **High Availability:** Failover to replicas if primary fails
2. **Read Scalability:** Distribute read queries across replicas
3. **Disaster Recovery:** Geographic redundancy
4. **Reduced Latency:** Serve users from nearby replicas
5. **Backup:** Take backups from replicas without impacting primary

### 1. Master-Slave Replication (Primary-Replica)

**Architecture:**
```
         Master (Primary)
         [Read/Write]
              ↓
    ┌─────────┼─────────┐
    ↓         ↓         ↓
 Slave 1   Slave 2   Slave 3
[Read Only] [Read Only] [Read Only]
```

**Characteristics:**
- One master handles all writes
- Multiple slaves handle reads
- Asynchronous or synchronous replication
- Master sends replication log to slaves

**Replication Methods:**

**a) Asynchronous Replication:**
- Master doesn't wait for slave acknowledgment
- Lower latency on writes
- Risk of data loss if master fails
- Slaves may lag behind (replication lag)

**b) Synchronous Replication:**
- Master waits for slave acknowledgment
- Higher latency on writes
- Strong consistency guarantee
- No data loss on failover

**c) Semi-Synchronous:**
- Wait for at least one slave
- Balance between performance and consistency

**Use Cases:**
- Read-heavy applications (blogs, news sites)
- Analytics and reporting (query replicas)
- Geographic distribution

**Pros:**
- Simple to implement
- Scales reads effectively
- Clear separation of read/write

**Cons:**
- Single point of failure (master)
- Replication lag issues
- Manual failover complexity
- Writes don't scale

**Replication Lag Mitigation:**
:::multilang
```python
# Read your own writes pattern
def create_post(user_id, content):
    # Write to master
    post_id = master_db.insert_post(user_id, content)

    # Store in cache for immediate read
    cache.set(f"post:{post_id}", content, ttl=60)

    # Subsequent reads check cache first
    return post_id

def get_post(post_id):
    # Try cache first (recent writes)
    cached = cache.get(f"post:{post_id}")
    if cached:
        return cached

    # Fall back to replica
    return replica_db.get_post(post_id)
```

```cpp
#include <string>
#include <optional>

// Assuming global dependencies
extern MasterDB master_db;
extern ReplicaDB replica_db;
extern Cache cache;

// Read your own writes pattern
int create_post(int user_id, const std::string& content) {
    // Write to master
    int post_id = master_db.insert_post(user_id, content);

    // Store in cache for immediate read
    std::string cache_key = "post:" + std::to_string(post_id);
    cache.set(cache_key, content, 60);  // TTL: 60 seconds

    // Subsequent reads check cache first
    return post_id;
}

std::optional<std::string> get_post(int post_id) {
    // Try cache first (recent writes)
    std::string cache_key = "post:" + std::to_string(post_id);
    auto cached = cache.get(cache_key);
    if (cached.has_value()) {
        return cached;
    }

    // Fall back to replica
    return replica_db.get_post(post_id);
}
```

```java
import java.util.Optional;

public class PostService {
    private final MasterDB masterDb;
    private final ReplicaDB replicaDb;
    private final Cache cache;

    public PostService(MasterDB masterDb, ReplicaDB replicaDb, Cache cache) {
        this.masterDb = masterDb;
        this.replicaDb = replicaDb;
        this.cache = cache;
    }

    // Read your own writes pattern
    public int createPost(int userId, String content) {
        // Write to master
        int postId = masterDb.insertPost(userId, content);

        // Store in cache for immediate read
        String cacheKey = "post:" + postId;
        cache.set(cacheKey, content, 60);  // TTL: 60 seconds

        // Subsequent reads check cache first
        return postId;
    }

    public Optional<String> getPost(int postId) {
        // Try cache first (recent writes)
        String cacheKey = "post:" + postId;
        Optional<String> cached = cache.get(cacheKey);
        if (cached.isPresent()) {
            return cached;
        }

        // Fall back to replica
        return replicaDb.getPost(postId);
    }
}
```
:::

### 2. Master-Master Replication (Multi-Primary)

**Architecture:**
```
    Master 1           Master 2
  [Read/Write]  ←→  [Read/Write]
       ↓                 ↓
    Slaves           Slaves
```

**Characteristics:**
- Multiple masters accept writes
- Bi-directional replication
- Active-active configuration
- Conflict resolution needed

**Conflict Resolution Strategies:**

**a) Last Write Wins (LWW):**
```
Master 1: UPDATE users SET name='Alice' WHERE id=1 at T1
Master 2: UPDATE users SET name='Bob' WHERE id=1 at T2

Result: name='Bob' (T2 > T1)
```

**b) Application-Level Conflict Resolution:**
```python
def resolve_conflict(version1, version2):
    # Custom business logic
    if version1.priority > version2.priority:
        return version1
    return version2
```

**c) Conflict-Free Replicated Data Types (CRDTs):**
- Mathematical guarantees of convergence
- No conflicts by design

**Use Cases:**
- Multi-region deployments
- High availability requirements
- Load distribution across regions

**Pros:**
- No single point of failure
- Writes can be distributed
- Better write scalability
- Geographic distribution

**Cons:**
- Complex conflict resolution
- Harder to maintain consistency
- More complex setup
- Potential for split-brain scenarios

### 3. Chain Replication

**Architecture:**
```
Master → Slave 1 → Slave 2 → Slave 3
         ↓         ↓         ↓
      Clients   Clients   Clients
```

**Characteristics:**
- Linear chain of replicas
- Write propagates through chain
- Reads from tail (most up-to-date replica)

**Benefits:**
- Strong consistency for reads from tail
- Better fault tolerance

### 4. Group Replication (Consensus-Based)

**Architecture:**
```
    Node 1  ←→  Node 2  ←→  Node 3
       ↕            ↕            ↕
    Consensus Protocol (Paxos, Raft)
```

**Characteristics:**
- Consensus-based replication (Paxos, Raft)
- Automatic failover
- Strong consistency

**Examples:**
- MySQL Group Replication
- PostgreSQL with Patroni
- MongoDB Replica Sets

---

## Database Sharding

Sharding is the process of splitting data across multiple databases (shards) to improve scalability.

### Why Shard?

**Problems with Single Database:**
- **Storage Limits:** Single server storage capacity
- **Performance:** CPU/Memory bottlenecks
- **Availability:** Single point of failure
- **Cost:** Vertical scaling becomes expensive

**Sharding Benefits:**
- Horizontal scalability
- Improved performance (parallel queries)
- Better availability (failure isolation)
- Cost-effective scaling

### 1. Horizontal Sharding (Row-Based)

**Definition:** Split rows across multiple databases based on a shard key

**Example:**
```
Users Table (10M rows)

Shard 1: user_id 1-2.5M
Shard 2: user_id 2.5M-5M
Shard 3: user_id 5M-7.5M
Shard 4: user_id 7.5M-10M
```

**Sharding Strategies:**

#### a) Range-Based Sharding
:::multilang
```python
def get_shard(user_id):
    if user_id <= 2_500_000:
        return "shard_1"
    elif user_id <= 5_000_000:
        return "shard_2"
    elif user_id <= 7_500_000:
        return "shard_3"
    else:
        return "shard_4"
```

```cpp
#include <string>

std::string get_shard(int user_id) {
    if (user_id <= 2500000) {
        return "shard_1";
    } else if (user_id <= 5000000) {
        return "shard_2";
    } else if (user_id <= 7500000) {
        return "shard_3";
    } else {
        return "shard_4";
    }
}
```

```java
public class ShardRouter {
    public String getShard(int userId) {
        if (userId <= 2_500_000) {
            return "shard_1";
        } else if (userId <= 5_000_000) {
            return "shard_2";
        } else if (userId <= 7_500_000) {
            return "shard_3";
        } else {
            return "shard_4";
        }
    }
}
```
:::

**Pros:**
- Simple implementation
- Range queries efficient within shard
- Easy to add new shards for new ranges

**Cons:**
- Uneven distribution (hotspots)
- Difficult to rebalance
- Recent data may be on same shard (temporal hotspot)

#### b) Hash-Based Sharding
:::multilang
```python
def get_shard(user_id, num_shards=4):
    return f"shard_{hash(user_id) % num_shards + 1}"
```

```cpp
#include <string>
#include <functional>

std::string get_shard(int user_id, int num_shards = 4) {
    std::hash<int> hash_fn;
    int shard_num = (hash_fn(user_id) % num_shards) + 1;
    return "shard_" + std::to_string(shard_num);
}
```

```java
public class HashShardRouter {
    public String getShard(int userId, int numShards) {
        int shardNum = (Math.abs(Integer.hashCode(userId)) % numShards) + 1;
        return "shard_" + shardNum;
    }

    public String getShard(int userId) {
        return getShard(userId, 4);  // Default: 4 shards
    }
}
```
:::

**Pros:**
- Even distribution
- No hotspots
- Simple logic

**Cons:**
- Adding shards requires rehashing
- Range queries across all shards
- Resizing is expensive

#### c) Consistent Hashing (See dedicated section below)

#### d) Directory-Based Sharding
:::multilang
```python
# Lookup table
shard_directory = {
    "user_1": "shard_1",
    "user_2": "shard_2",
    "user_3": "shard_1",
    # ...
}

def get_shard(user_id):
    return shard_directory.get(user_id)
```

```cpp
#include <string>
#include <unordered_map>
#include <optional>

// Lookup table
std::unordered_map<std::string, std::string> shard_directory = {
    {"user_1", "shard_1"},
    {"user_2", "shard_2"},
    {"user_3", "shard_1"},
    // ...
};

std::optional<std::string> get_shard(const std::string& user_id) {
    auto it = shard_directory.find(user_id);
    if (it != shard_directory.end()) {
        return it->second;
    }
    return std::nullopt;
}
```

```java
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class DirectoryShardRouter {
    // Lookup table
    private final Map<String, String> shardDirectory = new HashMap<>();

    public DirectoryShardRouter() {
        shardDirectory.put("user_1", "shard_1");
        shardDirectory.put("user_2", "shard_2");
        shardDirectory.put("user_3", "shard_1");
        // ...
    }

    public Optional<String> getShard(String userId) {
        return Optional.ofNullable(shardDirectory.get(userId));
    }
}
```
:::

**Pros:**
- Flexible routing
- Easy to move individual records
- No computation needed

**Cons:**
- Lookup table overhead
- Single point of failure (directory)
- Scalability of directory itself

### 2. Vertical Sharding (Column-Based)

**Definition:** Split tables/columns across databases by functionality

**Example:**
```
Database 1: Users table (user_id, email, password)
Database 2: Profiles table (user_id, bio, avatar)
Database 3: Posts table (post_id, user_id, content)
Database 4: Comments table (comment_id, post_id, content)
```

**Use Cases:**
- Microservices architecture
- Separate read/write patterns
- Different scaling requirements

**Pros:**
- Aligned with domain boundaries
- Different technologies per shard
- Independent scaling

**Cons:**
- Joins across shards are expensive
- Referential integrity challenges
- More complex application logic

### 3. Geo-Based Sharding

**Definition:** Shard by geographic region

**Example:**
```
Shard US-East:  Users in North America East
Shard US-West:  Users in North America West
Shard EU:       Users in Europe
Shard Asia:     Users in Asia-Pacific
```

**Routing:**
:::multilang
```python
region_mapping = {
    "US": "shard_us",
    "UK": "shard_eu",
    "FR": "shard_eu",
    "JP": "shard_asia",
    "IN": "shard_asia",
}

def get_shard(user_country):
    return region_mapping.get(user_country, "shard_default")
```

```cpp
#include <string>
#include <unordered_map>

std::unordered_map<std::string, std::string> region_mapping = {
    {"US", "shard_us"},
    {"UK", "shard_eu"},
    {"FR", "shard_eu"},
    {"JP", "shard_asia"},
    {"IN", "shard_asia"},
};

std::string get_shard(const std::string& user_country) {
    auto it = region_mapping.find(user_country);
    if (it != region_mapping.end()) {
        return it->second;
    }
    return "shard_default";
}
```

```java
import java.util.HashMap;
import java.util.Map;

public class GeoShardRouter {
    private final Map<String, String> regionMapping = new HashMap<>();

    public GeoShardRouter() {
        regionMapping.put("US", "shard_us");
        regionMapping.put("UK", "shard_eu");
        regionMapping.put("FR", "shard_eu");
        regionMapping.put("JP", "shard_asia");
        regionMapping.put("IN", "shard_asia");
    }

    public String getShard(String userCountry) {
        return regionMapping.getOrDefault(userCountry, "shard_default");
    }
}
```
:::

**Benefits:**
- Low latency (data close to users)
- Compliance (data residency requirements)
- Better user experience

**Challenges:**
- Cross-region queries are slow
- User migration (if user moves)
- Global features (e.g., global search)

### Sharding Challenges

#### 1. Cross-Shard Queries
```sql
-- Inefficient: Query all shards and merge
SELECT * FROM users WHERE age > 25;
```

**Solutions:**
- Denormalization
- Caching
- Pre-aggregated views
- Search engines (Elasticsearch)

#### 2. Cross-Shard Joins
```sql
-- Very expensive across shards
SELECT u.name, p.title
FROM users u
JOIN posts p ON u.user_id = p.user_id;
```

**Solutions:**
- Denormalize data (duplicate user info in posts)
- Application-level joins
- Shard by same key (co-location)

#### 3. Distributed Transactions

**Problem:** ACID across multiple shards

**Solutions:**
- Two-Phase Commit (2PC)
- Saga pattern (compensating transactions)
- Avoid distributed transactions (eventual consistency)

#### 4. Shard Key Selection

**Criteria for Good Shard Key:**
- High cardinality (many unique values)
- Even distribution
- Avoid hotspots
- Query-friendly (most queries include shard key)

**Examples:**
- Good: user_id, email, order_id
- Bad: status (few values), created_date (temporal hotspot)

#### 5. Resharding (Rebalancing)

**When to Reshard:**
- Uneven load distribution
- Adding more shards
- Removing shards

**Strategies:**
- Consistent hashing (minimal data movement)
- Virtual shards (move virtual shards between physical nodes)
- Offline migration (downtime)
- Online migration (complex, no downtime)

---

## Consistent Hashing

Consistent hashing is a distributed hashing technique that minimizes data movement when nodes are added or removed.

### Traditional Hashing Problem

**Simple Modulo Hashing:**
```python
def get_server(key, num_servers):
    return hash(key) % num_servers
```

**Problem:** When servers change, most keys rehash
```
3 servers → 4 servers:
- 75% of keys move to different servers
- Cache invalidation
- Data migration overhead
```

### Consistent Hashing Solution

**Concept:**
- Hash both keys and servers onto a hash ring (0 to 2^32-1)
- Key → first server clockwise on the ring
- Adding/removing server affects only neighboring keys

**Hash Ring:**
```
        0
        ↑
   S2   |   K1
        |
S3 ←----+----→ S1
        |
   K2   |   K3
        ↓
      2^32-1
```

**Algorithm:**
:::multilang
```python
class ConsistentHash:
    def __init__(self):
        self.ring = {}  # hash_value -> server
        self.sorted_keys = []

    def add_server(self, server):
        hash_val = hash(server) % (2**32)
        self.ring[hash_val] = server
        self.sorted_keys.append(hash_val)
        self.sorted_keys.sort()

    def remove_server(self, server):
        hash_val = hash(server) % (2**32)
        del self.ring[hash_val]
        self.sorted_keys.remove(hash_val)

    def get_server(self, key):
        if not self.ring:
            return None

        hash_val = hash(key) % (2**32)

        # Find first server clockwise
        for server_hash in self.sorted_keys:
            if server_hash >= hash_val:
                return self.ring[server_hash]

        # Wrap around to first server
        return self.ring[self.sorted_keys[0]]
```

```cpp
#include <map>
#include <vector>
#include <string>
#include <functional>
#include <algorithm>
#include <optional>

class ConsistentHash {
private:
    std::map<uint32_t, std::string> ring;  // hash_value -> server
    std::vector<uint32_t> sorted_keys;

    uint32_t hash_function(const std::string& key) {
        std::hash<std::string> hash_fn;
        return static_cast<uint32_t>(hash_fn(key));
    }

public:
    void add_server(const std::string& server) {
        uint32_t hash_val = hash_function(server);
        ring[hash_val] = server;
        sorted_keys.push_back(hash_val);
        std::sort(sorted_keys.begin(), sorted_keys.end());
    }

    void remove_server(const std::string& server) {
        uint32_t hash_val = hash_function(server);
        ring.erase(hash_val);
        sorted_keys.erase(
            std::remove(sorted_keys.begin(), sorted_keys.end(), hash_val),
            sorted_keys.end()
        );
    }

    std::optional<std::string> get_server(const std::string& key) {
        if (ring.empty()) {
            return std::nullopt;
        }

        uint32_t hash_val = hash_function(key);

        // Find first server clockwise
        for (uint32_t server_hash : sorted_keys) {
            if (server_hash >= hash_val) {
                return ring[server_hash];
            }
        }

        // Wrap around to first server
        return ring[sorted_keys[0]];
    }
};
```

```java
import java.util.*;

public class ConsistentHash {
    private final TreeMap<Integer, String> ring;  // hash_value -> server
    private final List<Integer> sortedKeys;

    public ConsistentHash() {
        this.ring = new TreeMap<>();
        this.sortedKeys = new ArrayList<>();
    }

    private int hashFunction(String key) {
        return key.hashCode();
    }

    public void addServer(String server) {
        int hashVal = hashFunction(server);
        ring.put(hashVal, server);
        sortedKeys.add(hashVal);
        Collections.sort(sortedKeys);
    }

    public void removeServer(String server) {
        int hashVal = hashFunction(server);
        ring.remove(hashVal);
        sortedKeys.remove(Integer.valueOf(hashVal));
    }

    public Optional<String> getServer(String key) {
        if (ring.isEmpty()) {
            return Optional.empty();
        }

        int hashVal = hashFunction(key);

        // Find first server clockwise using TreeMap's ceilingEntry
        Map.Entry<Integer, String> entry = ring.ceilingEntry(hashVal);

        if (entry != null) {
            return Optional.of(entry.getValue());
        }

        // Wrap around to first server
        return Optional.of(ring.firstEntry().getValue());
    }
}
```
:::

### Virtual Nodes (VNodes)

**Problem:** Uneven distribution with few physical nodes

**Solution:** Each physical server gets multiple virtual nodes

:::multilang
```python
class ConsistentHashWithVNodes:
    def __init__(self, num_vnodes=150):
        self.num_vnodes = num_vnodes
        self.ring = {}
        self.sorted_keys = []

    def add_server(self, server):
        for i in range(self.num_vnodes):
            # Create virtual node
            vnode_key = f"{server}:vnode{i}"
            hash_val = hash(vnode_key) % (2**32)
            self.ring[hash_val] = server
            self.sorted_keys.append(hash_val)

        self.sorted_keys.sort()
```

```cpp
#include <map>
#include <vector>
#include <string>
#include <functional>
#include <algorithm>

class ConsistentHashWithVNodes {
private:
    int num_vnodes;
    std::map<uint32_t, std::string> ring;
    std::vector<uint32_t> sorted_keys;

    uint32_t hash_function(const std::string& key) {
        std::hash<std::string> hash_fn;
        return static_cast<uint32_t>(hash_fn(key));
    }

public:
    ConsistentHashWithVNodes(int num_vnodes = 150)
        : num_vnodes(num_vnodes) {}

    void add_server(const std::string& server) {
        for (int i = 0; i < num_vnodes; i++) {
            // Create virtual node
            std::string vnode_key = server + ":vnode" + std::to_string(i);
            uint32_t hash_val = hash_function(vnode_key);
            ring[hash_val] = server;
            sorted_keys.push_back(hash_val);
        }

        std::sort(sorted_keys.begin(), sorted_keys.end());
    }
};
```

```java
import java.util.*;

public class ConsistentHashWithVNodes {
    private final int numVnodes;
    private final TreeMap<Integer, String> ring;
    private final List<Integer> sortedKeys;

    public ConsistentHashWithVNodes(int numVnodes) {
        this.numVnodes = numVnodes;
        this.ring = new TreeMap<>();
        this.sortedKeys = new ArrayList<>();
    }

    public ConsistentHashWithVNodes() {
        this(150);  // Default: 150 virtual nodes
    }

    private int hashFunction(String key) {
        return key.hashCode();
    }

    public void addServer(String server) {
        for (int i = 0; i < numVnodes; i++) {
            // Create virtual node
            String vnodeKey = server + ":vnode" + i;
            int hashVal = hashFunction(vnodeKey);
            ring.put(hashVal, server);
            sortedKeys.add(hashVal);
        }

        Collections.sort(sortedKeys);
    }
}
```
:::

**Benefits of Virtual Nodes:**
- More even distribution
- Smoother load balancing
- Better failure handling

**Typical VNode Counts:**
- 150-200 virtual nodes per physical node
- Trade-off: memory vs distribution quality

### Consistent Hashing in Practice

**Use Cases:**
- **Distributed Caches:** Memcached, Redis clusters
- **CDNs:** Route requests to edge servers
- **Load Balancers:** Distribute connections
- **Distributed Databases:** DynamoDB, Cassandra
- **Distributed Storage:** Riak, Amazon S3

**Real-World Example: Amazon DynamoDB:**
- Uses consistent hashing for partition key distribution
- Virtual nodes for load balancing
- Automatic rebalancing when capacity changes

**Real-World Example: Apache Cassandra:**
- Token ring with consistent hashing
- Each node owns a range of tokens
- Virtual nodes (default: 256 per node)

---

## ACID Properties

ACID guarantees strong consistency and reliability for database transactions.

### A - Atomicity

**Definition:** Transaction is all-or-nothing

**Example:**
```sql
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- If either UPDATE fails, both are rolled back
```

**Implementation:**
- Write-Ahead Logging (WAL)
- Undo logs
- Rollback on failure

**Real-World Example:**
Bank transfer: Both debit and credit must succeed, or neither happens.

### C - Consistency

**Definition:** Transaction brings database from one valid state to another

**Example:**
```sql
-- Constraint: balance >= 0

UPDATE accounts SET balance = balance - 500 WHERE id = 1;
-- If balance was 300, transaction fails (would violate constraint)
```

**Enforced By:**
- Constraints (NOT NULL, UNIQUE, CHECK, FOREIGN KEY)
- Triggers
- Application logic

**Real-World Example:**
E-commerce: Inventory count can't be negative.

### I - Isolation

**Definition:** Concurrent transactions don't interfere with each other

**Isolation Levels:**

#### 1. Read Uncommitted (Lowest)
- Transactions can read uncommitted changes
- **Dirty Reads:** Read data that may be rolled back
- Almost never used in practice

#### 2. Read Committed
- Only read committed data
- **Non-Repeatable Reads:** Data can change between reads in same transaction
- Default in PostgreSQL, Oracle

**Example:**
```sql
-- Transaction A
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- Returns 1000
-- Transaction B commits: UPDATE accounts SET balance = 500 WHERE id = 1
SELECT balance FROM accounts WHERE id = 1;  -- Returns 500 (changed!)
COMMIT;
```

#### 3. Repeatable Read
- Same query always returns same result within transaction
- **Phantom Reads:** New rows can appear
- Default in MySQL

**Example:**
```sql
-- Transaction A
BEGIN;
SELECT COUNT(*) FROM accounts WHERE balance > 1000;  -- Returns 5
-- Transaction B commits: INSERT INTO accounts (balance) VALUES (2000)
SELECT COUNT(*) FROM accounts WHERE balance > 1000;  -- Returns 6 (phantom!)
COMMIT;
```

#### 4. Serializable (Highest)
- Transactions execute as if serial (one at a time)
- No dirty reads, non-repeatable reads, or phantom reads
- Performance cost (locks, conflicts)

**Isolation Level Comparison:**

| Isolation Level | Dirty Reads | Non-Repeatable Reads | Phantom Reads |
|-----------------|-------------|----------------------|---------------|
| Read Uncommitted| Yes         | Yes                  | Yes           |
| Read Committed  | No          | Yes                  | Yes           |
| Repeatable Read | No          | No                   | Yes           |
| Serializable    | No          | No                   | No            |

**Implementation Techniques:**
- **Locking:** Pessimistic concurrency control
  - Shared locks (read), Exclusive locks (write)
  - Two-Phase Locking (2PL)
- **MVCC:** Multi-Version Concurrency Control (PostgreSQL, MySQL InnoDB)
  - Each transaction sees a snapshot
  - Better concurrency, less blocking

### D - Durability

**Definition:** Committed data is permanently stored

**Implementation:**
- Write-Ahead Logging (WAL)
- Fsync to disk
- Replication to replicas
- Battery-backed caches

**Example:**
```sql
COMMIT;  -- After this returns, data is durable (even if server crashes)
```

**Techniques:**
- **WAL:** Write changes to log before applying to data files
- **Checkpointing:** Periodically write dirty pages to disk
- **Replication:** Persist to multiple servers

---

## BASE Model

BASE is an alternative to ACID for distributed systems, prioritizing availability and performance.

**BASE = Basically Available, Soft state, Eventual consistency**

### B - Basically Available

**Definition:** System guarantees availability (most requests succeed)

**Characteristics:**
- System is up and responds to requests
- May not be the latest data
- Partial failures don't bring down entire system

**Example:** Amazon S3
- 99.9% availability SLA
- May serve stale data during network partitions
- System remains operational even with node failures

### S - Soft State

**Definition:** State may change over time without input (due to eventual consistency)

**Characteristics:**
- Data may be in flux
- Replicas may have different values temporarily
- No strong consistency guarantee at any point in time

**Example:** DNS
- DNS records are cached at multiple levels
- Updates propagate gradually (TTL-based)
- Old values may be served temporarily

### E - Eventual Consistency

**Definition:** System will become consistent over time, given no new updates

**Characteristics:**
- Replicas converge to same value
- Time to consistency varies (milliseconds to seconds)
- Conflicts resolved automatically or via business logic

**Example:** Social Media "Likes"
```python
# User likes a post
# Write goes to US-East datacenter: likes = 100
# Replica in EU still shows: likes = 99
# After replication lag (50ms-1s): likes = 100 everywhere
```

### ACID vs BASE

| Aspect | ACID | BASE |
|--------|------|------|
| Consistency | Strong, immediate | Eventual |
| Availability | May sacrifice during partitions | Prioritized |
| Use Case | Financial, critical data | Social, analytics, caching |
| Scalability | Vertical (harder) | Horizontal (easier) |
| Complexity | Simpler reasoning | Requires handling inconsistency |
| Examples | PostgreSQL, MySQL | DynamoDB, Cassandra, MongoDB |

### When to Use BASE

**Good Fits:**
- Social media (likes, views, comments)
- Analytics and metrics
- Shopping carts (can be merged)
- Content delivery
- Recommendation systems

**Poor Fits:**
- Banking transactions
- Inventory management (stock counts)
- Booking systems (airplane seats, hotel rooms)
- Accounting ledgers

### Consistency Models Spectrum

```
Strong Consistency          Eventual Consistency
    |                              |
    |------ Linearizability -------|
    |------ Sequential ------------|
    |------ Causal ---------------|
    |------ Read Your Writes ------|
    |------ Monotonic Reads -------|
    |------ Eventual --------------|
```

**Linearizability (Strongest):**
- Operations appear instantaneous
- Total ordering of all operations
- Example: Strongly consistent databases (Spanner, FoundationDB)

**Sequential:**
- All processes see same order of operations
- May not be real-time order

**Causal:**
- Related operations ordered
- Unrelated operations may be reordered

**Read Your Writes:**
- You always see your own writes
- Other users may not immediately

**Eventual (Weakest):**
- No ordering guarantees
- Will converge given enough time

---

## Real-World Examples

### Instagram: Photo Storage and Sharding

**Problem:** Billions of photos, fast growth

**Solution:**
- **Vertical Sharding:** Separate photo metadata from photo storage
  - Metadata DB: PostgreSQL (photo_id, user_id, caption, timestamp)
  - Photo Storage: S3 (binary data)

- **Horizontal Sharding:** Shard by photo_id
  - Custom ID generation (64-bit)
    - 41 bits: Timestamp
    - 13 bits: Shard ID
    - 10 bits: Auto-increment sequence
  - Guarantees: Time-sortable, unique across shards

:::multilang
```python
import time

EPOCH = 1420070400000  # Custom epoch (e.g., Jan 1, 2015)

def generate_photo_id(shard_id):
    timestamp = int(time.time() * 1000) - EPOCH
    sequence = get_next_sequence()

    photo_id = (timestamp << 23) | (shard_id << 10) | sequence
    return photo_id

def get_next_sequence():
    # Implementation would use atomic counter
    # For demo, returning placeholder
    return 0
```

```cpp
#include <chrono>
#include <cstdint>

const uint64_t EPOCH = 1420070400000ULL;  // Custom epoch (e.g., Jan 1, 2015)

uint64_t get_next_sequence() {
    // Implementation would use atomic counter
    // For demo, returning placeholder
    return 0;
}

uint64_t generate_photo_id(uint64_t shard_id) {
    auto now = std::chrono::system_clock::now();
    auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()
    ).count();

    uint64_t timestamp = millis - EPOCH;
    uint64_t sequence = get_next_sequence();

    uint64_t photo_id = (timestamp << 23) | (shard_id << 10) | sequence;
    return photo_id;
}
```

```java
import java.util.concurrent.atomic.AtomicLong;

public class PhotoIDGenerator {
    private static final long EPOCH = 1420070400000L;  // Custom epoch (e.g., Jan 1, 2015)
    private final AtomicLong sequence = new AtomicLong(0);

    private long getNextSequence() {
        // Use atomic counter for thread safety
        long seq = sequence.incrementAndGet();
        if (seq >= 1024) {  // 10 bits max (2^10 = 1024)
            sequence.set(0);
            seq = 0;
        }
        return seq;
    }

    public long generatePhotoId(long shardId) {
        long timestamp = System.currentTimeMillis() - EPOCH;
        long sequence = getNextSequence();

        long photoId = (timestamp << 23) | (shardId << 10) | sequence;
        return photoId;
    }
}
```
:::

**Sharding Strategy:**
- Range-based on user_id
- Co-locate user's photos on same shard
- Query efficiency (user timeline)

### Discord: Message Storage

**Problem:** Billions of messages, real-time access, high write volume

**Solution:**
- **Database:** Cassandra (NoSQL, distributed)
- **Partitioning:** By channel_id
- **Clustering:** By message_id (timestamp-based)
- **TTL:** Automatic expiration for old messages

**Schema:**
```cql
CREATE TABLE messages (
    channel_id bigint,
    message_id bigint,
    author_id bigint,
    content text,
    PRIMARY KEY ((channel_id), message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);
```

**Benefits:**
- Fast reads (single partition)
- Write scalability (distributed)
- No sharding complexity (Cassandra handles it)

**Challenge:** Migrations
- Moved from MongoDB to Cassandra
- Used dual-write pattern
- Gradual migration over months

### Netflix: Viewing History

**Problem:** Track viewing history for 200M+ users

**Solution:**
- **Database:** Cassandra
- **Consistency:** Eventual (BASE)
- **Replication:** Multi-region (low latency globally)

**Design:**
- Partition by user_id
- Each user's history on same nodes (co-location)
- Sacrifice strong consistency for availability

**Why BASE is Acceptable:**
- Missing a view event is not critical
- Can tolerate slight delay in history update
- Availability > Consistency for this use case

### Uber: Geo-Based Sharding

**Problem:** Match drivers and riders in real-time

**Solution:**
- **Sharding:** Geo-hash based sharding
- **Geospatial Index:** PostGIS (PostgreSQL extension)
- **Cell-Based Architecture:**
  - City divided into cells (hexagons)
  - Each cell maps to shards
  - Nearby cells on same/nearby shards

```python
def get_shard(latitude, longitude):
    cell = geohash.encode(latitude, longitude, precision=6)
    return shard_mapping[cell]
```

**Benefits:**
- Low latency (data localized)
- Efficient range queries (nearby drivers)
- Isolation (surge in one city doesn't affect others)

### Amazon DynamoDB: Consistent Hashing

**Problem:** Elastic scaling, automatic load balancing

**Solution:**
- Consistent hashing with virtual nodes
- Partition key hashed to determine placement
- Automatic rebalancing when capacity changes

**Architecture:**
- Ring-based partitioning
- 3-way replication (quorum reads/writes)
- Eventual consistency (default), optional strong consistency

### Twitter: Timeline Fanout

**Problem:** Generate timelines for users with millions of followers

**Solution (Hybrid Approach):**
- **Fanout-on-Write:** Pre-compute timelines
  - Celebrity posts → don't fanout (too expensive)
  - Regular users → fanout to followers' timelines

- **Fanout-on-Read:** Compute at read time
  - Celebrity tweets merged at read time

**Storage:**
- Redis (in-memory) for timeline cache
- MySQL for persistent storage
- Cassandra for tweet storage

---

## Best Practices

### Database Selection

1. **Understand Your Data:**
   - Structured and relational → SQL
   - Unstructured, flexible schema → NoSQL
   - Graph relationships → Graph DB
   - Time-series → Column-family or time-series DB

2. **Consider Access Patterns:**
   - Complex queries, joins → SQL
   - Key-value lookups → NoSQL (Redis, DynamoDB)
   - Real-time analytics → Column-family (Cassandra)

3. **Consistency Requirements:**
   - Strong consistency → SQL (ACID)
   - Eventual consistency acceptable → NoSQL (BASE)

4. **Scalability Needs:**
   - Moderate scale → SQL (vertical + read replicas)
   - Massive scale → NoSQL (horizontal sharding)

### Indexing

1. **Index Based on Queries:**
   - Analyze query patterns first
   - Index WHERE, JOIN, ORDER BY columns

2. **Monitor Index Performance:**
   - Check index usage statistics
   - Remove unused indexes

3. **Composite Index Order:**
   - Most selective column first
   - Match query patterns

4. **Avoid Over-Indexing:**
   - Balance read vs write performance
   - Each index costs storage and write speed

### Replication

1. **Choose Replication Type:**
   - Read-heavy → Master-Slave
   - Multi-region writes → Master-Master
   - High consistency → Synchronous replication

2. **Monitor Replication Lag:**
   - Set up alerts for lag > threshold
   - Use read-your-own-writes pattern

3. **Plan for Failover:**
   - Automated failover (consensus-based)
   - Regular failover drills
   - DNS/load balancer updates

### Sharding

1. **Shard Only When Necessary:**
   - Exhaust vertical scaling + read replicas first
   - Sharding adds complexity

2. **Choose Shard Key Carefully:**
   - High cardinality
   - Even distribution
   - Query-friendly

3. **Plan for Resharding:**
   - Use consistent hashing
   - Virtual shards for flexibility
   - Gradual migration strategy

4. **Avoid Cross-Shard Operations:**
   - Denormalize when appropriate
   - Use application-level joins
   - Cache aggregated data

### Migrations

1. **Zero-Downtime Migrations:**
   - Dual-write pattern
   - Blue-green deployment
   - Gradual traffic shifting

2. **Backward Compatibility:**
   - Make changes in phases
   - Support old and new schema simultaneously
   - Deprecation periods

3. **Data Validation:**
   - Compare old and new data
   - Run shadow mode (write to both, read from one)
   - Automate consistency checks

### Consistency Models

1. **Match Consistency to Use Case:**
   - Financial → Strong consistency (ACID)
   - Social → Eventual consistency (BASE)
   - Hybrid → Strong for critical, eventual for non-critical

2. **Handle Eventual Consistency:**
   - Conflict resolution strategy
   - Idempotent operations
   - Compensating transactions

3. **CAP Theorem Awareness:**
   - Partition tolerance is mandatory (network failures happen)
   - Choose between Consistency (CP) or Availability (AP)
   - Different components can make different choices

---

## Summary

### Key Takeaways

1. **SQL vs NoSQL:**
   - SQL for structured data, complex queries, strong consistency
   - NoSQL for scalability, flexibility, eventual consistency
   - Choose based on data model and access patterns

2. **Indexing:**
   - B-Tree for ranges, sorting, general purpose
   - Hash for exact matches, high performance
   - Bitmap for low-cardinality, analytics
   - Balance read performance vs write overhead

3. **Replication:**
   - Master-Slave for read scaling, simpler setup
   - Master-Master for write distribution, high availability
   - Understand replication lag and plan accordingly

4. **Sharding:**
   - Horizontal for row distribution, vertical for functionality
   - Geo-based for latency and compliance
   - Choose shard key wisely (high cardinality, even distribution)
   - Plan for resharding from the start

5. **Consistent Hashing:**
   - Minimize data movement when nodes change
   - Use virtual nodes for even distribution
   - Critical for distributed caches and databases

6. **ACID vs BASE:**
   - ACID for strong consistency, financial systems
   - BASE for availability, scalability, social apps
   - Not mutually exclusive (can use both in different parts)

7. **Real-World Patterns:**
   - Learn from industry examples (Instagram, Discord, Netflix)
   - Most systems are hybrid (SQL + NoSQL, ACID + BASE)
   - Trade-offs are inevitable, optimize for your use case

### Further Reading

- **Books:**
  - "Designing Data-Intensive Applications" by Martin Kleppmann
  - "Database Internals" by Alex Petrov
  - "The Art of PostgreSQL" by Dimitri Fontaine

- **Papers:**
  - "Dynamo: Amazon's Highly Available Key-value Store"
  - "Bigtable: A Distributed Storage System for Structured Data"
  - "The Google File System"
  - "CAP Theorem" by Eric Brewer

- **Online Resources:**
  - PostgreSQL Documentation (excellent for understanding SQL internals)
  - AWS Database Blog (real-world scaling patterns)
  - High Scalability Blog (architecture case studies)

---

**Next Week:** Caching, CDNs, and Content Delivery Strategies
