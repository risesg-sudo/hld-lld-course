# WhatsApp: Messaging Components

## Chat Service (WebSocket Server)

### The Problem

How do we maintain 100 million concurrent connections while delivering messages with sub-100ms latency? Traditional HTTP polling wastes bandwidth and introduces latency. We need a solution that keeps connections open and pushes messages instantly.

### The Solution: WebSocket-Based Chat Service

WebSockets provide full-duplex, bidirectional communication over a single TCP connection. Once established, either side can send data without the overhead of HTTP headers on every message.

### Component Architecture

```
┌───────────────────────────────────────┐
│        Chat Service Instance          │
├───────────────────────────────────────┤
│  Connection Manager                   │
│  - 50K concurrent connections         │
│  - User → Connection mapping          │
│  - Heartbeat monitoring               │
├───────────────────────────────────────┤
│  Message Handler                      │
│  - Receive messages from clients      │
│  - Validate format and permissions    │
│  - Publish to Kafka                   │
│  - Send ACK to sender                 │
├───────────────────────────────────────┤
│  Message Subscriber                   │
│  - Subscribe to user's Kafka partition│
│  - Receive messages for delivery      │
│  - Push to client via WebSocket       │
├───────────────────────────────────────┤
│  Session Manager                      │
│  - Authenticate users (JWT)           │
│  - Store session in Redis             │
│  - Multi-device support               │
└───────────────────────────────────────┘
```

### Connection Lifecycle

**1. Connection Establishment**

```javascript
// Client initiates WebSocket connection
const ws = new WebSocket('wss://chat.whatsapp.com/ws');

ws.onopen = () => {
  // Send authentication token
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'jwt_token_here'
  }));
};
```

**2. Server-Side Authentication**

```python
def on_connect(websocket):
    # Receive auth message
    auth_msg = await websocket.receive()
    token = auth_msg['token']

    # Validate JWT
    user_id = validate_jwt(token)
    if not user_id:
        await websocket.close(code=4001, reason='Invalid token')
        return

    # Store connection
    connection_manager.add(user_id, websocket)

    # Update session in Redis
    redis.set(f'session:{user_id}', {
        'server_id': SERVER_ID,
        'connected_at': now(),
        'device_type': 'mobile'
    }, ex=3600)  # 1 hour TTL

    # Subscribe to user's message queue
    kafka_consumer.subscribe(f'user.{user_id}.messages')
```

Why JWT? It's stateless - the server doesn't need to query a database to validate every connection. The token contains all necessary information and can be verified using public keys.

**3. Heartbeat Mechanism**

Clients send heartbeat every 30 seconds to prove they're alive:

```python
async def heartbeat_loop(websocket, user_id):
    while True:
        await asyncio.sleep(30)
        try:
            await websocket.ping()
            # Update presence in Redis
            redis.setex(f'presence:{user_id}', 60, 'online')
        except:
            # Connection dead, clean up
            connection_manager.remove(user_id, websocket)
            break
```

Why 30 seconds? It's a balance between:
- Too frequent: Wastes bandwidth and battery
- Too infrequent: Slow to detect disconnections

With 60-second Redis TTL, we have a 30-second buffer if one heartbeat is missed.

### Message Sending Flow

**Client Sends Message**

```python
async def handle_message(websocket, user_id, message):
    # 1. Validate message
    if len(message['content']) > 65536:  # 64KB limit
        await websocket.send_error('Message too long')
        return

    # 2. Enrich with server-side data
    enriched_message = {
        'message_id': generate_message_id(),  # Server-generated
        'sender_id': user_id,
        'recipient_id': message['recipient_id'],
        'content': message['content'],
        'client_timestamp': message['timestamp'],
        'server_timestamp': now(),
        'status': 'sent'
    }

    # 3. Publish to Kafka
    kafka_producer.send(
        topic='messages.incoming',
        key=enriched_message['recipient_id'],  # Partition by recipient
        value=enriched_message
    )

    # 4. Immediate ACK to sender (message is durable in Kafka)
    await websocket.send(json.dumps({
        'type': 'message_ack',
        'client_message_id': message['id'],
        'server_message_id': enriched_message['message_id'],
        'status': 'sent',
        'timestamp': enriched_message['server_timestamp']
    }))
```

