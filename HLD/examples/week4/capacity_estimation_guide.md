# Capacity Estimation Guide - Step-by-Step Calculations

This guide provides detailed capacity estimation calculations for popular systems. Learn how to estimate QPS, storage, bandwidth, and memory requirements.

## Table of Contents
1. [Essential Numbers](#essential-numbers)
2. [Estimation Framework](#estimation-framework)
3. [Twitter-like System](#twitter-like-system)
4. [Instagram-like System](#instagram-like-system)
5. [YouTube-like System](#youtube-like-system)
6. [URL Shortener](#url-shortener)
7. [WhatsApp-like System](#whatsapp-like-system)
8. [Practice Problems](#practice-problems)

---

## Essential Numbers

### Power of 10
```
1 Thousand   = 10^3     = 1,000
1 Million    = 10^6     = 1,000,000
1 Billion    = 10^9     = 1,000,000,000
1 Trillion   = 10^12    = 1,000,000,000,000
```

### Storage Units
```
1 Byte       = 8 bits
1 KB         = 1,000 bytes        = 10^3 bytes
1 MB         = 1,000 KB           = 10^6 bytes
1 GB         = 1,000 MB           = 10^9 bytes
1 TB         = 1,000 GB           = 10^12 bytes
1 PB         = 1,000 TB           = 10^15 bytes
```

### Time Units
```
1 minute     = 60 seconds
1 hour       = 3,600 seconds      ≈ 3.6 × 10^3 seconds
1 day        = 86,400 seconds     ≈ 10^5 seconds (100K)
1 week       = 604,800 seconds    ≈ 6 × 10^5 seconds
1 month      = 2,592,000 seconds  ≈ 2.5 × 10^6 seconds (2.5M)
1 year       = 31,536,000 seconds ≈ 3 × 10^7 seconds (30M)
```

### Typical Data Sizes
```
Character (ASCII)        = 1 byte
Character (Unicode)      = 2-4 bytes
Integer                  = 4 bytes
Long                     = 8 bytes
Timestamp                = 8 bytes
UUID                     = 16 bytes

Tweet text               = 280 chars = ~300 bytes
Short URL                = 7 chars = ~10 bytes
Profile picture          = 200 KB
Photo (Instagram)        = 500 KB - 2 MB
HD Video (1 min)         = 50-100 MB
4K Video (1 min)         = 300-500 MB
```

### Latency Numbers
```
L1 cache reference                 0.5 ns
L2 cache reference                 7 ns
Main memory reference              100 ns
SSD random read                    150 μs
Disk seek                          10 ms
Read 1 MB from SSD                 1 ms
Read 1 MB from disk                20 ms
Send packet CA to Netherlands      150 ms
```

---

## Estimation Framework

### Step-by-Step Process

#### 1. Clarify Requirements
- Ask about scale (users, traffic)
- Understand read/write ratio
- Data retention period
- Geographic distribution

#### 2. Make Assumptions
- Daily Active Users (DAU)
- Monthly Active Users (MAU)
- User behavior patterns
- Growth rate

#### 3. Calculate Traffic
```
QPS = Total Operations per Day / 86,400
Peak QPS = Average QPS × Peak Factor (2-3x)
```

#### 4. Calculate Storage
```
Daily Storage = Operations/Day × Size per Operation
Yearly Storage = Daily Storage × 365
Total Storage = Yearly Storage × Retention Years
Storage with Replication = Total Storage × Replication Factor
```

#### 5. Calculate Bandwidth
```
Ingress (Write) = Write QPS × Average Request Size
Egress (Read) = Read QPS × Average Response Size
```

#### 6. Calculate Memory (Cache)
```
Cache = 20% of Daily Reads × Size per Read (80/20 rule)
```

---

## Twitter-like System

Design a Twitter clone that can handle millions of users posting and reading tweets.

### Requirements Clarification
- Users can post tweets (text + optional media)
- Users can follow others
- Users can view their timeline
- Users can like and retweet

### Assumptions
```
Total Users: 1 Billion
Daily Active Users (DAU): 500 Million
Tweets per user per day: 2 (average)
Timeline reads per user per day: 50
Follow ratio: 200 following on average

Tweet composition:
- Text: 280 characters max ≈ 300 bytes
- Metadata (ID, user_id, timestamp, etc.): 200 bytes
- Total per tweet: 500 bytes

Media:
- 20% of tweets have images
- Average image size: 500 KB
- 5% of tweets have videos
- Average video size: 5 MB
```

### 1. Traffic Estimation

#### Write Traffic (Tweets)
```
Tweets per day = 500M DAU × 2 tweets/user
               = 1 Billion tweets/day

Write QPS = 1B / 86,400
          ≈ 11,600 requests/second

Peak Write QPS = 11,600 × 3
               = 34,800 requests/second
```

#### Read Traffic (Timeline)
```
Timeline views per day = 500M DAU × 50 views/user
                       = 25 Billion views/day

Read QPS = 25B / 86,400
         ≈ 289,000 requests/second

Peak Read QPS = 289,000 × 3
              = 867,000 requests/second
```

**Read:Write Ratio = 25:1** (Read-heavy system)

### 2. Storage Estimation

#### Text Storage
```
Daily tweets = 1B
Size per tweet = 500 bytes

Daily storage = 1B × 500 bytes
              = 500 GB/day

Yearly storage = 500 GB × 365
               = 182.5 TB/year

5-year storage = 182.5 TB × 5
               = 912.5 TB
               ≈ 1 PB
```

#### Image Storage
```
Images per day = 1B tweets × 20%
               = 200M images

Daily image storage = 200M × 500 KB
                    = 100 TB/day

Yearly storage = 100 TB × 365
               = 36,500 TB/year
               = 36.5 PB/year

5-year storage = 36.5 PB × 5
               = 182.5 PB
```

#### Video Storage
```
Videos per day = 1B tweets × 5%
               = 50M videos

Daily video storage = 50M × 5 MB
                    = 250 TB/day

Yearly storage = 250 TB × 365
               = 91,250 TB/year
               = 91.25 PB/year

5-year storage = 91.25 PB × 5
               = 456.25 PB
```

#### Total Storage (5 years)
```
Text:   1 PB
Images: 182.5 PB
Videos: 456.25 PB
--------------------
Total:  640 PB (raw)

With 3x replication = 640 PB × 3 = 1,920 PB ≈ 2 Exabytes
```

### 3. Bandwidth Estimation

#### Ingress (Write Bandwidth)
```
Text:
  11,600 QPS × 500 bytes = 5.8 MB/s

Images (20% of tweets):
  2,320 QPS × 500 KB = 1,160 MB/s ≈ 1.16 GB/s

Videos (5% of tweets):
  580 QPS × 5 MB = 2,900 MB/s ≈ 2.9 GB/s

Total Ingress ≈ 4 GB/s
Peak Ingress ≈ 12 GB/s
```

#### Egress (Read Bandwidth)
```
Text:
  289,000 QPS × 500 bytes = 144.5 MB/s

Images (assuming 20% of timeline has images):
  57,800 QPS × 500 KB = 28,900 MB/s ≈ 29 GB/s

Videos (assuming 5% of timeline has videos):
  14,450 QPS × 5 MB = 72,250 MB/s ≈ 72 GB/s

Total Egress ≈ 101 GB/s
Peak Egress ≈ 303 GB/s
```

### 4. Memory (Cache) Estimation

```
Using 80/20 rule: 20% of tweets generate 80% of traffic

Daily read data = 25B reads × 500 bytes
                = 12.5 TB

Cache 20% = 12.5 TB × 0.2
          = 2.5 TB

Add user data cache = 500 MB
Add metadata cache = 500 MB

Total cache needed ≈ 3 TB
```

### Summary - Twitter

| Metric | Value |
|--------|-------|
| Write QPS | 11,600 (peak: 34,800) |
| Read QPS | 289,000 (peak: 867,000) |
| Storage (5 years) | 640 PB (raw), 2 EB (with replication) |
| Ingress Bandwidth | 4 GB/s (peak: 12 GB/s) |
| Egress Bandwidth | 101 GB/s (peak: 303 GB/s) |
| Cache | 3 TB |

---

## Instagram-like System

Design an Instagram clone for photo sharing.

### Assumptions
```
Total Users: 2 Billion
Daily Active Users (DAU): 800 Million
Photos posted per user per day: 0.5 (1 photo every 2 days)
Feed views per user per day: 30
Average photo size: 1 MB
Photos per feed view: 20

User data:
- Profile info: 1 KB
- Photo metadata: 500 bytes
```

### 1. Traffic Estimation

#### Write Traffic (Upload Photos)
```
Photos per day = 800M × 0.5
               = 400M photos/day

Write QPS = 400M / 86,400
          ≈ 4,630 requests/second

Peak Write QPS = 4,630 × 3
               = 13,890 requests/second
```

#### Read Traffic (View Feed)
```
Feed views per day = 800M × 30
                   = 24B views/day

Photo views per day = 24B × 20 photos/view
                    = 480B photo views/day

Read QPS = 480B / 86,400
         ≈ 5,555,000 requests/second

Peak Read QPS = 5,555,000 × 3
              ≈ 16,665,000 requests/second
```

**Read:Write Ratio = 1200:1** (Extremely read-heavy)

### 2. Storage Estimation

#### Photo Storage
```
Daily photos = 400M
Size per photo = 1 MB

Daily storage = 400M × 1 MB
              = 400 TB/day

Yearly storage = 400 TB × 365
               = 146,000 TB/year
               = 146 PB/year

5-year storage = 146 PB × 5
               = 730 PB
```

#### Thumbnail Storage
```
Thumbnails per photo = 3 (small, medium, large)
Average thumbnail size = 50 KB

Daily thumbnails = 400M photos × 3 × 50 KB
                 = 60 TB/day

Yearly storage = 60 TB × 365
               = 21,900 TB/year
               ≈ 22 PB/year

5-year storage = 22 PB × 5
               = 110 PB
```

#### Metadata Storage
```
Photos over 5 years = 400M × 365 × 5
                    = 730B photos

Metadata per photo = 500 bytes

Total metadata = 730B × 500 bytes
               = 365 TB
```

#### Total Storage (5 years)
```
Photos:     730 PB
Thumbnails: 110 PB
Metadata:   0.365 TB ≈ 0 PB
--------------------------
Total:      840 PB (raw)

With 3x replication = 840 PB × 3 = 2,520 PB ≈ 2.5 Exabytes
```

### 3. Bandwidth Estimation

#### Ingress (Upload)
```
Photos: 4,630 QPS × 1 MB = 4,630 MB/s ≈ 4.6 GB/s
Peak Ingress ≈ 14 GB/s
```

#### Egress (View)
```
Original photos: 555,000 QPS × 1 MB = 555 GB/s
Thumbnails: 5,000,000 QPS × 50 KB = 250 GB/s

Total Egress ≈ 805 GB/s
Peak Egress ≈ 2,415 GB/s ≈ 2.4 TB/s
```

### 4. Memory (Cache) Estimation

```
Hot photos (20% of daily views):
  480B views × 0.2 = 96B views
  Assuming 100M unique photos
  100M × 1 MB = 100 TB

Thumbnail cache:
  Hot thumbnails: 50 TB

Metadata cache:
  100M photos × 500 bytes = 50 GB

Total cache ≈ 150 TB
```

### Summary - Instagram

| Metric | Value |
|--------|-------|
| Write QPS | 4,630 (peak: 13,890) |
| Read QPS | 5,555,000 (peak: 16,665,000) |
| Storage (5 years) | 840 PB (raw), 2.5 EB (with replication) |
| Ingress Bandwidth | 4.6 GB/s (peak: 14 GB/s) |
| Egress Bandwidth | 805 GB/s (peak: 2.4 TB/s) |
| Cache | 150 TB |

---

## YouTube-like System

Design a YouTube clone for video streaming.

### Assumptions
```
Total Users: 2.5 Billion
Daily Active Users (DAU): 1 Billion
Videos uploaded per day: 500,000 (by creators)
Video views per user per day: 5
Average video length: 5 minutes
Average video size: 500 MB (original)

Video quality variants:
- 4K (2160p): 500 MB (5 min)
- 1080p: 200 MB
- 720p: 100 MB
- 480p: 50 MB
- 360p: 25 MB

Viewing distribution:
- 5% watch in 4K
- 20% watch in 1080p
- 30% watch in 720p
- 30% watch in 480p
- 15% watch in 360p

Average watched = (0.05×500 + 0.2×200 + 0.3×100 + 0.3×50 + 0.15×25)
                = 25 + 40 + 30 + 15 + 3.75
                = 113.75 MB per view
```

### 1. Traffic Estimation

#### Write Traffic (Upload)
```
Videos per day = 500,000

Upload QPS = 500,000 / 86,400
           ≈ 5.8 requests/second

(Low QPS, but high data volume)
```

#### Read Traffic (Streaming)
```
Views per day = 1B users × 5 views
              = 5B views/day

View QPS = 5B / 86,400
         ≈ 57,870 concurrent streams

Peak View QPS = 57,870 × 3
              ≈ 173,610 concurrent streams
```

### 2. Storage Estimation

#### Original Videos
```
Daily uploads = 500,000 videos
Size per video = 500 MB

Daily storage = 500,000 × 500 MB
              = 250 TB/day

Yearly storage = 250 TB × 365
               = 91,250 TB/year
               ≈ 91 PB/year

5-year storage = 91 PB × 5
               = 455 PB
```

#### Transcoded Videos (All Qualities)
```
Storage per video across all qualities:
  4K: 500 MB
  1080p: 200 MB
  720p: 100 MB
  480p: 50 MB
  360p: 25 MB
  Total: 875 MB per video

Daily storage = 500,000 × 875 MB
              = 437.5 TB/day

Yearly storage = 437.5 TB × 365
               = 159,687.5 TB/year
               ≈ 160 PB/year

5-year storage = 160 PB × 5
               = 800 PB
```

#### Metadata
```
Videos over 5 years = 500,000 × 365 × 5
                    = 912.5M videos

Metadata per video = 2 KB (title, description, tags, etc.)

Total metadata = 912.5M × 2 KB
               = 1.825 TB
               ≈ 2 TB
```

#### Total Storage (5 years)
```
Transcoded videos: 800 PB
Metadata: 2 TB ≈ 0 PB
-------------------------
Total: 800 PB (raw)

With 2x replication = 800 PB × 2 = 1,600 PB = 1.6 Exabytes
```

### 3. Bandwidth Estimation

#### Ingress (Upload)
```
Upload: 5.8 QPS × 500 MB = 2,900 MB/s ≈ 2.9 GB/s
```

#### Egress (Streaming)
```
For 5-minute videos streamed over 5 minutes:
Average bitrate = 113.75 MB / 300 seconds
                = 379 KB/s per stream

Total egress = 57,870 streams × 379 KB/s
             = 21.9 GB/s

Peak egress = 21.9 GB/s × 3
            = 65.7 GB/s
```

### 4. Memory (Cache) Estimation

```
Hot videos (20% of views):
  5B views × 0.2 = 1B views
  Assuming 10M unique videos
  10M × 100 MB (720p average) = 1 PB

But we use CDN for video delivery, so:
  Metadata cache: 10M videos × 2 KB = 20 GB
  Thumbnail cache: 10M × 100 KB = 1 TB

Application cache ≈ 2 TB
CDN cache ≈ 1 PB (distributed globally)
```

### Summary - YouTube

| Metric | Value |
|--------|-------|
| Upload QPS | 5.8 (low, but high volume) |
| Streaming QPS | 57,870 (peak: 173,610) concurrent streams |
| Storage (5 years) | 800 PB (raw), 1.6 EB (with replication) |
| Ingress Bandwidth | 2.9 GB/s |
| Egress Bandwidth | 21.9 GB/s (peak: 65.7 GB/s) |
| App Cache | 2 TB |
| CDN Cache | 1 PB (distributed) |

---

## URL Shortener

Design a URL shortening service like bit.ly.

### Assumptions
```
Daily Active Users: 100 Million
URLs shortened per user per month: 0.1 (most are readers)
URL shortening requests per day = 100M × 0.1 / 30 ≈ 333,000

URL clicks per day: 10× shortening = 3.3M clicks/day
URL length: 100 characters average
Short code length: 7 characters
Retention: 10 years
```

### 1. Traffic Estimation

#### Write (Shorten URL)
```
Shortening requests = 333,000/day
Write QPS = 333,000 / 86,400
          ≈ 3.85 requests/second

Peak Write QPS ≈ 12 requests/second
```

#### Read (Redirect)
```
Click requests = 3.3M/day
Read QPS = 3.3M / 86,400
         ≈ 38 requests/second

Peak Read QPS ≈ 114 requests/second
```

**Read:Write Ratio = 10:1**

### 2. Storage Estimation

#### URL Mappings
```
Daily URLs = 333,000

Storage per URL:
  - Short code: 7 bytes
  - Original URL: 100 bytes
  - Created timestamp: 8 bytes
  - User ID: 8 bytes
  - Metadata: 20 bytes
  Total: 143 bytes ≈ 150 bytes

Daily storage = 333,000 × 150 bytes
              = 50 MB/day

Yearly storage = 50 MB × 365
               = 18.25 GB/year

10-year storage = 18.25 GB × 10
                = 182.5 GB

Total URLs in 10 years = 333,000 × 365 × 10
                        ≈ 1.2 Billion URLs
```

#### Analytics Data (Optional)
```
Click events = 3.3M/day

Storage per click:
  - Short code: 7 bytes
  - Timestamp: 8 bytes
  - IP address: 4 bytes
  - User agent hash: 4 bytes
  - Referrer hash: 4 bytes
  Total: 27 bytes ≈ 30 bytes

Daily analytics = 3.3M × 30 bytes
                = 99 MB/day

Yearly analytics = 99 MB × 365
                 = 36.135 GB/year

10-year analytics = 36.135 GB × 10
                  = 361.35 GB
```

#### Total Storage
```
URL mappings: 182.5 GB
Analytics: 361.35 GB
-----------------------------
Total: 544 GB ≈ 0.5 TB

With replication (3x) = 1.5 TB
```

### 3. Bandwidth Estimation

#### Ingress
```
Write: 3.85 QPS × 150 bytes = 578 bytes/s ≈ 0.6 KB/s
(Negligible)
```

#### Egress
```
Read: 38 QPS × 150 bytes = 5.7 KB/s
(Negligible - just metadata, actual redirect is HTTP 302)
```

### 4. Memory (Cache)

```
Using 80/20 rule:
  Hot URLs = 20% of daily clicks
  Cache size = 3.3M × 0.2 × 150 bytes
             = 99 MB ≈ 100 MB

Add metadata and indexes ≈ 1 GB total cache
```

### Summary - URL Shortener

| Metric | Value |
|--------|-------|
| Write QPS | 3.85 (peak: 12) |
| Read QPS | 38 (peak: 114) |
| Storage (10 years) | 544 GB (raw), 1.5 TB (with replication) |
| Bandwidth | Negligible (< 1 MB/s) |
| Cache | 1 GB |

---

## WhatsApp-like System

Design a messaging system like WhatsApp.

### Assumptions
```
Daily Active Users (DAU): 2 Billion
Messages per user per day: 50
Average message size: 100 bytes
Media messages: 10% (photos/videos)
Average media size: 500 KB
Group chat ratio: 30% of messages
Average group size: 10 members
```

### 1. Traffic Estimation

#### Write Traffic (Send Message)
```
Messages per day = 2B × 50
                 = 100B messages/day

Write QPS = 100B / 86,400
          ≈ 1,157,000 messages/second

Peak Write QPS = 1,157,000 × 3
               ≈ 3,471,000 messages/second
```

#### Read Traffic (Receive Message)
```
1-to-1 messages (70%): 70B messages → 70B deliveries
Group messages (30%): 30B messages × 10 members → 300B deliveries

Total deliveries = 70B + 300B = 370B/day

Read QPS = 370B / 86,400
         ≈ 4,282,000 messages/second

Peak Read QPS ≈ 12,846,000 messages/second
```

### 2. Storage Estimation

#### Text Messages
```
Text messages = 100B × 90% = 90B messages/day
Size per message = 100 bytes

Daily storage = 90B × 100 bytes
              = 9 TB/day

Yearly storage = 9 TB × 365
               = 3,285 TB/year
               ≈ 3.3 PB/year

5-year storage = 3.3 PB × 5
               = 16.5 PB
```

#### Media Messages
```
Media messages = 100B × 10% = 10B messages/day
Size per media = 500 KB

Daily storage = 10B × 500 KB
              = 5 PB/day

Yearly storage = 5 PB × 365
               = 1,825 PB/year

5-year storage = 1,825 PB × 5
               = 9,125 PB ≈ 9 Exabytes
```

#### Metadata
```
Metadata per message = 50 bytes (IDs, timestamps, status)

Daily metadata = 100B × 50 bytes
               = 5 TB/day

5-year metadata = 5 TB × 365 × 5
                = 9,125 TB
                ≈ 9 PB
```

#### Total Storage (5 years)
```
Text: 16.5 PB
Media: 9 EB (9,000 PB)
Metadata: 9 PB
---------------------------
Total: 9,025.5 PB ≈ 9 Exabytes (raw)

With 2x replication = 18 Exabytes
```

### 3. Bandwidth Estimation

#### Ingress
```
Text: 1,157,000 QPS × 100 bytes = 115.7 MB/s
Media: 115,700 QPS × 500 KB = 57.85 GB/s

Total Ingress ≈ 58 GB/s
Peak Ingress ≈ 174 GB/s
```

#### Egress
```
Text: 4,282,000 QPS × 100 bytes = 428.2 MB/s
Media: 428,200 QPS × 500 KB = 214.1 GB/s

Total Egress ≈ 214.5 GB/s
Peak Egress ≈ 643.5 GB/s
```

### 4. Memory (Cache)

```
Recent messages cache (24 hours):
  100B messages × 100 bytes = 10 TB

User presence/status:
  2B users × 50 bytes = 100 GB

Connection state:
  2B connections × 100 bytes = 200 GB

Total cache ≈ 10.3 TB
```

### Summary - WhatsApp

| Metric | Value |
|--------|-------|
| Write QPS | 1,157,000 (peak: 3,471,000) |
| Read QPS | 4,282,000 (peak: 12,846,000) |
| Storage (5 years) | 9 EB (raw), 18 EB (with replication) |
| Ingress Bandwidth | 58 GB/s (peak: 174 GB/s) |
| Egress Bandwidth | 214.5 GB/s (peak: 643.5 GB/s) |
| Cache | 10.3 TB |

---

## Practice Problems

### Problem 1: Design TikTok
**Requirements:**
- 1.5B DAU
- 10 video views per user per day
- 1% of users create videos (1 video per day)
- Average video: 30 seconds, 50 MB
- Retention: 3 years

**Calculate:**
1. Upload QPS and download QPS
2. Storage requirements
3. Bandwidth requirements
4. Cache requirements

### Problem 2: Design Uber
**Requirements:**
- 100M DAU
- 5 rides per user per month
- Location updates every 5 seconds while in ride
- Average ride duration: 20 minutes
- Store location history for 2 years

**Calculate:**
1. Location update QPS
2. Storage for location data
3. Bandwidth requirements

### Problem 3: Design Spotify
**Requirements:**
- 500M DAU
- 3 hours of music per user per day
- Average song: 4 minutes, 5 MB
- 100M total songs in catalog
- Retention: Forever

**Calculate:**
1. Streaming QPS
2. Storage for music catalog
3. Bandwidth requirements
4. CDN cache requirements

### Problem 4: Design Google Drive
**Requirements:**
- 2B users (100M DAU)
- Average storage per user: 15 GB
- Daily uploads per active user: 10 files
- Average file size: 2 MB
- Retention: Forever

**Calculate:**
1. Upload/download QPS
2. Total storage requirements
3. Bandwidth requirements

### Problem 5: Design Netflix
**Requirements:**
- 250M subscribers (50M concurrent viewers at peak)
- Average viewing: 2 hours per day
- Video qualities: 4K (25 GB/hr), 1080p (3 GB/hr), 720p (1 GB/hr)
- Distribution: 10% 4K, 40% 1080p, 50% 720p
- Retention: Forever

**Calculate:**
1. Concurrent streaming capacity
2. Storage for content library (100K titles, 100 hours each)
3. Bandwidth requirements
4. CDN requirements

---

## Tips for Interviews

1. **Always start with clarifying questions**
   - Don't assume numbers
   - Ask about scale
   - Understand read/write patterns

2. **Round numbers for easier math**
   - 86,400 seconds → 10^5 (100K)
   - 31.5M seconds → 3 × 10^7 (30M)

3. **Show your work**
   - Write down formulas
   - Explain each step
   - Make calculations visible

4. **State assumptions clearly**
   - "Assuming 100M DAU..."
   - "If we store data for 5 years..."

5. **Think about peak vs average**
   - Peak can be 2-3x average
   - Plan for peak capacity

6. **Don't forget replication**
   - At least 3x for critical data
   - 2x for less critical

7. **Consider 80/20 rule for caching**
   - 20% of data serves 80% of requests
   - Cache hot data

8. **Use proper units**
   - Convert MB → GB → TB → PB as needed
   - Show unit conversions

9. **Sanity check your numbers**
   - Does 1 PB/day make sense?
   - Compare with known systems

10. **Discuss tradeoffs**
    - Storage vs compute
    - Consistency vs availability
    - Cost vs performance

---

## Quick Reference Table

| System | DAU | Write QPS | Read QPS | Storage (5y) | Bandwidth |
|--------|-----|-----------|----------|--------------|-----------|
| Twitter | 500M | 11.6K | 289K | 640 PB | In: 4 GB/s, Out: 101 GB/s |
| Instagram | 800M | 4.6K | 5.5M | 840 PB | In: 4.6 GB/s, Out: 805 GB/s |
| YouTube | 1B | 5.8 | 57.8K streams | 800 PB | In: 2.9 GB/s, Out: 21.9 GB/s |
| WhatsApp | 2B | 1.15M | 4.28M | 9 EB | In: 58 GB/s, Out: 214.5 GB/s |
| URL Short | 100M | 3.85 | 38 | 544 GB | Negligible |

---

**Remember:** These are approximations. Real systems have many more variables. The goal is to demonstrate systematic thinking and ability to estimate at scale.
