# Network Protocol Comparison Chart

Comprehensive comparison of network protocols for system design decisions.

---

## 1. Transport Layer Protocols

### TCP vs UDP

| Feature | TCP | UDP |
|---------|-----|-----|
| **Connection Type** | Connection-oriented | Connectionless |
| **Reliability** | Guaranteed delivery | No guarantee |
| **Ordering** | In-order delivery | No ordering |
| **Speed** | Slower (overhead) | Faster (minimal overhead) |
| **Header Size** | 20-60 bytes | 8 bytes |
| **Flow Control** | Yes | No |
| **Congestion Control** | Yes | No |
| **Error Checking** | Extensive | Basic checksum |
| **Use Cases** | Web, Email, File Transfer | Gaming, Streaming, DNS |
| **Examples** | HTTP, FTP, SMTP | Video calls, Live streaming |

**Visual Comparison:**

```
TCP: [Handshake] ──→ [Data] ──→ [ACK] ──→ [Data] ──→ [ACK] ──→ [Close]
     (Reliable, ordered, but slower)

UDP: [Data] ──→ [Data] ──→ [Data] ──→
     (Fast, but no guarantees)
```

**When to Choose:**

- **Choose TCP when:**
  - Data integrity is critical
  - Order matters
  - Reliability > Speed
  - Examples: Banking, File downloads, Databases

- **Choose UDP when:**
  - Speed > Reliability
  - Can tolerate packet loss
  - Real-time is critical
  - Examples: Video streaming, Online gaming, VoIP

---

## 2. Application Layer Protocols

### HTTP/1.1 vs HTTP/2 vs HTTP/3

| Feature | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---------|----------|--------|--------|
| **Year** | 1997 | 2015 | 2022 |
| **Transport** | TCP | TCP | QUIC (UDP) |
| **Multiplexing** | No (6 connections) | Yes (single connection) | Yes (improved) |
| **Header Compression** | No | Yes (HPACK) | Yes (QPACK) |
| **Server Push** | No | Yes | Yes |
| **Binary Protocol** | No (Text) | Yes | Yes |
| **Head-of-Line Blocking** | Yes | Stream level | No |
| **Connection Setup** | ~3 RTT | ~3 RTT | ~1 RTT |
| **Encryption** | Optional (HTTPS) | Optional | Required |

**HTTP/1.1 - Sequential Requests:**
```
Request 1 ─────────────────────→ Response 1
              Request 2 ─────────────────────→ Response 2
                           Request 3 ─────────────────────→ Response 3
(Must wait for previous request to complete)
```

**HTTP/2 - Multiplexing:**
```
Request 1 ──┐
Request 2 ──┼──→ [Single Connection] ──┬──→ Response 1
Request 3 ──┘                           ├──→ Response 2
                                         └──→ Response 3
(Parallel requests on one connection)
```

**HTTP/3 - QUIC (UDP-based):**
```
Request 1 ──┐
Request 2 ──┼──→ [QUIC/UDP] ──┬──→ Response 1
Request 3 ──┘                  ├──→ Response 2
                                └──→ Response 3
(Faster connection, no head-of-line blocking)
```

---

### HTTP vs HTTPS

| Feature | HTTP | HTTPS |
|---------|------|-------|
| **Port** | 80 | 443 |
| **Security** | No encryption | TLS/SSL encryption |
| **Certificate** | Not required | Required |
| **Speed** | Faster | Slightly slower (encryption overhead) |
| **SEO** | Lower ranking | Higher ranking |
| **Trust** | Low | High (padlock icon) |
| **Man-in-Middle** | Vulnerable | Protected |
| **Use Case** | Local dev, Public info | Production, Sensitive data |

**HTTPS Handshake:**
```
Client                                    Server
  │                                          │
  │──── 1. ClientHello ────────────────────→│
  │                                          │
  │←─── 2. ServerHello + Certificate ───────│
  │                                          │
  │──── 3. Key Exchange ───────────────────→│
  │                                          │
  │←─── 4. Finished ────────────────────────│
  │                                          │
  │     [Encrypted Communication]            │
```