Why acknowledge before database write? The message is durable in Kafka. If the server crashes, another processor will handle it. This keeps the critical path (sender's experience) fast.

### Message Receiving Flow

```python
async def kafka_consumer_loop(user_id, websocket):
    """Consume messages destined for this user and deliver via WebSocket"""

    async for message in kafka_consumer:
        if message.recipient_id == user_id:
            try:
                # Deliver to client
                await websocket.send(json.dumps({
                    'type': 'new_message',
                    'message_id': message.message_id,
                    'sender_id': message.sender_id,
                    'content': message.content,
                    'timestamp': message.server_timestamp
                }))

                # Wait for delivery acknowledgment
                ack = await asyncio.wait_for(
                    websocket.receive(),
                    timeout=10.0
                )

                if ack['type'] == 'delivery_ack':
                    # Update message status
                    kafka_producer.send(
                        topic='message.status.updates',
                        value={
                            'message_id': message.message_id,
                            'status': 'delivered',
                            'delivered_at': now()
                        }
                    )
            except asyncio.TimeoutError:
                # Client didn't ACK, will retry later
                pass
```

### Scalability Strategies

**Connection Distribution**

With 100 million connections and 50K per server:
```
Required servers = 100M / 50K = 2,000 servers
```

**How do we route connections?**

Use consistent hashing based on user_id:
```python
def get_server_for_user(user_id):
    server_id = hash(user_id) % NUM_SERVERS
    return SERVER_IPS[server_id]
```

Benefits:
- Same user always connects to same server (unless it fails)
- Message delivery knows which server has the user's connection
- Simple to implement

**Handling Server Failures**

When a server dies, all connections are lost. Clients must:
1. Detect connection loss
2. Reconnect (possibly to different server)
3. Request missed messages

```python
# Client reconnection logic
def on_disconnect():
    last_message_id = get_last_received_message()
    reconnect()
    request_missed_messages(last_message_id)
```

The server sends all messages since `last_message_id` from Cassandra.

## Message Queue (Kafka)

### Why Kafka for Messaging?

Traditional message queues (RabbitMQ, SQS) work well for job queues, but Kafka offers unique advantages for chat:

**Durability**: Messages are persisted to disk, surviving crashes
**Ordering**: Partition-level ordering guarantees messages from the same conversation arrive in order
**Replay**: Can reprocess messages for debugging or recovery
**Multiple Consumers**: Different services can consume the same stream (delivery, analytics, search)
**Throughput**: Handles millions of messages per second

### Topic Design

**messages.incoming**
All new messages land here first.
- Partitions: 1000 (balance parallelism with overhead)
- Partition key: `recipient_id` (ensures ordering per user)
- Retention: 7 days (allow debugging)

**messages.outgoing**
Messages ready for delivery to recipients.
- Partitions: 1000
- Partition key: `recipient_id`
- Retention: 24 hours (shorter, as these are processed quickly)

**notifications.push**
Notifications for offline users.
- Partitions: 100
- Partition key: `user_id`
- Retention: 3 days

### Partition Strategy

Why partition by `recipient_id`?

**Ordering**: All messages to the same recipient go to the same partition, preserving order.

**Load Distribution**: With billions of users, recipients are distributed evenly across partitions.

**Consumer Parallelism**: Each partition can be consumed independently.

```python
# Kafka partition calculation
partition = hash(recipient_id) % NUM_PARTITIONS
```

### Configuration

```yaml
replication_factor: 3  # Survive 2 broker failures
acks: all  # Wait for all replicas to acknowledge
compression: lz4  # Fast compression
retention_ms: 604800000  # 7 days
```

Why `acks: all`? Messages are critical data. We cannot lose them. Waiting for all replicas ensures durability at the cost of slight latency increase (still under 10ms).

## Message Processor

### Responsibilities

The Message Processor is the workhorse that handles message lifecycle:

```
┌─────────────────────────────────────────┐
│         Message Processor               │
├─────────────────────────────────────────┤
│  1. Consume from Kafka                  │
│  2. Validate and deduplicate            │
│  3. Store in Cassandra (persistence)    │
│  4. Check recipient status (Redis)      │
│  5. Route: online → Kafka / offline → Push│
│  6. Update message status               │
│  7. Index in Elasticsearch (async)      │
└─────────────────────────────────────────┘
```

### Implementation

```python
class MessageProcessor:
    def __init__(self):
        self.kafka_consumer = KafkaConsumer('messages.incoming')
        self.kafka_producer = KafkaProducer()
        self.cassandra = CassandraClient()
        self.redis = RedisClient()
        self.elasticsearch = ElasticsearchClient()

    async def process_messages(self):
        async for message in self.kafka_consumer:
            try:
                await self.process_single_message(message)
            except Exception as e:
                # Log error, message will be reprocessed
                logger.error(f"Failed to process {message.id}: {e}")

    async def process_single_message(self, message):
        # 1. Deduplication check
        if await self.cassandra.message_exists(message.id):
            return  # Already processed

        # 2. Store in Cassandra
        await self.cassandra.insert_message(message)

        # 3. Check recipient status
        recipient_status = await self.redis.get(f'presence:{message.recipient_id}')

        if recipient_status == 'online':
            # 4a. Recipient is online, route to their Kafka partition
            await self.kafka_producer.send(
                topic=f'user.{message.recipient_id}.messages',
                value=message
            )
        else:
            # 4b. Recipient is offline, queue push notification
            await self.kafka_producer.send(
                topic='notifications.push',
                value={
                    'user_id': message.recipient_id,
                    'message_preview': message.content[:100],
                    'sender_name': await self.get_sender_name(message.sender_id)
                }
            )

        # 5. Update message status
        await self.cassandra.update_message_status(
            message.id,
            'sent' if recipient_status == 'online' else 'pending'
        )

        # 6. Index for search (async, fire-and-forget)
        asyncio.create_task(
            self.elasticsearch.index_message(message)
        )
```

### Optimizations

**Batch Processing**

Instead of writing one message at a time to Cassandra:

```python
batch = []
async for message in kafka_consumer:
    batch.append(message)

    if len(batch) >= 100:  # Batch size
        await cassandra.batch_insert(batch)
        batch = []
```

This reduces write latency by ~10x (fewer round trips).

**Connection Pooling**

Maintain a pool of database connections to avoid creation overhead:

```python
cassandra_pool = ConnectionPool(
    min_size=10,
    max_size=100,
    host='cassandra.internal'
)
```

**Circuit Breaker**

If Elasticsearch is down, don't let it block message processing:

```python
@circuit_breaker(failure_threshold=5, timeout=60)
async def index_message(message):
    await elasticsearch.index(message)
```

After 5 failures, the circuit opens and requests fast-fail for 60 seconds, then retry.

### Why Separate Processor from Chat Service?

**Separation of Concerns**: Chat service handles connections, processor handles business logic.

**Independent Scaling**: We can scale chat services and processors independently based on load.

**Fault Tolerance**: If processor crashes, chat service still accepts messages (Kafka buffers them).

**Flexibility**: Multiple processors can consume the same stream for different purposes.

This architecture ensures that messages flow through the system reliably while maintaining low latency and high availability.
