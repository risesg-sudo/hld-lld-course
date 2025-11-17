# Command Pattern

## The Hook: The Undo Button Mystery

Every text editor has undo/redo. How does it remember what you did? How can it reverse actions? The answer is the Command pattern: encapsulate each action as an object that knows how to execute and undo itself.

## The Problem: Encapsulating Requests

You need to:
- Queue operations for later execution
- Support undo/redo functionality
- Log operations for audit trails
- Schedule commands for specific times
- Parameterize objects with operations

**Without Command:**
- Direct method calls can't be undone
- Can't queue operations
- No operation history
- Hard to implement macros

## The Solution: Commands as Objects

Encapsulate requests as objects with execute() and undo() methods.

**Key Components:**
- Command: Interface with execute() and undo()
- Concrete Commands: Implement specific operations
- Invoker: Executes commands
- Receiver: Performs actual work

**When to Use:**
- Undo/redo functionality needed
- Queue or schedule operations
- Log operations for replay
- Support macros (composite commands)
- Decouple invoker from receiver

## Trade-offs

**Gains:**
- Undo/redo support
- Command queuing and scheduling
- Operation logging
- Macro composition
- Decoupling

**Losses:**
- Many small command classes
- Memory overhead for history
- Complexity for simple operations
- State management for undo

## The Verdict

Command is essential for editors, schedulers, and transactional systems. The ability to undo, queue, and log operations justifies the additional classes and complexity.
