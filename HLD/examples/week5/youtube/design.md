# YouTube System Design

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
1. **Video Upload**: Users can upload videos (up to 256 GB, 12 hours)
2. **Video Streaming**: Watch videos with adaptive quality
3. **Search**: Search for videos by title, description, tags
4. **Recommendations**: Personalized video recommendations
5. **Comments**: Users can comment on videos
6. **Likes/Dislikes**: Users can like or dislike videos
7. **Subscriptions**: Subscribe to channels for updates
8. **Playlists**: Create and manage playlists
9. **Live Streaming**: Real-time video broadcasting
10. **Notifications**: Notify subscribers of new videos

### Non-Functional Requirements
1. **Scalability**: Support 2 billion+ users
2. **Availability**: 99.9% uptime for streaming
3. **Consistency**: Eventual consistency acceptable
4. **Latency**: Video start time < 1 second
5. **Throughput**: 1 billion hours of video watched daily
6. **Storage**: Petabytes of video data
7. **Bandwidth**: Optimize for variable network speeds
8. **Reliability**: No data loss for uploaded videos
9. **Performance**: Handle 500 hours of video uploaded every minute

### Out of Scope (for this design)
- YouTube Premium/Ads system
- Content moderation (copyright detection)
- Analytics dashboard
- Mobile app specifics
- Monetization features

---

## Capacity Estimation

### Assumptions
- **Total Users**: 2.5 billion
- **Daily Active Users (DAU)**: 500 million (20% of total)
- **Videos watched per user per day**: 5 videos
- **Average video length**: 10 minutes
- **Average video size**: 50 MB (compressed)
- **Video upload rate**: 500 hours/minute = 30,000 hours/hour
- **Views to upload ratio**: 1000:1 (more views than uploads)

### Traffic Estimates

#### Video Views
```
Total views/day = 500M users × 5 videos = 2.5 billion views/day
Views per second = 2.5B / 86,400 ≈ 29,000 views/second
Peak (5x average): 145,000 views/second
```

#### Video Uploads
```
Upload rate = 500 hours/minute = 30,000 hours/hour
Assuming avg video = 10 min = 0.167 hours
Videos uploaded/hour = 30,000 / 0.167 ≈ 180,000 videos/hour
Videos uploaded/second = 50 videos/second
```

### Storage Estimates

#### Raw Video Storage (1 year)
```
Daily uploads = 500 hours/min × 60 min × 24 hours = 720,000 hours/day
Avg video size = 50 MB per minute
Daily storage = 720,000 hours × 60 min × 50 MB = 2.16 PB/day

Yearly storage = 2.16 PB/day × 365 = 788 PB/year
```

#### Multiple Formats (Transcoding)
YouTube stores each video in multiple formats:
- Original quality
- 4K (2160p)
- 1440p
- 1080p
- 720p
- 480p
- 360p
- 240p

Compression ratio varies, but average **3-5x storage multiplier**
```
Total storage with formats = 788 PB × 4 = 3.15 EB/year
```

#### Metadata Storage
```
Videos: 180K/hour × 24 × 365 = 1.58 billion videos/year
Metadata per video: 10 KB (title, description, tags, etc.)
Total metadata: 1.58B × 10 KB ≈ 15.8 TB/year (negligible)
```

#### Thumbnails
```
Thumbnails per video: 3 (different time points)
Thumbnail size: 200 KB
Total: 1.58B × 3 × 200 KB = 948 TB/year
```

### Bandwidth Estimates

#### Incoming (Upload)
```
Upload bandwidth = 50 videos/sec × 50 MB = 2.5 GB/sec = 20 Gbps
Peak (3x): 60 Gbps
```

#### Outgoing (Streaming)
```
Assume average bitrate: 2 Mbps (adaptive quality)
Concurrent viewers = 29,000 views/sec × 10 min avg watch time / 60
                   ≈ 4.8 million concurrent viewers

Streaming bandwidth = 4.8M × 2 Mbps = 9.6 Tbps (terabits per second!)
Peak (5x): 48 Tbps
```

**Note**: This is why CDNs are critical!

### Memory/Cache Estimates
```
Hot videos (80-20 rule): 20% of videos = 80% of views
Total videos: ~800 billion (estimated)
Hot videos: 160 billion

Cache metadata: 160B × 10 KB = 1.6 PB (distributed cache)
Cache thumbnails: 160B × 3 × 200 KB = 96 PB
Cache video chunks (first 10 seconds): 160B × 2 MB = 320 PB

Practical cache: 10-20 PB (most popular videos, distributed globally)
```

### Server Estimates
```
Upload servers (transcoding):
- Each server: 10 concurrent transcodings
- Need: 50 uploads/sec × 600 sec avg duration / 10 = 3,000 servers

Metadata servers:
- Each server: 10K requests/sec
- Peak reads: 145K views/sec × 2 requests (metadata + comments) = 290K req/sec
- Need: 290K / 10K = 29 servers (with redundancy: 100 servers)

API servers:
- Handles search, recommendations, user actions
- Need: 500-1000 servers
```

---

## High-Level Architecture

