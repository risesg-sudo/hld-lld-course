# Week 1: Networking & Protocols - High-Level Design

## Table of Contents
1. [Client-Server Architecture](#client-server-architecture)
2. [Network Protocols](#network-protocols)
3. [Monolith vs Microservices](#monolith-vs-microservices)
4. [WebSockets vs Server-Sent Events](#websockets-vs-server-sent-events)
5. [gRPC and Protocol Buffers](#grpc-and-protocol-buffers)
6. [REST vs GraphQL](#rest-vs-graphql)
7. [Interview Questions](#interview-questions)
8. [Practice Problems](#practice-problems)

---

## Client-Server Architecture

### Theory

Client-Server architecture is a distributed application structure that partitions tasks or workloads between service providers (servers) and service requesters (clients). In this model:

- **Client**: Initiates requests for services or resources
- **Server**: Listens for requests and provides responses
- **Communication**: Happens over a network using defined protocols

```
┌─────────────┐                    ┌─────────────┐
│             │   HTTP Request     │             │
│   Client    │ ─────────────────> │   Server    │
│  (Browser)  │                    │  (Web App)  │
│             │ <───────────────── │             │
│             │   HTTP Response    │             │
└─────────────┘                    └─────────────┘
```

### Architecture Patterns

#### 1. Two-Tier Architecture
```
┌──────────┐              ┌──────────┐
│  Client  │ ←─────────→ │ Database │
│   (App)  │              │  Server  │
└──────────┘              └──────────┘
```
- Direct connection between client and database
- Simple but less scalable
- Example: Desktop applications with direct DB access

#### 2. Three-Tier Architecture
```
┌──────────┐     ┌────────────┐     ┌──────────┐
│  Client  │ ──→ │Application │ ──→ │ Database │
│ (Browser)│ ←── │   Server   │ ←── │          │
└──────────┘     └────────────┘     └──────────┘
```
- Presentation Layer (Client)
- Application Layer (Business Logic)
- Data Layer (Database)
- Most common web architecture

#### 3. N-Tier Architecture
```
┌────────┐   ┌─────┐   ┌──────┐   ┌─────┐   ┌────┐
│ Client │──→│ CDN │──→│ Load │──→│ API │──→│ DB │
│        │   │     │   │Balancer│  │Svrs │   │    │
└────────┘   └─────┘   └──────┘   └─────┘   └────┘
```
- Multiple intermediate layers
- Highly scalable and maintainable
- Example: Modern cloud applications

### When to Use

**Use Client-Server When:**
- You need centralized data management
- Multiple clients need to access same data
- You want to control business logic centrally
- Security and access control are important

**Considerations:**
- Network latency affects performance
- Server becomes single point of failure (need redundancy)
- Scalability requires careful planning

### Pros and Cons

**Pros:**
- Centralized control and security
- Easy to maintain and update (update server, all clients benefit)
- Resource sharing
- Scalability (add more servers)
- Data consistency

**Cons:**
- Network dependency
- Server can become bottleneck
- Single point of failure
- Higher complexity than standalone apps
- Latency issues

### Real-World Examples

1. **Web Applications**: Browser (client) ↔ Web Server (server)
2. **Email**: Email client (Outlook) ↔ Mail Server (Gmail)
3. **Database Systems**: Application ↔ MySQL/PostgreSQL Server
4. **Gaming**: Game Client ↔ Game Server
5. **Banking**: ATM/Mobile App ↔ Banking Server

---

## Network Protocols

### HTTP (Hypertext Transfer Protocol)

#### Theory

HTTP is a stateless, application-layer protocol for distributed, collaborative, hypermedia information systems.

**Key Characteristics:**
- **Stateless**: Each request is independent
- **Port**: Default port 80
- **Methods**: GET, POST, PUT, DELETE, PATCH, etc.
- **Request-Response**: Client sends request, server sends response

**HTTP Request Structure:**
```
GET /api/users HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: application/json
Content-Type: application/json

{request body if applicable}
```

**HTTP Response Structure:**
```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 45
Date: Sun, 16 Nov 2025 12:00:00 GMT

{"id": 1, "name": "John Doe"}
```

**HTTP Status Codes:**
- **1xx**: Informational
- **2xx**: Success (200 OK, 201 Created, 204 No Content)
- **3xx**: Redirection (301 Moved Permanently, 302 Found)
- **4xx**: Client Error (400 Bad Request, 401 Unauthorized, 404 Not Found)
- **5xx**: Server Error (500 Internal Server Error, 503 Service Unavailable)

#### When to Use HTTP
- Standard web applications
- RESTful APIs
- Simple request-response patterns
- When caching is beneficial
- Public APIs

#### Pros and Cons

**Pros:**
- Simple and widely supported
- Human-readable
- Stateless (scales easily)
- Caching support
- Firewall-friendly

**Cons:**
- No built-in security (use HTTPS)
- Overhead with headers
- Half-duplex communication
- No built-in compression (HTTP/1.1)

---

### HTTPS (HTTP Secure)

#### Theory

HTTPS is HTTP with encryption using TLS/SSL. It provides:
- **Encryption**: Data encrypted in transit
- **Authentication**: Verify server identity
- **Data Integrity**: Detect tampering

```
Client                                    Server
  │                                          │
  │──── TCP Handshake ─────────────────────→│
  │                                          │
  │──── TLS Handshake (Certificate) ───────→│
  │←─── Server Certificate ─────────────────│
  │                                          │
  │──── Encrypted HTTP Request ────────────→│
  │←─── Encrypted HTTP Response ────────────│
```

**Port**: 443

#### When to Use HTTPS
- **Always** for production applications
- When handling sensitive data
- For authentication/authorization
- E-commerce sites
- APIs transmitting private information

#### Pros and Cons

**Pros:**
- Security through encryption
- Trust and credibility (browser indicators)
- SEO benefits
- Required for modern web features (Service Workers, etc.)
- Prevents man-in-the-middle attacks

**Cons:**
- Slight performance overhead (encryption/decryption)
- Certificate management required
- Debugging more complex

---

### TCP/IP (Transmission Control Protocol/Internet Protocol)

#### Theory

TCP/IP is a suite of communication protocols used to interconnect network devices on the internet.

**TCP Characteristics:**
- **Connection-oriented**: Three-way handshake
- **Reliable**: Guarantees delivery
- **Ordered**: Packets arrive in order
- **Error-checking**: Detects corrupted data
- **Flow control**: Prevents overwhelming receiver

**TCP Three-Way Handshake:**
```
Client                    Server
  │                          │
  │──── SYN ───────────────→│
  │                          │
  │←─── SYN-ACK ────────────│
  │                          │
  │──── ACK ───────────────→│
  │                          │
  │   Connection Established │
```

**TCP vs IP:**
- **IP (Internet Protocol)**: Handles addressing and routing
- **TCP**: Ensures reliable delivery

**Layers:**
```
┌─────────────────────────┐
│   Application Layer     │ (HTTP, FTP, SMTP)
├─────────────────────────┤
│   Transport Layer       │ (TCP, UDP)
├─────────────────────────┤
│   Internet Layer        │ (IP, ICMP)
├─────────────────────────┤
│   Network Access Layer  │ (Ethernet, Wi-Fi)
└─────────────────────────┘
```

#### When to Use TCP
- When data integrity is critical
- File transfers (FTP)
- Email (SMTP, IMAP)
- Web browsing (HTTP/HTTPS)
- Database connections

#### Pros and Cons

**Pros:**
- Reliable delivery
- Order guaranteed
- Error detection and correction
- Flow and congestion control
- Widely supported

**Cons:**
- Higher latency (handshake overhead)
- More bandwidth usage (acknowledgments)
- Slower than UDP
- Head-of-line blocking

---

### UDP (User Datagram Protocol)

#### Theory

UDP is a connectionless, unreliable transport protocol. It sends datagrams without establishing a connection.

**UDP Characteristics:**
- **Connectionless**: No handshake
- **Unreliable**: No delivery guarantee
- **Unordered**: Packets may arrive out of order
- **Lightweight**: Minimal overhead
- **Fast**: Lower latency than TCP

**UDP Communication:**
```
Client                    Server
  │                          │
  │──── Datagram 1 ────────→│
  │──── Datagram 2 ────────→│
  │──── Datagram 3 ────────→│
  │                          │
  (No acknowledgment)
```

#### When to Use UDP
- Real-time applications (gaming, video streaming)
- Voice over IP (VoIP)
- DNS queries
- Live broadcasts
- IoT sensors
- When speed > reliability

#### Pros and Cons

**Pros:**
- Lower latency
- No connection setup overhead
- Smaller packet overhead
- Supports broadcast/multicast
- Better for real-time applications

**Cons:**
- No delivery guarantee
- No ordering
- No congestion control
- Application must handle errors
- Can lead to packet loss

---

### WebSockets

#### Theory

WebSocket is a protocol providing full-duplex communication channels over a single TCP connection.

**Key Features:**
- **Persistent connection**: Stays open
- **Bi-directional**: Both client and server can send messages
- **Real-time**: Low latency
- **Efficient**: Less overhead than HTTP polling

**WebSocket Handshake:**
```
Client → Server (HTTP Upgrade Request)
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
Sec-WebSocket-Version: 13

Server → Client (HTTP 101 Switching Protocols)
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=

[WebSocket connection established]
```

**Communication Pattern:**
```
Client                    Server
  │                          │
  │──── Message ───────────→│
  │                          │
  │←─── Message ────────────│
  │                          │
  │←─── Message ────────────│
  │                          │
  │──── Message ───────────→│
```

#### When to Use WebSockets
- Chat applications
- Real-time notifications
- Live sports scores
- Collaborative editing (Google Docs)
- Multiplayer games
- Trading platforms
- IoT dashboards

#### Pros and Cons

**Pros:**
- True real-time communication
- Low latency
- Bi-directional
- Efficient (no HTTP overhead per message)
- Server can push to client

**Cons:**
- More complex than HTTP
- Requires persistent connection (resource intensive)
- Not supported by all proxies/firewalls
- Scalability challenges (connection state)
- No automatic reconnection

---

## Monolith vs Microservices

### Monolithic Architecture

#### Theory

A monolith is a single-tiered software application where all components are interconnected and interdependent.

```
┌─────────────────────────────────────────┐
│         Monolithic Application          │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────┐ │
│  │   User   │  │ Product  │  │ Order│ │
│  │ Service  │  │ Service  │  │Service│ │
│  └──────────┘  └──────────┘  └──────┘ │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │      Shared Database            │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

#### When to Use Monolith
- Small to medium applications
- Early-stage startups
- Simple business logic
- Limited team size
- Tight deadlines
- Proof of concept

#### Pros and Cons

**Pros:**
- Simple to develop and deploy
- Easier debugging
- No network latency between components
- ACID transactions easier
- Less operational overhead
- Easier testing

**Cons:**
- Tight coupling
- Difficult to scale specific components
- Long deployment times
- Technology stack lock-in
- Large codebase becomes complex
- Single point of failure

---

### Microservices Architecture

#### Theory

Microservices is an architectural style where an application is composed of small, independent services that communicate over a network.

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │    │ Product  │    │  Order   │
│ Service  │    │ Service  │    │ Service  │
│          │    │          │    │          │
│ ┌──────┐ │    │ ┌──────┐ │    │ ┌──────┐ │
│ │  DB  │ │    │ │  DB  │ │    │ │  DB  │ │
│ └──────┘ │    │ └──────┘ │    │ └──────┘ │
└──────────┘    └──────────┘    └──────────┘
      │               │               │
      └───────────────┴───────────────┘
                      │
              ┌───────────────┐
              │  API Gateway  │
              └───────────────┘
                      │
                  ┌───────┐
                  │Client │
                  └───────┘
```

#### When to Use Microservices
- Large, complex applications
- Need to scale specific services independently
- Different teams working on different services
- Want technology flexibility
- Need high availability
- Frequent deployments

#### Pros and Cons

**Pros:**
- Independent deployment
- Technology flexibility
- Scalability (scale only what you need)
- Fault isolation
- Better organization for large teams
- Easier to understand individual services

**Cons:**
- Increased complexity
- Network latency
- Distributed system challenges
- Data consistency issues
- Testing is harder
- Higher operational overhead
- Deployment complexity

---

### Comparison Matrix

| Aspect | Monolith | Microservices |
|--------|----------|---------------|
| **Deployment** | Single unit | Multiple services |
| **Scaling** | Scale entire app | Scale individual services |
| **Development** | Simpler initially | Complex from start |
| **Team Structure** | Single team | Multiple teams |
| **Technology** | Single stack | Multiple stacks possible |
| **Testing** | Easier | More complex |
| **Data Management** | Single database | Database per service |
| **Performance** | Lower latency | Higher network overhead |
| **Fault Tolerance** | Single failure point | Isolated failures |
| **Time to Market** | Faster (initially) | Slower (initially) |

---

## WebSockets vs Server-Sent Events

### Server-Sent Events (SSE)

#### Theory

SSE is a server push technology enabling a server to push data to a client over HTTP.

**Characteristics:**
- **Unidirectional**: Server to client only
- **HTTP-based**: Uses standard HTTP
- **Auto-reconnection**: Built-in
- **Text-based**: UTF-8 encoded
- **Event stream**: Continuous stream of events

**SSE Communication:**
```
Client                    Server
  │                          │
  │──── HTTP GET Request ──→│
  │                          │
  │←─── Event Stream ────────│
  │←─── Event ───────────────│
  │←─── Event ───────────────│
  │←─── Event ───────────────│
  │                          │
  (Connection stays open)
```

**SSE Event Format:**
```
event: message
data: {"temp": 25}
id: 1

event: message
data: {"temp": 26}
id: 2
```

#### When to Use SSE
- Stock tickers
- News feeds
- Notifications
- Progress updates
- Live scores
- Social media feeds
- When client doesn't need to send data frequently

---

### WebSockets vs SSE Comparison

| Feature | WebSockets | SSE |
|---------|------------|-----|
| **Direction** | Bi-directional | Server to Client only |
| **Protocol** | WS/WSS | HTTP/HTTPS |
| **Data Format** | Binary or Text | Text only (UTF-8) |
| **Browser Support** | Excellent | Good (IE not supported) |
| **Reconnection** | Manual | Automatic |
| **Max Connections** | More flexible | Limited (~6 per browser) |
| **Overhead** | Lower | Higher (HTTP) |
| **Complexity** | Higher | Lower |
| **Use Case** | Chat, Gaming | Notifications, Feeds |

#### Decision Tree

```
Need bidirectional communication?
├─ YES → Use WebSockets
└─ NO
    │
    Need binary data?
    ├─ YES → Use WebSockets
    └─ NO
        │
        Want simpler implementation?
        ├─ YES → Use SSE
        └─ NO
            │
            Need compatibility with old browsers?
            ├─ YES → Use Long Polling
            └─ NO → Use SSE
```

---

## gRPC and Protocol Buffers

### gRPC Theory

gRPC (Google Remote Procedure Call) is a high-performance, open-source framework for RPC.

**Key Features:**
- Uses HTTP/2
- Protocol Buffers for serialization
- Support for streaming
- Multiple language support
- Built-in load balancing

**gRPC Architecture:**
```
┌─────────────┐                 ┌─────────────┐
│   Client    │                 │   Server    │
│             │                 │             │
│  ┌───────┐  │                 │  ┌───────┐  │
│  │ Stub  │  │ ──── gRPC ────→│  │Service│  │
│  └───────┘  │    (HTTP/2)     │  └───────┘  │
│             │                 │             │
└─────────────┘                 └─────────────┘
        │                               │
        └──── Protocol Buffers ─────────┘
             (Serialization)
```

**gRPC Communication Types:**

1. **Unary RPC** (Request-Response)
```
Client ──request──→ Server
Client ←─response── Server
```

2. **Server Streaming**
```
Client ──request──→ Server
Client ←─response1─ Server
Client ←─response2─ Server
Client ←─response3─ Server
```

3. **Client Streaming**
```
Client ──request1─→ Server
Client ──request2─→ Server
Client ──request3─→ Server
Client ←─response── Server
```

4. **Bidirectional Streaming**
```
Client ←──────────→ Server
 (continuous two-way stream)
```

---

### Protocol Buffers (Protobuf)

#### Theory

Protocol Buffers is a language-neutral, platform-neutral, extensible mechanism for serializing structured data.

**Example .proto file:**
```protobuf
syntax = "proto3";

package users;

service UserService {
  rpc GetUser(UserRequest) returns (UserResponse);
  rpc ListUsers(Empty) returns (stream UserResponse);
}

message UserRequest {
  int32 id = 1;
}

message UserResponse {
  int32 id = 1;
  string name = 2;
  string email = 3;
  int32 age = 4;
}

message Empty {}
```

**Advantages of Protobuf:**
- Smaller size (3-10x smaller than JSON)
- Faster serialization/deserialization
- Strongly typed
- Schema evolution support
- Code generation

**Size Comparison:**
```json
// JSON (58 bytes)
{"id":1,"name":"John","age":30}

// Protobuf (approximately 9 bytes)
// Binary format - much smaller
```

---

### When to Use gRPC

**Use gRPC When:**
- Microservices communication
- Need high performance
- Real-time streaming required
- Multiple language environments
- Strong typing needed
- Bandwidth is limited

**Don't Use gRPC When:**
- Browser clients (limited support)
- Need human-readable messages
- Simple REST is sufficient
- No HTTP/2 support in infrastructure

---

### gRPC Pros and Cons

**Pros:**
- High performance (HTTP/2, Protobuf)
- Streaming support (all 4 types)
- Strong typing
- Code generation
- Multi-language support
- Efficient (smaller payloads)
- Built-in features (auth, load balancing)

**Cons:**
- Limited browser support
- Not human-readable
- Steeper learning curve
- More complex than REST
- Debugging harder
- Requires HTTP/2

---

## REST vs GraphQL

### REST (Representational State Transfer)

#### Theory

REST is an architectural style for designing networked applications using HTTP.

**REST Principles:**
1. **Stateless**: Each request contains all needed information
2. **Client-Server**: Separation of concerns
3. **Cacheable**: Responses can be cached
4. **Uniform Interface**: Consistent resource URIs
5. **Layered System**: Architecture can be layered

**REST Resource Design:**
```
GET    /api/users           # Get all users
GET    /api/users/1         # Get user 1
POST   /api/users           # Create user
PUT    /api/users/1         # Update user 1
PATCH  /api/users/1         # Partial update user 1
DELETE /api/users/1         # Delete user 1

GET    /api/users/1/orders  # Get orders for user 1
```

**REST Response:**
```json
// GET /api/users/1
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "orders": [
    {"id": 101, "total": 99.99},
    {"id": 102, "total": 149.99}
  ]
}
```

---

### GraphQL

#### Theory

GraphQL is a query language for APIs and a runtime for executing those queries.

**Key Concepts:**
- **Schema**: Defines data structure
- **Query**: Read data
- **Mutation**: Modify data
- **Subscription**: Real-time updates
- **Single Endpoint**: Usually `/graphql`

**GraphQL Schema:**
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  orders: [Order!]!
}

type Order {
  id: ID!
  total: Float!
  items: [Item!]!
}

type Query {
  user(id: ID!): User
  users: [User!]!
}

type Mutation {
  createUser(name: String!, email: String!): User
  updateUser(id: ID!, name: String, email: String): User
  deleteUser(id: ID!): Boolean
}

type Subscription {
  userUpdated(id: ID!): User
}
```

**GraphQL Query:**
```graphql
# Client requests only what it needs
query {
  user(id: 1) {
    name
    email
    orders {
      id
      total
    }
  }
}
```

**GraphQL Response:**
```json
{
  "data": {
    "user": {
      "name": "John Doe",
      "email": "john@example.com",
      "orders": [
        {"id": 101, "total": 99.99},
        {"id": 102, "total": 149.99}
      ]
    }
  }
}
```

---

### REST vs GraphQL Comparison

| Aspect | REST | GraphQL |
|--------|------|---------|
| **Endpoints** | Multiple endpoints | Single endpoint |
| **Data Fetching** | Fixed data structure | Request exactly what you need |
| **Over-fetching** | Common | Eliminated |
| **Under-fetching** | Requires multiple requests | Single request |
| **Versioning** | URL versioning (v1, v2) | Schema evolution |
| **Caching** | HTTP caching works well | More complex caching |
| **Learning Curve** | Easier | Steeper |
| **Tooling** | Mature | Growing |
| **Real-time** | WebSockets/SSE needed | Built-in subscriptions |
| **File Upload** | Native support | Requires additional setup |

---

### When to Use What

**Use REST When:**
- Simple CRUD operations
- Caching is important
- HTTP features needed (status codes, methods)
- Team familiar with REST
- Public API for wide consumption
- File uploads/downloads

**Use GraphQL When:**
- Flexible data requirements
- Mobile clients (reduce over-fetching)
- Multiple clients with different needs
- Rapid frontend development
- Complex data relationships
- Real-time features needed

**Example Scenarios:**

1. **E-commerce Product Page** (REST has issues):
```
REST requires:
GET /api/products/1         # Product details
GET /api/products/1/reviews # Reviews
GET /api/products/1/related # Related products
GET /api/users/123          # User info for reviews
(4 requests, potential over-fetching)

GraphQL solution:
query {
  product(id: 1) {
    name
    price
    reviews {
      rating
      comment
      user { name }
    }
    relatedProducts {
      name
      price
    }
  }
}
(1 request, exact data needed)
```

---

## Interview Questions

### Basic Level

1. **What is the difference between HTTP and HTTPS?**
   - HTTP is unencrypted, HTTPS uses TLS/SSL for encryption
   - HTTPS provides authentication, encryption, and data integrity
   - HTTPS uses port 443, HTTP uses port 80

2. **Explain the TCP three-way handshake.**
   - SYN: Client sends SYN packet to server
   - SYN-ACK: Server responds with SYN-ACK
   - ACK: Client sends ACK, connection established

3. **When would you use UDP over TCP?**
   - Real-time applications where speed > reliability
   - Video streaming, VoIP, online gaming
   - DNS queries, IoT sensors

4. **What is the difference between WebSockets and HTTP?**
   - HTTP: Request-response, half-duplex
   - WebSocket: Persistent, full-duplex, bi-directional
   - WebSocket: Lower latency for real-time apps

5. **What are the main HTTP methods and their purposes?**
   - GET: Retrieve resource
   - POST: Create resource
   - PUT: Update/replace resource
   - PATCH: Partial update
   - DELETE: Remove resource

---

### Intermediate Level

6. **How do you handle authentication in microservices?**
   - JWT tokens with API Gateway
   - OAuth 2.0 / OpenID Connect
   - Service mesh with mutual TLS
   - Centralized authentication service
   - Token propagation between services

7. **Explain the N+1 query problem in REST and how GraphQL solves it.**
   - N+1: One query for list, N queries for related data
   - Example: Get users, then get orders for each user
   - GraphQL: DataLoader batches and caches requests
   - Solves with single query and field resolvers

8. **What are the challenges of migrating from monolith to microservices?**
   - Data consistency and transactions
   - Service boundaries definition
   - Network latency and reliability
   - Distributed tracing and monitoring
   - Team organization and DevOps
   - Gradual migration strategy (strangler pattern)

9. **Compare Server-Sent Events and WebSockets. When would you use each?**
   - SSE: Unidirectional, HTTP-based, auto-reconnect, simpler
   - WebSocket: Bi-directional, persistent, more overhead
   - Use SSE for: Notifications, feeds, progress updates
   - Use WebSocket for: Chat, gaming, collaborative editing

10. **How does gRPC achieve better performance than REST?**
    - HTTP/2 multiplexing
    - Protobuf binary serialization (smaller, faster)
    - Connection reuse
    - Header compression
    - Streaming support

---

### Advanced Level

11. **Design a real-time notification system. What protocol would you use and why?**
    ```
    Solution:
    - WebSocket or SSE for browser clients
    - gRPC for service-to-service
    - Message queue (Kafka/RabbitMQ) for reliability
    - Redis for presence/state management

    Architecture:
    [Clients] ←WebSocket→ [WebSocket Servers]
                              ↓
                         [Message Queue]
                              ↓
                      [Notification Service]
                              ↓
                         [User Database]

    Why:
    - WebSocket: Bi-directional, real-time
    - Message Queue: Decoupling, reliability
    - Multiple WebSocket servers: Scalability
    - Redis Pub/Sub: Fast message distribution
    ```

12. **How would you handle API versioning in a microservices architecture?**
    ```
    Strategies:

    1. URL Versioning:
       /api/v1/users
       /api/v2/users

    2. Header Versioning:
       Accept: application/vnd.company.v1+json

    3. Query Parameter:
       /api/users?version=1

    4. Content Negotiation:
       Accept: application/json; version=1

    Best Practice:
    - Use semantic versioning (major.minor.patch)
    - Maintain backward compatibility for minor versions
    - Deprecation strategy with sunset headers
    - API Gateway handles routing to correct version
    ```

13. **Explain CAP theorem in context of microservices data management.**
    ```
    CAP Theorem: Can only guarantee 2 of 3:
    - Consistency: All nodes see same data
    - Availability: System always responds
    - Partition Tolerance: Works despite network failures

    In Microservices:

    CP (Consistency + Partition Tolerance):
    - Banking transactions
    - Inventory management
    - Use: Strong consistency patterns
    - Example: HBase, MongoDB (default)

    AP (Availability + Partition Tolerance):
    - Social media feeds
    - Shopping cart
    - Use: Eventual consistency
    - Example: Cassandra, DynamoDB

    Solution:
    - Use Saga pattern for distributed transactions
    - Event sourcing for audit trail
    - CQRS for read/write optimization
    ```

14. **Design a GraphQL schema for an e-commerce platform with pagination and filtering.**
    ```graphql
    type Product {
      id: ID!
      name: String!
      price: Float!
      category: Category!
      reviews(first: Int, after: String): ReviewConnection!
      inStock: Boolean!
    }

    type Category {
      id: ID!
      name: String!
      products(
        first: Int
        after: String
        filter: ProductFilter
        sort: ProductSort
      ): ProductConnection!
    }

    input ProductFilter {
      minPrice: Float
      maxPrice: Float
      inStock: Boolean
      category: ID
    }

    enum ProductSort {
      PRICE_ASC
      PRICE_DESC
      NAME_ASC
      NEWEST
    }

    type ProductConnection {
      edges: [ProductEdge!]!
      pageInfo: PageInfo!
      totalCount: Int!
    }

    type ProductEdge {
      cursor: String!
      node: Product!
    }

    type PageInfo {
      hasNextPage: Boolean!
      hasPreviousPage: Boolean!
      startCursor: String
      endCursor: String
    }

    type Query {
      products(
        first: Int = 20
        after: String
        filter: ProductFilter
        sort: ProductSort = NEWEST
      ): ProductConnection!
      product(id: ID!): Product
    }
    ```

15. **How would you implement rate limiting across microservices?**
    ```
    Strategies:

    1. API Gateway Level:
       - Rate limit at entry point
       - Token bucket algorithm
       - Redis for distributed counting
       - Example: Kong, AWS API Gateway

    2. Service Level:
       - Individual service limits
       - Prevents internal abuse
       - Circuit breaker pattern

    3. User/Tenant Level:
       - Different tiers (free, premium)
       - JWT claims for tier information
       - Redis sorted sets for sliding window

    Implementation:

    Token Bucket Algorithm:
    - Bucket capacity: Max requests
    - Refill rate: Requests per second
    - Token consumed per request

    Redis Implementation:
    INCR user:123:requests
    EXPIRE user:123:requests 60  # 1 minute window

    If count > limit:
      Return 429 Too Many Requests
      Retry-After: 60

    Advanced: Distributed Rate Limiting
    - Use Redis Cluster
    - Lua scripts for atomicity
    - Sliding window log algorithm
    ```

---

## Practice Problems

### Problem 1: Design a Chat Application

**Requirements:**
- Real-time messaging
- User presence (online/offline)
- Message history
- Support 10,000 concurrent users

**Solution:**
```
Architecture:

[Mobile/Web Clients]
        ↓
[Load Balancer]
        ↓
[WebSocket Servers] (Multiple instances)
        ↓
[Redis Pub/Sub] (Message distribution)
        ↓
[Message Queue] (Kafka/RabbitMQ)
        ↓
[Message Service] (Persistence)
        ↓
[Database] (Message storage)

Additional Components:
- Redis: User presence, online status
- CDN: Static assets, images
- Object Storage: File uploads

Protocol Choice: WebSocket
Why:
- Bi-directional (send/receive messages)
- Real-time with low latency
- Persistent connection
- Efficient for frequent updates

Data Model:
- Users: ID, name, status
- Messages: ID, sender, receiver, content, timestamp
- Rooms: ID, participants, type (direct/group)

Scaling Considerations:
- Horizontal scaling of WebSocket servers
- Session affinity or Redis for shared state
- Message queue for reliability
- Database sharding by user_id
```

---

### Problem 2: REST API for Social Media

**Design a REST API for a social media platform with posts, comments, and likes.**

**Solution:**
```
Resources and Endpoints:

# Users
GET    /api/v1/users                    # List users
GET    /api/v1/users/:id                # Get user
POST   /api/v1/users                    # Create user
PUT    /api/v1/users/:id                # Update user
DELETE /api/v1/users/:id                # Delete user

# Posts
GET    /api/v1/posts                    # List all posts
GET    /api/v1/posts/:id                # Get specific post
POST   /api/v1/posts                    # Create post
PUT    /api/v1/posts/:id                # Update post
DELETE /api/v1/posts/:id                # Delete post
GET    /api/v1/users/:id/posts          # Get user's posts

# Comments
GET    /api/v1/posts/:id/comments       # Get post comments
POST   /api/v1/posts/:id/comments       # Add comment
PUT    /api/v1/comments/:id             # Update comment
DELETE /api/v1/comments/:id             # Delete comment

# Likes
POST   /api/v1/posts/:id/likes          # Like post
DELETE /api/v1/posts/:id/likes          # Unlike post
GET    /api/v1/posts/:id/likes          # Get post likes

# Following
POST   /api/v1/users/:id/follow         # Follow user
DELETE /api/v1/users/:id/follow         # Unfollow user
GET    /api/v1/users/:id/followers      # Get followers
GET    /api/v1/users/:id/following      # Get following

# Feed
GET    /api/v1/feed                     # Get user feed

Pagination Example:
GET /api/v1/posts?page=2&limit=20

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "totalPages": 8,
    "hasNext": true,
    "hasPrev": true
  }
}

Filtering & Sorting:
GET /api/v1/posts?sort=-createdAt&filter[status]=published

Error Response:
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      }
    ]
  }
}
```

---

### Problem 3: Microservices Decomposition

**Break down a monolithic e-commerce application into microservices.**

**Solution:**
```
Monolith Components:
- User Management
- Product Catalog
- Shopping Cart
- Order Processing
- Payment
- Inventory
- Shipping
- Notifications

Microservices Design:

1. User Service
   - Authentication/Authorization
   - User profiles
   - Database: PostgreSQL
   - API: REST or gRPC

2. Product Service
   - Product catalog
   - Categories
   - Search
   - Database: MongoDB (flexible schema)
   - Cache: Redis
   - API: REST + GraphQL

3. Cart Service
   - Shopping cart operations
   - Session management
   - Database: Redis (fast, temporary)
   - API: REST

4. Order Service
   - Order creation
   - Order tracking
   - Order history
   - Database: PostgreSQL
   - API: REST

5. Payment Service
   - Payment processing
   - Payment methods
   - Transaction history
   - Database: PostgreSQL (ACID)
   - API: gRPC (internal only)

6. Inventory Service
   - Stock management
   - Warehouse operations
   - Database: PostgreSQL
   - Event-driven updates
   - API: gRPC

7. Shipping Service
   - Shipping calculation
   - Carrier integration
   - Tracking
   - Database: PostgreSQL
   - API: REST

8. Notification Service
   - Email/SMS
   - Push notifications
   - Message Queue: RabbitMQ
   - API: Internal events

Communication Patterns:

Synchronous (gRPC/REST):
User Service → Product Service (get product details)
Order Service → Payment Service (process payment)
Order Service → Inventory Service (check stock)

Asynchronous (Events):
Order Created → Inventory Service (reduce stock)
Order Created → Notification Service (send confirmation)
Payment Completed → Shipping Service (create shipment)

API Gateway:
[Client] → [API Gateway] → [Microservices]

API Gateway handles:
- Authentication
- Rate limiting
- Request routing
- Response aggregation
- Caching

Data Management:
- Each service owns its database
- Saga pattern for distributed transactions
- Event sourcing for audit trail
- CQRS for read-heavy services

Example Flow: Place Order

1. Client → API Gateway: POST /orders
2. API Gateway → Auth: Validate token
3. Order Service → Product Service: Get product details
4. Order Service → Inventory Service: Check stock
5. Order Service → Payment Service: Process payment
6. Order Service: Create order
7. Order Service → Event Bus: OrderCreated event
8. Inventory Service: Reduce stock (async)
9. Notification Service: Send email (async)
10. Shipping Service: Create shipment (async)
```

---

### Problem 4: Protocol Selection

**For each scenario, choose the appropriate protocol and justify:**

**Scenarios:**

1. **Stock Trading Platform**
   - **Protocol**: WebSocket
   - **Why**: Real-time price updates, bi-directional (place orders), low latency critical
   - **Alternative**: gRPC for service-to-service

2. **Weather Dashboard**
   - **Protocol**: Server-Sent Events (SSE)
   - **Why**: Unidirectional updates, simple, auto-reconnect, HTTP-based
   - **Alternative**: HTTP polling with caching

3. **Microservice Communication (Internal)**
   - **Protocol**: gRPC
   - **Why**: High performance, type-safe, efficient, streaming support
   - **Alternative**: REST for simpler services

4. **Public API for Third-Party Developers**
   - **Protocol**: REST
   - **Why**: Widely understood, HTTP caching, easy debugging, language-agnostic
   - **Alternative**: GraphQL for flexibility

5. **Video Streaming Service**
   - **Protocol**: HTTP/2 with adaptive streaming (HLS/DASH)
   - **Why**: Adaptive bitrate, buffering, HTTP compatibility
   - **Data Transport**: UDP for live streaming (WebRTC)

6. **IoT Sensor Data Collection**
   - **Protocol**: MQTT or UDP
   - **Why**: Lightweight, supports unreliable networks, low power
   - **Alternative**: gRPC for reliable, structured data

7. **Real-time Multiplayer Game**
   - **Protocol**: UDP with custom reliability layer
   - **Why**: Low latency critical, can tolerate some packet loss
   - **State Sync**: WebSocket for lobby/chat

---

### Problem 5: Design GraphQL Schema

**Design a GraphQL schema for a blog platform with posts, authors, comments, and tags.**

**Solution:**
```graphql
# Schema Definition
type Author {
  id: ID!
  name: String!
  email: String!
  bio: String
  avatar: String
  posts(first: Int, after: String): PostConnection!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  excerpt: String
  author: Author!
  tags: [Tag!]!
  comments(first: Int, after: String): CommentConnection!
  published: Boolean!
  publishedAt: DateTime
  createdAt: DateTime!
  updatedAt: DateTime!
  viewCount: Int!
  likeCount: Int!
}

type Comment {
  id: ID!
  content: String!
  author: Author!
  post: Post!
  parent: Comment
  replies(first: Int): CommentConnection!
  createdAt: DateTime!
}

type Tag {
  id: ID!
  name: String!
  slug: String!
  posts(first: Int, after: String): PostConnection!
}

# Connection Types (Pagination)
type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PostEdge {
  cursor: String!
  node: Post!
}

type CommentConnection {
  edges: [CommentEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type CommentEdge {
  cursor: String!
  node: Comment!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# Input Types
input CreatePostInput {
  title: String!
  content: String!
  excerpt: String
  tagIds: [ID!]!
  published: Boolean = false
}

input UpdatePostInput {
  title: String
  content: String
  excerpt: String
  tagIds: [ID!]
  published: Boolean
}

input CreateCommentInput {
  postId: ID!
  content: String!
  parentId: ID
}

# Enums
enum PostSortField {
  CREATED_AT
  PUBLISHED_AT
  TITLE
  VIEW_COUNT
  LIKE_COUNT
}

enum SortOrder {
  ASC
  DESC
}

input PostFilter {
  authorId: ID
  tagIds: [ID!]
  published: Boolean
  search: String
}

# Queries
type Query {
  # Posts
  posts(
    first: Int = 10
    after: String
    filter: PostFilter
    sortBy: PostSortField = CREATED_AT
    order: SortOrder = DESC
  ): PostConnection!

  post(id: ID!): Post
  postBySlug(slug: String!): Post

  # Authors
  author(id: ID!): Author
  authors(first: Int, after: String): AuthorConnection!

  # Tags
  tag(id: ID!): Tag
  tags: [Tag!]!

  # Search
  search(query: String!, first: Int = 10): SearchResult!

  # Current User
  me: Author
}

# Mutations
type Mutation {
  # Post mutations
  createPost(input: CreatePostInput!): Post!
  updatePost(id: ID!, input: UpdatePostInput!): Post!
  deletePost(id: ID!): Boolean!
  likePost(id: ID!): Post!
  unlikePost(id: ID!): Post!

  # Comment mutations
  createComment(input: CreateCommentInput!): Comment!
  updateComment(id: ID!, content: String!): Comment!
  deleteComment(id: ID!): Boolean!

  # Tag mutations
  createTag(name: String!): Tag!

  # Author mutations
  updateProfile(name: String, bio: String, avatar: String): Author!
}

# Subscriptions
type Subscription {
  postPublished: Post!
  commentAdded(postId: ID!): Comment!
  postLiked(postId: ID!): Post!
}

# Custom Scalars
scalar DateTime

# Search Result Union
union SearchResult = Post | Author | Tag

# Example Queries

# 1. Get recent posts with author and tags
query GetRecentPosts {
  posts(first: 10, sortBy: PUBLISHED_AT, order: DESC) {
    edges {
      node {
        id
        title
        excerpt
        author {
          name
          avatar
        }
        tags {
          name
        }
        publishedAt
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

# 2. Get single post with comments
query GetPost($id: ID!) {
  post(id: $id) {
    id
    title
    content
    author {
      name
      bio
    }
    tags {
      name
    }
    comments(first: 20) {
      edges {
        node {
          id
          content
          author {
            name
          }
          replies(first: 5) {
            edges {
              node {
                content
                author {
                  name
                }
              }
            }
          }
        }
      }
    }
  }
}

# 3. Create post mutation
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    author {
      name
    }
  }
}

# 4. Subscribe to new comments
subscription OnCommentAdded($postId: ID!) {
  commentAdded(postId: $postId) {
    id
    content
    author {
      name
    }
  }
}
```

---

## Summary

This week covered fundamental networking and protocol concepts essential for system design:

1. **Client-Server Architecture**: Foundation of distributed systems
2. **Network Protocols**: HTTP, HTTPS, TCP, UDP, WebSockets
3. **Architecture Patterns**: Monolith vs Microservices
4. **Real-time Communication**: WebSockets vs SSE
5. **RPC Frameworks**: gRPC and Protocol Buffers
6. **API Design**: REST vs GraphQL

**Key Takeaways:**
- Choose protocols based on requirements (latency, reliability, complexity)
- Start with monolith, migrate to microservices when needed
- Use REST for simplicity, GraphQL for flexibility, gRPC for performance
- WebSockets for bi-directional, SSE for server-to-client
- Consider trade-offs: performance, complexity, maintainability

**Next Steps:**
- Practice implementing each protocol
- Study real-world architectures
- Understand when to use each approach
- Focus on trade-offs and decision-making

---

## Additional Resources

**Books:**
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Building Microservices" by Sam Newman
- "System Design Interview" by Alex Xu

**Online:**
- gRPC Documentation: https://grpc.io/docs/
- GraphQL Documentation: https://graphql.org/learn/
- HTTP/2 Specification: https://http2.github.io/

**Practice:**
- Implement each example in this guide
- Build a full-stack application using different protocols
- Contribute to open-source projects using these technologies
