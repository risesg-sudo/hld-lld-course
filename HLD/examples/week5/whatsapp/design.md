# WhatsApp System Design

## Table of Contents
1. [Requirements](#requirements)
2. [Capacity Estimation](#capacity-estimation)
3. [High-Level Architecture](#high-level-architecture)
4. [Component Design](#component-design)
5. [Data Models](#data-models)
6. [API Design](#api-design)
7. [Scalability](#scalability)
8. [Potential Bottlenecks](#potential-bottlenecks)

---

## Requirements

### Functional Requirements
1. **One-on-One Messaging**: Users can send text messages to each other
2. **Group Messaging**: Users can create groups and send messages to multiple users
3. **Media Sharing**: Support for images, videos, documents, and audio
4. **Online Status**: Show when users are online/offline and last seen
5. **Message Status**: Sent, Delivered, Read receipts
6. **Push Notifications**: Notify users of new messages when offline
7. **Multi-Device Support**: Access from multiple devices simultaneously
8. **Message Search**: Search through message history
9. **Voice/Video Calls**: Real-time audio and video communication

### Non-Functional Requirements
1. **Scalability**: Support 2 billion+ users
2. **High Availability**: 99.99% uptime
3. **Low Latency**: Messages delivered in < 100ms
4. **Reliability**: No message loss
5. **Consistency**: Messages delivered in order
6. **Security**: End-to-end encryption
7. **Efficiency**: Optimize for mobile networks (low bandwidth)
8. **Real-time**: Instant message delivery when users are online

### Out of Scope (for this design)
- End-to-end encryption implementation details
- Payment features (WhatsApp Pay)
- Business API
- Status/Stories feature

---

## Capacity Estimation

### Assumptions
- **Total Users**: 2 billion
- **Daily Active Users (DAU)**: 1 billion (50% of total)
- **Messages per user per day**: 50
- **Group messages**: 20% of all messages
- **Media messages**: 10% of all messages
- **Average message size**: 100 bytes (text)
- **Average media size**: 500 KB
- **Concurrent connections**: 100 million peak

### Traffic Estimates

#### Messages per Day
```
Total messages/day = 1 billion users × 50 messages = 50 billion messages/day
```

#### Messages per Second
```
Average: 50 billion / 86,400 seconds ≈ 580,000 messages/second
Peak (3x average): 1.74 million messages/second
```

#### Data Generation
```
Text messages/day = 50B × 0.9 = 45B messages
Text data = 45B × 100 bytes = 4.5 TB/day

Media messages/day = 50B × 0.1 = 5B messages
Media data = 5B × 500 KB = 2.5 PB/day
```

### Storage Estimates

#### Message Storage (5-year retention)
```
Text storage = 4.5 TB/day × 365 days × 5 years = 8.2 PB
Media storage = 2.5 PB/day × 365 days × 5 years = 4.5 EB (exabytes)

With replication (3x):
- Text: 24.6 PB
- Media: 13.5 EB
```

#### Metadata Storage
```
User profiles: 2B users × 1 KB = 2 TB
Groups: 100M groups × 10 KB = 1 TB
Total metadata: ~3 TB (negligible compared to messages)
```

### Bandwidth Estimates

#### Incoming (Upload)
```
Text: 4.5 TB/day / 86,400 sec = 52 MB/s
Media: 2.5 PB/day / 86,400 sec = 28.9 GB/s
Total incoming: ~29 GB/s
```

#### Outgoing (Download)
```
Each message delivered to 1 user (1-on-1) or N users (group avg 10)
Multiplier = 0.8 × 1 + 0.2 × 10 = 2.8

Outgoing = Incoming × 2.8 = 81 GB/s
Peak (3x): 243 GB/s
```

### Memory/Cache Estimates
```
Active users concurrently: 100M
Cache user data: 100M × 10 KB = 1 TB
Cache recent messages: 100M users × 10 messages × 100 bytes = 100 GB
Total cache: ~1.1 TB (distributed across servers)
```

### Server Estimates
```
Assuming each server handles:
- 50,000 concurrent WebSocket connections
- 10,000 messages/second

WebSocket servers: 100M connections / 50K = 2,000 servers
Message processing: 1.74M messages/sec / 10K = 174 servers

Total application servers: ~2,500 (with redundancy)
```

---

## High-Level Architecture

```
                                    ┌─────────────────┐
                                    │   DNS/CDN       │
                                    └────────┬────────┘
                                             │
                                             ▼
┌──────────┐                        ┌─────────────────┐
│  Mobile  │◄──────────────────────►│  Load Balancer  │
│  Client  │       WebSocket        │   (Layer 7)     │
└──────────┘                        └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    ▼                        ▼                        ▼
           ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
           │  Chat Service   │     │ Presence Service│     │  Media Service  │
           │   (WebSocket)   │     │   (Online/Last) │     │ (Upload/Download)│
           └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
                    │                       │                       │
                    ▼                       ▼                       ▼
           ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
           │ Message Queue   │     │  Redis Cluster  │     │   S3/Blob Store │
           │    (Kafka)      │     │ (Presence Cache)│     │  (Media Files)  │
           └────────┬────────┘     └─────────────────┘     └─────────────────┘
                    │
                    ▼
      ┌────────────────────────────┐
      │   Message Processor        │
      │   (Consumer Service)       │
      └────────┬───────────────────┘
               │
               ▼
      ┌────────────────────────────┐           ┌─────────────────┐
      │  Cassandra Cluster         │           │  PostgreSQL     │
      │  (Message Storage)         │           │  (Users/Groups) │
      └────────────────────────────┘           └─────────────────┘
               │
               ▼
      ┌────────────────────────────┐
      │  Elasticsearch             │
      │  (Message Search)          │
      └────────────────────────────┘
```

### Component Overview

1. **Load Balancer**: Distributes incoming connections across chat servers
2. **Chat Service**: Handles WebSocket connections and real-time messaging
3. **Message Queue (Kafka)**: Decouples message ingestion from processing
4. **Message Processor**: Consumes from queue, stores messages, sends notifications
5. **Presence Service**: Manages online/offline status and last seen
6. **Media Service**: Handles upload/download of images, videos, documents
7. **Cassandra**: Stores messages with high write throughput
8. **PostgreSQL**: Stores user profiles, groups, contacts
9. **Redis**: Caches presence info, user sessions, recent messages
10. **S3/Blob Storage**: Stores media files
11. **Elasticsearch**: Enables message search
12. **Push Notification Service**: Sends notifications to offline users

---

## Component Design

### 1. Chat Service (WebSocket Server)

**Responsibilities**:
- Maintain persistent WebSocket connections
- Receive messages from clients
- Publish messages to Kafka
- Deliver messages to online recipients
- Handle connection lifecycle

**Architecture**:
```
┌───────────────────────────────────────┐
│        Chat Service Instance          │
├───────────────────────────────────────┤
│                                       │
│  ┌─────────────────────────────────┐ │
│  │  Connection Manager             │ │
│  │  - 50K concurrent connections   │ │
│  │  - Connection → User mapping    │ │
│  │  - Heartbeat/Ping-Pong          │ │
│  └─────────────────────────────────┘ │
│                                       │
│  ┌─────────────────────────────────┐ │
│  │  Message Handler                │ │
│  │  - Validate message             │ │
│  │  - Publish to Kafka             │ │
│  │  - Send ACK to sender           │ │
│  └─────────────────────────────────┘ │
│                                       │
│  ┌─────────────────────────────────┐ │
│  │  Session Manager                │ │
│  │  - User authentication          │ │
│  │  - Session state (Redis)        │ │
│  │  - Multi-device support         │ │
│  └─────────────────────────────────┘ │
│                                       │
└───────────────────────────────────────┘
```

**Flow**:
1. Client connects via WebSocket
2. Server authenticates using JWT token
3. Server stores connection info in memory and session in Redis
4. Server subscribes to user's Kafka topic for incoming messages
5. On receiving message from client: validate → Kafka → ACK
6. On receiving from Kafka: find user's connection → deliver

**Scalability**:
- Stateless design (session in Redis)
- Horizontal scaling (add more servers)
- Connection routing via consistent hashing
- Graceful shutdown with connection draining

### 2. Message Queue (Kafka)

**Purpose**: Decouple message ingestion from processing

**Topics**:
- `messages.incoming`: All incoming messages
- `messages.outgoing`: Messages ready for delivery
- `notifications`: Push notifications for offline users
- `analytics`: Message events for analytics

**Partitioning Strategy**:
- Partition by recipient_id for ordering guarantees
- Number of partitions: 1000 (balance parallelism and overhead)

**Configuration**:
```
Replication Factor: 3
Retention: 7 days
Compression: LZ4
Acks: all (ensure durability)
```

**Benefits**:
- High throughput (millions of messages/sec)
- Durability (messages persisted to disk)
- Replay capability (debugging, recovery)
- Backpressure handling

### 3. Message Processor (Consumer Service)

**Responsibilities**:
- Consume messages from Kafka
- Store in Cassandra
- Index in Elasticsearch
- Update message status
- Send to online recipients
- Trigger push notifications

**Flow**:
```
┌─────────────────────────────────────────┐
│                                         │
│  1. Consume from Kafka                  │
│     ▼                                   │
│  2. Validate & Deduplicate              │
│     ▼                                   │
│  3. Store in Cassandra                  │
│     ▼                                   │
│  4. Check recipient online (Redis)      │
│     ├─ Online → Publish to WebSocket    │
│     └─ Offline → Push Notification      │
│     ▼                                   │
│  5. Update status (sent/delivered)      │
│     ▼                                   │
│  6. Index in Elasticsearch (async)      │
│                                         │
└─────────────────────────────────────────┘
```

**Optimizations**:
- Batch writes to Cassandra (100 messages)
- Async Elasticsearch indexing
- Connection pooling for databases
- Circuit breaker for external services

### 4. Presence Service

**Responsibilities**:
- Track online/offline status
- Update last seen timestamp
- Notify contacts when status changes

**Data Structure (Redis)**:
```
Key: presence:user:{user_id}
Value: {
  "status": "online|offline",
  "last_seen": timestamp,
  "device": "mobile|web|desktop"
}
TTL: 60 seconds (auto-expire)
```

**Flow**:
1. Client sends heartbeat every 30 seconds
2. Server updates Redis with online status + TTL
3. If heartbeat stops, Redis auto-expires → offline
4. On status change, notify user's contacts

**Optimization**:
- Batch status updates (every 10 seconds)
- Pub/Sub for status change notifications
- Cache user's contact list in Redis

### 5. Media Service

**Upload Flow**:
```
Client                  Media Service           S3              Cassandra
  │                           │                  │                  │
  ├─1. Request upload URL────►│                  │                  │
  │                           ├─2. Generate ID───┤                  │
  │                           │                  │                  │
  │◄──3. Return presigned URL─┤                  │                  │
  │                           │                  │                  │
  ├─4. Upload directly────────┼─────────────────►│                  │
  │                           │                  │                  │
  │◄──5. Upload complete──────┼──────────────────┤                  │
  │                           │                  │                  │
  ├─6. Confirm upload─────────►│                  │                  │
  │                           ├─7. Create thumbnails                │
  │                           │                  │                  │
  │                           ├─8. Store metadata┼─────────────────►│
  │                           │                  │                  │
  │◄──9. Media ID──────────────┤                  │                  │
```

**Storage**:
- Original files: S3/GCS (cheap, durable)
- Thumbnails: S3 + CDN (fast access)
- Metadata: Cassandra (media_id, url, size, type)

**Optimizations**:
- Direct client-to-S3 upload (reduce server load)
- Lazy thumbnail generation (on first access)
- Compression (reduce bandwidth)
- CDN for popular media

### 6. Group Service

**Responsibilities**:
- Create/update/delete groups
- Manage group members
- Handle group messaging

**Data Model**:
```sql
-- PostgreSQL
groups (
  group_id UUID PRIMARY KEY,
  name VARCHAR(256),
  created_by UUID,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

group_members (
  group_id UUID,
  user_id UUID,
  role ENUM('admin', 'member'),
  joined_at TIMESTAMP,
  PRIMARY KEY (group_id, user_id)
)
```

**Group Message Flow**:
1. User sends message to group
2. Message processor fetches group members
3. Fan-out: Create N messages (one per member)
4. Each member receives individual message
5. Optimization: Cache group members in Redis

**Fan-out Strategies**:
- **Fan-out on write** (WhatsApp approach):
  - Store message separately for each user
  - Pros: Fast reads, simple queries
  - Cons: Higher storage, write amplification

- **Fan-out on read** (alternative):
  - Store message once with group_id
  - Pros: Lower storage
  - Cons: Slower reads, complex queries

WhatsApp uses fan-out on write for simplicity and read performance.

---

## Data Models

### 1. User Service (PostgreSQL)

```sql
-- Users table
users (
  user_id UUID PRIMARY KEY,
  phone_number VARCHAR(20) UNIQUE NOT NULL,
  username VARCHAR(100),
  profile_picture_url TEXT,
  status TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
)
CREATE INDEX idx_phone ON users(phone_number);

-- Contacts table (who you've added)
contacts (
  user_id UUID,
  contact_id UUID,
  display_name VARCHAR(100),
  added_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (user_id, contact_id)
)
CREATE INDEX idx_user_contacts ON contacts(user_id);

-- Devices (multi-device support)
devices (
  device_id UUID PRIMARY KEY,
  user_id UUID,
  device_type ENUM('mobile', 'web', 'desktop'),
  push_token TEXT,
  last_active TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
)
CREATE INDEX idx_user_devices ON devices(user_id);
```

### 2. Message Service (Cassandra)

**Why Cassandra?**
- High write throughput (millions of writes/sec)
- Horizontal scalability
- Time-series data (messages sorted by time)
- Eventually consistent (acceptable for chat)

```cql
-- One-on-One Messages
CREATE TABLE messages (
  conversation_id UUID,      -- Hash of sorted(user1_id, user2_id)
  message_id TIMEUUID,       -- Time-based UUID for ordering
  sender_id UUID,
  recipient_id UUID,
  content TEXT,
  media_id UUID,
  message_type TEXT,         -- 'text', 'image', 'video', etc.
  status TEXT,               -- 'sent', 'delivered', 'read'
  created_at TIMESTAMP,
  PRIMARY KEY (conversation_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);

CREATE INDEX idx_message_sender ON messages(sender_id);

-- Group Messages
CREATE TABLE group_messages (
  group_id UUID,
  message_id TIMEUUID,
  sender_id UUID,
  content TEXT,
  media_id UUID,
  message_type TEXT,
  created_at TIMESTAMP,
  PRIMARY KEY (group_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);

-- User's Messages (inbox view - fan-out on write)
CREATE TABLE user_messages (
  user_id UUID,
  conversation_id UUID,      -- user_id or group_id
  message_id TIMEUUID,
  sender_id UUID,
  content TEXT,
  media_id UUID,
  message_type TEXT,
  status TEXT,
  is_group BOOLEAN,
  created_at TIMESTAMP,
  PRIMARY KEY (user_id, conversation_id, message_id)
) WITH CLUSTERING ORDER BY (conversation_id ASC, message_id DESC);
```

**Partitioning Strategy**:
- Partition key: conversation_id or user_id (distributes load)
- Clustering key: message_id (time-based ordering)
- Tombstones: Handle deleted messages with TTL

### 3. Media Service (Metadata in Cassandra)

```cql
CREATE TABLE media (
  media_id UUID PRIMARY KEY,
  uploader_id UUID,
  file_type TEXT,            -- 'image', 'video', 'audio', 'document'
  file_size BIGINT,
  original_url TEXT,
  thumbnail_url TEXT,
  encryption_key TEXT,       -- For E2E encryption
  uploaded_at TIMESTAMP
)

CREATE INDEX idx_media_uploader ON media(uploader_id);
```

### 4. Presence Service (Redis)

```
# Online status
Key: presence:online:{user_id}
Value: {
  "status": "online",
  "last_heartbeat": 1699999999,
  "devices": ["device_id_1", "device_id_2"]
}
TTL: 60 seconds

# Last seen (persistent)
Key: presence:lastseen:{user_id}
Value: timestamp
TTL: None (persist in DB daily)

# Typing indicator
Key: typing:{conversation_id}:{user_id}
Value: "1"
TTL: 10 seconds
```

---

## API Design

### REST APIs (User Management)

#### 1. User Registration
```http
POST /api/v1/users/register
Content-Type: application/json

Request:
{
  "phone_number": "+1234567890",
  "verification_code": "123456"
}

Response: 201 Created
{
  "user_id": "uuid",
  "phone_number": "+1234567890",
  "auth_token": "jwt_token"
}
```

#### 2. Get User Profile
```http
GET /api/v1/users/{user_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "user_id": "uuid",
  "phone_number": "+1234567890",
  "username": "John Doe",
  "profile_picture_url": "https://cdn.example.com/...",
  "status": "Hey there! I'm using WhatsApp"
}
```

#### 3. Update Profile
```http
PUT /api/v1/users/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "username": "John Doe",
  "status": "Busy"
}

Response: 200 OK
```

#### 4. Get Contacts
```http
GET /api/v1/users/{user_id}/contacts
Authorization: Bearer {token}

Response: 200 OK
{
  "contacts": [
    {
      "contact_id": "uuid",
      "display_name": "Alice",
      "phone_number": "+1234567891",
      "profile_picture_url": "...",
      "last_seen": 1699999999
    }
  ]
}
```

### WebSocket APIs (Real-time Messaging)

#### Connection Establishment
```javascript
// Client
const ws = new WebSocket('wss://chat.whatsapp.com/ws');

// Send authentication
ws.send(JSON.stringify({
  type: 'auth',
  token: 'jwt_token'
}));

// Server response
{
  type: 'auth_success',
  user_id: 'uuid',
  server_time: 1699999999
}
```

#### Send Message
```javascript
// Client → Server
{
  type: 'message',
  message_id: 'client_generated_uuid',  // For deduplication
  recipient_id: 'uuid',
  content: 'Hello!',
  timestamp: 1699999999
}

// Server → Client (ACK)
{
  type: 'message_ack',
  message_id: 'client_generated_uuid',
  server_message_id: 'server_uuid',
  status: 'sent',
  timestamp: 1699999999
}
```

#### Receive Message
```javascript
// Server → Client
{
  type: 'new_message',
  message_id: 'uuid',
  conversation_id: 'uuid',
  sender_id: 'uuid',
  content: 'Hello!',
  timestamp: 1699999999
}

// Client → Server (Delivery ACK)
{
  type: 'delivery_ack',
  message_id: 'uuid'
}
```

#### Message Status Updates
```javascript
// Server → Sender
{
  type: 'message_status',
  message_id: 'uuid',
  status: 'delivered',  // or 'read'
  timestamp: 1699999999
}
```

#### Typing Indicator
```javascript
// Client → Server
{
  type: 'typing',
  conversation_id: 'uuid',
  is_typing: true
}

// Server → Recipient
{
  type: 'user_typing',
  conversation_id: 'uuid',
  user_id: 'uuid',
  is_typing: true
}
```

#### Presence Updates
```javascript
// Server → Client (when contact goes online/offline)
{
  type: 'presence_update',
  user_id: 'uuid',
  status: 'online',
  last_seen: 1699999999
}
```

### Group APIs

#### Create Group
```http
POST /api/v1/groups
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "name": "Family",
  "member_ids": ["uuid1", "uuid2", "uuid3"]
}

Response: 201 Created
{
  "group_id": "uuid",
  "name": "Family",
  "created_by": "uuid",
  "members": [...]
}
```

#### Send Group Message
```javascript
// WebSocket
{
  type: 'group_message',
  message_id: 'client_uuid',
  group_id: 'uuid',
  content: 'Hello everyone!',
  timestamp: 1699999999
}
```

---

## Scalability

### 1. Database Scalability

#### Cassandra (Messages)
**Current**: Petabytes of data, billions of rows

**Scaling Strategy**:
- **Horizontal Scaling**: Add more nodes
- **Replication Factor**: 3 (data on 3 nodes)
- **Consistency Level**: QUORUM (read/write)
- **Partitioning**: By conversation_id (even distribution)

**Optimization**:
- Compaction strategy: TimeWindowCompactionStrategy
- Bloom filters: Reduce disk reads
- Memtable size: Increase for write-heavy workload
- SSTables: Optimize for sequential reads

#### PostgreSQL (Users/Groups)
**Current**: Billions of users, millions of groups

**Scaling Strategy**:
- **Read Replicas**: 5-10 replicas per master
- **Sharding**: By user_id (consistent hashing)
  - Shard 1: user_id % 10 == 0
  - Shard 2: user_id % 10 == 1
  - ...
- **Connection Pooling**: PgBouncer (reduce connection overhead)

**Read/Write Split**:
- Writes → Master
- Reads → Replicas (round-robin)

### 2. Cache Scalability (Redis)

**Current Setup**:
- 50 Redis clusters (sharded by user_id)
- Each cluster: 1 master + 2 replicas
- Total memory: 1 TB+

**Scaling Strategy**:
- **Redis Cluster**: Auto-sharding across 16,384 slots
- **Consistent Hashing**: Minimize redistribution on scaling
- **Eviction Policy**: LRU (Least Recently Used)

**Cached Data**:
- User sessions (30 min TTL)
- Presence info (60 sec TTL)
- Recent messages (24 hour TTL)
- Group members (1 hour TTL)

### 3. Message Queue Scalability (Kafka)

**Current Setup**:
- 100+ Kafka brokers
- 1000 partitions per topic
- Replication factor: 3

**Scaling Strategy**:
- **Add Brokers**: Horizontal scaling
- **Increase Partitions**: More parallelism (careful, can't reduce)
- **Consumer Groups**: Parallel message processing

**Partition Assignment**:
```
Partition(message) = hash(recipient_id) % num_partitions
```
This ensures messages to same user go to same partition (ordering).

### 4. WebSocket Server Scalability

**Challenge**: 100M concurrent connections

**Solution**:
- 2,000 WebSocket servers (50K connections each)
- Stateless design (session in Redis)
- Sticky sessions at load balancer (by user_id)

**Connection Routing**:
```
Server = consistent_hash(user_id) % num_servers
```

**Load Balancing**:
- Layer 7 load balancer (Nginx, HAProxy)
- Health checks every 10 seconds
- Graceful connection draining on deploy

### 5. Geographic Distribution

**Multi-Region Deployment**:
```
Region 1 (US East)      Region 2 (EU)         Region 3 (Asia)
     │                       │                      │
     ├─ Load Balancers       ├─ Load Balancers     ├─ Load Balancers
     ├─ Chat Servers         ├─ Chat Servers       ├─ Chat Servers
     ├─ Kafka Cluster        ├─ Kafka Cluster      ├─ Kafka Cluster
     ├─ Cassandra Nodes      ├─ Cassandra Nodes    ├─ Cassandra Nodes
     └─ Redis Clusters       └─ Redis Clusters     └─ Redis Clusters
           │                       │                      │
           └───────────────────────┴──────────────────────┘
                         Cross-region replication
```

**Cross-Region Strategy**:
- Users routed to nearest region (DNS geolocation)
- Cassandra: Multi-DC replication (eventual consistency)
- Messages: Async replication across regions
- Media: CDN handles global distribution

---

## Scalability (Continued)

### 6. Auto-Scaling Strategy

**Metrics to Monitor**:
- WebSocket connections per server
- Kafka consumer lag
- Database query latency
- Cache hit rate
- CPU/Memory utilization

**Scaling Rules**:
```yaml
# Chat Servers
scale_up:
  - metric: avg_connections > 40K per server
  - metric: cpu > 70%
  - action: add 10% more servers

scale_down:
  - metric: avg_connections < 20K per server
  - metric: cpu < 30%
  - action: remove 10% servers (gracefully)

# Kafka Consumers
scale_up:
  - metric: consumer_lag > 100K messages
  - action: add consumer instances

# Database
scale_up:
  - metric: query_latency > 100ms (p99)
  - action: add read replicas
```

### 7. Handling Viral Messages

**Problem**: A message shared in many groups → write amplification

**Example**:
- Message shared in 100 groups
- Each group has 100 members
- Total writes: 10,000 (fan-out)

**Solutions**:
1. **Rate Limiting**: Limit group size to 256 members
2. **Batch Writes**: Group database writes
3. **Async Processing**: Use queue, process in background
4. **Deduplication**: Store media once, reference multiple times

---

## Potential Bottlenecks

### 1. WebSocket Connection Bottleneck

**Problem**: Each server limited by file descriptors (OS limit)

**Default Linux limit**: 1024 file descriptors
**WhatsApp needs**: 50K+ connections per server

**Solutions**:
```bash
# Increase file descriptor limit
ulimit -n 1000000

# /etc/sysctl.conf
fs.file-max = 2000000
net.ipv4.ip_local_port_range = 1024 65535
net.core.somaxconn = 4096
```

**Additional Optimizations**:
- Use epoll (Linux) for efficient I/O multiplexing
- Reduce memory per connection (< 10 KB)
- Connection pooling to databases
- Lazy loading of user data

### 2. Database Write Bottleneck

**Problem**: 1.74M messages/second → database writes

**Cassandra can handle**, but optimizations:
- **Batch Writes**: Group 100 writes into 1 batch
- **Async Writes**: Don't block message delivery
- **Write-through Cache**: Write to cache, async to DB
- **TTL on old messages**: Archive after 1 year

**Monitoring**:
- Write latency (p50, p99, p999)
- Pending write queue depth
- Node saturation

### 3. Message Ordering Bottleneck

**Problem**: Ensure messages delivered in order

**Challenge**:
- Network delays vary
- Multiple servers process messages
- Distributed system (no global clock)

**Solutions**:
1. **Kafka Partitioning**: Same recipient → same partition (ordered)
2. **Message ID**: TIMEUUID (includes timestamp)
3. **Client-side Ordering**: Client reorders if needed
4. **Vector Clocks**: For complex scenarios (not used in WhatsApp)

**Trade-off**: Perfect ordering vs. availability
- WhatsApp chooses: Eventual ordering (99.9% ordered immediately)

### 4. Presence Service Bottleneck

**Problem**: 100M users going online simultaneously (morning)

**Load**:
- 100M status updates
- Each user has ~50 contacts
- Notifications: 100M × 50 = 5 billion events

**Solutions**:
1. **Batching**: Send status every 10 seconds, not every second
2. **Sampling**: Don't notify all contacts, just active chats
3. **Rate Limiting**: Max 10 status updates/min per user
4. **Lazy Loading**: Fetch status when user opens chat
5. **Pub/Sub**: Redis Pub/Sub for status broadcasts

### 5. Group Message Bottleneck

**Problem**: Large groups (256 members) → fan-out writes

**Calculation**:
- 1 message to 256-member group
- Write 256 copies (fan-out on write)
- 10K such messages/sec → 2.56M writes/sec

**Solutions**:
1. **Limit Group Size**: 256 members max
2. **Async Fan-out**: Queue the fan-out, process async
3. **Read-optimized Storage**: Denormalize for fast reads
4. **Group Message Compression**: Store once + pointers

**WhatsApp Approach**: Accept write amplification for read performance

### 6. Media Storage Bottleneck

**Problem**: 2.5 PB of media uploaded daily

**Challenges**:
- Storage cost
- Upload/download bandwidth
- Global distribution

**Solutions**:
1. **Compression**: Reduce image/video size (lossy)
2. **Tiered Storage**:
   - Hot (30 days): SSD
   - Warm (1 year): HDD
   - Cold (archive): Glacier
3. **CDN**: Cache popular media globally
4. **Deduplication**: Same image sent multiple times → store once
5. **Client-side Upload**: Direct to S3 (reduce server load)

### 7. Read Replica Lag

**Problem**: Write to master, read from replica → stale data

**Example**:
- User sends message (written to master)
- Immediately opens chat (read from replica)
- Message not yet replicated → doesn't see own message

**Solutions**:
1. **Read Your Writes**: After write, read from master (1 minute)
2. **Monotonic Reads**: Always read from same replica
3. **Versioning**: Client tracks version, requests newer data
4. **Fast Replication**: < 100ms replication lag

### 8. Network Partition

**Problem**: Network split → some servers can't communicate

**Scenario**:
- US datacenter can't reach EU datacenter
- User's devices connected to different DCs
- Messages diverge

**Solutions (CAP Theorem)**:
- **Partition Tolerance**: Must tolerate network splits
- **Choose Availability over Consistency**:
  - Allow writes in both DCs
  - Reconcile later (eventual consistency)
- **Conflict Resolution**: Last write wins (LWW)
- **Vector Clocks**: For complex conflict resolution

**WhatsApp Approach**: Availability > Consistency
- Users can send messages even during partition
- Messages sync when partition heals

### 9. Hot Shards

**Problem**: Celebrity/influencer → disproportionate load on one shard

**Example**:
- Celebrity has 10M followers
- Posts status update
- All 10M fetch update → one shard overloaded

**Solutions**:
1. **Shard by Content, not User**: Distribute load
2. **Caching**: Cache celebrity status heavily
3. **Rate Limiting**: Limit requests to celebrity accounts
4. **Dedicated Shards**: Special handling for hot accounts

### 10. Thundering Herd

**Problem**: Cache expires → millions of requests hit DB

**Scenario**:
- Popular group's members cached (1 hour TTL)
- Cache expires at 12:00 PM
- Next second, 10K requests → cache miss → hit DB

**Solutions**:
1. **Staggered Expiration**: Random TTL jitter
   ```
   TTL = base_ttl + random(0, 60 seconds)
   ```
2. **Cache Warming**: Proactively refresh before expiration
3. **Request Coalescing**: First request fetches, others wait
4. **Circuit Breaker**: Stop requests if DB is overloaded

---

## Additional Considerations

### 1. Security

**End-to-End Encryption (E2EE)**:
- Signal Protocol (used by WhatsApp)
- Messages encrypted on sender device
- Decrypted only on recipient device
- Server cannot read message content

**Authentication**:
- Phone number verification (SMS/call)
- JWT tokens for API authentication
- Device-specific keys for multi-device

**Authorization**:
- User can only read own messages
- Group messages: Verify membership before delivery
- Media access: Signed URLs with expiration

### 2. Monitoring & Observability

**Key Metrics**:
- **Availability**: Uptime, error rate
- **Latency**: Message delivery time (p50, p99, p999)
- **Throughput**: Messages/second
- **Resource Utilization**: CPU, memory, disk, network

**Tools**:
- Prometheus: Metrics collection
- Grafana: Visualization
- ELK Stack: Logs aggregation
- Jaeger: Distributed tracing
- PagerDuty: Alerting

**SLIs (Service Level Indicators)**:
- 99.9% of messages delivered < 100ms
- 99.99% uptime
- < 0.01% message loss

### 3. Disaster Recovery

**Backup Strategy**:
- **Database**: Daily snapshots + continuous WAL archiving
- **Kafka**: Replication to backup cluster
- **Media**: S3 cross-region replication

**RTO/RPO**:
- Recovery Time Objective: < 1 hour
- Recovery Point Objective: < 5 minutes data loss

**Failover Plan**:
1. Detect failure (automated health checks)
2. Promote read replica to master
3. Redirect traffic to healthy region
4. Investigate and fix root cause

### 4. Cost Optimization

**Major Costs**:
- Media storage: 13.5 EB (largest cost)
- Bandwidth: 243 GB/s peak
- Compute: 2,500+ servers
- Data transfer: Cross-region replication

**Optimization Strategies**:
- **Compression**: Reduce storage and bandwidth
- **Tiered Storage**: Move old data to cheap storage
- **Spot Instances**: For batch jobs (Elasticsearch indexing)
- **Reserved Instances**: For predictable workloads
- **CDN**: Reduce origin bandwidth cost

---

## Summary

WhatsApp's architecture is a masterclass in scalable system design:

**Key Takeaways**:
1. **Simple Protocol**: WebSocket for bidirectional communication
2. **Asynchronous Processing**: Kafka decouples ingestion from processing
3. **Denormalization**: Fan-out on write for fast reads
4. **Eventual Consistency**: Accept for availability and performance
5. **Stateless Services**: Horizontal scaling without limits
6. **Multi-layered Caching**: Redis for hot data, reducing DB load
7. **Optimized for Mobile**: Efficient protocols, compression

**Design Philosophy**:
- **Availability > Consistency**: Users can always send messages
- **Performance > Features**: Fast and reliable over fancy features
- **Simple > Complex**: Easier to operate and debug

**Numbers to Remember**:
- 2 billion users, 1 billion DAU
- 50 billion messages/day
- 100 million concurrent connections
- < 100ms message delivery latency
- 99.99% uptime

This design scales to billions of users while maintaining simplicity and reliability!
