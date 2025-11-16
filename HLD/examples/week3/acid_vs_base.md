# ACID vs BASE: Transaction Models Explained

## Table of Contents
1. [Overview](#overview)
2. [ACID Properties](#acid-properties)
3. [BASE Properties](#base-properties)
4. [Comparison](#comparison)
5. [Real-World Examples](#real-world-examples)
6. [Choosing Between ACID and BASE](#choosing-between-acid-and-base)

---

## Overview

### The CAP Theorem Connection

Before understanding ACID vs BASE, we need to understand the **CAP Theorem**:

```
        Consistency
           △
          ╱ ╲
         ╱   ╲
        ╱     ╲
       ╱  CAP  ╲
      ╱ Theorem ╲
     ╱___________╲
    Availability  Partition Tolerance
```

**CAP Theorem:** In a distributed system, you can only guarantee **2 out of 3**:
- **C**onsistency: All nodes see the same data at the same time
- **A**vailability: Every request receives a response (success or failure)
- **P**artition Tolerance: System continues despite network failures

**Reality:** Network partitions WILL happen, so you must choose:
- **CP Systems (ACID):** Sacrifice availability for consistency
- **AP Systems (BASE):** Sacrifice consistency for availability

### Transaction Models

| Model | Full Form | Priority | Use Case |
|-------|-----------|----------|----------|
| **ACID** | Atomicity, Consistency, Isolation, Durability | Consistency > Availability | Transactional systems (banking, e-commerce) |
| **BASE** | Basically Available, Soft state, Eventual consistency | Availability > Consistency | Distributed systems (social media, analytics) |

---

## ACID Properties

ACID provides strong consistency guarantees for database transactions.

### A - Atomicity

**Definition:** A transaction is **all-or-nothing**. Either all operations succeed, or none do.

#### Example 1: Bank Transfer

```sql
-- Transfer $100 from Account A to Account B
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 'A';  -- Debit
    UPDATE accounts SET balance = balance + 100 WHERE id = 'B';  -- Credit
COMMIT;
```

**Scenarios:**

✅ **Success:** Both updates succeed → transaction committed
```
Account A: $1000 → $900
Account B: $500  → $600
```

❌ **Failure:** Second update fails → entire transaction rolled back
```
Account A: $1000 → $1000  (rollback)
Account B: $500  → $500   (no change)
```

**No partial state** (e.g., money debited but not credited)

#### Example 2: E-Commerce Order

```sql
BEGIN TRANSACTION;
    INSERT INTO orders (user_id, total) VALUES (123, 99.99);
    UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 456;
    INSERT INTO payments (order_id, amount, status) VALUES (1001, 99.99, 'pending');
COMMIT;
```

**If ANY operation fails:**
- No order created
- Inventory unchanged
- No payment record

**Implementation Techniques:**
- **Write-Ahead Logging (WAL):** Log changes before applying
- **Undo Logs:** Roll back on failure
- **Two-Phase Commit (2PC):** Distributed transactions

---

### C - Consistency

**Definition:** Transactions bring the database from one **valid state** to another valid state. All constraints are satisfied.

#### Example 1: Constraints Enforcement

```sql
CREATE TABLE accounts (
    id VARCHAR(10) PRIMARY KEY,
    balance DECIMAL(10, 2) CHECK (balance >= 0)  -- Constraint: no negative balance
);

-- This transaction will FAIL
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 500 WHERE id = 'A';  -- balance becomes -200
COMMIT;
-- Error: CHECK constraint violated
```

**Result:** Transaction is rolled back, database remains consistent.

#### Example 2: Referential Integrity

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id)  -- Foreign key constraint
);

-- This will FAIL if user doesn't exist
INSERT INTO orders (user_id, total) VALUES (999, 100);
-- Error: violates foreign key constraint
```

**Database enforces:**
- NOT NULL constraints
- UNIQUE constraints
- CHECK constraints
- FOREIGN KEY constraints

**Application-level consistency:**
```sql
-- Business rule: Total = sum of items
BEGIN TRANSACTION;
    INSERT INTO orders (user_id, total) VALUES (123, 100);
    INSERT INTO order_items (order_id, price) VALUES (1, 40);
    INSERT INTO order_items (order_id, price) VALUES (1, 30);
    INSERT INTO order_items (order_id, price) VALUES (1, 30);
    -- Total: 40 + 30 + 30 = 100 ✓
COMMIT;
```

---

### I - Isolation

**Definition:** Concurrent transactions **do not interfere** with each other. Each transaction executes as if it's the only one.

#### Isolation Levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Performance |
|-------|------------|---------------------|--------------|-------------|
| **Read Uncommitted** | Yes | Yes | Yes | Fastest |
| **Read Committed** | No | Yes | Yes | Fast |
| **Repeatable Read** | No | No | Yes | Slower |
| **Serializable** | No | No | No | Slowest |

#### Problem 1: Dirty Reads (Reading Uncommitted Data)

```sql
-- Transaction A
BEGIN;
UPDATE accounts SET balance = 1000 WHERE id = 'A';
-- Not committed yet

-- Transaction B (with READ UNCOMMITTED)
BEGIN;
SELECT balance FROM accounts WHERE id = 'A';  -- Reads 1000
COMMIT;

-- Transaction A
ROLLBACK;  -- Oops! Balance is back to 500
```

**Problem:** Transaction B read data that was later rolled back (dirty read).

**Solution:** Use **Read Committed** or higher isolation level.

#### Problem 2: Non-Repeatable Reads

```sql
-- Transaction A
BEGIN;
SELECT balance FROM accounts WHERE id = 'A';  -- Returns 500

-- Transaction B
BEGIN;
UPDATE accounts SET balance = 1000 WHERE id = 'A';
COMMIT;

-- Transaction A (same query)
SELECT balance FROM accounts WHERE id = 'A';  -- Returns 1000 (changed!)
COMMIT;
```

**Problem:** Same query returns different results within the same transaction.

**Solution:** Use **Repeatable Read** or **Serializable** isolation level.

#### Problem 3: Phantom Reads

```sql
-- Transaction A
BEGIN;
SELECT COUNT(*) FROM orders WHERE user_id = 123;  -- Returns 5

-- Transaction B
BEGIN;
INSERT INTO orders (user_id, total) VALUES (123, 100);
COMMIT;

-- Transaction A
SELECT COUNT(*) FROM orders WHERE user_id = 123;  -- Returns 6 (phantom row!)
COMMIT;
```

**Problem:** New rows appear (phantom reads) within the same transaction.

**Solution:** Use **Serializable** isolation level.

#### Implementation: Multi-Version Concurrency Control (MVCC)

PostgreSQL and MySQL InnoDB use MVCC:

```
Transaction T1 (timestamp: 100)
    ↓
Reads snapshot at T=100

Transaction T2 (timestamp: 101)
    ↓
Updates row (creates new version)

Transaction T1 still reads old version (T=100)
    ↓
No blocking!
```

**Benefits:**
- Readers don't block writers
- Writers don't block readers
- Better concurrency

---

### D - Durability

**Definition:** Once a transaction is **committed**, it is **permanent** (even if the system crashes).

#### Example: System Crash

```sql
-- User transfers money
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 'A';
    UPDATE accounts SET balance = balance + 100 WHERE id = 'B';
COMMIT;  -- Success message returned to user

-- 1 second later: Power failure! Server crashes!
```

**After restart:**
- Transaction is still persisted
- Changes are NOT lost
- Database recovers to consistent state

#### Implementation Techniques

**1. Write-Ahead Logging (WAL)**

```
┌──────────────────────────────────────┐
│  Transaction Execution               │
└────────────┬─────────────────────────┘
             ↓
┌──────────────────────────────────────┐
│  1. Write to WAL (sequential writes) │  ← Fast
└────────────┬─────────────────────────┘
             ↓
┌──────────────────────────────────────┐
│  2. Fsync WAL to disk                │  ← Durable
└────────────┬─────────────────────────┘
             ↓
┌──────────────────────────────────────┐
│  3. Return success to client         │
└────────────┬─────────────────────────┘
             ↓
┌──────────────────────────────────────┐
│  4. Apply changes to data files      │  ← Asynchronous (background)
│     (can happen later)               │
└──────────────────────────────────────┘
```

**Recovery Process:**
- On crash: Replay WAL to reconstruct state
- Redo committed transactions
- Undo uncommitted transactions

**2. Checkpointing**

Periodically write dirty pages from memory to disk:
- Reduces recovery time
- Truncates WAL

**3. Replication**

Write to multiple servers for durability:
```
Primary Server
    ↓
Synchronous Replication
    ↓
Replica Server (commits)
    ↓
Success returned to client
```

**Trade-off:** Durability vs Performance
- `fsync=on` (PostgreSQL): Slow but durable
- `fsync=off`: Fast but risk data loss on crash

---

## BASE Properties

BASE is a consistency model for distributed systems that prioritizes availability.

### B - Basically Available

**Definition:** The system **guarantees availability** (responds to requests) but may not return the latest data.

#### Example: Amazon Shopping Cart

```
User in US adds item to cart
    ↓
US Datacenter writes to cart
    ↓
Replication to EU Datacenter (in progress...)
    ↓
User in EU views cart
    ↓
EU Datacenter returns cart (may be stale)
```

**Basically Available:**
- Request succeeds (200 OK)
- May show old cart items
- System is "available" even if not fully synchronized

#### Example: Social Media Likes

```python
# User likes a post
POST /posts/123/like
    ↓
Write to nearest datacenter: likes = 100
    ↓
Return success immediately (201 Created)

# Different user views post (different datacenter)
GET /posts/123
    ↓
Returns: likes = 99 (stale data)
    ↓
After replication: likes = 100 (eventually consistent)
```

**User experience:**
- Like action succeeds immediately
- Like count may be slightly off
- **Acceptable** for most users

---

### S - Soft State

**Definition:** System state may **change over time** without new input (due to eventual consistency).

#### Example: DNS Propagation

```
1. Update DNS record: example.com → 1.2.3.4
   ↓
2. Propagate to DNS servers (TTL: 300s)
   ↓
3. Different DNS servers have different values (soft state)
   ↓
   - Server A: example.com → 1.2.3.4 (new)
   - Server B: example.com → 5.6.7.8 (old)
   ↓
4. Eventually (after TTL expires): All servers converge
```

**Soft state:**
- State is in flux
- Will stabilize eventually
- No strong guarantees at any point in time

#### Example: Shopping Cart

```javascript
// User adds item to cart (US datacenter)
cart.add({ id: 123, name: "Book", price: 20 });

// Replicate to EU datacenter (async)
setTimeout(() => {
    eu_cart.add({ id: 123, name: "Book", price: 20 });
}, 50);  // 50ms replication lag

// User views cart from EU immediately
// May not see the item yet (soft state)
```

---

### E - Eventual Consistency

**Definition:** Given **no new updates**, all replicas will **eventually converge** to the same value.

#### Example: Collaborative Editing

```
User A types "Hello"
User B types "World"

Node 1: "Hello"
Node 2: "World"
    ↓
Replicate & merge
    ↓
Both nodes: "Hello World" (eventually)
```

**Guarantees:**
- ✅ Will be consistent eventually
- ❌ NOT consistent at all times

#### Consistency Window

```
Time →
─────────────────────────────────────────────────────

Write happens
    ↓
    │  ← Inconsistent period (replication lag)
    │
    ↓
Eventually consistent
```

**Replication lag examples:**
- **Redis Cluster:** 0-10ms
- **DynamoDB:** Usually <1 second
- **Cassandra:** Configurable (ms to seconds)
- **DNS:** Minutes to hours (TTL-based)

#### Conflict Resolution

**Last Write Wins (LWW):**
```python
# Node A: Write value="Alice" at timestamp=100
# Node B: Write value="Bob" at timestamp=101

# Eventual state: value="Bob" (timestamp 101 > 100)
```

**Vector Clocks:**
```python
# Track causality
Node A: {A:1, B:0}
Node B: {A:1, B:1}  # B knows about A's change

# Can determine: B's change happened after A's
```

**CRDTs (Conflict-Free Replicated Data Types):**
```python
# Mathematical guarantees of convergence
# Example: G-Counter (grow-only counter)
Node A: {A:5, B:3}  # Total: 8
Node B: {A:4, B:4}  # Total: 8

# Merge: {A:max(5,4), B:max(3,4)} = {A:5, B:4}  # Total: 9
```

---

## Comparison

### Side-by-Side Comparison

| Aspect | ACID | BASE |
|--------|------|------|
| **Consistency** | Strong, immediate | Eventual |
| **Availability** | May sacrifice during failures | Prioritized (always available) |
| **Partition Tolerance** | May fail during partitions | Continues during partitions |
| **Latency** | Higher (waits for consensus) | Lower (immediate response) |
| **Scalability** | Vertical (harder to scale) | Horizontal (scales easily) |
| **Complexity** | Simpler reasoning | Complex (handle inconsistency) |
| **Use Cases** | Banking, e-commerce checkout | Social media, analytics, caching |

### Visual Comparison

**ACID (Strong Consistency):**
```
User writes value=10
    ↓
[Wait for all replicas to acknowledge]
    ↓
All replicas synchronized: value=10
    ↓
Return success to user

Any read immediately sees: value=10
```

**BASE (Eventual Consistency):**
```
User writes value=10
    ↓
Write to nearest replica
    ↓
Return success immediately
    ↓
[Asynchronous replication in background]

Read from different replica: value=old (possibly)
    ↓
After replication completes: value=10 (eventually)
```

### CAP Theorem Trade-offs

**ACID Systems (CP - Consistency + Partition Tolerance):**
```
Network Partition Detected
    ↓
Choose Consistency over Availability
    ↓
Reject writes to minority partition
    ↓
Users may get errors (unavailable)
```

**Examples:** PostgreSQL (synchronous replication), MongoDB (majority writes)

**BASE Systems (AP - Availability + Partition Tolerance):**
```
Network Partition Detected
    ↓
Choose Availability over Consistency
    ↓
Allow writes to both partitions
    ↓
Users can always write (available)
    ↓
Resolve conflicts later (when partition heals)
```

**Examples:** DynamoDB, Cassandra, Riak

---

## Real-World Examples

### ACID Use Cases

#### 1. Banking System
```sql
-- Transfer $100 from Alice to Bob
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    -- Check balance
    SELECT balance FROM accounts WHERE user='Alice' FOR UPDATE;

    -- Debit
    UPDATE accounts SET balance = balance - 100 WHERE user='Alice';

    -- Credit
    UPDATE accounts SET balance = balance + 100 WHERE user='Bob';

    -- Log transaction
    INSERT INTO transactions (from, to, amount) VALUES ('Alice', 'Bob', 100);

COMMIT;
```

**Why ACID:**
- **Atomicity:** All or nothing (can't lose $100)
- **Consistency:** No negative balances
- **Isolation:** Prevent concurrent transfers from over-drafting
- **Durability:** Transaction is permanent

**Cost of ACID:**
- Higher latency (waits for locks)
- Lower throughput (serializable isolation)
- Single-region (cross-region ACID is slow)

#### 2. E-Commerce Checkout
```sql
BEGIN TRANSACTION;

    -- Reserve inventory
    UPDATE products SET inventory = inventory - 1
    WHERE id = 123 AND inventory > 0;

    -- Create order
    INSERT INTO orders (user_id, product_id, status)
    VALUES (456, 123, 'pending');

    -- Charge payment
    INSERT INTO payments (order_id, amount, status)
    VALUES (1001, 99.99, 'processing');

COMMIT;
```

**Why ACID:**
- Prevent overselling (strong consistency)
- Payment and order must match (consistency)
- No partial orders (atomicity)

---

### BASE Use Cases

#### 1. Social Media Likes
```python
# User likes a post
async def like_post(user_id, post_id):
    # Write to local datacenter (fast)
    await local_db.increment('post:123:likes')

    # Asynchronous replication to other datacenters
    await replicate_async('post:123:likes', increment=1)

    # Return success immediately
    return {"status": "liked", "likes": "~1000"}  # Approximate count
```

**Why BASE:**
- **Speed:** Sub-100ms response (no waiting)
- **Availability:** Works even if other datacenters are down
- **Eventual consistency:** Exact like count not critical
- **Scale:** Millions of likes/second globally

**Acceptable trade-offs:**
- Like count may be off by a few
- Different users see slightly different counts
- Converges eventually

#### 2. Netflix Viewing History
```python
# User watches a video
async def record_view(user_id, video_id, position):
    # Write to nearest Cassandra node
    await cassandra.write(
        f"user:{user_id}:history",
        {video_id: position},
        consistency_level="ONE"  # Write to 1 replica, don't wait for others
    )

    # Async replication to other replicas
    # (happens in background)

    return {"status": "recorded"}
```

**Why BASE:**
- **Availability:** Service stays up even if nodes fail
- **Low latency:** Don't wait for cross-region replication
- **Eventual consistency:** Viewing history will sync eventually
- **Scale:** 200M+ users globally

**Acceptable trade-offs:**
- Resume position may be slightly off if switching devices quickly
- Different devices may show different history temporarily
- Converges within seconds

#### 3. Twitter Followers Count
```python
# User follows another user
async def follow_user(follower_id, followee_id):
    # Write relationship
    await graph_db.create_edge(follower_id, followee_id, 'FOLLOWS')

    # Increment counter (eventually consistent)
    await async_increment_counter(f"user:{followee_id}:followers")

    # No need to wait for count to be accurate
    return {"status": "following"}
```

**Why BASE:**
- **Speed:** Immediate response to user
- **Availability:** Works even during datacenter issues
- **Eventual consistency:** Exact follower count not critical
- **Scale:** Millions of follow actions daily

**Acceptable trade-offs:**
- Follower count may be off by a few
- Different users see slightly different counts

---

## Choosing Between ACID and BASE

### Decision Framework

#### Choose ACID When:

1. **Correctness is Critical**
   - Financial transactions
   - Inventory management (prevent overselling)
   - Booking systems (seats, rooms)
   - Healthcare records

2. **Data Integrity is Paramount**
   - No duplicate charges
   - No lost transactions
   - Referential integrity required

3. **Regulatory Compliance**
   - SOX compliance (financial reporting)
   - HIPAA (healthcare)
   - PCI DSS (payments)

4. **Strong Consistency Required**
   - Read-your-own-writes
   - Immediate visibility of changes
   - No stale data acceptable

**Examples:**
- Payment processing
- Stock trading
- Reservation systems
- Bank transfers

#### Choose BASE When:

1. **Availability > Consistency**
   - Service must always be up
   - Network partitions expected
   - Global distribution required

2. **Eventual Consistency Acceptable**
   - Like counts, view counts
   - Comments, posts
   - Analytics data

3. **Massive Scale Required**
   - Billions of operations/day
   - Global user base
   - Horizontal scaling needed

4. **Low Latency Critical**
   - Real-time features
   - Gaming leaderboards
   - Social media feeds

**Examples:**
- Social media platforms
- Content delivery
- Real-time analytics
- IoT sensor data

### Hybrid Approach

**Many systems use BOTH:**

```
┌─────────────────────────────────────┐
│         Modern Application          │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴───────────┐
    │                      │
    ↓                      ↓
┌───────────┐        ┌──────────┐
│   ACID    │        │   BASE   │
│PostgreSQL │        │Cassandra │
│           │        │          │
│- Orders   │        │- Logs    │
│- Payments │        │- Views   │
│- Users    │        │- Events  │
└───────────┘        └──────────┘
```

**Example: E-Commerce Platform**

| Component | Database | Model | Reason |
|-----------|----------|-------|--------|
| Checkout | PostgreSQL | ACID | Payment accuracy critical |
| Product Catalog | MongoDB | BASE | Flexible schema, high read |
| Session Store | Redis | BASE | Fast, ephemeral data |
| Search | Elasticsearch | BASE | Eventually consistent index |
| Analytics | Cassandra | BASE | Time-series, massive scale |

---

## Summary

### Key Takeaways

1. **ACID provides strong guarantees** but may sacrifice availability and performance
2. **BASE prioritizes availability** but requires handling eventual consistency
3. **Not either/or:** Most large systems use both ACID and BASE in different components
4. **Choose based on requirements:** Correctness vs availability vs scale
5. **CAP Theorem:** Understand the trade-offs you're making

### Quick Reference

**ACID (Traditional Relational Databases):**
- ✅ Strong consistency
- ✅ Data integrity
- ✅ Simpler reasoning
- ❌ Harder to scale
- ❌ Lower availability
- ❌ Higher latency

**BASE (Distributed NoSQL Systems):**
- ✅ High availability
- ✅ Horizontal scalability
- ✅ Low latency
- ❌ Eventual consistency
- ❌ Complex conflict resolution
- ❌ Harder to reason about

### When in Doubt

**Start with ACID (SQL)** for:
- New applications
- Unknown scale
- Correctness is critical

**Add BASE (NoSQL)** when:
- Scale proves ACID insufficient
- Specific use cases benefit (caching, search, analytics)
- You can tolerate eventual consistency

**Most successful approach:** Use ACID for core transactional data, BASE for scalability and availability where strong consistency isn't required.
