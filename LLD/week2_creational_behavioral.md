# Week 2: Creational & Behavioral Design Patterns

## Table of Contents
1. [Creational Patterns](#creational-patterns)
   - [Singleton Pattern](#singleton-pattern)
   - [Builder Pattern](#builder-pattern)
   - [Prototype Pattern](#prototype-pattern)
2. [Behavioral Patterns](#behavioral-patterns)
   - [Observer Pattern](#observer-pattern)
   - [Command Pattern](#command-pattern)
   - [Chain of Responsibility Pattern](#chain-of-responsibility-pattern)
   - [Iterator Pattern](#iterator-pattern)
3. [Key Takeaways](#key-takeaways)
4. [Interview Tips](#interview-tips)
5. [Practice Problems](#practice-problems)

---

## Creational Patterns

Creational patterns deal with object creation mechanisms, trying to create objects in a manner suitable to the situation.

### Singleton Pattern

#### Intent
Ensure a class has only one instance and provide a global point of access to it.

#### When to Use
- **Logging systems** - Need a single logger across the application
- **Database connections** - Single connection pool
- **Configuration managers** - One centralized configuration
- **Thread pools** - Single executor service
- **Cache managers** - Single cache instance

#### Benefits
- **Global access point** - Easy to access singleton instance anywhere
- **Lazy initialization** - Can defer expensive initialization until needed
- **Thread safety** - Single point of synchronization
- **Memory efficiency** - Only one instance ever exists

#### Drawbacks
- **Hidden dependencies** - Tests and components have implicit dependency on singleton
- **Testing complexity** - Hard to mock/stub singletons
- **Multithreading issues** - Requires careful synchronization (though thread-safe approaches solve this)
- **Violates Single Responsibility Principle** - Manages both its own creation and responsibility
- **Global state** - Can make debugging harder

#### Implementation Patterns
1. **Eager initialization** - Instance created when class loads
2. **Lazy initialization** - Instance created on first use
3. **Thread-safe lazy initialization** - Double-checked locking or synchronization
4. **Bill Pugh Singleton** - Uses inner static helper class (Java)
5. **Enum Singleton** (Java) - Serialization and reflection-proof

#### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week2/singleton_pattern.py`

#### Key Takeaways
- Always consider if you really need a singleton - often you can inject dependency
- Thread safety is crucial in multithreaded environments
- Singletons make testing harder - consider using dependency injection instead
- For Python, module-level instances often serve the same purpose

---

### Builder Pattern

#### Intent
Separate the construction of a complex object from its representation so that the same construction process can create different representations.

#### When to Use
- **Complex object construction** - Objects with many optional parameters
- **Immutable objects** - Building immutable objects step-by-step
- **Fluent interfaces** - Creating readable, chainable method calls
- **Multiple configurations** - Different combinations of parameters
- **Telescoping constructors** - Avoiding multiple constructor overloads

#### Benefits
- **Readability** - Clear, self-documenting construction process
- **Flexibility** - Easy to add/remove parameters
- **Immutability** - Can build immutable objects
- **Validation** - Can validate at each step or at the end
- **Different representations** - Same builder can create different products

#### Drawbacks
- **More code** - Requires builder class in addition to product class
- **Performance** - Creating intermediate objects during construction
- **Unnecessary complexity** - Overkill for simple objects
- **Parameter validation delayed** - Errors detected only after build()

#### Variations
1. **Fluent builder** - Chainable method calls
2. **Director pattern** - Separate director controls building steps
3. **Hierarchical builders** - Builder inheritance for complex hierarchies
4. **Optional vs required parameters** - Using method overloading or separate methods

#### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week2/builder_pattern.py`

#### Key Takeaways
- Ideal for objects with 3+ optional parameters
- Consider dataclasses or named tuples as simpler alternatives for simple objects
- Can be combined with fluent interfaces for elegant APIs
- Useful for immutable objects in concurrent environments

---

### Prototype Pattern

#### Intent
Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype.

#### When to Use
- **Expensive object creation** - Cloning cheaper than creating from scratch
- **Dynamic object creation** - Need to create objects based on runtime conditions
- **Avoiding subclasses** - Alternative to class hierarchies
- **Circular references** - Need deep copying of complex structures
- **Plugin systems** - Creating instances from registered prototypes

#### Benefits
- **Performance** - Faster than creating new objects (shallow copy)
- **Avoids subclassing** - Don't need separate subclasses for variations
- **Dynamic object creation** - Objects can be created at runtime
- **Decoupling** - Clients don't need to know concrete classes
- **Reduced initialization** - Cloning pre-initialized objects

#### Drawbacks
- **Complex cloning** - Deep cloning can be complex and slow
- **Circular references** - Difficult to handle in circular structures
- **Runtime overhead** - Deep cloning might negate performance benefits
- **Confusion** - Easy to confuse shallow vs deep copy
- **Not always faster** - Depends on object complexity and initialization cost

#### Cloning Strategies
1. **Shallow copy** - Only copies object's own attributes
2. **Deep copy** - Recursively copies all nested objects
3. **Smart copy** - Selective deep copying of specific attributes
4. **Copy constructor** - Explicit constructor for copying

#### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week2/prototype_pattern.py`

#### Key Takeaways
- Python's `copy` module provides shallow and deep copy utilities
- Be explicit about shallow vs deep copy requirements
- Consider initialization overhead before assuming cloning is faster
- Useful for object pools and caching scenarios
- Handle circular references carefully in deep cloning

---

## Behavioral Patterns

Behavioral patterns are concerned with object collaboration and the delegation of responsibility.

### Observer Pattern

#### Intent
Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified automatically.

#### When to Use
- **Event handling systems** - UI button clicks, user actions
- **Model-View architectures** - View updates when model changes
- **Publish-Subscribe systems** - Decoupled event propagation
- **Stock market tickers** - Multiple clients track same stocks
- **Notification systems** - Broadcasting updates to subscribers
- **Real-time data feeds** - Chat systems, live notifications

#### Benefits
- **Loose coupling** - Subject and observers are loosely coupled
- **Dynamic relationships** - Observers can be added/removed at runtime
- **Broadcasting** - Efficient one-to-many communication
- **Separation of concerns** - Subject doesn't need to know observer details
- **Real-time updates** - Automatic notification of changes

#### Drawbacks
- **Unpredictable order** - Notification order may be unpredictable
- **Memory leaks** - Unregistered observers may not be garbage collected
- **Performance** - Many observers can cause performance issues
- **Debugging difficulty** - Hard to trace observer notification chains
- **Unexpected updates** - Observers might be notified at unexpected times

#### Variations
1. **Push model** - Subject pushes changed data to observers
2. **Pull model** - Observers pull changed data from subject
3. **Event-based** - Using event objects to pass state changes
4. **Weak references** - Using weak references to avoid memory leaks

#### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week2/observer_pattern.py`

#### Key Takeaways
- Always unregister observers to prevent memory leaks
- Consider push vs pull models based on use case
- Use weak references in languages that support them
- Modern frameworks often provide event systems (React, Django signals, etc.)
- Can be implemented with callbacks, events, or listeners

---

### Command Pattern

#### Intent
Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue requests, and log requests. Support undoable operations.

#### When to Use
- **Undo/Redo systems** - Text editors, graphic applications
- **Queuing operations** - Thread pools, task schedulers
- **Macro recording** - Recording and replaying sequences of operations
- **Transactional systems** - Grouping multiple operations as one unit
- **Remote invocation** - Sending commands over network
- **Smart home automation** - Scheduling commands for devices
- **Workflow engines** - Complex workflows with multiple steps

#### Benefits
- **Encapsulation** - Encapsulates requests as objects
- **Undo/Redo** - Easy to implement undo/redo functionality
- **Queuing** - Can queue and schedule commands
- **Decoupling** - Decouples invoker from receiver
- **Macros** - Can easily compose commands
- **Logging** - Commands can be logged and replayed

#### Drawbacks
- **Complexity** - Introduces many small classes
- **Memory overhead** - Command objects consume memory
- **Invocation overhead** - Extra layer of indirection
- **State management** - Tracking undo/redo history can be complex
- **Serialization** - Serializing commands can be tricky

#### Variations
1. **Reversible commands** - Commands that can undo their effects
2. **Command history** - Stack of executed commands for undo
3. **Composite commands** - Combining multiple commands into one
4. **Async commands** - Commands that execute asynchronously
5. **Command scheduler** - Queue and schedule command execution

#### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week2/command_pattern.py`

#### Key Takeaways
- Perfect for implementing undo/redo functionality
- Keep commands small and focused on single operations
- Command history can be serialized for audit logs
- Consider memory implications for large command histories
- Works well with transaction patterns

---

### Chain of Responsibility Pattern

#### Intent
Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain until an object handles it.

#### When to Use
- **Event handling** - Pass event up hierarchy until handled
- **Logging systems** - Log at different levels (DEBUG, INFO, WARNING, ERROR)
- **Request processing pipelines** - HTTP middleware chains
- **Approval workflows** - Multi-level approval chains
- **Error handling** - Multiple catch handlers
- **Support ticket routing** - Route to appropriate support tier

#### Benefits
- **Loose coupling** - Sender doesn't know which handler will process request
- **Dynamic handler chain** - Can build chains at runtime
- **Single Responsibility** - Each handler handles one type of request
- **Open/Closed Principle** - Easy to add new handlers without modifying existing ones
- **Flexible responsibility** - Can pass request up the chain if can't handle

#### Drawbacks
- **Unpredictable** - Request handling might not be obvious
- **Debugging** - Hard to trace which handler processes the request
- **Performance** - Request might traverse entire chain
- **Infinite loops** - Possible if chain has cycles
- **Request unhandled** - Request might not be handled by any handler

#### Variations
1. **Linear chain** - Simple list of handlers
2. **Tree-based chain** - Hierarchical handler structure
3. **Conditional chain** - Handlers make decisions about passing request
4. **Fallback chain** - Default handler if none can handle

#### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week2/chain_of_responsibility.py`

#### Key Takeaways
- Always consider what happens if no handler processes the request
- Use for hierarchical processing (UI events, approval workflows)
- Middleware in web frameworks is a common application
- Be careful about request traversal efficiency
- Log which handler processes the request for debugging

---

### Iterator Pattern

#### Intent
Provide a way to access the elements of a collection sequentially without exposing its underlying representation.

#### When to Use
- **Collection abstractions** - Different collection types (list, set, tree)
- **Tree traversal** - DFS, BFS, level-order traversal
- **Database cursors** - Iterating over query results
- **File systems** - Traversing directory structures
- **Graph traversal** - BFS, DFS on graph structures
- **Remote collections** - Lazy loading from remote sources

#### Benefits
- **Encapsulation** - Hides internal structure of collection
- **Multiple iterators** - Can have multiple iterators on same collection
- **Lazy evaluation** - Elements can be computed on-demand
- **Uniform interface** - Same interface for different collection types
- **Concurrent traversal** - Multiple iterations can happen simultaneously

#### Drawbacks
- **Performance overhead** - Extra abstraction layer
- **Additional classes** - Needs separate iterator classes
- **Covariance issues** - Iterator types might not be compatible
- **Complexity** - Over-engineering for simple collections
- **State management** - Iterator state can be tricky to manage

#### Variations
1. **Internal iterator** - Collection controls iteration (callbacks/generators)
2. **External iterator** - Client controls iteration
3. **Bidirectional iterator** - Can move forward and backward
4. **Lazy iterator** - Computes elements on-demand
5. **Generator-based** (Python) - Using generators for iteration

#### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week2/iterator_pattern.py`

#### Key Takeaways
- Python generators are a simple form of iterators
- Most modern languages have built-in iteration support
- Useful for complex traversals (tree, graph)
- Consider generator expressions for simple cases
- Lazy evaluation can improve performance for large collections

---

## Key Takeaways

### Creational Patterns
1. **Singleton**: One instance, but consider dependency injection in tests
2. **Builder**: For complex objects with multiple optional parameters
3. **Prototype**: When cloning is cheaper than creation from scratch

### Behavioral Patterns
1. **Observer**: For event-driven architectures and decoupled updates
2. **Command**: For undo/redo, scheduling, and request encapsulation
3. **Chain of Responsibility**: For hierarchical request handling and workflows
4. **Iterator**: For uniform traversal across different collection types

### Pattern Selection Guide
- **Too many constructor parameters?** → Builder
- **Need global instance?** → Singleton (or dependency injection)
- **Expensive object creation?** → Prototype
- **Need to notify multiple objects of changes?** → Observer
- **Need undo/redo?** → Command
- **Need hierarchical request processing?** → Chain of Responsibility
- **Need uniform collection access?** → Iterator

---

## Interview Tips

### Singleton Pattern Interview
1. **Discuss thread safety** - Explain different approaches (lazy init, double-checked locking)
2. **Testing challenges** - How to test code that depends on singletons?
3. **Dependency injection** - When to use DI instead of singleton
4. **Real-world example** - Logger, database connection pool
5. **Anti-pattern discussion** - Singletons are often criticized; explain when they're justified

### Builder Pattern Interview
1. **Problem it solves** - Telescoping constructors, complex initialization
2. **Fluent interface** - Show understanding of method chaining
3. **Immutability** - How builder helps create immutable objects
4. **Comparison with alternatives** - Dataclasses (Python), lombok (Java)
5. **Real-world example** - SQL query builders, HTTP request builders

### Prototype Pattern Interview
1. **Deep vs shallow copy** - Explain the difference and implications
2. **Performance considerations** - When is cloning actually faster?
3. **Circular references** - How do you handle them?
4. **Use cases** - Caching, object pools, configuration templates
5. **Language support** - How different languages support cloning

### Observer Pattern Interview
1. **Push vs pull models** - When to use each approach
2. **Memory leaks** - How to prevent them (unregister, weak references)
3. **Ordering** - What happens when multiple observers need specific notification order?
4. **Event design** - What data to include in events?
5. **Real-world examples** - UI frameworks, MVC pattern, Pub-Sub systems

### Command Pattern Interview
1. **Undo/Redo implementation** - How to track command history?
2. **Reversibility** - How to ensure commands can be undone?
3. **Transaction-like behavior** - Grouping commands
4. **Serialization** - Saving and replaying commands
5. **Comparison with callbacks** - When to use command vs callback?

### Chain of Responsibility Interview
1. **Request flow** - Explain how request flows through chain
2. **Handler ordering** - Does order matter?
3. **Default handler** - What if no handler can process request?
4. **Performance** - Chain traversal overhead?
5. **Real-world examples** - Middleware, logging levels, approval chains

### Iterator Pattern Interview
1. **Collection independence** - How to provide uniform interface?
2. **Multiple iterators** - Can collection be modified during iteration?
3. **Lazy vs eager** - When to compute elements on-demand?
4. **Bidirectional traversal** - Supporting forward and backward?
5. **Python generators** - Simpler alternative to iterator classes?

---

## Practice Problems

### Easy
1. **Logger Singleton** - Create a thread-safe logger that logs to both console and file
2. **Pizza Builder** - Build pizza with different toppings using builder pattern
3. **Simple Observer** - Implement temperature sensor that notifies observers
4. **Undo/Redo Text** - Implement simple text editor with undo/redo using commands
5. **Iterator** - Implement iterator for simple list/array

### Medium
1. **Database Connection Pool** - Singleton pattern for managing DB connections
2. **SQL Query Builder** - Complex query builder with fluent interface
3. **Document Template Cloning** - Prototype pattern for document templates
4. **Event System** - Robust event system with priority-based observer notification
5. **Smart Home Commands** - Command pattern for home automation devices
6. **Request Processing Pipeline** - Chain of responsibility for request validation/processing
7. **Tree Traversal** - Iterator for different tree traversal methods

### Hard
1. **Thread-safe Configuration Manager** - Singleton with hot-reload capability
2. **Dialog Builder with Validation** - Multi-step dialog builder with validation
3. **Deep Copy with Circular References** - Handle circular references in prototyping
4. **Observing Complex State Changes** - Multi-level state change notifications
5. **Transaction Command System** - Atomic commands with rollback support
6. **Authorization Chain** - Multi-level authorization with chain of responsibility
7. **Lazy-Loading Iterator** - Iterator that loads data on-demand from remote source

### Real-World Scenarios
1. **Design a settings/configuration system** - Use singleton or module instance
2. **Design an undo/redo system** - Full implementation for text editor
3. **Design a publish-subscribe system** - Event broker with multiple subscribers
4. **Design a workflow approval system** - Chain of responsibility for multi-level approvals
5. **Design a caching system** - Singleton cache with cloning for performance

---

## Code Examples Location

All code examples are in `/home/user/hld-lld-course/LLD/examples/week2/`:
- `singleton_pattern.py` - Singleton implementations and logger example
- `builder_pattern.py` - Builder and fluent interface examples
- `prototype_pattern.py` - Cloning and prototype examples
- `observer_pattern.py` - Observer and event system examples
- `command_pattern.py` - Command and undo/redo examples
- `chain_of_responsibility.py` - Chain of responsibility examples
- `iterator_pattern.py` - Iterator and traversal examples

Each file contains:
- Multiple real-world examples
- Best practices and anti-patterns
- Runnable code with clear output
- Detailed comments and docstrings
- Key takeaways and learning points
