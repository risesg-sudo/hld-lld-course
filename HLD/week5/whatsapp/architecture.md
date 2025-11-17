# WhatsApp: High-Level Architecture

## Architectural Philosophy

WhatsApp's architecture is built on several key principles:

**Simplicity over Complexity**: Use proven technologies and simple designs. Complexity is the enemy of reliability at scale.

**Availability over Consistency**: Users must be able to send messages even if some servers are down. Eventual consistency is acceptable for a messaging platform.

**Asynchronous Processing**: Decouple message receipt from message delivery. This creates backpressure resistance and enables the system to handle spikes.

**Stateless Services**: Application servers should not store state. This enables horizontal scaling and easy failover.

## System Components

```
┌──────────┐
│  Mobile  │
│  Client  │
└─────┬────┘
      │ WebSocket (persistent connection)
      ▼
┌─────────────────┐
│ Load Balancer   │
│   (Layer 7)     │
└────────┬────────┘
         │
         ├──────────────┬───────────────┬──────────────┐
         ▼              ▼               ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Chat Service  │ │Presence Svc  │ │Media Service │ │Group Service │
│(WebSocket)   │ │(Online/Last) │ │(Upload/Down) │ │(Management)  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │                │
       └────────┬───────┴────────────────┴────────────────┘
                │
                ▼
       ┌────────────────┐
       │Message Queue   │
       │   (Kafka)      │
       └────────┬───────┘
                │
                ▼
       ┌────────────────┐
       │Message         │
       │Processor       │
       └────────┬───────┘
                │
        ┌───────┴────────┬───────────────┬────────────────┐
        ▼                ▼               ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Redis Cluster │ │Cassandra     │ │PostgreSQL    │ │S3/Blob Store │
│(Cache/       │ │(Messages)    │ │(Users/Groups)│ │(Media Files) │
│ Presence)    │ │              │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │
        ▼
┌──────────────┐
│Elasticsearch │
│(Search)      │
└──────────────┘
```

## Component Responsibilities

### Client Layer

**Mobile Clients**
- Maintain persistent WebSocket connection to server
- Send heartbeat every 30 seconds to maintain connection
- Handle offline message queue (store-and-forward when network available)
- Encrypt/decrypt messages locally (E2EE)

Why WebSocket? HTTP polling is inefficient for real-time messaging. WebSockets provide full-duplex communication with minimal overhead.

### Load Balancer

**Layer 7 Load Balancer**
- Routes WebSocket connections to chat servers
- Uses consistent hashing based on user_id to maintain affinity
- Performs health checks and removes unhealthy servers
- Handles TLS termination

Why Layer 7? We need to inspect the WebSocket upgrade request to route based on user_id, which requires application-layer understanding.

### Chat Service

**Responsibilities**:
- Maintain WebSocket connections with clients (50,000 per server)
- Validate incoming messages
- Publish messages to Kafka
- Subscribe to Kafka for messages destined to connected users
- Send acknowledgments back to senders

**Why this design?**
The chat service is a thin routing layer. It doesn't store messages itself - it hands them to Kafka and moves on. This keeps it stateless and fast.

### Message Queue (Kafka)

**Responsibilities**:
- Durably persist all messages before processing
- Provide ordering guarantees per partition
- Enable replay for debugging and recovery
- Decouple message ingestion from delivery

**Topics**:
- `messages.incoming`: All new messages
- `messages.outgoing`: Messages ready for delivery
- `notifications`: Push notifications for offline users
- `analytics`: Message events for metrics

**Partitioning Strategy**:
Partition by `recipient_id` to ensure messages to the same user are ordered.

Why Kafka? It handles millions of messages per second, provides durability, and enables multiple consumers to process the same stream for different purposes (delivery, analytics, search indexing).

### Message Processor

**Responsibilities**:
- Consume messages from Kafka
- Store in Cassandra for persistence
- Check if recipient is online (Redis lookup)
- If online: publish to recipient's Kafka partition
- If offline: trigger push notification
- Update message status (sent → delivered)
- Index in Elasticsearch for search

Why separate processor? This allows the chat service to handle connections while the processor handles the complex logic of routing and persistence.

### Presence Service

**Responsibilities**:
- Track which users are currently online
- Store last seen timestamps
- Notify contacts when user's status changes
- Auto-expire stale presence data

**How it works**:
- Client sends heartbeat every 30 seconds
- Server updates Redis with TTL of 60 seconds
- If heartbeat stops, Redis auto-expires entry → user offline
- Status changes broadcast via Pub/Sub to user's contacts

Why Redis? Sub-second latency for lookups, built-in TTL for auto-expiry, Pub/Sub for status broadcasts.

### Media Service

**Responsibilities**:
- Generate pre-signed upload URLs for clients
- Handle direct client-to-S3 uploads
- Process uploaded media (thumbnails, compression)
- Serve media through CDN

**Why direct uploads?**
Uploading through application servers wastes server bandwidth and CPU. S3 pre-signed URLs allow clients to upload directly to storage, reducing server load by 90%.