```
                                 ┌─────────────────────┐
                                 │    CloudFront CDN   │
                                 │  (Global Edge PoPs) │
                                 └──────────┬──────────┘
                                            │
┌──────────────┐                  ┌─────────▼──────────┐
│              │                  │                    │
│   Client     ├─────────────────►│   Load Balancer    │
│  (Browser/   │   HTTPS/QUIC     │   (API Gateway)    │
│   Mobile)    │                  │                    │
│              │                  └─────────┬──────────┘
└──────────────┘                            │
                                            │
                 ┌──────────────────────────┼──────────────────────────┐
                 │                          │                          │
                 ▼                          ▼                          ▼
        ┌────────────────┐        ┌────────────────┐        ┌────────────────┐
        │ Upload Service │        │ Stream Service │        │  API Service   │
        │  (Transcoding) │        │   (Playback)   │        │(Search/Reco)   │
        └───────┬────────┘        └───────┬────────┘        └───────┬────────┘
                │                         │                         │
                │                         │                         │
                ▼                         ▼                         ▼
        ┌────────────────┐        ┌────────────────┐        ┌────────────────┐
        │  Video Queue   │        │  Memcached/    │        │  Elasticsearch │
        │   (Kafka)      │        │     Redis      │        │   (Search)     │
        └───────┬────────┘        │   (Metadata)   │        └────────────────┘
                │                 └────────────────┘                 │
                │                                                    │
                ▼                                                    │
        ┌────────────────┐                                          │
        │   Transcoding  │                                          │
        │    Workers     │                                          │
        │   (FFmpeg)     │                                          │
        └───────┬────────┘                                          │
                │                                                    │
                ▼                                                    ▼
        ┌────────────────┐                                  ┌────────────────┐
        │   GCS/S3       │◄─────────────────────────────────│   MySQL/       │
        │ (Video Blobs)  │                                  │   Spanner      │
        │ Multiple       │                                  │  (Metadata)    │
        │ Formats        │                                  │                │
        └────────────────┘                                  └────────┬───────┘
                │                                                    │
                │                                                    ▼
                │                                            ┌────────────────┐
                │                                            │   BigTable     │
                │                                            │ (View counts,  │
                │                                            │  comments)     │
                │                                            └────────────────┘
                │
                ▼
        ┌────────────────┐
        │   CDN Origin   │
        │   (Regional)   │
        └────────────────┘
                │
                ▼
        ┌────────────────┐
        │  Global CDN    │
        │ (Akamai/CF)    │
        └────────────────┘


        ┌────────────────────────────────────────────┐
        │      Recommendation Engine                 │
        │   ┌──────────────────────────────────┐     │
        │   │  ML Models (TensorFlow)          │     │
        │   │  - Collaborative Filtering       │     │
        │   │  - Content-based Filtering       │     │
        │   │  - Deep Learning (Watch history) │     │
        │   └──────────────────────────────────┘     │
        └────────────────────────────────────────────┘
```

### Component Overview

1. **CDN (Content Delivery Network)**: Caches and serves video globally
2. **Load Balancer**: Distributes requests across services
3. **Upload Service**: Handles video uploads and initiates transcoding
4. **Transcoding Workers**: Convert videos to multiple formats
5. **Stream Service**: Serves video chunks for playback
6. **API Service**: Handles search, recommendations, user actions
7. **MySQL/Spanner**: Stores video metadata, users, channels
8. **BigTable**: Stores high-volume data (views, comments)
9. **Elasticsearch**: Powers video search
10. **Kafka**: Message queue for async processing
11. **Redis/Memcached**: Cache for hot data
12. **Blob Storage (GCS/S3)**: Stores video files
13. **Recommendation Engine**: ML-powered recommendations

---

## Component Design

### 1. Video Upload Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Video Upload Flow                            │
└─────────────────────────────────────────────────────────────────┘

Client                 Upload Service           Kafka           Transcoding Worker
  │                          │                    │                      │
  ├──1. Request upload URL──►│                    │                      │
  │                          ├──2. Generate ID────┤                      │
  │                          │   Store in DB      │                      │
  │                          │                    │                      │
  │◄─3. Return upload URL────┤                    │                      │
  │   (signed S3 URL)        │                    │                      │
  │                          │                    │                      │
  ├──4. Upload video chunks─────────────────►GCS/S3                      │
  │   (multipart upload)     │                    │                      │
  │                          │                    │                      │
  ├──5. Confirm upload───────►│                    │                      │
  │                          ├──6. Publish event──►│                      │
  │                          │                    │                      │
  │                          │                    ├──7. Consume event────►│
  │                          │                    │                      │
  │                          │                    │    8. Download video │
  │                          │                    │    9. Transcode:     │
  │                          │                    │       - 240p         │
  │                          │                    │       - 360p         │
  │                          │                    │       - 480p         │
  │                          │                    │       - 720p         │
  │                          │                    │       - 1080p        │
  │                          │                    │       - 1440p        │
  │                          │                    │       - 2160p (4K)   │
  │                          │                    │    10. Generate      │
  │                          │                    │        thumbnails    │
  │                          │                    │    11. Extract       │
  │                          │                    │        metadata      │
  │                          │                    │    12. Upload to GCS │
  │                          │                    │                      │
  │                          │◄───13. Update DB (video ready)────────────┤
  │                          │                    │                      │
  │◄─14. Notify user─────────┤                    │                      │
  │   (push notification)    │                    │                      │
