# WhatsApp: Group Messaging

## The Group Messaging Challenge

When someone sends a message to a 256-member group, what happens? Do we store one message or 256 copies? How do we ensure all members receive it? What about members who join later?

This is the fan-out problem: a single write must reach N readers.

## Design Approaches

### Approach 1: Fan-Out on Read

Store one message, fetch when each user reads:

```sql
-- Store once
INSERT INTO group_messages (group_id, message_id, sender_id, content)
VALUES ('group123', 'msg456', 'alice', 'Hello everyone');

-- Each user queries
SELECT * FROM group_messages
WHERE group_id = 'group123'
ORDER BY created_at DESC
LIMIT 50;
```

**Pros**: Efficient writes, minimal storage
**Cons**: Slow reads (must check which messages user has seen), complex query logic

### Approach 2: Fan-Out on Write (WhatsApp's Choice)

Create a copy for each member:

```python
async def send_group_message(group_id, sender_id, content):
    # 1. Get group members
    members = await get_group_members(group_id)

    # 2. Create message ID
    message_id = generate_id()

    # 3. Fan out: create copy for each member
    for member_id in members:
        await cassandra.execute("""
            INSERT INTO user_messages (
                user_id, conversation_id, message_id,
                sender_id, content, is_group, created_at
            ) VALUES (?, ?, ?, ?, ?, true, ?)
        """, (member_id, group_id, message_id, sender_id, content, now()))
```

**Pros**: Fast reads (simple query per user), simple logic
**Cons**: Write amplification (256 writes for one message), more storage

**Why WhatsApp chooses this**: Read performance matters more. Users read messages far more than they send (100:1 ratio in groups).

## Implementation

### Group Creation

```python
async def create_group(creator_id, name, member_ids):
    group_id = generate_id()

    # 1. Create group in PostgreSQL
    await postgres.execute("""
        INSERT INTO groups (group_id, name, created_by, created_at)
        VALUES (?, ?, ?, ?)
    """, (group_id, name, creator_id, now()))

    # 2. Add members
    for member_id in [creator_id] + member_ids:
        await postgres.execute("""
            INSERT INTO group_members (group_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?)
        """, (group_id, member_id, 'admin' if member_id == creator_id else 'member', now()))

    # 3. Cache group membership in Redis for fast lookups
    await redis.sadd(f'group:{group_id}:members', *([creator_id] + member_ids))
    await redis.expire(f'group:{group_id}:members', 3600)  # 1 hour TTL

    return group_id
```

### Sending Group Messages

```python
async def send_group_message(sender_id, group_id, content):
    # 1. Verify sender is group member
    is_member = await redis.sismember(f'group:{group_id}:members', sender_id)
    if not is_member:
        # Check database if not in cache
        is_member = await postgres.execute(
            "SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?",
            (group_id, sender_id)
        )
        if not is_member:
            raise PermissionError("Not a group member")

    # 2. Get all members (from cache if available)
    members = await redis.smembers(f'group:{group_id}:members')
    if not members:
        # Cache miss, fetch from database
        members = await postgres.execute(
            "SELECT user_id FROM group_members WHERE group_id = ?",
            (group_id,)
        )
        # Populate cache
        await redis.sadd(f'group:{group_id}:members', *members)
        await redis.expire(f'group:{group_id}:members', 3600)

    # 3. Create message
    message_id = generate_id()

    # 4. Fan-out: queue for each member
    for member_id in members:
        await kafka.send('messages.fanout', {
            'message_id': message_id,
            'group_id': group_id,
            'sender_id': sender_id,
            'recipient_id': member_id,
            'content': content,
            'is_group': True,
            'created_at': now()
        })

    return message_id
```

### Fan-Out Worker

Process fan-out messages asynchronously:

```python
async def process_fanout_messages():
    async for message in kafka_consumer('messages.fanout'):
        # Write to recipient's message store
        await cassandra.execute("""
            INSERT INTO user_messages (
                user_id, conversation_id, message_id,
                sender_id, content, is_group, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            message['recipient_id'],
            message['group_id'],
            message['message_id'],
            message['sender_id'],
            message['content'],
            True,
            message['created_at']
        ))

        # If member is online, deliver immediately
        if await is_online(message['recipient_id']):
            await deliver_message(message['recipient_id'], message)
```

## Optimizations

### Group Membership Caching

Cache group members in Redis:

```python
# Cache structure
Key: group:{group_id}:members
Type: Set
Members: [user_id1, user_id2, ...]
TTL: 1 hour
```

This avoids database queries for every message. Cache hit rate > 95% because active groups are messaged frequently.

### Batch Fan-Out Writes

Instead of 256 individual Cassandra writes:

```python
async def batch_fanout_write(messages):
    # Prepare batch (max 100 per batch for Cassandra)
    batch = []
    for msg in messages:
        batch.append((
            msg['recipient_id'], msg['group_id'], msg['message_id'],
            msg['sender_id'], msg['content'], msg['created_at']
        ))

        if len(batch) >= 100:
            await cassandra.execute_batch(
                "INSERT INTO user_messages (...) VALUES (?, ?, ?, ?, ?, ?)",
                batch
            )
            batch = []
```

This reduces write latency by 10x.

### Limit Group Size

WhatsApp limits groups to 256 members. Why?

**Write Amplification**: 256 writes per message is manageable. 10,000 writes per message is not.

**Notification Storm**: 256 push notifications is acceptable. 10,000 is overwhelming.

**Trade-off**: Limits very large broadcast scenarios, but keeps system scalable.

## Group Metadata

```sql
-- PostgreSQL schema
CREATE TABLE groups (
  group_id UUID PRIMARY KEY,
  name VARCHAR(256),
  description TEXT,
  icon_url TEXT,
  created_by UUID,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE group_members (
  group_id UUID,
  user_id UUID,
  role ENUM('admin', 'member'),
  joined_at TIMESTAMP,
  PRIMARY KEY (group_id, user_id)
);

CREATE INDEX idx_user_groups ON group_members(user_id);
```

## Admin Operations

### Add Member

```python
async def add_member(admin_id, group_id, new_member_id):
    # 1. Verify admin permission
    member = await postgres.execute(
        "SELECT role FROM group_members WHERE group_id = ? AND user_id = ?",
        (group_id, admin_id)
    )
    if member['role'] != 'admin':
        raise PermissionError("Only admins can add members")

    # 2. Add to database
    await postgres.execute("""
        INSERT INTO group_members (group_id, user_id, role, joined_at)
        VALUES (?, ?, 'member', ?)
    """, (group_id, new_member_id, now()))

    # 3. Invalidate cache (will refresh on next message)
    await redis.delete(f'group:{group_id}:members')

    # 4. Send system message
    await send_system_message(group_id, f"{new_member_id} was added to the group")
```

### Remove Member

Similar flow, but also prevents removed user from sending messages.

## Why This Design Works

**Fan-out on write optimizes for reads**: WhatsApp is read-heavy, so optimizing read path makes sense.

**Caching group membership eliminates database queries**: Redis cache hit rate > 95% for active groups.

**Async fan-out prevents blocking**: Message is accepted immediately, fan-out happens in background.

**256 member limit keeps writes manageable**: Write amplification controlled by group size limit.

**Per-user message storage simplifies queries**: Each user has their own inbox, no complex filtering needed.

This design efficiently handles billions of group messages daily.
