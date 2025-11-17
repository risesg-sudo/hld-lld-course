# WhatsApp: Overview and Requirements

## What Are We Designing?

WhatsApp is a real-time messaging platform that enables billions of users to exchange messages, media, and calls globally. At its core, it solves the fundamental problem of instant, reliable communication across different devices and network conditions. The system must handle message delivery with millisecond latency while maintaining consistency and ensuring no message is lost.

The challenge is not just sending messages between two users. The real complexity emerges when considering:
- How do we maintain real-time connections for 100 million concurrent users?
- How do we ensure message ordering when network delays vary?
- How do we deliver messages to offline users when they come online?
- How do we scale group messaging where a single message fans out to hundreds of recipients?

## Functional Requirements

### Core Messaging Features

**One-on-One Messaging**
Users can send text messages directly to each other. This forms the foundation of the platform and must be optimized for speed and reliability.

**Group Messaging**
Users can create groups and broadcast messages to multiple participants. This introduces the fan-out problem: a single message must be delivered to N recipients, potentially creating N writes to storage.

**Media Sharing**
Support for images, videos, documents, and audio files. Media files require different handling than text due to their size. We cannot store 500KB images in the same way we store 100-byte text messages.

**Online Status and Last Seen**
Show when users are online or when they were last active. This seems simple but creates significant load: millions of status changes per minute that must be broadcast to user contacts.

**Message Status Indicators**
Track message lifecycle: sent, delivered, read. Each status change requires updates and notifications to the sender.

**Push Notifications**
Notify offline users of new messages. When a user is not connected, we must queue notifications and deliver them through platform-specific services (FCM for Android, APNS for iOS).

**Multi-Device Support**
Access messages from multiple devices simultaneously. This complicates message synchronization - all devices must stay in sync without conflicts.

### Out of Scope

For this design exercise, we will not cover:
- End-to-end encryption implementation details (Signal Protocol)
- Payment features (WhatsApp Pay)
- Business API and enterprise features
- Status/Stories feature
- Voice and video calls infrastructure

## Non-Functional Requirements

### Scale Requirements

**User Base**
- Total users: 2 billion globally
- Daily active users: 1 billion (50% of total)
- Concurrent connections at peak: 100 million

Why does this matter? Each concurrent connection consumes system resources. Managing 100 million WebSocket connections requires careful resource planning and horizontal scaling.

### Performance Requirements

**Low Latency**
Messages must be delivered in under 100 milliseconds. Users expect instant delivery - any delay is noticeable and degrades the experience.

Why 100ms? Human perception of "instant" is roughly 100-200ms. Beyond this, users notice lag.

**High Availability**
Target: 99.99% uptime (52 minutes downtime per year).

Why this target? Messaging is critical infrastructure. People rely on it for emergency communication, business coordination, and daily life. Downtime directly impacts billions of users.

**Messages Per Second**
- Average: 580,000 messages/second
- Peak: 1.74 million messages/second (3x average during peak hours)

### Reliability Requirements

**No Message Loss**
Every message must be persisted and delivered. Once a sender receives confirmation, the message must not be lost even if systems fail.

How do we guarantee this? Write-ahead logs, replication, and acknowledgment protocols ensure durability.

**Message Ordering**
Messages must be delivered in the order they were sent (within a conversation). Out-of-order delivery confuses conversations and breaks user expectations.

**Exactly-Once Delivery**
Each message should be delivered exactly once, not duplicated. Duplicate messages annoy users and can cause confusion.

### Efficiency Requirements

**Mobile Network Optimization**
The system must work well on slow 2G/3G networks common in developing markets. This means:
- Minimal data transfer per message
- Efficient compression
- Smart batching of operations
- Offline capability with sync when connected

**Real-Time Delivery**
When both users are online, delivery should be instant. The system should maintain persistent connections rather than polling, which wastes bandwidth.

## Why These Requirements Matter

The requirements shape our architectural decisions:

**High concurrency** drives us toward stateless services with distributed state management.

**Low latency** pushes us to use WebSockets over HTTP polling and to cache aggressively.

**Mobile optimization** influences our choice of protocols and data formats.

**No message loss** requires robust persistence and replication strategies.

Each requirement creates constraints that guide our design choices in the architecture phase.