```

**Upload Service Responsibilities**:
- Generate unique video ID (UUID)
- Create signed upload URL (S3 presigned URL)
- Store initial metadata in database
- Publish upload event to Kafka
- Handle upload status updates

**Transcoding Worker Responsibilities**:
- Download original video from blob storage
- Transcode to multiple resolutions using FFmpeg
- Generate adaptive bitrate streaming manifests (HLS/DASH)
- Create thumbnails (3-5 per video)
- Extract metadata (duration, resolution, codec)
- Upload all outputs to blob storage
- Update database with video status

**Optimizations**:
- **Parallel Transcoding**: Each resolution on separate worker
- **Chunked Processing**: Process video in chunks (parallel)
- **GPU Acceleration**: Use NVENC for faster encoding
- **Smart Defaults**: Auto-detect optimal bitrates
- **Progressive Upload**: Start transcoding while upload in progress

### 2. Video Streaming Service

**HLS (HTTP Live Streaming) Architecture**:
```
Original Video (1080p, 2 GB)
        │
        ├─ Segment into chunks (10 seconds each)
        │
        ├─ Chunk 1 (00:00-00:10)
        ├─ Chunk 2 (00:10-00:20)
        ├─ Chunk 3 (00:20-00:30)
        └─ ...

Each chunk transcoded to multiple qualities:
        ├─ 240p (0.5 Mbps)
        ├─ 360p (1 Mbps)
        ├─ 480p (1.5 Mbps)
        ├─ 720p (3 Mbps)
        ├─ 1080p (6 Mbps)
        └─ 1440p (12 Mbps)

Manifest file (playlist.m3u8):
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=426x240
240p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=640x360
360p/playlist.m3u8
...
```

**Playback Flow**:
```
Client                  Streaming Service         CDN                 Origin (GCS)
  │                            │                    │                      │
  ├──1. Request video──────────►│                    │                      │
  │   GET /watch?v=xyz         │                    │                      │
  │                            │                    │                      │
  │◄─2. Return player page─────┤                    │                      │
  │   (HTML + video player)    │                    │                      │
  │                            │                    │                      │
  ├──3. Request manifest───────┼────────────────────►│                      │
  │   GET /video/xyz/master.m3u8                    │                      │
  │                            │                    │                      │
  │                            │         ┌──────────┴──────────┐           │
  │                            │         │ Cache hit? Yes!     │           │
  │◄───4. Return manifest──────┼─────────┤ Return cached       │           │
  │                            │         └─────────────────────┘           │
  │                            │                    │                      │
  ├──5. Request chunk──────────┼────────────────────►│                      │
  │   GET /video/xyz/720p/chunk_001.ts              │                      │
  │                            │                    │                      │
  │                            │         ┌──────────┴──────────┐           │
  │                            │         │ Cache miss?         │           │
  │                            │         │ Fetch from origin───┼──────────►│
  │                            │         │                     │           │
  │                            │         │◄────────────────────┼───────────┤
  │◄───6. Stream chunk─────────┼─────────┤ Cache + Return      │           │
  │                            │         └─────────────────────┘           │
  │                            │                    │                      │
  ├──7. Request next chunk─────┼────────────────────►│                      │
  │   (adaptive bitrate switch)│                    │                      │
  │                            │                    │                      │
```

**Adaptive Bitrate Streaming (ABR)**:
- Client measures available bandwidth
- Switches between qualities dynamically
- Algorithm: Start low (360p) → measure → upgrade if possible
- Prevents buffering on slow connections

**CDN Strategy**:
- **Edge PoPs**: 200+ global locations
- **Cache Hit Ratio**: 95%+ (most views are repeat/popular videos)
- **Origin Shield**: Regional cache tier (reduce origin load)
- **Video Chunks**: Each chunk cached independently (efficient)

### 3. Recommendation Engine

```
┌────────────────────────────────────────────────────────────┐
│             Recommendation System Architecture             │
└────────────────────────────────────────────────────────────┘

User Activity          Data Pipeline         ML Models        Serving
     │                      │                    │              │
     │                      │                    │              │
┌────▼─────┐         ┌──────▼──────┐      ┌─────▼────┐   ┌────▼────┐
│  Watch   │         │   Kafka     │      │ Training │   │ Model   │
│  History │────────►│   Stream    │─────►│ Pipeline │──►│ Serving │
│          │         │             │      │(TensorFlow)   │ (gRPC)  │
└──────────┘         └─────────────┘      └──────────┘   └────┬────┘
                                                                │
┌───────────┐        ┌─────────────┐      ┌──────────┐         │
│  Likes    │        │  BigQuery   │      │ Feature  │         │
│  Comments │───────►│   (Data     │─────►│  Store   │         │
│  Shares   │        │  Warehouse) │      │          │         │
└───────────┘        └─────────────┘      └────┬─────┘         │
                                                │               │
