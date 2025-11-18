# Week 2: Servers, Scaling, and Caching

## Table of Contents
1. [Latency and Throughput](#latency-and-throughput)
2. [Consistency and Availability](#consistency-and-availability)
3. [CAP Theorem](#cap-theorem)
4. [Load Balancers](#load-balancers)
5. [Horizontal vs Vertical Scaling](#horizontal-vs-vertical-scaling)
6. [Caching Strategies](#caching-strategies)
7. [Cache Eviction Policies](#cache-eviction-policies)
8. [Pub/Sub Systems](#pubsub-systems)
9. [Interview Tips](#interview-tips)

---

## Latency and Throughput

### Latency
**Definition**: Time taken to perform a single operation or deliver a single message.

**Key Concepts**:
- Measured in milliseconds (ms) or microseconds (μs)
- Lower is better
- Types of latency:
  - **Network latency**: Time for data to travel between nodes
  - **Processing latency**: Time to process a request
  - **Disk I/O latency**: Time to read/write from disk
  - **Database latency**: Time to execute a query

**Latency Numbers Every Programmer Should Know** (2024):
```
L1 cache reference                           0.5 ns
Branch mispredict                            5   ns
L2 cache reference                           7   ns
Mutex lock/unlock                           25   ns
Main memory reference                      100   ns
Compress 1K bytes with Snappy            3,000   ns  =   3 μs
Send 1K bytes over 1 Gbps network       10,000   ns  =  10 μs
Read 4K randomly from SSD              150,000   ns  = 150 μs
Read 1 MB sequentially from memory     250,000   ns  = 250 μs
Round trip within same datacenter      500,000   ns  = 500 μs
Read 1 MB sequentially from SSD      1,000,000   ns  =   1 ms
Disk seek                           10,000,000   ns  =  10 ms
Read 1 MB sequentially from disk    20,000,000   ns  =  20 ms
Send packet CA->Netherlands->CA    150,000,000   ns  = 150 ms
```

### Throughput
**Definition**: Number of operations or messages processed per unit time.

**Key Concepts**:
- Measured in operations/sec, requests/sec, or MB/sec
- Higher is better
- Affected by:
  - System resources (CPU, memory, network bandwidth)
  - Parallelization
  - Bottlenecks in the system

### Latency vs Throughput Trade-offs

```
┌─────────────────────────────────────────────────────────┐
│              Latency vs Throughput Matrix               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  High Throughput ▲                                     │
│                  │  ┌─────────────┐                    │
│                  │  │   Batch      │                   │
│                  │  │  Processing  │                   │
│                  │  │ (High T/     │                   │
│                  │  │  High L)     │                   │
│                  │  └─────────────┘                    │
│                  │                                      │
│                  │  ┌─────────────┐ ┌─────────────┐   │
│                  │  │   Ideal     │ │  Message    │   │
│                  │  │  (High T/   │ │   Queues    │   │
│                  │  │   Low L)    │ │ (Med T/L)   │   │
│                  │  └─────────────┘ └─────────────┘   │
│                  │                                      │
│  Low Throughput  │  ┌─────────────┐                    │
│                  │  │  Real-time  │                    │
│                  │  │   Gaming    │                    │
│                  │  │  (Low T/    │                    │
│                  │  │   Low L)    │                    │
│                  └──┴─────────────┴───────────────────►│
│                    Low Latency      High Latency        │
└─────────────────────────────────────────────────────────┘
```

**Examples**:
- **Low Latency, Low Throughput**: Real-time gaming, stock trading
- **Low Latency, High Throughput**: CDN, in-memory databases
- **High Latency, High Throughput**: Batch processing, data warehouses
- **High Latency, Low Throughput**: Avoid this scenario!

---

## Consistency and Availability

### Consistency
**Definition**: All nodes see the same data at the same time.

**Consistency Models**:

#### 1. Strong Consistency
- Read always returns the most recent write
- Highest data accuracy
- May have higher latency
- Example: Financial transactions, inventory systems

```
Client A: WRITE(x=5) ─────────────────┐
                                       ▼
                                   [Database]
                                       │
Client B: READ(x) ────────────────────┴─► Returns: 5 (always latest)
```

#### 2. Eventual Consistency
- Updates propagate asynchronously
- Eventually all nodes converge to same value
- Lower latency, higher availability
- Example: DNS, social media feeds, shopping carts

```
Client A: WRITE(x=5) ────► [Node 1: x=5]
                                 │
                                 │ (async replication)
                                 ▼
Client B: READ(x) ───────► [Node 2: x=3] Returns: 3 (stale)
                                 │
                                 │ (after sync)
                                 ▼
Client B: READ(x) ───────► [Node 2: x=5] Returns: 5 (consistent)
```

#### 3. Weak Consistency
- No guarantee reads will see latest write
- Best effort
- Example: Live video streaming, VoIP, real-time multiplayer games

#### 4. Causal Consistency
- Maintains causal relationships between operations
- If operation B depends on operation A, all nodes see A before B
- Example: Comment threads, messaging apps

### Availability
**Definition**: System remains operational and responsive to requests.

**Availability Metrics**:
```
Availability % | Downtime/Year | Downtime/Month | Downtime/Week
---------------|---------------|----------------|---------------
90% (1 nine)   | 36.5 days     | 72 hours       | 16.8 hours
99% (2 nines)  | 3.65 days     | 7.2 hours      | 1.68 hours
99.9% (3 nines)| 8.76 hours    | 43.2 minutes   | 10.1 minutes
99.99% (4 nines)| 52.6 minutes | 4.32 minutes   | 1.01 minutes
99.999% (5 nines)| 5.26 minutes| 25.9 seconds   | 6.05 seconds
99.9999% (6 nines)| 31.5 seconds| 2.59 seconds  | 0.605 seconds
```

**High Availability Strategies**:
1. **Redundancy**: Multiple instances of components
2. **Failover**: Automatic switch to backup systems
3. **Load Balancing**: Distribute traffic across servers
4. **Health Checks**: Monitor and detect failures
5. **Geographic Distribution**: Multi-region deployment

---

## CAP Theorem

### The CAP Theorem
**Formulated by Eric Brewer (2000)**

States that a distributed system can provide only **TWO** of the following three guarantees:

1. **Consistency (C)**: All nodes see the same data at the same time
2. **Availability (A)**: Every request receives a response (success or failure)
3. **Partition Tolerance (P)**: System continues to operate despite network partitions

```
                    CAP Theorem Triangle

                           C
                          /│\
                         / │ \
                        /  │  \
                       /   │   \
                      /    │    \
                     /     │     \
                    /  CP  │  CA  \
                   /       │       \
                  /        │        \
                 /         │         \
                /__________│__________\
               A           P           P
                    \  AP  /
                     \    /
                      \  /
                       \/
```

### CAP Trade-offs

#### CP Systems (Consistency + Partition Tolerance)
- **Choose**: Consistency over Availability
- **Behavior**: Reject requests if cannot guarantee consistency
- **Examples**:
  - MongoDB (with default settings)
  - HBase
  - Redis (with synchronous replication)
  - Banking systems
  - Zookeeper

**Use Case**: Financial transactions, inventory management

```
Scenario: Network partition occurs
┌─────────┐   X   ┌─────────┐
│ Node A  │ ─┼──► │ Node B  │
│ x = 5   │   X   │ x = 3   │
└─────────┘       └─────────┘

Client → Node B: READ(x)
Response: ERROR (503 Service Unavailable)
// Prefer consistency over availability
```

#### AP Systems (Availability + Partition Tolerance)
- **Choose**: Availability over Consistency
- **Behavior**: Always respond, accept stale data temporarily
- **Examples**:
  - Cassandra
  - DynamoDB
  - Couchbase
  - DNS
  - Social media platforms

**Use Case**: Social media, shopping carts, product catalogs

```
Scenario: Network partition occurs
┌─────────┐   X   ┌─────────┐
│ Node A  │ ─┼──► │ Node B  │
│ x = 5   │   X   │ x = 3   │
└─────────┘       └─────────┘

Client → Node B: READ(x)
Response: 3 (stale data, but available)
// Prefer availability, eventual consistency
```

#### CA Systems (Consistency + Availability)
- **Choose**: Consistency and Availability (no partition tolerance)
- **Reality**: Not practical for distributed systems
- **Examples**:
  - Traditional RDBMS (PostgreSQL, MySQL) on single node
  - In-memory databases on single machine

**Note**: In distributed systems, network partitions are inevitable, so P is mandatory. Real choice is between CP and AP.

### PACELC Theorem (Extended CAP)

**PACELC** extends CAP to address normal operation (no partition):

- **If Partition (P)**: Choose between Availability (A) and Consistency (C)
- **Else (E)**: Choose between Latency (L) and Consistency (C)

```
Examples:
- Cassandra: PA/EL (Partition→Availability, Normal→Latency)
- MongoDB: PC/EC (Partition→Consistency, Normal→Consistency)
- DynamoDB: PA/EL
- HBase: PC/EC
```

---

## Load Balancers

### What is a Load Balancer?

A load balancer distributes incoming network traffic across multiple servers to ensure:
- No single server bears too much demand
- Improved responsiveness and availability
- Redundancy and fault tolerance

```
                      Internet
                         │
                         ▼
                  ┌─────────────┐
                  │    Load     │
                  │  Balancer   │
                  └─────────────┘
                    │    │    │
        ┌───────────┘    │    └───────────┐
        ▼                ▼                ▼
   ┌─────────┐     ┌─────────┐     ┌─────────┐
   │Server 1 │     │Server 2 │     │Server 3 │
   └─────────┘     └─────────┘     └─────────┘
```

### Load Balancing Algorithms

#### 1. Round Robin
**Description**: Distributes requests sequentially in circular order.

**Pros**:
- Simple to implement
- Fair distribution
- Works well when servers have similar capacity

**Cons**:
- Doesn't consider server load or capacity
- Long sessions can cause imbalance

**Example**:
```
Request 1 → Server 1
Request 2 → Server 2
Request 3 → Server 3
Request 4 → Server 1
Request 5 → Server 2
...
```

**Best For**: Servers with equal specs, stateless applications

#### 2. Weighted Round Robin
**Description**: Assigns weights based on server capacity.

**Example**:
```
Server 1 (weight=3): ███
Server 2 (weight=2): ██
Server 3 (weight=1): █

Distribution:
Req 1→S1, Req 2→S1, Req 3→S1, Req 4→S2, Req 5→S2, Req 6→S3
```

#### 3. Least Connections
**Description**: Routes to server with fewest active connections.

**Pros**:
- Considers current server load
- Better for long-lived connections
- Handles varying request durations well

**Cons**:
- More complex tracking
- Slightly higher overhead

**Example**:
```
Server 1: 5 connections
Server 2: 3 connections ← Next request goes here
Server 3: 7 connections
```

**Best For**: Chat applications, database connections, WebSocket servers

#### 4. Weighted Least Connections
**Description**: Combines server capacity with current connections.

**Formula**: Score = Connections / Weight (route to lowest score)

#### 5. IP Hash
**Description**: Hash client IP to determine server.

**Pros**:
- Session persistence (same client → same server)
- No session storage needed
- Cache efficiency on servers

**Cons**:
- Uneven distribution if clients behind NAT
- Server failures affect specific clients
- Difficult to add/remove servers

**Hash Function**:
```
server_index = hash(client_ip) % num_servers
```

**Best For**: Session-based applications, caching scenarios

#### 6. Least Response Time
**Description**: Routes to server with lowest response time and fewest connections.

**Best For**: Performance-critical applications

#### 7. Random
**Description**: Randomly selects a server.

**Best For**: Simple scenarios, testing

### Load Balancer Types

#### Layer 4 (Transport Layer)
- **Protocol**: TCP/UDP
- **Decision based on**: IP, Port
- **Pros**: Fast, low latency
- **Cons**: Limited routing intelligence
- **Examples**: AWS NLB (Network Load Balancer)

#### Layer 7 (Application Layer)
- **Protocol**: HTTP/HTTPS
- **Decision based on**: URL, headers, cookies, message content
- **Pros**: Intelligent routing, content-based decisions
- **Cons**: Higher latency, more processing
- **Examples**: AWS ALB (Application Load Balancer), Nginx, HAProxy

```
Layer 7 Routing Examples:
- /api/* → API Server Pool
- /images/* → Image Server Pool
- /video/* → Video Server Pool
- Cookie[user=premium] → Premium Server Pool
```

### Load Balancer Health Checks

:::multilang
```python
# Health check configuration
health_check = {
    "interval": 30,  # seconds
    "timeout": 5,    # seconds
    "unhealthy_threshold": 3,  # consecutive failures
    "healthy_threshold": 2,    # consecutive successes
    "path": "/health",
    "expected_status": 200
}
```

```cpp
#include <string>

// Health check configuration
struct HealthCheckConfig {
    int interval = 30;              // seconds
    int timeout = 5;                // seconds
    int unhealthy_threshold = 3;    // consecutive failures
    int healthy_threshold = 2;      // consecutive successes
    std::string path = "/health";
    int expected_status = 200;
};

// Usage
HealthCheckConfig health_check;
```

```java
// Health check configuration
public class HealthCheckConfig {
    private int interval = 30;              // seconds
    private int timeout = 5;                // seconds
    private int unhealthyThreshold = 3;     // consecutive failures
    private int healthyThreshold = 2;       // consecutive successes
    private String path = "/health";
    private int expectedStatus = 200;

    // Getters and setters
    public int getInterval() { return interval; }
    public void setInterval(int interval) { this.interval = interval; }
    public int getTimeout() { return timeout; }
    public void setTimeout(int timeout) { this.timeout = timeout; }
    public int getUnhealthyThreshold() { return unhealthyThreshold; }
    public void setUnhealthyThreshold(int threshold) { this.unhealthyThreshold = threshold; }
    public int getHealthyThreshold() { return healthyThreshold; }
    public void setHealthyThreshold(int threshold) { this.healthyThreshold = threshold; }
    public String getPath() { return path; }
    public void setPath(String path) { this.path = path; }
    public int getExpectedStatus() { return expectedStatus; }
    public void setExpectedStatus(int status) { this.expectedStatus = status; }
}

// Usage
HealthCheckConfig healthCheck = new HealthCheckConfig();
```
:::

---

## Horizontal vs Vertical Scaling

### Vertical Scaling (Scale Up)

**Definition**: Increase capacity of existing server (more CPU, RAM, disk).

```
Before:                    After:
┌─────────────┐           ┌─────────────┐
│   Server    │           │   Server    │
│  4 CPU      │  ──────►  │  16 CPU     │
│  8 GB RAM   │           │  64 GB RAM  │
│  100 GB SSD │           │  1 TB SSD   │
└─────────────┘           └─────────────┘
```

**Pros**:
- ✅ Simple implementation
- ✅ No application changes needed
- ✅ No distributed system complexity
- ✅ Lower software licensing costs
- ✅ Data consistency maintained
- ✅ No network latency between components

**Cons**:
- ❌ Single point of failure
- ❌ Hardware limits (max CPU/RAM)
- ❌ Expensive high-end hardware
- ❌ Downtime during upgrades
- ❌ Limited by single machine capacity
- ❌ No geographic distribution

**When to Use**:
- Small to medium applications
- Applications with tight consistency requirements
- Legacy systems that can't be distributed
- Database scaling (initial phase)
- Development/testing environments

**Cost Analysis**:
```
Example Cloud Provider Pricing (monthly):
- 2 CPU, 8 GB:   $40
- 4 CPU, 16 GB:  $80
- 8 CPU, 32 GB:  $160
- 16 CPU, 64 GB: $320
- 32 CPU, 128 GB: $640
```

### Horizontal Scaling (Scale Out)

**Definition**: Add more servers to distribute load.

```
Before:                    After:
┌─────────────┐           ┌─────────────┐
│   Server    │           │  Server 1   │
│  4 CPU      │           │  4 CPU      │
│  8 GB RAM   │  ──────►  ├─────────────┤
│  100 GB SSD │           │  Server 2   │
└─────────────┘           │  4 CPU      │
                          ├─────────────┤
                          │  Server 3   │
                          │  4 CPU      │
                          └─────────────┘
```

**Pros**:
- ✅ Near infinite scalability
- ✅ High availability and redundancy
- ✅ Cost-effective (commodity hardware)
- ✅ No downtime during scaling
- ✅ Geographic distribution possible
- ✅ Fault tolerance
- ✅ Load distribution

**Cons**:
- ❌ Complex architecture
- ❌ Data consistency challenges
- ❌ Network overhead
- ❌ Load balancer needed
- ❌ Higher operational complexity
- ❌ Distributed system bugs
- ❌ Session management complexity

**When to Use**:
- High traffic applications
- Need for high availability
- Microservices architecture
- Global applications
- Stateless applications
- Cloud-native applications

**Cost Analysis**:
```
Example: Same total capacity
Vertical: 1x (16 CPU, 64 GB) = $320/month
Horizontal: 4x (4 CPU, 16 GB) = 4 × $80 = $320/month

Benefits of Horizontal:
- 4 servers vs 1 (redundancy)
- Can scale to 5-10 servers easily
- Individual server failure: 25% capacity loss vs 100%
```

### Comparison Matrix

| Feature | Vertical Scaling | Horizontal Scaling |
|---------|-----------------|-------------------|
| **Complexity** | Low | High |
| **Consistency** | Strong | Eventual |
| **Availability** | Lower | Higher |
| **Scalability Limit** | Hardware max | Near infinite |
| **Cost (small scale)** | Lower | Higher |
| **Cost (large scale)** | Much higher | Lower |
| **Downtime** | Required | Zero |
| **Geographic Distribution** | No | Yes |
| **Data Sync** | Not needed | Complex |
| **Load Balancing** | Not needed | Required |
| **Application Changes** | Minimal | Significant |

### Hybrid Approach

Most production systems use **both**:

```
Hybrid Scaling Strategy:

1. Start with Vertical Scaling
   - Simple, fast to implement
   - Good for MVP and early growth

2. Add Horizontal Scaling
   - When traffic grows
   - For high availability

3. Optimize Both
   - Vertical: Database servers (better I/O)
   - Horizontal: Application servers (stateless)

Example Architecture:
┌─────────────────────────────────────┐
│       Load Balancer (HA Pair)       │
└─────────────────┬───────────────────┘
                  │
     ┌────────────┼────────────┐
     ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│  App    │  │  App    │  │  App    │  ← Horizontal (Scale Out)
│Server 1 │  │Server 2 │  │Server 3 │     Stateless, many servers
│ 4C/16GB │  │ 4C/16GB │  │ 4C/16GB │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  ▼
          ┌──────────────┐
          │  Database    │              ← Vertical (Scale Up)
          │  Server      │                 Stateful, powerful
          │  32C/256GB   │                 High I/O, SSD
          └──────────────┘
```

---

## Caching Strategies

### What is Caching?

Caching stores frequently accessed data in fast storage (memory) to reduce:
- Database load
- API calls
- Computation time
- Latency

**Cache Hit Ratio**: `Hits / (Hits + Misses) × 100%`
- Good: > 80%
- Excellent: > 95%

### Caching Strategies

#### 1. Cache-Aside (Lazy Loading)

**How it works**:
1. Application checks cache first
2. If miss, fetch from database
3. Store in cache for future requests
4. Return data

```
Read Flow:
                ┌─────────────┐
                │ Application │
                └──────┬──────┘
                       │
                       │ 1. GET(key)
                       ▼
                 ┌──────────┐
                 │  Cache   │
                 └──────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
    Hit │                             │ Miss
        ▼                             ▼
   ┌────────┐                   ┌─────────┐
   │ Return │                   │ Fetch   │
   │  Data  │                   │ from DB │
   └────────┘                   └─────────┘
                                      │
                                      │ 2. Store in cache
                                      ▼
                                 ┌─────────┐
                                 │ Return  │
                                 │  Data   │
                                 └─────────┘

Write Flow:
┌─────────────┐
│ Application │
└──────┬──────┘
       │ 1. WRITE to DB
       ▼
  ┌─────────┐
  │Database │
  └─────────┘
       │
       │ 2. INVALIDATE cache
       ▼
  ┌──────────┐
  │  Cache   │
  └──────────┘
```

**Pros**:
- ✅ Cache only what's needed (efficient memory use)
- ✅ Cache failures don't break system
- ✅ Simple to implement
- ✅ Works well with read-heavy workloads

**Cons**:
- ❌ Cache miss penalty (3 trips: cache, DB, cache)
- ❌ Stale data possible
- ❌ Initial requests always miss (cold start)

**Best For**: Read-heavy applications, user sessions, product catalogs

**Implementation**:
:::multilang
```python
def get_user(user_id):
    # 1. Try cache
    user = cache.get(f"user:{user_id}")

    if user:
        return user  # Cache hit

    # 2. Cache miss - fetch from DB
    user = database.get_user(user_id)

    # 3. Store in cache
    cache.set(f"user:{user_id}", user, ttl=3600)

    return user

def update_user(user_id, data):
    # 1. Update database
    database.update_user(user_id, data)

    # 2. Invalidate cache
    cache.delete(f"user:{user_id}")
```

```cpp
#include <string>
#include <optional>
#include <memory>

// Assuming cache and database are global or injected dependencies
extern Cache cache;
extern Database database;

// Get user with cache-aside pattern
std::optional<User> get_user(int user_id) {
    // 1. Try cache
    std::string cache_key = "user:" + std::to_string(user_id);
    auto user = cache.get(cache_key);

    if (user.has_value()) {
        return user;  // Cache hit
    }

    // 2. Cache miss - fetch from DB
    auto db_user = database.get_user(user_id);

    if (db_user.has_value()) {
        // 3. Store in cache
        cache.set(cache_key, db_user.value(), 3600);  // TTL: 3600 seconds
    }

    return db_user;
}

// Update user and invalidate cache
void update_user(int user_id, const UserData& data) {
    // 1. Update database
    database.update_user(user_id, data);

    // 2. Invalidate cache
    std::string cache_key = "user:" + std::to_string(user_id);
    cache.remove(cache_key);
}
```

```java
import java.util.Optional;

public class UserService {
    private final Cache cache;
    private final Database database;

    public UserService(Cache cache, Database database) {
        this.cache = cache;
        this.database = database;
    }

    // Get user with cache-aside pattern
    public Optional<User> getUser(int userId) {
        // 1. Try cache
        String cacheKey = "user:" + userId;
        Optional<User> user = cache.get(cacheKey);

        if (user.isPresent()) {
            return user;  // Cache hit
        }

        // 2. Cache miss - fetch from DB
        user = database.getUser(userId);

        if (user.isPresent()) {
            // 3. Store in cache
            cache.set(cacheKey, user.get(), 3600);  // TTL: 3600 seconds
        }

        return user;
    }

    // Update user and invalidate cache
    public void updateUser(int userId, UserData data) {
        // 1. Update database
        database.updateUser(userId, data);

        // 2. Invalidate cache
        String cacheKey = "user:" + userId;
        cache.delete(cacheKey);
    }
}
```
:::

#### 2. Read-Through Cache

**How it works**:
1. Application requests data from cache
2. Cache library handles DB fetch on miss
3. Cache populates itself automatically

```
                ┌─────────────┐
                │ Application │
                └──────┬──────┘
                       │ GET(key)
                       ▼
                 ┌──────────────┐
                 │ Cache Layer  │
                 │ (Smart Proxy)│
                 └──────┬───────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
     Hit │                             │ Miss
         ▼                             ▼
    ┌────────┐                   ┌──────────┐
    │ Return │                   │Auto Fetch│
    │  Data  │                   │ from DB  │
    └────────┘                   └──────────┘
                                       │
                                       │ Cache + Return
                                       ▼
```

**Pros**:
- ✅ Application code simplified
- ✅ Consistent data access pattern
- ✅ Cache manages its own population

**Cons**:
- ❌ Cache miss still has penalty
- ❌ Tighter coupling with cache system
- ❌ More complex cache implementation

**Best For**: Libraries providing transparent caching, ORMs

#### 3. Write-Through Cache

**How it works**:
1. Application writes to cache
2. Cache synchronously writes to database
3. Both updated before return

```
Write Flow:
┌─────────────┐
│ Application │
└──────┬──────┘
       │ WRITE(key, value)
       ▼
 ┌────────────┐
 │   Cache    │
 └──────┬─────┘
        │
        │ 1. Update cache
        │ 2. Write to DB (sync)
        ▼
   ┌─────────┐
   │Database │
   └─────────┘
        │
        │ Confirm
        ▼
 ┌────────────┐
 │   Return   │
 │  Success   │
 └────────────┘
```

**Pros**:
- ✅ Cache always consistent with DB
- ✅ No stale data
- ✅ Data not lost if cache fails
- ✅ Simplified read logic

**Cons**:
- ❌ Higher write latency (2 writes)
- ❌ Unnecessary writes to cache for rarely-read data
- ❌ Wasted cache space
- ❌ Cache failure affects writes

**Best For**: Applications requiring strong consistency, financial systems

**Implementation**:
:::multilang
```python
def update_user(user_id, data):
    # Write to cache
    cache.set(f"user:{user_id}", data)

    # Synchronously write to database
    database.update_user(user_id, data)

    return data
```

```cpp
#include <string>

// Assuming cache and database are global or injected dependencies
extern Cache cache;
extern Database database;

// Write-through cache update
UserData update_user(int user_id, const UserData& data) {
    // Write to cache
    std::string cache_key = "user:" + std::to_string(user_id);
    cache.set(cache_key, data);

    // Synchronously write to database
    database.update_user(user_id, data);

    return data;
}
```

```java
public class UserService {
    private final Cache cache;
    private final Database database;

    public UserService(Cache cache, Database database) {
        this.cache = cache;
        this.database = database;
    }

    // Write-through cache update
    public UserData updateUser(int userId, UserData data) {
        // Write to cache
        String cacheKey = "user:" + userId;
        cache.set(cacheKey, data);

        // Synchronously write to database
        database.updateUser(userId, data);

        return data;
    }
}
```
:::

#### 4. Write-Back (Write-Behind) Cache

**How it works**:
1. Application writes to cache only
2. Cache asynchronously writes to DB later
3. Immediate response to application

```
Write Flow:
┌─────────────┐
│ Application │
└──────┬──────┘
       │ WRITE(key, value)
       ▼
 ┌────────────┐
 │   Cache    │ ← Immediate return
 └──────┬─────┘
        │
        │ Async (batched)
        │ after delay
        ▼
   ┌─────────┐
   │Database │
   └─────────┘
```

**Pros**:
- ✅ Lowest write latency
- ✅ Can batch writes (higher throughput)
- ✅ Reduces DB load
- ✅ Best performance

**Cons**:
- ❌ Risk of data loss if cache crashes
- ❌ Complex implementation
- ❌ Eventual consistency
- ❌ Need for persistent cache or write-ahead log

**Best For**: Write-heavy applications, analytics, logging, social media

**Implementation Considerations**:
:::multilang
```python
# Write-back queue
write_queue = []

def update_user(user_id, data):
    # 1. Write to cache immediately
    cache.set(f"user:{user_id}", data)

    # 2. Queue for async DB write
    write_queue.append((user_id, data))

    # Immediate return
    return data

# Background worker
def flush_writes():
    while True:
        if len(write_queue) >= BATCH_SIZE or time_elapsed > MAX_DELAY:
            batch = write_queue[:BATCH_SIZE]
            database.batch_update(batch)
            write_queue = write_queue[BATCH_SIZE:]
        time.sleep(1)
```

```cpp
#include <queue>
#include <thread>
#include <mutex>
#include <chrono>
#include <vector>

// Assuming cache and database are global or injected dependencies
extern Cache cache;
extern Database database;

// Thread-safe write queue
std::queue<std::pair<int, UserData>> write_queue;
std::mutex queue_mutex;

const int BATCH_SIZE = 100;
const int MAX_DELAY_MS = 1000;

// Write-back update
UserData update_user(int user_id, const UserData& data) {
    // 1. Write to cache immediately
    std::string cache_key = "user:" + std::to_string(user_id);
    cache.set(cache_key, data);

    // 2. Queue for async DB write
    {
        std::lock_guard<std::mutex> lock(queue_mutex);
        write_queue.push({user_id, data});
    }

    // Immediate return
    return data;
}

// Background worker
void flush_writes() {
    while (true) {
        std::vector<std::pair<int, UserData>> batch;

        {
            std::lock_guard<std::mutex> lock(queue_mutex);
            int count = std::min(BATCH_SIZE, (int)write_queue.size());

            for (int i = 0; i < count; i++) {
                batch.push_back(write_queue.front());
                write_queue.pop();
            }
        }

        if (!batch.empty()) {
            database.batch_update(batch);
        }

        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
}
```

```java
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class WriteBackCache {
    private final Cache cache;
    private final Database database;
    private final BlockingQueue<UserUpdate> writeQueue;

    private static final int BATCH_SIZE = 100;
    private static final int MAX_DELAY_MS = 1000;

    public WriteBackCache(Cache cache, Database database) {
        this.cache = cache;
        this.database = database;
        this.writeQueue = new LinkedBlockingQueue<>();

        // Start background worker
        new Thread(this::flushWrites).start();
    }

    // Write-back update
    public UserData updateUser(int userId, UserData data) {
        // 1. Write to cache immediately
        String cacheKey = "user:" + userId;
        cache.set(cacheKey, data);

        // 2. Queue for async DB write
        writeQueue.offer(new UserUpdate(userId, data));

        // Immediate return
        return data;
    }

    // Background worker
    private void flushWrites() {
        while (true) {
            try {
                List<UserUpdate> batch = new ArrayList<>();

                // Collect batch
                while (batch.size() < BATCH_SIZE && !writeQueue.isEmpty()) {
                    UserUpdate update = writeQueue.poll();
                    if (update != null) {
                        batch.add(update);
                    }
                }

                // Write batch to database
                if (!batch.isEmpty()) {
                    database.batchUpdate(batch);
                }

                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }

    private static class UserUpdate {
        final int userId;
        final UserData data;

        UserUpdate(int userId, UserData data) {
            this.userId = userId;
            this.data = data;
        }
    }
}
```
:::

#### 5. Write-Around Cache

**How it works**:
1. Writes go directly to database
2. Cache is bypassed on write
3. Cache populated on read miss

```
Write Flow:
┌─────────────┐
│ Application │
└──────┬──────┘
       │ WRITE
       │ (bypass cache)
       ▼
   ┌─────────┐
   │Database │
   └─────────┘

Read Flow:
┌─────────────┐
│ Application │
└──────┬──────┘
       │ READ
       ▼
 ┌────────────┐
 │   Cache    │
 └──────┬─────┘
        │
   Miss │
        ▼
   ┌─────────┐
   │Database │
   └─────────┘
```

**Pros**:
- ✅ No cache pollution from one-time writes
- ✅ Good for write-heavy, read-light workloads
- ✅ Simpler than write-through

**Cons**:
- ❌ Recently written data not cached
- ❌ Read miss after write
- ❌ Higher latency for reads after writes

**Best For**: Write-once-read-rarely data, logs, archives

### Strategy Comparison

| Strategy | Write Latency | Read Latency | Consistency | Complexity | Data Loss Risk |
|----------|---------------|--------------|-------------|------------|----------------|
| **Cache-Aside** | Low (DB only) | Med (miss penalty) | Eventual | Low | Low |
| **Read-Through** | Low (DB only) | Med (miss penalty) | Eventual | Medium | Low |
| **Write-Through** | High (2 writes) | Low | Strong | Medium | Very Low |
| **Write-Back** | Very Low | Low | Eventual | High | Medium |
| **Write-Around** | Low (DB only) | High (miss likely) | Strong | Low | Low |

---

## Cache Eviction Policies

When cache is full, eviction policy determines what to remove.

### 1. LRU (Least Recently Used)

**Description**: Evict the least recently accessed item.

**How it works**:
- Track access time for each item
- Remove item with oldest access time
- Usually implemented with HashMap + Doubly Linked List

```
Cache: [A:1, B:2, C:3]  (A oldest, C newest)

Access B:
Cache: [A:1, C:3, B:2]  (B moved to end)

Add D (cache full):
Cache: [C:3, B:2, D:4]  (A evicted)
```

**Data Structure**:
```
    Head                                    Tail
     │                                       │
     ▼                                       ▼
┌────────┐    ┌────────┐    ┌────────┐
│   A:1  │◄──►│   B:2  │◄──►│   C:3  │
└────────┘    └────────┘    └────────┘
     ▲             ▲             ▲
     │             │             │
  ┌──┴─────────────┴─────────────┴───┐
  │  HashMap: {A→Node, B→Node, C→Node}│
  └────────────────────────────────────┘
```

**Time Complexity**:
- Get: O(1)
- Put: O(1)
- Space: O(n)

**Pros**:
- ✅ Simple to understand
- ✅ Works well for temporal locality
- ✅ O(1) operations

**Cons**:
- ❌ Doesn't consider access frequency
- ❌ One-time bulk access can pollute cache

**Best For**:
- General purpose caching
- Web page caching
- Database query results
- Most caching scenarios

**Real-World Use**: Redis, Memcached, Linux page cache

### 2. LFU (Least Frequently Used)

**Description**: Evict item with lowest access count.

**How it works**:
- Track access frequency for each item
- Remove item with lowest frequency
- Break ties with LRU

```
Cache with frequencies:
A: count=5, B: count=2, C: count=8

Add D (cache full):
Evict B (lowest frequency)
Cache: A: count=5, C: count=8, D: count=1
```

**Data Structure**:
```
Frequency Lists:
Freq 1: [D] ─┐
Freq 2: []   │
Freq 3: [A] ─┤
Freq 4: []   ├─ Min-Heap or Ordered Structure
Freq 5: []   │
Freq 6: [C] ─┘

HashMap: {A→(value, freq), C→(value, freq), D→(value, freq)}
```

**Time Complexity**:
- Get: O(1) or O(log n)
- Put: O(1) or O(log n)
- Space: O(n)

**Pros**:
- ✅ Captures access patterns well
- ✅ Resistant to one-time access spikes
- ✅ Better hit ratio for frequency-based access

**Cons**:
- ❌ More complex implementation
- ❌ Old popular items hard to evict
- ❌ New items easily evicted
- ❌ Doesn't adapt to changing patterns

**Best For**:
- Content popularity (videos, articles)
- Long-term access patterns
- Recommendation systems

**Real-World Use**: CDN caching, Apache Traffic Server

### 3. FIFO (First In, First Out)

**Description**: Evict oldest item in cache (by insertion time).

```
Cache: [A, B, C] (A inserted first)

Add D (cache full):
Cache: [B, C, D] (A evicted)
```

**Data Structure**: Queue

**Time Complexity**:
- Get: O(1)
- Put: O(1)
- Space: O(n)

**Pros**:
- ✅ Very simple
- ✅ Low overhead
- ✅ Predictable behavior

**Cons**:
- ❌ Ignores access patterns
- ❌ May evict frequently used items
- ❌ Poor cache hit ratio

**Best For**:
- Simple buffers
- Streaming data
- When access pattern is random

### 4. LIFO (Last In, First Out)

**Description**: Evict most recently added item.

**Data Structure**: Stack

**Best For**: Very specific use cases, rarely used in practice

### 5. Random Replacement

**Description**: Randomly select item to evict.

**Pros**:
- ✅ Simplest implementation
- ✅ No tracking overhead
- ✅ Works well with uniform access

**Cons**:
- ❌ Unpredictable
- ❌ May evict hot items

**Best For**: Testing, simple scenarios

### 6. TTL (Time To Live)

**Description**: Each item has expiration time, evict expired items.

```python
cache.set("user:123", user_data, ttl=3600)  # 1 hour
# After 3600 seconds, item auto-expires
```

**Pros**:
- ✅ Guarantees data freshness
- ✅ Prevents stale data
- ✅ Works with any eviction policy

**Cons**:
- ❌ Requires time tracking
- ❌ Need background cleanup

**Best For**:
- Session data
- API responses
- Time-sensitive data

### 7. MRU (Most Recently Used)

**Description**: Evict most recently accessed item.

**Best For**: When next access is unlikely to be recent item (rare)

### 8. Adaptive Replacement Cache (ARC)

**Description**: Balances between LRU and LFU dynamically.

**How it works**:
- Maintains two LRU lists: recent and frequent
- Adapts based on workload

**Pros**:
- ✅ Best of both LRU and LFU
- ✅ Adapts to changing patterns
- ✅ Better hit ratio

**Cons**:
- ❌ Complex implementation
- ❌ Higher overhead
- ❌ Patent concerns (expired now)

**Best For**: Enterprise caching systems, ZFS

### Eviction Policy Comparison

| Policy | Complexity | Hit Ratio | Use Case | Overhead |
|--------|-----------|-----------|----------|----------|
| **LRU** | Medium | Good | General purpose | Medium |
| **LFU** | High | Very Good | Frequency patterns | High |
| **FIFO** | Low | Poor | Simple buffers | Low |
| **Random** | Very Low | Fair | Uniform access | Very Low |
| **TTL** | Low | N/A | Time-sensitive | Low |
| **ARC** | Very High | Excellent | Enterprise | High |

### Choosing Eviction Policy - Decision Tree

```
Start
  │
  ├─ Time-sensitive data? ──Yes──► TTL
  │                                  │
  No                                 └─ + LRU/LFU
  │
  ├─ Temporal locality? ──Yes──► LRU
  │
  No
  │
  ├─ Frequency matters? ──Yes──► LFU
  │
  No
  │
  ├─ Changing patterns? ──Yes──► ARC
  │
  No
  │
  └─ Simple/Random? ──Yes──► FIFO or Random
```

---

## Pub/Sub Systems

### What is Pub/Sub?

**Publish/Subscribe** is a messaging pattern where:
- **Publishers** send messages to topics/channels
- **Subscribers** receive messages from topics they're interested in
- Publishers and subscribers are decoupled

```
Publishers                Topic                Subscribers

┌───────────┐                              ┌───────────┐
│Publisher 1│──┐                      ┌───│Subscriber1│
└───────────┘  │                      │   └───────────┘
               ├──► ┌──────────┐  ◄──┤
┌───────────┐  │    │  Topic   │     │   ┌───────────┐
│Publisher 2│──┘    │  "Orders"│     └───│Subscriber2│
└───────────┘       └──────────┘         └───────────┘
                                              │
                                         ┌───────────┐
                                         │Subscriber3│
                                         └───────────┘
```

### Key Concepts

**1. Topics/Channels**: Named message streams
**2. Publishers**: Send messages to topics
**3. Subscribers**: Consume messages from topics
**4. Message Broker**: Routes messages between publishers and subscribers

**Benefits**:
- ✅ Decoupling: Publishers don't know subscribers
- ✅ Scalability: Add subscribers without changing publishers
- ✅ Flexibility: Multiple consumers for same message
- ✅ Asynchronous: Non-blocking communication

### Apache Kafka

**Type**: Distributed streaming platform

**Key Features**:
- High throughput (millions of messages/sec)
- Horizontal scalability
- Fault tolerance through replication
- Message persistence (disk-based)
- Strong ordering guarantees (per partition)

**Architecture**:
```
                    Kafka Cluster

┌─────────────────────────────────────────────┐
│  Topic: "orders"                            │
│                                             │
│  ┌─────────────┐  ┌─────────────┐         │
│  │ Partition 0 │  │ Partition 1 │         │
│  │ [M1][M2][M3]│  │ [M4][M5][M6]│         │
│  └─────────────┘  └─────────────┘         │
│        │                 │                  │
│        ▼                 ▼                  │
│  ┌──────────┐     ┌──────────┐            │
│  │ Broker 1 │     │ Broker 2 │            │
│  └──────────┘     └──────────┘            │
└─────────────────────────────────────────────┘
       ▲                    ▲
       │                    │
    Producers          Consumer Groups
```

**Core Concepts**:

1. **Topics**: Category of messages
2. **Partitions**: Topics split for parallelism
   - Each partition is ordered
   - Messages with same key → same partition
3. **Brokers**: Kafka servers
4. **Producers**: Write to topics
5. **Consumers**: Read from topics
6. **Consumer Groups**: Parallel processing
   - Each partition consumed by one consumer in group
7. **Offsets**: Message position in partition

**Message Flow**:
```
Producer
   │ publish(topic="orders", key="user123", value={...})
   ▼
Kafka Broker
   │ hash(key) % num_partitions = partition_id
   │ append to partition log
   ▼
Consumer Group
   │ poll(topics=["orders"])
   │ assign partitions to consumers
   ▼
Consumer reads from partition
```

**Guarantees**:
- **At-least-once**: Message delivered ≥ 1 time
- **At-most-once**: Message delivered ≤ 1 time
- **Exactly-once**: Message delivered exactly 1 time (with config)

**Use Cases**:
- Event sourcing
- Log aggregation
- Stream processing
- Metrics collection
- Real-time analytics
- Microservice communication

**Pros**:
- ✅ Extreme throughput
- ✅ Durability (messages persisted)
- ✅ Scalable (add brokers/partitions)
- ✅ Replay capability (offset control)
- ✅ Strong ordering per partition

**Cons**:
- ❌ Complex setup and operations
- ❌ Requires ZooKeeper (pre-3.x) or KRaft
- ❌ Higher resource usage
- ❌ Steep learning curve

### RabbitMQ

**Type**: Message broker (AMQP protocol)

**Key Features**:
- Flexible routing
- Multiple messaging protocols
- Message acknowledgments
- Easy setup
- Rich plugins

**Architecture**:
```
Producer ──► Exchange ──► Queue ──► Consumer
                │
                ├─► Binding Rules
                │   (Routing Keys, Patterns)
                │
                └─► Multiple Queues
```

**Exchange Types**:

1. **Direct Exchange**: Route by exact routing key
```
Producer ──► [Direct Exchange] ──routing_key="error"──► [Error Queue] ──► Consumer
                    │
                    └──routing_key="info"──► [Info Queue]
```

2. **Fanout Exchange**: Broadcast to all queues
```
Producer ──► [Fanout Exchange] ──► [Queue 1] ──► Consumer 1
                    │           ├─► [Queue 2] ──► Consumer 2
                    │           └─► [Queue 3] ──► Consumer 3
```

3. **Topic Exchange**: Pattern matching
```
Producer ──► [Topic Exchange]
                    │
                    ├─► pattern="user.*" ──► [User Queue]
                    ├─► pattern="*.error" ──► [Error Queue]
                    └─► pattern="order.#" ──► [Order Queue]
```

4. **Headers Exchange**: Route by message headers

**Message Flow**:
```
1. Producer publishes to Exchange
2. Exchange routes to Queue(s) based on binding
3. Queue stores message
4. Consumer receives message
5. Consumer acknowledges (ACK)
6. Message deleted from queue
```

**Guarantees**:
- Message acknowledgments (ACK/NACK)
- Publisher confirms
- Persistent queues/messages
- Dead letter queues

**Use Cases**:
- Task queues
- Work distribution
- Request/response patterns
- RPC (Remote Procedure Call)
- Complex routing scenarios

**Pros**:
- ✅ Easy to set up
- ✅ Flexible routing
- ✅ Good documentation
- ✅ Management UI
- ✅ Multiple protocols
- ✅ Lower latency

**Cons**:
- ❌ Lower throughput than Kafka
- ❌ No built-in replay
- ❌ Vertical scaling limitations
- ❌ Message deleted after consumption

### Kafka vs RabbitMQ

| Feature | Kafka | RabbitMQ |
|---------|-------|----------|
| **Type** | Streaming platform | Message broker |
| **Throughput** | Very High (millions/sec) | Medium (tens of thousands/sec) |
| **Latency** | Medium | Low |
| **Message Retention** | Persistent (days/weeks) | Until consumed |
| **Message Replay** | Yes (offset-based) | No |
| **Ordering** | Per partition | Per queue |
| **Routing** | Simple (topics/partitions) | Complex (exchanges) |
| **Use Case** | Event streaming, logs | Task queues, RPC |
| **Setup Complexity** | High | Low |
| **Scalability** | Horizontal (excellent) | Vertical (limited) |
| **Consumer Model** | Pull | Push + Pull |
| **Protocols** | Custom | AMQP, MQTT, STOMP |

### Other Pub/Sub Systems

**1. Redis Pub/Sub**
- In-memory
- Very fast
- No persistence
- Fire-and-forget
- Use: Real-time notifications, chat

**2. Google Cloud Pub/Sub**
- Managed service
- Global scale
- At-least-once delivery
- Auto-scaling
- Use: Cloud-native apps

**3. AWS SNS/SQS**
- SNS: Pub/sub (fan-out)
- SQS: Message queue
- Managed, serverless
- Use: AWS ecosystem

**4. NATS**
- Lightweight
- High performance
- Simple
- Use: Microservices, IoT

### Choosing Pub/Sub System

```
Decision Tree:

Need message replay? ──Yes──► Kafka
        │
       No
        │
        ▼
High throughput ──Yes──► Kafka
(>100K msg/sec)?
        │
       No
        │
        ▼
Complex routing? ──Yes──► RabbitMQ
        │
       No
        │
        ▼
Simple/Fast? ──Yes──► Redis Pub/Sub
        │
       No
        │
        ▼
Cloud-native? ──Yes──► Cloud Pub/Sub (GCP/AWS)
        │
       No
        │
        ▼
Lightweight? ──Yes──► NATS
```

---

## Interview Tips

### Common Questions

#### 1. Latency vs Throughput
**Q**: "How would you optimize for low latency vs high throughput?"

**Answer Framework**:
- **Low Latency**:
  - Use caching (Redis, Memcached)
  - CDN for static content
  - Connection pooling
  - Async processing where possible
  - Regional deployment (closer to users)
  - Example: Trading platforms, gaming

- **High Throughput**:
  - Horizontal scaling
  - Load balancing
  - Batch processing
  - Message queues
  - Database sharding
  - Example: Analytics, log processing

#### 2. CAP Theorem
**Q**: "Design a system that handles network partitions."

**Answer Framework**:
1. Identify if you need CP or AP
2. For CP: Use strong consistency (RDBMS, MongoDB)
3. For AP: Use eventual consistency (Cassandra, DynamoDB)
4. Discuss trade-offs for your use case
5. Mention PACELC for normal operation

**Example**:
- Banking → CP (consistency critical)
- Social media → AP (availability critical)

#### 3. Caching Strategy
**Q**: "How would you cache user profile data?"

**Answer Framework**:
```
1. Identify access pattern:
   - Read-heavy? → Cache-aside or Read-through
   - Write-heavy? → Write-back
   - Need consistency? → Write-through

2. Choose eviction policy:
   - User profiles → LRU (temporal locality)
   - Popular content → LFU (frequency-based)

3. Set TTL appropriately:
   - Profile data: 1-24 hours
   - Session data: 30 minutes

4. Handle invalidation:
   - Update user → invalidate cache
   - Or use write-through for critical data

5. Calculate cache size:
   - 1M active users × 10KB/user = 10GB
   - Redis with 16GB server
```

#### 4. Scaling Strategy
**Q**: "Your API is experiencing high traffic. How do you scale?"

**Answer Framework**:
1. **Immediate** (Vertical):
   - Scale up current servers
   - Quick fix, no code changes

2. **Short-term** (Horizontal):
   - Add load balancer
   - Deploy more app servers
   - Use auto-scaling

3. **Long-term** (Architecture):
   - Cache frequently accessed data
   - Database read replicas
   - CDN for static assets
   - Async processing for heavy tasks
   - Microservices if needed

#### 5. Load Balancing
**Q**: "Which load balancing algorithm would you choose?"

**Answer Framework**:
- **Round Robin**: Equal servers, stateless apps
- **Least Connections**: Long-lived connections, WebSockets
- **IP Hash**: Session persistence, caching
- **Weighted**: Servers with different capacities
- **Least Response Time**: Performance-critical

**Example**:
"For a stateless REST API with equal servers, I'd use Round Robin for simplicity. For WebSocket chat, Least Connections to handle variable session lengths."

### System Design Checklist

When designing systems in interviews:

1. **Clarify Requirements**:
   - Functional requirements
   - Non-functional (scale, latency, availability)
   - Constraints

2. **High-Level Design**:
   - Client → Load Balancer → App Servers → Database
   - Add caching, queues as needed

3. **Deep Dive**:
   - Database choice (SQL vs NoSQL)
   - Caching strategy
   - Scaling approach
   - Consistency model

4. **Trade-offs**:
   - Discuss alternatives
   - Explain why you chose X over Y
   - Mention limitations

5. **Numbers**:
   - Estimate QPS, storage, bandwidth
   - Justify cache size, number of servers
   - Use back-of-envelope calculations

### Key Metrics to Remember

**Storage**:
- 1 character = 1 byte
- 1 million users × 1KB data = 1 GB
- Video: 1 hour HD = 2-4 GB

**Network**:
- 1 Gbps network = 125 MB/sec
- CDN can handle 10-100 Gbps

**Throughput**:
- MySQL: ~10K QPS
- Redis: ~100K QPS
- Kafka: ~1M messages/sec

**Latency**:
- Memory: <1ms
- SSD: 1-10ms
- HDD: 10-20ms
- Network (same region): 1-5ms
- Network (cross-region): 50-200ms

### Red Flags to Avoid

❌ Single point of failure
❌ No caching for read-heavy workloads
❌ Synchronous calls for everything
❌ No consideration for scaling
❌ Ignoring CAP theorem implications
❌ Over-engineering (don't add Kafka if simple queue works)
❌ Under-engineering (don't use single server for 1M users)

### Good Practices

✅ Start simple, then scale
✅ Discuss trade-offs explicitly
✅ Use numbers to justify decisions
✅ Consider failure scenarios
✅ Think about monitoring and observability
✅ Mention real-world examples (AWS, Netflix, etc.)
✅ Ask clarifying questions

---

## Summary

### Week 2 Key Takeaways

1. **Latency vs Throughput**:
   - Latency: Time for one operation (lower is better)
   - Throughput: Operations per second (higher is better)
   - Often trade-off between them

2. **CAP Theorem**:
   - Choose 2 of 3: Consistency, Availability, Partition Tolerance
   - In practice: Choose CP or AP (P is mandatory)
   - PACELC extends for normal operation

3. **Load Balancing**:
   - Round Robin: Simple, equal distribution
   - Least Connections: Variable load
   - IP Hash: Session persistence
   - Layer 4 (fast) vs Layer 7 (intelligent)

4. **Scaling**:
   - Vertical: Bigger server (simple, limited)
   - Horizontal: More servers (complex, scalable)
   - Most systems use hybrid approach

5. **Caching Strategies**:
   - Cache-Aside: Most common, lazy loading
   - Write-Through: Strong consistency
   - Write-Back: Best performance, risk of loss
   - Choose based on read/write pattern

6. **Eviction Policies**:
   - LRU: General purpose, temporal locality
   - LFU: Frequency-based, content popularity
   - TTL: Time-sensitive data
   - Choose based on access pattern

7. **Pub/Sub**:
   - Kafka: High throughput, streaming, replay
   - RabbitMQ: Flexible routing, task queues
   - Choose based on use case and scale

### Next Steps

- Practice implementing LRU/LFU caches
- Set up local Kafka/RabbitMQ
- Experiment with different load balancing algorithms
- Design systems with different CAP requirements
- Calculate capacity for real-world scenarios

---

## Additional Resources

### Books
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "System Design Interview" by Alex Xu

### Online
- [High Scalability Blog](http://highscalability.com/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)
- [Google SRE Book](https://sre.google/books/)

### Practice
- LeetCode System Design
- System Design Primer (GitHub)
- Educative.io System Design courses

---

**End of Week 2 Content**
