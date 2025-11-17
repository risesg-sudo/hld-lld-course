# YouTube: Overview and Requirements

## What Are We Designing?

YouTube is a global video platform serving over 1 billion hours of video daily to 2.5 billion users. The core challenge is not just storing videos - it's transcoding them into multiple formats, distributing them globally with minimal latency, and personalizing recommendations for billions of users.

## The Scale Challenge

Consider what happens when someone uploads a 10-minute video:
- Must transcode to 7 different resolutions (240p through 4K)
- Each resolution has multiple bitrates for adaptive streaming
- Must generate thumbnails and extract metadata
- Must distribute to hundreds of edge locations globally
- Must make searchable and recommendable within minutes

This happens 500 hours of video every minute. The system must handle this reliably while maintaining low latency for viewers.

## Functional Requirements

**Video Upload**: Users can upload videos up to 256 GB and 12 hours in length. The system must handle unreliable networks and support resumable uploads.

**Video Streaming**: Watch videos with adaptive quality based on network conditions. Quality should switch seamlessly without buffering.

**Search**: Find videos by title, description, tags, or content. Results must be relevant and personalized.

**Recommendations**: Suggest videos based on watch history and preferences. This drives 70% of watch time.

**Engagement**: Like, comment, subscribe to channels, create playlists. These social signals feed back into recommendations.

**Live Streaming**: Real-time video broadcasting with minimal delay to viewers worldwide.

## Non-Functional Requirements

**Scale**: 
- 500 million daily active users
- 2.5 billion video views per day  
- 500 hours of video uploaded per minute

**Performance**:
- Video start time under 1 second
- Smooth playback without buffering
- Search results in under 200ms

**Availability**: 99.9% uptime for streaming (45 minutes downtime per month acceptable)

**Storage**: Petabytes of video data, growing by multiple petabytes daily

**Bandwidth**: 48 Tbps peak bandwidth with CDN (impossible to serve from origin)

## Why These Requirements Are Challenging

**Transcoding bottleneck**: Each video needs hours of CPU time to transcode all formats. With 50 videos/second uploaded, we need massive parallel processing.

**Storage explosion**: Storing each video in 7 formats multiplies storage by 4-5x. Combined with indefinite retention, this creates exabyte-scale storage needs.

**Global distribution**: Serving 48 Tbps from origin servers is impossible. CDN with 95%+ cache hit rate is not optional, it's essential for feasibility.

**Personalization at scale**: Computing recommendations for 2.5 billion users with billions of videos requires sophisticated machine learning infrastructure.

**Real-time nature**: Users expect uploaded videos to be watchable within minutes, not hours. This requires fast transcoding pipelines.

