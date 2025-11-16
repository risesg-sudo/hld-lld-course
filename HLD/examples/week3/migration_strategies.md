# Database Migration Strategies: Zero-Downtime Approaches

## Table of Contents
1. [Overview](#overview)
2. [Types of Migrations](#types-of-migrations)
3. [Zero-Downtime Migration Patterns](#zero-downtime-migration-patterns)
4. [Schema Migration Strategies](#schema-migration-strategies)
5. [Data Migration Strategies](#data-migration-strategies)
6. [Real-World Examples](#real-world-examples)
7. [Best Practices](#best-practices)

---

## Overview

### Why Database Migrations are Challenging

**Common Challenges:**
- **Downtime:** Traditional migrations require taking the system offline
- **Data Consistency:** Ensuring data integrity during transition
- **Rollback:** Ability to revert if something goes wrong
- **Performance Impact:** Migration shouldn't degrade user experience
- **Data Volume:** Large datasets take time to migrate

**Goals of Modern Migrations:**
- ✅ Zero or minimal downtime
- ✅ No data loss
- ✅ Easy rollback
- ✅ Gradual, safe transition
- ✅ Maintain data consistency

---

## Types of Migrations

### 1. Schema Migrations

**Definition:** Changes to database structure (tables, columns, indexes)

**Examples:**
- Adding/removing columns
- Changing column types
- Adding indexes
- Table renames
- Adding constraints

### 2. Data Migrations

**Definition:** Moving data between systems or transforming data

**Examples:**
- MySQL → PostgreSQL
- Monolith DB → Microservices DBs
- SQL → NoSQL
- On-premise → Cloud
- Database version upgrades

### 3. Technology Migrations

**Definition:** Changing database technology

**Examples:**
- Oracle → PostgreSQL (cost reduction)
- MongoDB → DynamoDB (managed service)
- Self-hosted → AWS RDS (operational simplicity)
- Single region → Multi-region

---

## Zero-Downtime Migration Patterns

### 1. Dual-Write Pattern (Shadow Writing)

**Concept:** Write to both old and new databases simultaneously

#### Architecture

```
┌─────────────┐
│ Application │
└──────┬──────┘
       │
   ┌───┴────┐
   │ Router │
   └───┬────┘
       │
    ┌──┴────────────┐
    ↓               ↓
┌────────┐      ┌────────┐
│ Old DB │      │ New DB │
│ PRIMARY│      │ SHADOW │
└────────┘      └────────┘
    ↑               ↑
    │               │
  Reads           Verify
```

#### Steps

**Phase 1: Dual-Write**
```python
def create_user(user_data):
    # Write to old database (primary)
    old_user_id = old_db.insert_user(user_data)

    # Write to new database (shadow)
    try:
        new_user_id = new_db.insert_user(user_data)
        # Log for verification
        log_dual_write(old_user_id, new_user_id)
    except Exception as e:
        # Don't fail the request
        log_error(f"Shadow write failed: {e}")

    return old_user_id
```

**Phase 2: Backfill Historical Data**
```python
def backfill_users():
    """
    Copy historical data from old DB to new DB
    Run in batches to avoid overloading
    """
    offset = 0
    batch_size = 1000

    while True:
        users = old_db.get_users(offset=offset, limit=batch_size)
        if not users:
            break

        for user in users:
            # Check if already exists (from dual-write)
            if not new_db.user_exists(user.id):
                new_db.insert_user(user)

        offset += batch_size
        time.sleep(1)  # Rate limiting
```

**Phase 3: Verify Data Consistency**
```python
def verify_consistency():
    """
    Compare data between old and new databases
    """
    discrepancies = []

    for user_id in old_db.get_all_user_ids():
        old_user = old_db.get_user(user_id)
        new_user = new_db.get_user(user_id)

        if old_user != new_user:
            discrepancies.append({
                'user_id': user_id,
                'old': old_user,
                'new': new_user
            })

    return discrepancies
```

**Phase 4: Switch Reads to New DB**
```python
# Gradual rollout using feature flags
def get_user(user_id):
    # 0% of traffic to new DB
    if random.random() < 0.0:
        return new_db.get_user(user_id)

    return old_db.get_user(user_id)

# Increase gradually: 0% → 1% → 5% → 25% → 50% → 100%
```

**Phase 5: Deprecate Old DB Writes**
```python
def create_user(user_data):
    # Write to new database (primary)
    new_user_id = new_db.insert_user(user_data)

    # Shadow write to old database (for rollback)
    try:
        old_db.insert_user(user_data)
    except Exception as e:
        log_error(f"Shadow write to old DB failed: {e}")

    return new_user_id
```

**Phase 6: Decommission Old DB**
- Stop shadow writes
- Archive old database
- Redirect all traffic to new database

#### Pros & Cons

**Pros:**
- ✅ Zero downtime
- ✅ Easy rollback (just stop using new DB)
- ✅ Gradual validation
- ✅ Low risk

**Cons:**
- ❌ Temporary complexity (dual writes)
- ❌ Resource overhead (two databases)
- ❌ Data consistency challenges
- ❌ Longer migration timeline

---

### 2. Blue-Green Deployment

**Concept:** Run two identical production environments (Blue and Green)

#### Architecture

```
                ┌──────────────┐
                │ Load Balancer│
                └───────┬──────┘
                        │
           ┌────────────┴────────────┐
           │                         │
           ↓                         ↓
    ┌─────────────┐          ┌─────────────┐
    │ Blue (Old)  │          │ Green (New) │
    │             │          │             │
    │ App + DB    │          │ App + DB    │
    └─────────────┘          └─────────────┘
         100%                      0%
```

#### Steps

**Step 1: Set Up Green Environment**
```bash
# Green environment setup
1. Provision new infrastructure
2. Deploy new application version
3. Set up new database
4. Migrate data to green database
```

**Step 2: Data Synchronization**
```python
# Continuous sync from Blue to Green
def sync_data():
    while True:
        # Tail database logs (CDC - Change Data Capture)
        changes = blue_db.get_changes_since(last_timestamp)

        for change in changes:
            green_db.apply_change(change)

        last_timestamp = changes[-1].timestamp
        time.sleep(1)
```

**Step 3: Testing**
```bash
# Route small percentage of traffic to Green
# Load Balancer: Blue=99%, Green=1%

# Monitor:
- Error rates
- Response times
- Data consistency
```

**Step 4: Cutover**
```bash
# Gradual traffic shift
Blue=90%, Green=10%
Blue=75%, Green=25%
Blue=50%, Green=50%
Blue=25%, Green=75%
Blue=0%,  Green=100%

# Each step validated before proceeding
```

**Step 5: Keep Blue as Fallback**
```bash
# Maintain Blue environment for 24-48 hours
# Quick rollback if issues arise

# After validation:
# Decommission Blue
```

#### Pros & Cons

**Pros:**
- ✅ Easy rollback (switch traffic back)
- ✅ Full validation before cutover
- ✅ Zero downtime
- ✅ Clean separation

**Cons:**
- ❌ Requires 2x infrastructure (temporary)
- ❌ Complex for stateful systems
- ❌ Data sync challenges
- ❌ Cost overhead

---

### 3. Strangler Fig Pattern

**Concept:** Gradually replace parts of the old system with new system

**Metaphor:** Like the strangler fig tree that grows around a host tree, eventually replacing it

#### Architecture

```
Phase 1: Monolith
┌──────────────────────┐
│   Monolith + DB      │
└──────────────────────┘

Phase 2: Partial Migration
┌──────────────────────┐
│   Proxy/Router       │
└───┬──────────────┬───┘
    │              │
    ↓              ↓
┌────────┐    ┌────────┐
│Service1│    │Monolith│
│+ New DB│    │+ Old DB│
└────────┘    └────────┘

Phase 3: Complete Migration
┌──────────────────────┐
│   Proxy/Router       │
└───┬────┬────┬────┬───┘
    ↓    ↓    ↓    ↓
┌────┐┌────┐┌────┐┌────┐
│Svc1││Svc2││Svc3││Svc4│
│DB1 ││DB2 ││DB3 ││DB4 │
└────┘└────┘└────┘└────┘
```

#### Steps

**Step 1: Add Routing Layer**
```python
# API Gateway / Proxy
def handle_request(request):
    if request.path.startswith('/users'):
        # New service
        return users_service.handle(request)
    else:
        # Old monolith
        return monolith.handle(request)
```

**Step 2: Extract Service by Service**
```python
# Extract Users Service
# 1. Create new users microservice
# 2. Create new users database
# 3. Migrate user data
# 4. Route /users/* to new service
# 5. Validate and monitor

# Repeat for each service
```

**Step 3: Data Migration per Service**
```python
# Migrate users data
def migrate_users_service():
    # 1. Dual-write pattern
    def create_user(user_data):
        # Write to monolith DB
        old_db.insert_user(user_data)

        # Also write to new users DB
        users_db.insert_user(user_data)

    # 2. Backfill historical data
    backfill_users_data()

    # 3. Switch reads to new DB
    # 4. Stop writing to monolith DB
```

**Step 4: Gradually Shrink Monolith**
```
Iteration 1: Extract Users (10% of data)
Iteration 2: Extract Orders (20% of data)
Iteration 3: Extract Products (15% of data)
...
Iteration N: Decommission monolith (0% of data)
```

#### Pros & Cons

**Pros:**
- ✅ Incremental migration (low risk)
- ✅ Continuous value delivery
- ✅ Easy rollback per service
- ✅ Team can work in parallel

**Cons:**
- ❌ Long migration timeline
- ❌ Temporary complexity (hybrid system)
- ❌ Cross-service transactions difficult
- ❌ Requires routing layer

---

### 4. Change Data Capture (CDC)

**Concept:** Stream database changes in real-time to new system

#### Architecture

```
┌──────────┐
│ Old DB   │
│(Source)  │
└────┬─────┘
     │
     ↓ (Binary Log / WAL)
┌──────────┐
│CDC Tool  │
│(Debezium,│
│ DMS)     │
└────┬─────┘
     │
     ↓ (Event Stream)
┌──────────┐
│ Kafka    │
└────┬─────┘
     │
     ↓
┌──────────┐
│ New DB   │
│(Target)  │
└──────────┘
```

#### Tools

| Tool | Source | Target | Features |
|------|--------|--------|----------|
| **Debezium** | MySQL, Postgres, MongoDB | Kafka, Kinesis | Open source, flexible |
| **AWS DMS** | Various | AWS databases | Managed, cloud-native |
| **Oracle GoldenGate** | Oracle, MySQL | Various | Enterprise, bi-directional |
| **Maxwell** | MySQL | Kafka | Simple, lightweight |

#### Example: Debezium + Kafka

**Setup:**
```yaml
# Debezium MySQL Connector
{
  "name": "mysql-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "mysql.example.com",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "password",
    "database.server.id": "1",
    "database.server.name": "old_db",
    "table.include.list": "public.users,public.orders",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "schema-changes"
  }
}
```

**Consumer:**
```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'old_db.public.users',
    bootstrap_servers=['kafka:9092']
)

for message in consumer:
    event = json.loads(message.value)

    if event['op'] == 'c':  # Create
        new_db.insert(event['after'])
    elif event['op'] == 'u':  # Update
        new_db.update(event['after'])
    elif event['op'] == 'd':  # Delete
        new_db.delete(event['before']['id'])
```

#### Pros & Cons

**Pros:**
- ✅ Real-time synchronization
- ✅ Minimal impact on source database
- ✅ Event-driven architecture
- ✅ Can transform data in-flight

**Cons:**
- ❌ Additional infrastructure (Kafka, etc.)
- ❌ Complexity in setup
- ❌ Eventual consistency
- ❌ Schema evolution challenges

---

## Schema Migration Strategies

### Backward Compatible Changes

**Safe Changes (No Downtime):**

#### 1. Adding Nullable Column
```sql
-- Safe: New column is nullable
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Deploy code that uses new column
-- No data migration needed
```

#### 2. Adding Column with Default
```sql
-- Safe: New column has default value
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;

-- Existing rows automatically get default value
```

#### 3. Adding Index
```sql
-- Safe: Can be done online (PostgreSQL)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Does not lock table
```

### Backward Incompatible Changes

**Dangerous Changes (Require Multi-Phase Migration):**

#### 1. Renaming Column (Multi-Phase)

**Phase 1: Add New Column**
```sql
-- Add new column
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- Backfill data
UPDATE users SET email_address = email WHERE email_address IS NULL;
```

**Phase 2: Dual-Write**
```python
# Application code writes to both columns
def update_user(user_id, email):
    db.execute(
        "UPDATE users SET email = %s, email_address = %s WHERE id = %s",
        (email, email, user_id)
    )
```

**Phase 3: Switch Reads**
```python
# Read from new column
def get_user_email(user_id):
    # Old code: user.email
    # New code: user.email_address
    return user.email_address
```

**Phase 4: Remove Old Column**
```sql
-- After all code deployed
ALTER TABLE users DROP COLUMN email;
```

#### 2. Changing Column Type

**Phase 1: Add New Column**
```sql
-- Change user_id from INT to BIGINT
ALTER TABLE users ADD COLUMN user_id_new BIGINT;

-- Backfill
UPDATE users SET user_id_new = user_id;
```

**Phase 2: Switch Application**
```python
# Use new column
def get_user(user_id_new):
    return db.query("SELECT * FROM users WHERE user_id_new = %s", user_id_new)
```

**Phase 3: Swap Columns**
```sql
-- Rename columns
ALTER TABLE users RENAME COLUMN user_id TO user_id_old;
ALTER TABLE users RENAME COLUMN user_id_new TO user_id;

-- Drop old column
ALTER TABLE users DROP COLUMN user_id_old;
```

#### 3. Adding NOT NULL Constraint

**Phase 1: Add Column as Nullable**
```sql
ALTER TABLE users ADD COLUMN country VARCHAR(2);
```

**Phase 2: Backfill Data**
```sql
UPDATE users SET country = 'US' WHERE country IS NULL;
```

**Phase 3: Add Constraint**
```sql
-- Now safe to add NOT NULL
ALTER TABLE users ALTER COLUMN country SET NOT NULL;
```

---

## Data Migration Strategies

### 1. Batch Migration

**Concept:** Migrate data in batches to avoid overloading systems

```python
def batch_migrate(source_db, target_db, batch_size=1000):
    offset = 0
    total_migrated = 0

    while True:
        # Fetch batch from source
        batch = source_db.query(
            "SELECT * FROM users ORDER BY id LIMIT %s OFFSET %s",
            (batch_size, offset)
        )

        if not batch:
            break

        # Transform if needed
        transformed = [transform_user(user) for user in batch]

        # Insert into target
        target_db.bulk_insert(transformed)

        total_migrated += len(batch)
        offset += batch_size

        # Rate limiting
        time.sleep(0.1)

        # Progress logging
        if total_migrated % 10000 == 0:
            print(f"Migrated {total_migrated} records")

    return total_migrated
```

### 2. Streaming Migration

**Concept:** Use CDC to stream changes in real-time

```python
# Real-time streaming with Kafka
def stream_migrate():
    consumer = KafkaConsumer('source_db_changes')

    for message in consumer:
        change = parse_change(message)

        if change.operation == 'INSERT':
            target_db.insert(change.data)
        elif change.operation == 'UPDATE':
            target_db.update(change.data)
        elif change.operation == 'DELETE':
            target_db.delete(change.data['id'])

        # Commit offset
        consumer.commit()
```

### 3. Snapshot + Incremental

**Concept:** Initial snapshot + ongoing incremental updates

```python
def snapshot_and_incremental():
    # Step 1: Take snapshot
    snapshot_time = datetime.now()
    batch_migrate(source_db, target_db)

    # Step 2: Apply incremental changes since snapshot
    changes = source_db.get_changes_since(snapshot_time)
    for change in changes:
        apply_change(target_db, change)

    # Step 3: Switch to real-time CDC
    start_cdc_stream()
```

---

## Real-World Examples

### 1. GitHub: MySQL to MySQL (Sharding)

**Challenge:** Single MySQL instance couldn't handle growth

**Solution:**
1. **Ghost Tool:** Online schema changes without downtime
2. **Vitess:** MySQL sharding and clustering
3. **Gradual Migration:** Shard table by table

**Steps:**
```
1. Add Vitess proxy layer
2. Route reads through Vitess
3. Backfill data to shards
4. Switch writes to Vitess
5. Decommission old MySQL
```

### 2. Uber: PostgreSQL to MySQL + Schemaless

**Challenge:** PostgreSQL replication lag, need for flexibility

**Solution:**
1. **Dual-Write:** PostgreSQL + Schemaless (MySQL-backed)
2. **Backfill:** Historical data migration
3. **Gradual Cutover:** Service by service
4. **Validation:** Compare data between systems

**Timeline:** 18 months for complete migration

### 3. Discord: MongoDB to Cassandra

**Challenge:** MongoDB hotspots, scalability issues

**Solution:**
1. **Dual-Write:** Write to both MongoDB and Cassandra
2. **Backfill:** Migrate historical messages (billions)
3. **Read Migration:** Gradually shift reads to Cassandra
4. **Validation:** Compare data, performance

**Learnings:**
- Used Elixir to handle dual-write complexity
- Batch migration took weeks (billions of messages)
- Careful validation prevented data loss

### 4. Dropbox: MySQL to Custom File System

**Challenge:** Storing billions of files in S3, metadata in MySQL

**Solution:**
1. **Magic Pocket:** Custom distributed file system
2. **Dual-Write:** S3 + Magic Pocket
3. **Traffic Shift:** Gradually move reads to Magic Pocket
4. **Validation:** Extensive testing, checksum verification

**Results:**
- Reduced costs significantly
- Improved performance
- Full control over infrastructure

---

## Best Practices

### 1. Planning

**Before Migration:**
- ✅ Document current schema and data
- ✅ Identify dependencies
- ✅ Plan rollback strategy
- ✅ Set success metrics
- ✅ Communicate with stakeholders

### 2. Testing

**Test Thoroughly:**
- ✅ Migrate staging environment first
- ✅ Load testing with production-like data
- ✅ Validate data integrity
- ✅ Test rollback procedure
- ✅ Monitor for performance degradation

### 3. Gradual Rollout

**Incremental Approach:**
```
0% → 1% → 5% → 10% → 25% → 50% → 100%
```

**Each step:**
- Monitor error rates
- Validate data consistency
- Check performance metrics
- Get stakeholder approval

### 4. Monitoring

**Key Metrics:**
- Error rates
- Response times
- Data consistency (compare old vs new)
- Replication lag
- Database load

**Alerts:**
```python
# Example: Alert on high error rate
if error_rate > 0.1:  # 0.1%
    alert("Migration error rate high: {error_rate}")
    pause_migration()
```

### 5. Rollback Plan

**Always Have a Rollback:**
```python
def rollback():
    # Stop writes to new database
    feature_flag.set('use_new_db', False)

    # Ensure old database is still synchronized
    if not verify_old_db_is_current():
        alert("CRITICAL: Old DB out of sync!")

    # Route all traffic to old database
    load_balancer.route_to('old_db')
```

### 6. Data Validation

**Continuous Validation:**
```python
def validate_data():
    """
    Compare random sample of records
    """
    sample_ids = random.sample(all_ids, 1000)

    discrepancies = 0
    for id in sample_ids:
        old_record = old_db.get(id)
        new_record = new_db.get(id)

        if old_record != new_record:
            discrepancies += 1
            log_discrepancy(id, old_record, new_record)

    return discrepancies / len(sample_ids)
```

### 7. Communication

**Keep Stakeholders Informed:**
- Regular status updates
- Risk assessment
- Timeline estimates
- Post-migration review

---

## Summary

### Migration Strategy Selection

| Strategy | Best For | Complexity | Downtime |
|----------|----------|------------|----------|
| **Dual-Write** | Same database, different instances | Medium | Zero |
| **Blue-Green** | Complete system replacement | High | Zero |
| **Strangler Fig** | Monolith to microservices | High | Zero |
| **CDC** | Real-time sync | Medium | Zero |
| **Batch** | One-time migration | Low | Possible |

### Key Takeaways

1. **Zero-downtime is possible** but requires careful planning
2. **Gradual migrations are safer** than big-bang
3. **Always have a rollback plan**
4. **Validate data continuously**
5. **Monitor everything**
6. **Communicate with stakeholders**

### Golden Rules

1. **Test in staging first**
2. **Migrate in small batches**
3. **Validate at every step**
4. **Keep both systems running temporarily**
5. **Have a rollback plan**
6. **Monitor continuously**
7. **Don't rush**

**Remember:** Migrations are risky. Take your time, validate thoroughly, and always have a backup plan.