┌───────────┐                                   │               │
│  Video    │                                   │               │
│  Metadata │───────────────────────────────────┘               │
│  (Tags,   │                                                   │
│  Category)│                                                   │
└───────────┘                                                   │
                                                                │
User Request ───────────────────────────────────────────────────┘
  │
  ├─ Get user_id
  ├─ Fetch user features (watch history, preferences)
  ├─ Call recommendation service (gRPC)
  ├─ Receive ranked video IDs
  └─ Fetch video metadata and return
```

**Recommendation Algorithms**:

1. **Collaborative Filtering**:
   - "Users who watched X also watched Y"
   - Matrix factorization (user-video interactions)
   - Pros: Discovers unexpected content
   - Cons: Cold start problem (new users/videos)

2. **Content-Based Filtering**:
   - Recommend similar videos (based on tags, category, title)
   - Pros: Works for new videos
   - Cons: Limited diversity

3. **Deep Learning (Neural Networks)**:
   - Input: User features (watch history, demographics, time of day)
   - Hidden layers: Learn complex patterns
   - Output: Probability scores for each video
   - Model: Two-tower architecture (user tower + video tower)

**Features Used**:
- **User Features**:
  - Watch history (last 100 videos)
  - Search history
  - Liked videos
  - Subscribed channels
  - Demographics (age, location)
  - Time of day, device type

- **Video Features**:
  - Title, description, tags
  - Category, upload date
  - View count, like ratio
  - Watch time (engagement)
  - Creator (channel)

**Ranking Factors**:
1. **Relevance**: How well video matches user interests (70%)
2. **Freshness**: Newer videos ranked higher (10%)
3. **Quality**: High engagement (watch time, likes) (10%)
4. **Diversity**: Avoid filter bubble (10%)

**Serving**:
- **Batch Scoring**: Pre-compute recommendations for all users (overnight)
- **Real-time Scoring**: Adjust based on recent activity
- **A/B Testing**: Multiple models running, compare metrics
- **Personalization**: Per-user recommendations

### 4. Search Service

```
┌────────────────────────────────────────────────────────────┐
│                 Search Architecture                        │
└────────────────────────────────────────────────────────────┘

Video Upload         Indexing Pipeline       Elasticsearch      Search API
     │                      │                      │                │
     │                      │                      │                │
┌────▼─────┐         ┌──────▼──────┐         ┌─────▼────┐    ┌────▼────┐
│  Video   │         │   Kafka     │         │  Index   │    │  Query  │
│ Metadata │────────►│  Stream     │────────►│  Update  │    │ Parser  │
│ Created  │         │             │         │          │    │         │
└──────────┘         └─────────────┘         └────┬─────┘    └────┬────┘
                                                   │               │
                                                   ▼               ▼
                                            ┌─────────────┐  ┌──────────┐
                                            │Elasticsearch│  │ Ranking  │
                                            │   Cluster   │◄─┤ & Scoring│
                                            │  (Sharded)  │  │          │
                                            └─────────────┘  └────┬─────┘
                                                                  │
                                                                  ▼
                                                            ┌──────────┐
                                                            │ Results  │
                                                            │  Return  │
                                                            └──────────┘
```

**Elasticsearch Schema**:
```json
{
  "video_id": "xyz123",
  "title": "How to design YouTube",
  "description": "System design interview question...",
  "tags": ["system design", "interview", "youtube"],
  "category": "Education",
  "channel_id": "abc789",
  "channel_name": "Tech Interviews",
  "upload_date": "2024-01-15",
  "view_count": 1000000,
  "like_count": 50000,
  "duration_seconds": 1800,
  "language": "en"
}
```

**Search Query**:
```json
GET /videos/_search
{
  "query": {
    "multi_match": {
      "query": "system design interview",
      "fields": [
        "title^3",           // 3x weight
        "description^2",     // 2x weight
        "tags^2",
        "channel_name"
      ],
      "type": "best_fields",
      "fuzziness": "AUTO"   // Handle typos
    }
  },
  "sort": [
    { "_score": "desc" },
    { "view_count": "desc" },
    { "upload_date": "desc" }
  ],
  "from": 0,
  "size": 20
}
```

**Ranking Factors**:
1. Text relevance (TF-IDF, BM25)
2. View count (popularity)
3. Upload date (freshness)
4. User engagement (CTR, watch time)
5. User personalization (search history)

**Optimizations**:
- **Auto-suggest**: Trie data structure for typeahead
- **Spell Check**: Did you mean "system design"?
- **Filters**: By duration, upload date, features (HD, CC)
- **Sharding**: Index sharded by language/region
- **Caching**: Cache popular search queries

### 5. View Count Aggregation

**Challenge**: Accurately count views for 2.5 billion views/day

**Naive Approach** (doesn't scale):
```sql
UPDATE videos SET view_count = view_count + 1 WHERE video_id = 'xyz';
```
Problem: 29,000 writes/second to same row!

**YouTube's Approach**: Approximate counting with batching

```
┌────────────────────────────────────────────────────────────┐
│              View Count Architecture                       │
└────────────────────────────────────────────────────────────┘

