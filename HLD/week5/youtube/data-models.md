# YouTube: Data Models

## Database Selection

**Spanner** (globally distributed SQL): Video metadata, channels, users
**BigTable** (NoSQL): View counts, comments (high write volume)
**Elasticsearch**: Video search
**GCS/S3**: Video files (blob storage)

## Spanner Schemas

```sql
CREATE TABLE videos (
  video_id STRING(11) PRIMARY KEY,
  channel_id STRING(24) NOT NULL,
  title STRING(100) NOT NULL,
  description STRING(5000),
  category_id INT64,
  duration_seconds INT64,
  upload_date TIMESTAMP NOT NULL,
  status STRING(20),  -- 'processing', 'ready', 'failed'
  visibility STRING(20),  -- 'public', 'unlisted', 'private'
  view_count INT64 DEFAULT 0,
  like_count INT64 DEFAULT 0,
  INDEX idx_channel (channel_id),
  INDEX idx_upload_date (upload_date DESC)
);

CREATE TABLE channels (
  channel_id STRING(24) PRIMARY KEY,
  user_id INT64 NOT NULL,
  name STRING(100) NOT NULL,
  description STRING(5000),
  subscriber_count INT64 DEFAULT 0,
  total_views INT64 DEFAULT 0,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE subscriptions (
  user_id INT64,
  channel_id STRING(24),
  subscribed_at TIMESTAMP NOT NULL,
  notifications_enabled BOOL DEFAULT TRUE,
  PRIMARY KEY (user_id, channel_id)
);
```

## BigTable Schemas

```
-- View counts (time-series aggregation)
Row Key: video_id#timestamp_hour
Column Family: stats
  - view_count: 1000
  - unique_viewers: 800
  - watch_time_seconds: 50000
  
-- Comments (high write volume)
Row Key: video_id#comment_id
Column Family: comment_data
  - user_id: <id>
  - text: "Great video!"
  - timestamp: 1699999999
  - like_count: 100
```

## Storage Structure (GCS)

```
youtube-videos/
├── {video_id}/
│   ├── original.mp4
│   ├── 240p/
│   │   ├── segment_001.ts
│   │   ├── segment_002.ts
│   │   └── playlist.m3u8
│   ├── 360p/
│   ├── 720p/
│   ├── 1080p/
│   ├── thumbnails/
│   │   ├── thumb1.jpg
│   │   ├── thumb2.jpg
│   │   └── thumb3.jpg
│   └── master.m3u8
```