---

## 3. Real-Time Communication Protocols

### WebSockets vs SSE vs Long Polling

| Feature | WebSockets | SSE | Long Polling |
|---------|------------|-----|--------------|
| **Direction** | Bi-directional | Server → Client | Bi-directional |
| **Protocol** | WS/WSS | HTTP/HTTPS | HTTP/HTTPS |
| **Connection** | Persistent | Persistent | Request per update |
| **Browser Support** | Excellent | Good (no IE) | Universal |
| **Reconnection** | Manual | Automatic | Automatic |
| **Data Format** | Binary or Text | Text only | Any |
| **Overhead** | Low | Medium | High |
| **Complexity** | High | Low | Medium |
| **Max Connections** | Server limit | ~6 per domain | Many |
| **Use Case** | Chat, Gaming | Feeds, Notifications | Fallback |

**WebSocket Flow:**
```
Client                                Server
  │                                     │
  │──── HTTP Upgrade Request ─────────→│
  │←─── 101 Switching Protocols ───────│
  │                                     │
  │←───────── Persistent WS ──────────→│
  │   (Both can send anytime)           │
```

**SSE Flow:**
```
Client                                Server
  │                                     │
  │──── HTTP GET /events ─────────────→│
  │                                     │
  │←─── event: message ─────────────────│
  │←─── data: {...} ────────────────────│
  │←─── (continuous stream) ────────────│
```

**Long Polling Flow:**
```
Client                                Server
  │                                     │
  │──── Request ──────────────────────→│
  │     (waits for data)                │
  │←─── Response (when available) ─────│
  │                                     │
  │──── New Request ──────────────────→│
  │     (immediately)                   │
```

**Decision Tree:**

```
Need bidirectional?
├─ YES → WebSocket
└─ NO
    │
    Need real-time updates?
    ├─ YES
    │   │
    │   Need IE support?
    │   ├─ YES → Long Polling
    │   └─ NO → SSE
    │
    └─ NO → Regular HTTP
```

---

## 4. RPC Protocols

### REST vs gRPC vs GraphQL

| Feature | REST | gRPC | GraphQL |
|---------|------|------|---------|
| **Architecture** | Resource-based | RPC | Query language |
| **Protocol** | HTTP/1.1 | HTTP/2 | HTTP/1.1+ |
| **Format** | JSON (usually) | Protobuf | JSON |
| **Endpoints** | Multiple | Multiple | Single |
| **Schema** | OpenAPI (optional) | .proto (required) | Schema (required) |
| **Typing** | Weak | Strong | Strong |
| **Streaming** | No (native) | Yes (4 types) | Subscriptions |
| **Caching** | Excellent | Complex | Complex |
| **Browser** | Native | gRPC-Web needed | Native |
| **Learning Curve** | Easy | Medium | Medium |
| **Payload Size** | Large | Small | Medium |
| **Performance** | Good | Excellent | Good |

**REST - Multiple Endpoints:**
```
GET  /api/users/1
GET  /api/users/1/posts
GET  /api/posts/101/comments
```

**gRPC - Typed Service Calls:**
```protobuf
service UserService {
  rpc GetUser(UserRequest) returns (UserResponse);
  rpc ListPosts(stream PostRequest) returns (stream Post);
}
```

**GraphQL - Single Endpoint:**
```graphql
POST /graphql
{
  user(id: 1) {
    name
    posts {
      title
      comments { text }
    }
  }
}
```

**Performance Comparison:**

```
Scenario: Get user with posts and comments

REST:
  Requests: 5+
  Data Size: 10 KB
  Time: 500ms

gRPC:
  Requests: 1
  Data Size: 2 KB
  Time: 100ms

GraphQL:
  Requests: 1
  Data Size: 4 KB
  Time: 200ms
```

---

## 5. Messaging Protocols

### Message Queue Protocols

