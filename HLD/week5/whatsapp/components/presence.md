# WhatsApp: Presence Service

## The Presence Problem

How do we track whether someone is online or offline across billions of users? More importantly, how do we broadcast status changes to their contacts without overwhelming the system?

Consider the scale:
- 100 million users come online during morning hours
- Each user has approximately 50 contacts
- Each status change must notify all contacts
- This means 5 billion presence notifications in a short window

A naive implementation would collapse under this load. We need a clever design that balances real-time updates with system scalability.

## Design Approach

### Core Concept: Heartbeat with Auto-Expiry

Instead of explicitly tracking connect/disconnect events, we use a heartbeat mechanism combined with automatic expiration:

**When online**: Client sends heartbeat every 30 seconds
**Server action**: Updates Redis with 60-second TTL
**When offline**: Client stops sending heartbeats
**Auto-detect**: Redis automatically expires the entry after 60 seconds

This approach eliminates the need for explicit disconnect handling, which is unreliable (network issues, crashes, battery death).

## Implementation

### Data Structure in Redis

```redis
# Online status with auto-expiry
Key: presence:user:{user_id}
Type: Hash
TTL: 60 seconds

Value: {
  "status": "online",
  "last_heartbeat": 1699999999,
  "device_type": "mobile",
  "server_id": "chat-server-42"
}
```

### Heartbeat Flow

**Client Side**

```javascript
// Send heartbeat every 30 seconds
setInterval(() => {
  ws.send(JSON.stringify({
    type: 'heartbeat',
    timestamp: Date.now()
  }));
}, 30000);  // 30 seconds
```

**Server Side**

```python
async def handle_heartbeat(user_id):
    # Update presence with 60-second TTL
    redis.hset(f'presence:user:{user_id}', {
        'status': 'online',
        'last_heartbeat': now(),
        'device_type': 'mobile',
        'server_id': SERVER_ID
    })
    redis.expire(f'presence:user:{user_id}', 60)  # TTL

    # Note: We don't notify contacts on every heartbeat
    # Only when status changes (offline → online)
```

Why 60-second TTL with 30-second heartbeat?

This provides a 30-second buffer. If one heartbeat is dropped due to network issues, the user doesn't immediately appear offline. This reduces flapping (rapid online/offline transitions) that confuses users.

### Status Change Detection

We don't want to spam contacts with notifications on every heartbeat. We only notify when status actually changes:

```python
class PresenceService:
    def __init__(self):
        self.redis = RedisClient()

    async def update_presence(self, user_id, device_type):
        key = f'presence:user:{user_id}'

        # Check previous status
        previous_status = await self.redis.get(f'{key}:status')

        # Update status
        await self.redis.hset(key, {
            'status': 'online',
            'last_heartbeat': now(),
            'device_type': device_type
        })
        await self.redis.expire(key, 60)

        # If status changed (was offline, now online)
        if previous_status != 'online':
            await self.notify_contacts_online(user_id)

    async def notify_contacts_online(self, user_id):
        # Get user's contacts
        contacts = await self.get_contacts(user_id)

        # Publish status change
        for contact_id in contacts:
            await self.redis.publish(
                channel=f'presence:{contact_id}',
                message=json.dumps({
                    'user_id': user_id,
                    'status': 'online',
                    'timestamp': now()
                })
            )
```

### Offline Detection

Redis automatically expires entries after TTL. We monitor expiration events to detect when users go offline:

```python
# Subscribe to Redis keyspace notifications
async def monitor_expirations():
    pubsub = redis.pubsub()
    await pubsub.psubscribe('__keyevent@0__:expired')

    async for message in pubsub.listen():
        key = message['data']
        if key.startswith('presence:user:'):
            user_id = extract_user_id(key)
            await handle_user_offline(user_id)

async def handle_user_offline(user_id):
    # User went offline (heartbeat stopped)
    contacts = await get_contacts(user_id)

    # Update last seen timestamp
    await redis.set(
        f'lastseen:user:{user_id}',
        now()
    )

    # Notify contacts
    for contact_id in contacts:
        await redis.publish(
            channel=f'presence:{contact_id}',
            message=json.dumps({
                'user_id': user_id,
                'status': 'offline',
                'last_seen': now()
            })
        )
```

### Last Seen Timestamp

When a user goes offline, we store their last seen time persistently:

```redis
Key: lastseen:user:{user_id}
Type: String
Value: timestamp (e.g., 1699999999)
TTL: None (persist forever)
```

This allows us to show "last seen 5 minutes ago" even after Redis cache is cleared.

## Optimizations for Scale

### Problem: Notification Storm

When 1 million users come online, each with 50 contacts, we need to send 50 million presence notifications. How do we handle this?

### Solution 1: Batching

Instead of sending notifications immediately, batch them:

