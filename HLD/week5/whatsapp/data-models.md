# WhatsApp: Data Models

## Database Selection Rationale

WhatsApp uses a polyglot persistence approach - different databases for different needs:

**PostgreSQL**: Structured relational data (users, groups, contacts)
**Cassandra**: High-volume time-series data (messages, locations)
**Redis**: Cache and ephemeral data (sessions, presence)
**S3**: Large binary objects (media files)
**Elasticsearch**: Full-text search

Why this combination? Each database is optimized for its specific use case. Using the right tool for each job results in better performance and lower costs than forcing everything into one database.

## PostgreSQL Schemas

### Users and Contacts

```sql
-- Users table
CREATE TABLE users (
  user_id UUID PRIMARY KEY,
  phone_number VARCHAR(20) UNIQUE NOT NULL,
  username VARCHAR(100),
  profile_picture_url TEXT,
  status TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_phone ON users(phone_number);

-- Contacts (who you've added)
CREATE TABLE contacts (
  user_id UUID,
  contact_id UUID,
  display_name VARCHAR(100),
  added_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (user_id, contact_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (contact_id) REFERENCES users(user_id)
);

CREATE INDEX idx_user_contacts ON contacts(user_id);

-- Multi-device support
CREATE TABLE devices (
  device_id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  device_type ENUM('mobile', 'web', 'desktop'),
  push_token TEXT,
  last_active TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_user_devices ON devices(user_id);
```

### Groups

```sql
CREATE TABLE groups (
  group_id UUID PRIMARY KEY,
  name VARCHAR(256) NOT NULL,
  description TEXT,
  icon_url TEXT,
  created_by UUID NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE group_members (
  group_id UUID,
  user_id UUID,
  role ENUM('admin', 'member') DEFAULT 'member',
  joined_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (group_id, user_id),
  FOREIGN KEY (group_id) REFERENCES groups(group_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_user_groups ON group_members(user_id);
CREATE INDEX idx_group_members ON group_members(group_id);
```

## Cassandra Schemas

### Messages

```cql
-- One-on-one messages (conversation view)
CREATE TABLE messages (
  conversation_id UUID,      -- Hash of sorted(user1_id, user2_id)
  message_id TIMEUUID,       -- Time-based UUID for ordering
  sender_id UUID,
  recipient_id UUID,
  content TEXT,
  media_id UUID,
  message_type TEXT,         -- 'text', 'image', 'video', 'audio', 'document'
  status TEXT,               -- 'sent', 'delivered', 'read'
  created_at TIMESTAMP,
  PRIMARY KEY (conversation_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy'};

-- User's inbox (all messages for a user, including groups)
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

-- Group messages
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
```

Why TIMEUUID? It combines timestamp with uniqueness, providing natural time-based ordering without additional columns.

Why separate tables? Each table optimized for its access pattern:
- `messages`: Fetch conversation between two users
- `user_messages`: Fetch user's inbox across all conversations
- `group_messages`: Fetch group history

### Media Metadata

```cql
CREATE TABLE media (
  media_id UUID PRIMARY KEY,
  uploader_id UUID,
  file_type TEXT,            -- 'image/jpeg', 'video/mp4', etc.
  file_size BIGINT,
  s3_key TEXT,               -- Path in S3
  thumbnail_s3_key TEXT,
  encryption_key TEXT,       -- For E2EE
  uploaded_at TIMESTAMP,
  status TEXT                -- 'uploading', 'ready', 'deleted'
);

CREATE INDEX idx_media_uploader ON media(uploader_id);
```

## Redis Data Structures

### Presence

```
# Online status (auto-expiring)
Key: presence:user:{user_id}
Type: Hash
Fields:
  - status: "online" | "offline"
  - last_heartbeat: timestamp
  - device_type: "mobile" | "web" | "desktop"
  - server_id: "chat-server-42"
TTL: 60 seconds

# Last seen (persistent fallback)
Key: lastseen:user:{user_id}
Type: String
Value: timestamp
TTL: None
```

### Sessions

```
# User session
Key: session:{user_id}
Type: Hash
Fields:
  - auth_token: "jwt_token"
  - device_id: "uuid"
  - device_type: "mobile"
  - connected_server: "chat-server-42"
  - connected_at: timestamp
TTL: 30 days
```

### Caching

```
# Recent messages cache
Key: messages:{conversation_id}:recent
Type: List
Value: [message_json, message_json, ...]
TTL: 24 hours

# Group membership cache
Key: group:{group_id}:members
Type: Set
Members: [user_id1, user_id2, user_id3, ...]
TTL: 1 hour
```

### Typing Indicators

```
Key: typing:{conversation_id}:{user_id}
Type: String
Value: "1"
TTL: 10 seconds
```

## S3/Blob Storage Structure

```
whatsapp-media/
├── uploads/
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── {media_id}.jpg
│   │   │   ├── {media_id}_thumb.jpg
│   │   │   ├── {media_id}_compressed.jpg
│   │   ├── 02/
│   ├── 2023/
├── profile-pictures/
│   └── {user_id}.jpg
└── group-icons/
    └── {group_id}.jpg
```

## Elasticsearch Index

```json
{
  "messages": {
    "mappings": {
      "properties": {
        "message_id": {"type": "keyword"},
        "user_id": {"type": "keyword"},
        "conversation_id": {"type": "keyword"},
        "sender_id": {"type": "keyword"},
        "content": {
          "type": "text",
          "analyzer": "standard"
        },
        "created_at": {"type": "date"},
        "message_type": {"type": "keyword"}
      }
    }
  }
}
```

## Data Lifecycle

**Messages**:
- Store indefinitely in Cassandra
- Index in Elasticsearch for 90 days (then purge)
- Cache recent 10 messages per conversation in Redis

**Media**:
- S3 Standard for 30 days
- S3 IA for 30 days - 1 year
- S3 Glacier for > 1 year

**Presence**:
- Auto-expire after 60 seconds (Redis TTL)
- Persist last_seen separately

This polyglot approach optimizes each data type for its access patterns and cost requirements.