| Protocol | Use Case | Transport | Guarantee |
|----------|----------|-----------|-----------|
| **AMQP** | Enterprise messaging | TCP | At-least-once |
| **MQTT** | IoT, sensors | TCP | QoS levels 0-2 |
| **STOMP** | Simple messaging | TCP/WebSocket | Depends |
| **Kafka Protocol** | Event streaming | TCP | Configurable |

**AMQP (Advanced Message Queuing Protocol):**
- Used by: RabbitMQ
- Features: Routing, queuing, reliability
- Use: Enterprise systems, microservices

**MQTT (Message Queuing Telemetry Transport):**
- Used by: IoT devices
- Features: Lightweight, pub/sub
- Use: Sensors, mobile apps

**Kafka Protocol:**
- Used by: Apache Kafka
- Features: High throughput, persistence
- Use: Event streaming, log aggregation

---

## 6. Database Protocols

| Protocol | Database Type | Port | Use Case |
|----------|---------------|------|----------|
| **MySQL Protocol** | Relational | 3306 | General purpose |
| **PostgreSQL Protocol** | Relational | 5432 | Complex queries |
| **MongoDB Wire Protocol** | Document | 27017 | Flexible schema |
| **Redis Protocol (RESP)** | Key-Value | 6379 | Caching, sessions |
| **Cassandra Protocol (CQL)** | Wide-column | 9042 | High availability |

---

## 7. Streaming Protocols

### Video/Audio Streaming

| Protocol | Type | Transport | Latency | Use Case |
|----------|------|-----------|---------|----------|
| **RTMP** | Live streaming | TCP | ~5s | Twitch, YouTube Live |
| **HLS** | Adaptive | HTTP | 10-30s | Apple devices |
| **DASH** | Adaptive | HTTP | 10-30s | Cross-platform |
| **WebRTC** | Peer-to-peer | UDP (SRTP) | <1s | Video calls |
| **RTSP** | Control | TCP/UDP | Low | IP cameras |

**Latency Comparison:**
```
WebRTC:  ████░░░░░░░░░░░░░░░░ (<1s)
RTMP:    ████████░░░░░░░░░░░░ (~5s)
HLS:     ████████████████████ (10-30s)
```

---

## 8. Protocol Selection Matrix

### By Use Case

| Use Case | Recommended Protocol | Alternative |
|----------|---------------------|-------------|
| **Web API** | REST or GraphQL | gRPC |
| **Real-time Chat** | WebSocket | SSE (simple) |
| **Notifications** | SSE or WebSocket | Long Polling |
| **Microservices** | gRPC | REST |
| **File Download** | HTTP/HTTPS | FTP |
| **Video Streaming** | HLS or DASH | RTMP |
| **Video Call** | WebRTC | - |
| **IoT Data** | MQTT or UDP | HTTP |
| **Gaming** | UDP | WebSocket |
| **Message Queue** | AMQP or Kafka | MQTT |

### By Requirement

| Requirement | Protocol Choice |
|-------------|----------------|
| **Low latency required** | UDP, WebSocket, WebRTC |
| **Reliability required** | TCP, AMQP, Kafka |
| **Browser compatibility** | HTTP, WebSocket, SSE |
| **Bandwidth constrained** | gRPC, MQTT, UDP |
| **Binary data** | WebSocket, gRPC, MQTT |
| **Request-response** | HTTP, gRPC, REST |
| **Publish-subscribe** | MQTT, Kafka, SSE |
| **Streaming** | gRPC, WebSocket, WebRTC |

---

## 9. Performance Metrics

### Protocol Overhead Comparison

| Protocol | Header Size | Connection Setup | Serialization |
|----------|-------------|------------------|---------------|
| **HTTP/1.1** | ~500-800 bytes | 3-way handshake | JSON/XML |
| **HTTP/2** | ~50 bytes (compressed) | 3-way handshake | Binary |
| **HTTP/3** | ~50 bytes | 0-RTT | Binary |
| **WebSocket** | 2-14 bytes | Upgrade handshake | Any |
| **gRPC** | ~30 bytes | HTTP/2 setup | Protobuf |
| **UDP** | 8 bytes | None | Any |
| **TCP** | 20-60 bytes | 3-way handshake | Any |