```python
class PresenceNotifier:
    def __init__(self):
        self.batch = defaultdict(set)  # contact_id → set of user_ids
        self.batch_size = 100
        self.batch_interval = 10  # seconds

    async def notify_contact(self, contact_id, user_id, status):
        self.batch[contact_id].add((user_id, status))

        if len(self.batch[contact_id]) >= self.batch_size:
            await self.flush_batch(contact_id)

    async def flush_batch(self, contact_id):
        updates = self.batch.pop(contact_id, set())
        if updates:
            await self.send_bulk_update(contact_id, updates)

    async def periodic_flush(self):
        """Flush batches every 10 seconds"""
        while True:
            await asyncio.sleep(self.batch_interval)
            for contact_id in list(self.batch.keys()):
                await self.flush_batch(contact_id)
```

Instead of 50 million individual notifications, we send batched updates: "Alice, Bob, and Charlie are now online."

### Solution 2: Sampling

Not all contacts need instant notifications. We can prioritize:

```python
async def should_notify_contact(user_id, contact_id):
    # Always notify if they're in an active conversation
    if await has_recent_chat(user_id, contact_id):
        return True

    # Otherwise, sample (notify 10% of contacts)
    return hash(f'{user_id}:{contact_id}') % 10 == 0
```

This reduces load by 90% while still showing status for active conversations.

### Solution 3: Client-Side Polling for Less Important Contacts

For contacts you haven't chatted with recently, fetch status lazily:

```python
# Client requests status when opening contact list
async def get_bulk_presence(user_ids):
    """Return presence for multiple users at once"""
    presence = {}
    for user_id in user_ids:
        status = await redis.get(f'presence:user:{user_id}')
        presence[user_id] = status if status else 'offline'
    return presence
```

This trades real-time updates for reduced server load on the long tail of contacts.

## Multi-Device Presence

Users often have WhatsApp on multiple devices (phone, tablet, desktop). How do we handle this?

### Approach: Aggregate Presence

A user is "online" if ANY of their devices is online:

```python
async def update_device_presence(user_id, device_id, device_type):
    # Store per-device status
    await redis.hset(
        f'presence:user:{user_id}:devices',
        device_id,
        json.dumps({
            'type': device_type,
            'last_heartbeat': now()
        })
    )
    await redis.expire(f'presence:user:{user_id}:devices', 60)

    # Check if user should be marked online
    devices = await redis.hgetall(f'presence:user:{user_id}:devices')

    # User is online if any device is active
    is_online = len(devices) > 0

    await redis.set(
        f'presence:user:{user_id}',
        'online' if is_online else 'offline'
    )
```

### Last Seen Across Devices

```python
async def get_last_seen(user_id):
    # Get last heartbeat from each device
    devices = await redis.hgetall(f'presence:user:{user_id}:devices')

    if devices:
        # User is currently online
        return {
            'status': 'online',
            'devices': [json.loads(d)['type'] for d in devices.values()]
        }

    # User is offline, get last seen
    last_seen = await redis.get(f'lastseen:user:{user_id}')
    return {
        'status': 'offline',
        'last_seen': last_seen
    }
```

## Privacy Considerations

Not all users want to share their online status:

```python
async def get_presence_for_contact(viewer_id, target_user_id):
    # Check privacy settings
    privacy = await get_privacy_settings(target_user_id)

    if privacy['last_seen'] == 'everyone':
        return await get_presence(target_user_id)
    elif privacy['last_seen'] == 'contacts':
        if await are_contacts(viewer_id, target_user_id):
            return await get_presence(target_user_id)
    elif privacy['last_seen'] == 'nobody':
        return {'status': 'unknown'}

    return {'status': 'unknown'}
```

## Presence Data Model Summary

```
Redis Keys:

1. Current Presence (ephemeral, 60s TTL)
   presence:user:{user_id} → {status, last_heartbeat, device_type, server_id}

2. Device-Level Presence (ephemeral, 60s TTL)
   presence:user:{user_id}:devices → {device_id → device_info}

3. Last Seen (persistent)
   lastseen:user:{user_id} → timestamp

4. Presence Notifications (Pub/Sub)
   Channel: presence:{contact_id}
   Message: {user_id, status, timestamp}
```

## Performance Characteristics

**Write Load**:
- 100 million users × 1 heartbeat/30s = 3.3 million writes/second
- Redis handles this easily across a sharded cluster

**Read Load**:
- Presence checks when viewing contact list
- Batched bulk reads: O(1) per user with MGET
- Mostly cached, minimal load

**Notification Load**:
- Reduced by batching, sampling, and lazy loading
- Peak: ~10 million notifications/minute during morning rush
- Spread across Pub/Sub channels

**Storage**:
- 100 million concurrent users × 200 bytes = 20 GB
- Easily fits in memory across Redis cluster

## Why This Design Works

**Auto-expiry eliminates explicit disconnect handling**: Network failures, crashes, and battery death are handled automatically.

**Heartbeat interval balances freshness and load**: 30-second interval keeps status reasonably current without overwhelming the network.

**Batching and sampling reduce notification storm**: We don't need to notify every contact instantly.

**Redis is perfect for this use case**: Sub-millisecond latency, built-in TTL, Pub/Sub for notifications.

**Lazy loading for scale**: Fetch status when needed rather than pushing to everyone.

This design handles billions of presence updates daily while keeping the user experience responsive and real-time.
