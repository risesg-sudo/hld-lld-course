# Chain of Responsibility Pattern

## The Hook: The Support Ticket Escalation

You submit a support ticket. If tier-1 can handle it, great. If not, it escalates to tier-2. Still too complex? It goes to tier-3 management. Each handler tries, then passes along if needed.

This is Chain of Responsibility: pass a request along a chain of handlers until one processes it.

## The Problem: Coupling Sender to Receiver

You need to:
- Process requests at different levels
- Let multiple handlers attempt to handle request
- Add/remove handlers dynamically
- Not know which handler will process request

**Without Chain:**
- Tight coupling between sender and specific handler
- Hard-coded if-else chains
- Can't add handlers without modifying code
- Request routing logic spread throughout

## The Solution: Handler Chain

Chain handlers where each can process or pass request to next handler.

**Key Components:**
- Handler: Abstract handler with next reference
- Concrete Handlers: Implement specific handling logic
- Client: Initiates request to chain

**When to Use:**
- Multiple objects can handle request
- Handler not known in advance
- Dynamic handler set
- Request should traverse multiple handlers

**Common Applications:**
- HTTP middleware chains
- Logging levels (DEBUG, INFO, ERROR)
- Approval workflows
- Event propagation
- Exception handling

## Trade-offs

**Gains:**
- Decouples sender from receiver
- Dynamic chain configuration
- Single Responsibility (each handler focused)
- Open/Closed (add handlers without modifying existing)

**Losses:**
- Request might not be handled
- Hard to debug (which handler processed it?)
- Performance (traversing chain)
- Can create infinite loops if not careful

## The Verdict

Chain of Responsibility excels for multi-level processing like middleware, logging, and approval workflows. Essential for flexible request routing. But always handle the "unhandled request" case and log which handler processes each request.