Video View Event      Kafka          Counter Service      BigTable
      │                 │                  │                  │
      │                 │                  │                  │
  ┌───▼───┐      ┌──────▼──────┐    ┌──────▼───────┐   ┌─────▼────┐
  │ View  │      │   Stream    │    │   Batch      │   │  Store   │
  │ Event │─────►│   Buffer    │───►│  Aggregator  │──►│  Counts  │
  │       │      │  (1 minute) │    │  (5 minutes) │   │          │
  └───────┘      └─────────────┘    └──────────────┘   └──────────┘
                                            │
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │  Update UI   │
                                    │  (every 5min)│
                                    └──────────────┘
```

**Implementation**:
1. **Stream Events**: Write view events to Kafka (low latency)
2. **Batch Aggregation**: Every 5 minutes, sum up views
3. **Update Database**: Increment view_count by aggregated amount
4. **Approximate Counts**: Display may be off by few minutes (acceptable!)

**BigTable Schema**:
```
Row Key: video_id#timestamp (hourly)
Column Family: stats
  - view_count: 1000
  - unique_viewers: 800
  - watch_time_seconds: 50000
```

**Daily Rollup**:
- Aggregate hourly counts into daily
- Store in data warehouse (BigQuery)
- Powers analytics dashboard

---

## Data Models

### 1. Video Metadata (MySQL/Spanner)

```sql
-- Videos table
CREATE TABLE videos (
  video_id VARCHAR(11) PRIMARY KEY,     -- YouTube's ID format
  channel_id VARCHAR(24) NOT NULL,
  title VARCHAR(100) NOT NULL,
  description TEXT,
  category_id INT,
  duration_seconds INT,
  upload_date TIMESTAMP DEFAULT NOW(),
  status ENUM('processing', 'ready', 'failed') DEFAULT 'processing',
  visibility ENUM('public', 'unlisted', 'private') DEFAULT 'public',
  view_count BIGINT DEFAULT 0,
  like_count INT DEFAULT 0,
  dislike_count INT DEFAULT 0,
  comment_count INT DEFAULT 0,
  thumbnail_url VARCHAR(255),
  INDEX idx_channel (channel_id),
  INDEX idx_upload_date (upload_date),
  INDEX idx_view_count (view_count)
);

-- Channels table
CREATE TABLE channels (
  channel_id VARCHAR(24) PRIMARY KEY,
  user_id BIGINT NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  subscriber_count BIGINT DEFAULT 0,
  total_views BIGINT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  INDEX idx_user (user_id),
  INDEX idx_subscribers (subscriber_count)
);

-- Users table
CREATE TABLE users (
  user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  hashed_password VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);

-- Video tags (many-to-many)
CREATE TABLE video_tags (
  video_id VARCHAR(11),
  tag VARCHAR(50),
  PRIMARY KEY (video_id, tag),
  INDEX idx_tag (tag)
);

-- Subscriptions
CREATE TABLE subscriptions (
  user_id BIGINT,
  channel_id VARCHAR(24),
  subscribed_at TIMESTAMP DEFAULT NOW(),
  notifications_enabled BOOLEAN DEFAULT TRUE,
  PRIMARY KEY (user_id, channel_id),
  INDEX idx_channel_subs (channel_id)
);
```

**Sharding Strategy**:
- Shard videos by `video_id` hash (distribute load)
- Shard users by `user_id` (query locality)
- Cross-shard queries via application logic or federation

### 2. Comments & Interactions (BigTable)

**Why BigTable/Cassandra?**
- High write throughput (millions of comments/day)
- Append-only workload
- Time-series data

```
-- Comments
Row Key: video_id#comment_id
Column Family: comment_data
  - user_id: <user_id>
  - text: "Great video!"
  - timestamp: 1699999999
  - like_count: 100
  - parent_comment_id: <id>  (for replies)

Row Key: user_id#comment_id
Column Family: user_comments
  - video_id: <video_id>
  - text: "Great video!"
  - timestamp: 1699999999

-- Likes (user -> video)
Row Key: user_id#video_id
Column Family: likes
  - liked_at: 1699999999

Row Key: video_id#user_id
Column Family: video_likes
  - liked_at: 1699999999

-- Watch history
Row Key: user_id#timestamp
Column Family: watches
  - video_id: <video_id>
  - watch_duration: 300  (seconds)
  - completion_rate: 0.75
```

### 3. Video Storage (GCS/S3)

**Blob Storage Structure**:
```
/videos/
  ├─ <video_id>/
      ├─ original/
      │   └─ video.mp4
      ├─ 240p/
      │   ├─ segment_001.ts
      │   ├─ segment_002.ts
      │   └─ playlist.m3u8
      ├─ 360p/
      │   ├─ segment_001.ts
      │   └─ playlist.m3u8
      ├─ 480p/
      ├─ 720p/
      ├─ 1080p/
      ├─ thumbnails/
      │   ├─ thumb1.jpg
      │   ├─ thumb2.jpg
      │   └─ thumb3.jpg
      └─ master.m3u8
