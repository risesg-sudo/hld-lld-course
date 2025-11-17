# HLD Week 1: Networking and Protocols

This week covers fundamental networking concepts and communication protocols essential for system design.

## Directory Structure

```
week1/
├── client-server/
│   ├── concept.md - Client-server architecture fundamentals
│   ├── tcp_example.py - TCP-based client-server implementation
│   └── dry_run.md - Step-by-step execution trace
│
├── protocols/
│   ├── http/
│   │   ├── concept.md - HTTP protocol fundamentals
│   │   ├── example.py - REST API implementation
│   │   └── dry_run.md - HTTP request-response flow
│   │
│   ├── websockets/
│   │   ├── concept.md - WebSocket protocol fundamentals
│   │   ├── example.py - Real-time chat application
│   │   └── dry_run.md - WebSocket connection lifecycle
│   │
│   ├── sse/
│   │   ├── concept.md - Server-Sent Events fundamentals
│   │   ├── example.py - Live updates and notifications
│   │   └── dry_run.md - SSE stream processing
│   │
│   └── grpc/
│       ├── concept.md - gRPC and Protocol Buffers
│       ├── example.py - gRPC service implementation
│       └── dry_run.md - gRPC message flow
│
└── architectures/
    ├── monolith-vs-microservices/
    │   ├── concept.md - Architecture comparison
    │   └── comparison.md - Trade-offs and decision matrix
    │
    └── rest-vs-graphql/
        ├── concept.md - API design patterns
        └── comparison.md - When to use each approach
```

## Learning Path

### 1. Foundation: Client-Server Architecture
Start here to understand the basic pattern underlying all networked applications.

- Read: `client-server/concept.md`
- Implement: Run `client-server/tcp_example.py`
- Trace: Follow `client-server/dry_run.md`

**Key Takeaways**: Request-response pattern, TCP handshake, multi-threading

### 2. HTTP Protocol
Learn the protocol powering the web and most RESTful APIs.

- Read: `protocols/http/concept.md`
- Implement: Run `protocols/http/example.py`
- Practice: Use curl to test different HTTP methods

**Key Takeaways**: HTTP methods, status codes, headers, stateless nature

### 3. Real-Time Protocols
Understand when and how to implement real-time communication.

**WebSockets** (Bi-directional):
- Use case: Chat, gaming, collaborative editing
- Read: `protocols/websockets/concept.md`
- Implement: `protocols/websockets/example.py`

**Server-Sent Events** (Server-to-client):
- Use case: Notifications, live feeds, progress updates
- Read: `protocols/sse/concept.md`
- Implement: `protocols/sse/example.py`

### 4. gRPC
High-performance RPC framework for microservices.

- Read: `protocols/grpc/concept.md`
- Compare: gRPC vs REST performance and use cases

**Key Takeaways**: Protocol Buffers, HTTP/2, streaming support

### 5. Architectural Patterns
Choose the right architecture for your system.

**Monolith vs Microservices**:
- Read: `architectures/monolith-vs-microservices/concept.md`
- Decision guide: When to use each pattern

**REST vs GraphQL**:
- Read: `architectures/rest-vs-graphql/concept.md`
- Understand: Over-fetching, under-fetching, and query flexibility

## Quick Reference

### Protocol Selection Guide

| Requirement | Choose |
|------------|--------|
| Simple CRUD operations | HTTP/REST |
| Bi-directional real-time | WebSockets |
| Server-to-client streaming | Server-Sent Events |
| High-performance microservices | gRPC |
| Flexible client data needs | GraphQL |

### When to Use Each Protocol

**HTTP/REST**:
- Public APIs
- Simple request-response
- Caching important
- Wide compatibility needed

**WebSockets**:
- Chat applications
- Real-time gaming
- Collaborative tools
- Trading platforms

**Server-Sent Events**:
- Notifications
- Live feeds
- Progress updates
- Stock tickers

**gRPC**:
- Microservice communication
- Need streaming
- Performance critical
- Type safety important

## Hands-On Exercises

1. **Build a Chat Server**: Extend the WebSocket example to support multiple rooms
2. **Create a REST API**: Implement CRUD operations for a todo list
3. **Real-time Dashboard**: Use SSE to stream metrics from a monitoring system
4. **Compare Protocols**: Measure latency differences between HTTP polling, SSE, and WebSockets

## Common Interview Questions

1. What's the difference between HTTP and WebSockets?
2. When would you choose REST over GraphQL?
3. How does TCP ensure reliable delivery?
4. Explain the trade-offs of monolith vs microservices
5. How would you design a real-time notification system?

## Next Steps

After completing Week 1, move to Week 2 to learn about:
- Scaling strategies (horizontal vs vertical)
- Load balancing algorithms
- Caching strategies and eviction policies
- CAP theorem and distributed systems
- Message queues and pub/sub systems

## Resources

All examples in this directory are runnable Python scripts. Requirements:
- Python 3.7+
- `websockets` library for WebSocket examples: `pip install websockets`
- `grpcio` and `grpcio-tools` for gRPC examples: `pip install grpcio grpcio-tools`

Each example includes:
- Clear documentation
- Step-by-step dry run
- Real-world use case context
- Performance considerations
- Trade-offs and limitations