### Group Service

**Responsibilities**:
- Create and manage groups
- Add/remove members
- Handle group message fan-out
- Cache group membership for fast lookups

**Fan-out Strategy**:
WhatsApp uses write fan-out: when someone posts to a group, we create N individual messages (one per member). This trades write amplification for fast, simple reads.

## Data Storage Layer

### Redis (Cache and Presence)

**Stored Data**:
- User session information
- Presence status (online/offline, last seen)
- Recent messages (for quick retrieval)
- Group membership (cached for fast lookups)

**Configuration**:
- Multiple clusters sharded by user_id
- 2 replicas per shard for availability
- LRU eviction policy for cache entries
- No persistence needed (can rebuild from source)

### Cassandra (Message Storage)

**Why Cassandra?**
- Handles massive write throughput (1.7M writes/second at peak)
- Horizontally scalable (add nodes as needed)
- Perfect for time-series data (messages ordered by time)
- Eventual consistency is acceptable for chat

**Data Model**:
- Partition key: conversation_id
- Clustering key: message_id (time-based UUID)
- Natural ordering by time
- Efficient range queries for message history

### PostgreSQL (Structured Data)

**Why PostgreSQL?**
- Complex relationships (users, contacts, groups)
- ACID compliance for critical data
- Rich query capabilities for analytics
- Better suited for low-volume, high-consistency data

**Stored Data**:
- User profiles
- Contact relationships
- Group metadata
- Device information

### S3/Blob Storage (Media)

**Why object storage?**
- Designed for large files
- Highly durable (99.999999999%)
- Cheap compared to database storage
- Integrates well with CDN

**Storage Strategy**:
- Original files in S3
- Thumbnails in S3 + CDN for fast access
- Lifecycle policies for tiered storage (hot/warm/cold)

### Elasticsearch (Search)

**Purpose**: Full-text search across message history

**Indexing Strategy**:
- Async indexing from Kafka stream
- Index message content, sender, timestamp
- Shard by user_id for query locality

Why async? Indexing is not on the critical path for message delivery. We can tolerate a few seconds lag.

## Message Flow: End to End

### Sending a Message (Alice → Bob)

1. **Alice's Client** → Sends message via WebSocket to Chat Service
2. **Chat Service** → Validates message, publishes to Kafka `messages.incoming`
3. **Chat Service** → Immediately sends ACK to Alice (message is durable in Kafka)
4. **Message Processor** → Consumes from Kafka
5. **Message Processor** → Writes to Cassandra for persistence
6. **Message Processor** → Checks Redis: Is Bob online?
7. **If Bob online** → Publishes to `messages.outgoing` for Bob's partition
8. **If Bob offline** → Publishes to `notifications` topic
9. **Chat Service** (connected to Bob) → Receives from Kafka, delivers via WebSocket
10. **Bob's Client** → Sends delivery ACK
11. **Message Processor** → Updates message status to "delivered"
12. **Notification Service** (if Bob offline) → Sends push notification

### Why This Flow?

**Kafka in the middle**: Provides durability and decoupling. If Bob's chat service crashes, the message is safe in Kafka.

**Async processing**: The chat service doesn't wait for database writes. It gets the message into Kafka and moves on.

**Status updates**: Each stage updates the message status, providing feedback to the sender.

## Scalability Considerations

### Horizontal Scaling

Every component scales horizontally:
- Chat Service: Add more servers, load balancer routes connections
- Kafka: Add more brokers and partitions
- Cassandra: Add more nodes to the cluster
- Redis: Add more shards
- PostgreSQL: Read replicas + sharding

### Geographic Distribution

Deploy full stacks in multiple regions:
- US East, US West, Europe, Asia, etc.
- Users connect to nearest region (GeoDNS)
- Cross-region replication for user data
- Media stored globally via CDN

### Why Multiple Regions?

- Reduced latency (users connect to nearby servers)
- Fault tolerance (region failure doesn't take down the system)
- Regulatory compliance (data residency requirements)

## Design Decisions and Trade-offs

**Why WebSocket over HTTP/2?**
- Full-duplex communication
- Lower overhead than repeated HTTP requests
- Native support in mobile platforms
- Trade-off: Requires persistent connections (more server memory)

**Why Kafka over RabbitMQ?**
- Higher throughput (millions of messages/sec)
- Durable by design (disk-backed)
- Built-in partitioning and ordering
- Trade-off: More complex to operate

**Why Cassandra over MySQL?**
- Better write scalability
- Natural fit for time-series data
- Horizontal scaling built-in
- Trade-off: Eventually consistent, no joins

**Fan-out on Write vs Read?**
- Choice: Fan-out on write (create N copies for group messages)
- Benefit: Fast reads (simple queries)
- Trade-off: Write amplification (more storage, more writes)
- Why it's worth it: WhatsApp is read-heavy (people read more than write)

This architecture handles billions of messages daily while maintaining low latency and high availability. The key is using the right tool for each job and embracing asynchronous, distributed design patterns.