```

**Metadata in Object Storage**:
```json
{
  "video_id": "xyz123",
  "formats": [
    {
      "resolution": "240p",
      "bitrate": "500kbps",
      "codec": "h264",
      "path": "s3://youtube-videos/xyz123/240p/"
    },
    ...
  ],
  "thumbnails": [
    "s3://youtube-videos/xyz123/thumbnails/thumb1.jpg"
  ]
}
```

---

## API Design

### REST APIs

#### 1. Upload Video
```http
POST /api/v1/videos/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

Request:
- title: "My Video"
- description: "..."
- category_id: 22
- tags: ["tech", "tutorial"]
- visibility: "public"
- video_file: <binary>

Response: 202 Accepted
{
  "video_id": "xyz123",
  "status": "processing",
  "upload_url": "https://upload.youtube.com/xyz123"
}
```

#### 2. Get Video Details
```http
GET /api/v1/videos/{video_id}

Response: 200 OK
{
  "video_id": "xyz123",
  "title": "How to design YouTube",
  "description": "...",
  "channel": {
    "channel_id": "abc789",
    "name": "Tech Interviews",
    "subscriber_count": 1000000
  },
  "statistics": {
    "view_count": 1000000,
    "like_count": 50000,
    "comment_count": 500
  },
  "streaming_url": "https://streaming.youtube.com/xyz123/master.m3u8",
  "thumbnails": {
    "default": "https://i.ytimg.com/vi/xyz123/default.jpg",
    "high": "https://i.ytimg.com/vi/xyz123/hqdefault.jpg"
  },
  "duration": 1800,
  "upload_date": "2024-01-15T10:00:00Z"
}
```

#### 3. Search Videos
```http
GET /api/v1/search?q=system+design&page=1&per_page=20

Response: 200 OK
{
  "results": [
    {
      "video_id": "xyz123",
      "title": "How to design YouTube",
      "channel_name": "Tech Interviews",
      "view_count": 1000000,
      "thumbnail": "...",
      "duration": 1800
    }
  ],
  "total_results": 50000,
  "page": 1,
  "per_page": 20
}
```

#### 4. Get Recommendations
```http
GET /api/v1/recommendations?user_id={user_id}&count=20

Response: 200 OK
{
  "recommendations": [
    {
      "video_id": "abc456",
      "title": "...",
      "score": 0.95
    }
  ]
}
```

#### 5. Like Video
```http
POST /api/v1/videos/{video_id}/like
Authorization: Bearer {token}

Response: 200 OK
{
  "status": "liked",
  "like_count": 50001
}
```

#### 6. Post Comment
```http
POST /api/v1/videos/{video_id}/comments
Authorization: Bearer {token}
Content-Type: application/json

Request:
{
  "text": "Great video!",
  "parent_comment_id": null
}

Response: 201 Created
{
  "comment_id": "comment123",
  "text": "Great video!",
  "user": {...},
  "timestamp": "2024-01-15T10:00:00Z",
  "like_count": 0
}
```

#### 7. Subscribe to Channel
```http
POST /api/v1/channels/{channel_id}/subscribe
Authorization: Bearer {token}

Response: 200 OK
{
  "status": "subscribed",
  "subscriber_count": 1000001
}
```

### Streaming APIs

#### HLS Manifest Request
```http
GET /streaming/v1/videos/{video_id}/master.m3u8

Response: 200 OK
Content-Type: application/vnd.apple.mpegurl

#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=426x240
240p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=640x360
360p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=1500000,RESOLUTION=854x480
480p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=3000000,RESOLUTION=1280x720
720p/playlist.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=6000000,RESOLUTION=1920x1080
1080p/playlist.m3u8
```

#### Segment Request
```http
GET /streaming/v1/videos/{video_id}/720p/segment_001.ts

Response: 200 OK
Content-Type: video/MP2T
Content-Length: 2097152
Cache-Control: public, max-age=31536000

<binary video data>
```

---

## Scalability

### 1. Database Scaling

#### Read/Write Split
```
             ┌──────────────┐
             │   Master DB  │  (Writes)
             └──────┬───────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
  ┌─────────┐ ┌─────────┐ ┌─────────┐
  │Replica 1│ │Replica 2│ │Replica 3│  (Reads)
  └─────────┘ └─────────┘ └─────────┘
```

**Read Replicas**:
- Video metadata reads: 95% read, 5% write
- Use 10+ read replicas per master
- Route reads to nearest replica (latency)
- Eventually consistent (acceptable)

#### Sharding (Horizontal Partitioning)
```
Shard 1: video_id starting with 0-3
Shard 2: video_id starting with 4-7
Shard 3: video_id starting with 8-b
Shard 4: video_id starting with c-f

Hash(video_id) % num_shards = shard_id
```

**Sharding Benefits**:
- Distribute load across servers
- Linear scalability (add more shards)
- Isolated failures (shard 1 down ≠ shard 2 down)

**Challenges**:
- Cross-shard queries (trending videos)
- Resharding (changing num_shards)

### 2. Caching Strategy

**Multi-Layer Cache**:
```
Client (Browser)
     │
     ├─ Browser Cache (5 minutes)
     │
     ▼
