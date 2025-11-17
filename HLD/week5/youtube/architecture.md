# YouTube: High-Level Architecture

## Architectural Principles

**Separate upload from streaming**: These are different workloads with different requirements.

**Asynchronous processing**: Accept uploads fast, transcode in background.

**CDN-first design**: Origin servers are fallback, not primary serving path.

**Microservices approach**: Upload, transcoding, streaming, recommendations, search all separate.

## System Components

```
┌────────────┐
│   Client   │
└──────┬─────┘
       │
       ▼
┌──────────────────┐
│  Load Balancer   │
└────────┬─────────┘
         │
    ┌────┴────┬──────────┬────────────┐
    ▼         ▼          ▼            ▼
┌────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
│Upload  │ │Stream  │ │Search   │ │Recommend │
│Service │ │Service │ │Service  │ │Service   │
└───┬────┘ └───┬────┘ └────┬────┘ └────┬─────┘
    │          │           │          │
    ▼          ▼           ▼          ▼
┌────────────────────────────────────────┐
│            Kafka Event Bus             │
└─────┬──────────────────────┬───────────┘
      │                      │
      ▼                      ▼
┌──────────────┐      ┌─────────────┐
│ Transcoding  │      │   CDN       │
│  Workers     │      │  (Global)   │
└──────┬───────┘      └──────┬──────┘
       │                     │
       ▼                     ▼
┌──────────────┐      ┌─────────────┐
│  GCS/S3      │      │ Caches      │
│  (Video      │      │ (Edge PoPs) │
│   Blobs)     │      │             │
└──────────────┘      └─────────────┘
       │
       ▼
┌──────────────────────┐
│  Metadata DBs        │
│  - Spanner (Videos)  │
│  - BigTable (Views)  │
│  - Elasticsearch     │
└──────────────────────┘
```

## Component Roles

**Upload Service**: Handle video uploads, generate pre-signed URLs, queue transcoding jobs.

**Transcoding Workers**: Convert videos to multiple formats, generate thumbnails, extract metadata.

**Stream Service**: Serve HLS/DASH manifests, route to CDN.

**CDN**: Cache and serve video segments globally. 95%+ hit rate.

**Search Service**: Index and query videos using Elasticsearch.

**Recommendation Service**: ML models suggesting personalized videos.

## Why This Architecture

**Upload/Stream separation**: Uploads are write-heavy, streaming is read-heavy. Different scaling needs.

**Kafka for orchestration**: Decouples upload from transcoding. Upload confirms fast, transcoding happens async.

**Object storage for videos**: Designed for large files, durable, cheap.

**CDN is primary path**: Edge serving reduces latency and origin load dramatically.

**Polyglot persistence**: Each database optimized for its use case (Spanner for metadata, BigTable for counters, Elasticsearch for search).