**Bandwidth Usage (1000 messages):**
```
Protocol      Bandwidth
HTTP/1.1:     ███████████████████████░░ 500 KB
HTTP/2:       ████████████░░░░░░░░░░░░░ 250 KB
gRPC:         ██████░░░░░░░░░░░░░░░░░░░ 120 KB
WebSocket:    ████████░░░░░░░░░░░░░░░░░ 150 KB
```

---

## 10. Security Comparison

| Protocol | Encryption | Authentication | Authorization |
|----------|------------|----------------|---------------|
| **HTTP** | No | No | Application-level |
| **HTTPS** | TLS/SSL | Certificate | Application-level |
| **WebSocket (WS)** | No | Application-level | Application-level |
| **WebSocket (WSS)** | TLS/SSL | Application-level | Application-level |
| **gRPC** | TLS (recommended) | Token-based | Token-based |
| **MQTT** | TLS (optional) | Username/password | Topic-based |
| **AMQP** | TLS/SSL | SASL | Queue-based |

---

## 11. Scalability Comparison

| Protocol | Horizontal Scaling | Load Balancing | State |
|----------|-------------------|----------------|-------|
| **HTTP** | Excellent | Round-robin, etc. | Stateless |
| **WebSocket** | Challenging | Sticky sessions | Stateful |
| **gRPC** | Excellent | Client-side LB | Stateless |
| **REST** | Excellent | Standard LB | Stateless |
| **GraphQL** | Good | Standard LB | Stateless |
| **MQTT** | Good | Broker clustering | Pub/Sub |

**WebSocket Scaling Challenge:**
```
Without sticky sessions:
Client ──→ Server 1 (connection)
Client ──→ Server 2 (different server!)
           ❌ Connection lost

With sticky sessions:
Client ──→ Server 1 (connection)
Client ──→ Server 1 (same server)
           ✓ Connection maintained
```

---

## 12. Decision Framework

### Step-by-Step Protocol Selection

```
1. What type of communication?
   ├─ Request-Response → HTTP/REST or gRPC
   ├─ Real-time → WebSocket or SSE
   ├─ Streaming → gRPC or WebRTC
   └─ Messaging → MQTT or AMQP

2. What are the constraints?
   ├─ Low latency? → UDP, WebSocket
   ├─ High reliability? → TCP, AMQP
   ├─ Low bandwidth? → gRPC, MQTT
   └─ Browser-based? → HTTP, WebSocket, SSE

3. What's the scale?
   ├─ < 1K clients → Any protocol works
   ├─ 1K-100K clients → Consider stateless (HTTP, gRPC)
   └─ > 100K clients → Optimize for your bottleneck

4. What's the team expertise?
   ├─ Familiar with REST → Start with REST
   ├─ Need learning → gRPC, GraphQL
   └─ Time to market → Use familiar tech
```

---

## Summary

**Golden Rules:**

1. **Start simple**: HTTP/REST is often sufficient
2. **Optimize when needed**: Measure before switching protocols
3. **Consider the ecosystem**: Team expertise, tooling, support
4. **Security first**: Always use encryption (HTTPS, WSS, TLS)
5. **Plan for scale**: Choose protocols that can grow with your app

**Common Combinations:**

- **Web App**: HTTPS (pages) + WebSocket (real-time) + REST (API)
- **Mobile App**: HTTPS (API) + gRPC (efficiency) + Push notifications
- **IoT System**: MQTT (devices) + HTTP (dashboard) + Kafka (processing)
- **Microservices**: gRPC (internal) + REST (public API) + Message queue
- **Gaming**: UDP (game state) + WebSocket (chat) + HTTP (matchmaking)

Remember: **There's no one-size-fits-all protocol. Choose based on your specific requirements!**