CDN (Edge PoP)
     │
     ├─ CDN Cache (24 hours)
     │
     ▼
Regional Cache (Origin Shield)
     │
     ├─ Regional Cache (1 hour)
     │
     ▼
Application Cache (Redis/Memcached)
     │
     ├─ Video Metadata (15 minutes)
     ├─ User Session (30 minutes)
     ├─ Recommendations (5 minutes)
     │
     ▼
Database
```

**Cache Invalidation**:
- **TTL-based**: Most common (eventual consistency OK)
- **Event-driven**: Invalidate on video update (complexity)
- **Versioning**: Include version in cache key

**Cache Warming**:
- Pre-populate cache with popular videos
- Avoid thundering herd on cache expiration

### 3. CDN Scaling

**Global CDN Strategy**:
- 200+ Edge PoPs worldwide
- 95%+ cache hit ratio
- Origin shield reduces origin load

**CDN Configuration**:
```
Cache-Control: public, max-age=31536000, immutable
```
Video segments are immutable → cache forever!

**Bandwidth Savings**:
- Without CDN: 48 Tbps from origin (impossible!)
- With CDN: 2.4 Tbps from origin (95% cache hit)
- Cost savings: Massive (CDN cheaper than origin bandwidth)

### 4. Transcoding Scaling

**Distributed Transcoding**:
- 3,000+ transcoding workers
- Each video: 7 formats × 10 min avg = 70 min of transcoding
- Parallelization: All formats simultaneously = 10 min wall time

**Priority Queue**:
1. High priority: Popular creators, live streams
2. Medium priority: Regular uploads
3. Low priority: Re-transcodes, quality improvements

**GPU Acceleration**:
- NVIDIA NVENC for H.264 encoding (10x faster)
- Reduces transcoding time from 1x to 0.1x video length

### 5. Live Streaming Scaling

**Challenges**:
- Real-time transcoding (< 2 seconds latency)
- Millions of concurrent viewers
- Global distribution

**Architecture**:
```
Streamer → Ingest Server → Transcoding → CDN → Viewers
           (WebRTC)         (Real-time)   (HLS/DASH)
```

**Low Latency Protocols**:
- WebRTC: < 500ms latency (peer-to-peer)
- LL-HLS (Low Latency HLS): 2-3 seconds
- Standard HLS: 10-30 seconds

---

## Potential Bottlenecks

### 1. Upload Bottleneck

**Problem**: 500 hours/minute = massive upload bandwidth

**Current**: 50 videos/sec × 50 MB = 2.5 GB/sec = 20 Gbps

**Solutions**:
1. **Geographic Distribution**: Upload to nearest datacenter
2. **Resumable Uploads**: Handle network interruptions
3. **Client-side Compression**: Reduce upload size
4. **Multipart Upload**: Parallel upload of chunks
5. **Throttling**: Limit concurrent uploads per user

### 2. Hot Video Bottleneck

**Problem**: Viral video → millions of views in minutes

**Example**: New music video release
- Expected views: 10M in first hour
- Concurrent viewers: 1M+
- Bandwidth: 1M × 2 Mbps = 2 Tbps

**Solutions**:
1. **CDN**: Absolutely critical (cache at edge)
2. **Pre-warming**: Notify CDN of expected hot videos
3. **Origin Shield**: Additional cache tier
4. **Overflow Capacity**: Auto-scale origin servers

### 3. Recommendation Latency

**Problem**: ML inference for recommendations is slow

**Current**: 200ms for model inference
**Target**: < 50ms API latency

**Solutions**:
1. **Pre-computation**: Batch compute recommendations overnight
2. **Cache Results**: Store recommendations per user (Redis)
3. **Approximate Nearest Neighbors**: Fast similarity search
4. **Model Simplification**: Trade accuracy for speed
5. **GPU Inference**: Faster than CPU for neural networks

### 4. Search Index Update Lag

**Problem**: New videos not immediately searchable

**Current**: 5-10 minute indexing lag
**User expectation**: Immediate searchability

**Solutions**:
1. **Near Real-time Indexing**: Kafka → Elasticsearch (1 min)
2. **Prioritize New Videos**: Index hot videos first
3. **Incremental Updates**: Don't reindex entire document
4. **Bulk API**: Batch index updates (more efficient)

### 5. Database Hotspots

**Problem**: Popular videos → many writes to same row

**Example**:
- Video view count update
- 100K views/sec on viral video
- Single row write bottleneck

**Solutions**:
1. **Eventual Consistency**: Batch updates (5 min)
2. **Separate Hot Tables**: Move view counts to BigTable
3. **Sharding**: Even with sharding, hot rows exist
4. **Optimistic Locking**: Allow concurrent updates

### 6. Transcoding Queue Backlog

**Problem**: Upload spike → transcoding queue grows

**During Events** (e.g., elections, sports):
- Upload rate: 3x normal = 150 videos/sec
- Transcoding capacity: 100 videos/sec
- Queue backlog: 50 videos/sec accumulation

**Solutions**:
1. **Auto-scaling**: Add workers when queue > threshold
2. **Priority Queue**: Process popular creators first
3. **Degraded Mode**: Skip 4K transcoding if backlog high
4. **Resource Reservation**: Reserve capacity for events

### 7. Comment Spam

**Problem**: Bots posting millions of spam comments

**Scale**: 1M spam comments/hour

**Solutions**:
1. **Rate Limiting**: Max 10 comments/min per user
2. **CAPTCHA**: For suspicious activity
3. **ML Spam Detection**: Auto-flag spam comments
4. **Shadow Banning**: Hide spam without notification
5. **User Reporting**: Crowdsource spam detection

### 8. DDoS Attacks

**Problem**: Distributed Denial of Service attack

**Attack Vector**: Request expensive operations (search, recommendations)

**Solutions**:
1. **Rate Limiting**: Per IP, per user
2. **CDN Protection**: DDoS mitigation at edge
3. **Web Application Firewall (WAF)**: Block malicious patterns
4. **Geo-blocking**: Block regions during attack
5. **Graceful Degradation**: Disable non-critical features

### 9. Storage Cost Explosion

**Problem**: 3.15 EB/year storage growth is expensive

**Current Cost** (AWS S3 pricing):
- 3.15 EB × $0.023/GB = $72M/year (S3 Standard)
- Plus bandwidth: $0.09/GB egress

**Solutions**:
1. **Tiered Storage**:
   - Hot (30 days): S3 Standard
   - Warm (1 year): S3 IA (Infrequent Access)
   - Cold (archive): Glacier ($0.004/GB)
2. **Delete Old Videos**: Remove videos with <100 views after 2 years
3. **Compression**: Better codecs (VP9, AV1)
4. **Deduplication**: Same video uploaded multiple times

### 10. Metadata Database Growth

**Problem**: Billions of videos → large database

**Current**: 100B videos × 10 KB = 1 PB metadata

**Solutions**:
1. **Archiving**: Move old video metadata to cold storage
2. **Sharding**: Distribute across shards
3. **Denormalization**: Duplicate data to avoid joins
4. **Indexing**: Careful index design (storage overhead)

---

## Additional Considerations

### 1. Copyright Detection

**Content ID System**:
- Fingerprint all uploaded videos
- Match against copyright database
- Auto-flag matches for manual review
- Monetization sharing with copyright owners

**Technology**:
- Perceptual hashing
- Audio fingerprinting
- Video fingerprinting (scene detection)

### 2. Content Moderation

**Challenges**:
- 500 hours uploaded/minute = impossible to manually review
- Illegal content (terrorism, CSAM)
- Misinformation, hate speech

**Solutions**:
1. **ML Classification**: Auto-flag suspicious content
2. **User Reporting**: Crowdsource moderation
3. **Human Review**: Final decision by moderators
4. **Age Restriction**: Limit certain content
5. **Demonetization**: Remove ads from inappropriate content

### 3. Monetization (Ads)

**Ad Insertion**:
- Pre-roll (before video)
- Mid-roll (during video, for 8+ min videos)
- Post-roll (after video)

**Targeting**:
- User demographics
- Video content
- Search keywords
- Watch history

**Technology**:
- VAST (Video Ad Serving Template)
- Server-side ad insertion (SSAI) vs client-side

### 4. Analytics

**Creator Analytics**:
- Views over time
- Traffic sources
- Audience demographics
- Engagement (likes, comments, shares)
- Revenue

**Platform Analytics**:
- Total views
- Popular videos, trending
- User growth
- Storage/bandwidth usage

**Technology**:
- BigQuery: Data warehouse
- Dataflow: Batch processing
- Dashboards: Looker, Grafana

---

## Summary

YouTube is one of the most complex systems ever built:

**Key Design Decisions**:
1. **CDN is Critical**: 95% cache hit ratio saves massive bandwidth
2. **Asynchronous Processing**: Upload → transcode → publish pipeline
3. **Multiple Storage Tiers**: Hot/warm/cold for cost optimization
4. **Eventual Consistency**: Accept for view counts, recommendations
5. **Adaptive Streaming**: HLS/DASH for varying network conditions
6. **ML-Powered**: Recommendations, search, moderation

**Scale Numbers**:
- 2.5 billion users
- 500 hours uploaded every minute
- 1 billion hours watched daily
- 48 Tbps peak bandwidth (with CDN)
- 3.15 EB storage added yearly

**Technology Stack**:
- **Storage**: GCS/S3 (blob), MySQL/Spanner (metadata), BigTable (analytics)
- **Caching**: Redis, Memcached, CDN (multi-layer)
- **Streaming**: HLS, DASH (adaptive bitrate)
- **Transcoding**: FFmpeg, NVENC (GPU acceleration)
- **Search**: Elasticsearch
- **ML**: TensorFlow (recommendations)
- **Infrastructure**: Kubernetes, Docker

This design showcases how to build a globally distributed, highly scalable video platform!
