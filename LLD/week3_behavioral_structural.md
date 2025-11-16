# Week 3: Behavioral & Structural Design Patterns

## Table of Contents

### Behavioral Patterns
1. [Strategy Pattern](#strategy-pattern)
2. [Template Method Pattern](#template-method-pattern)

### Structural Patterns
3. [Adapter Pattern](#adapter-pattern)
4. [Decorator Pattern](#decorator-pattern)
5. [Bridge Pattern](#bridge-pattern)
6. [Composite Pattern](#composite-pattern)
7. [Proxy Pattern](#proxy-pattern)
8. [Facade Pattern](#facade-pattern)

### Summary
9. [Key Takeaways](#key-takeaways)
10. [Interview Tips](#interview-tips)
11. [Practice Problems](#practice-problems)

---

## Behavioral Patterns

Behavioral patterns deal with object collaboration and responsibility distribution.

---

## Strategy Pattern

### Intent
Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it.

### When to Use
- **Multiple algorithm variations** - Different payment methods, sorting algorithms, compression formats
- **Runtime algorithm selection** - Choosing algorithm based on runtime conditions
- **Avoiding complex conditionals** - Replacing if/else chains with strategy objects
- **Algorithm encapsulation** - Isolating algorithm implementation details
- **Performance tuning** - Swapping algorithms to optimize performance
- **Testing algorithms** - Easy to test different implementations
- **Plugin systems** - Dynamically loading different algorithms

### Benefits
- **Encapsulation** - Encapsulates algorithms in separate objects
- **Runtime switching** - Can switch algorithms at runtime
- **Eliminates conditionals** - Removes complex if/else chains
- **Open/Closed Principle** - Open for extension (new strategies), closed for modification
- **Testability** - Easy to test each strategy in isolation
- **Flexibility** - Multiple ways to solve same problem
- **Code reuse** - Strategies can be reused in different contexts

### Drawbacks
- **Increased classes** - Many strategy classes can clutter codebase
- **Complexity overhead** - Overkill for simple problems
- **Strategy selection overhead** - Deciding which strategy to use
- **Memory overhead** - Creating strategy objects for each use case
- **Unfamiliar pattern** - Team might not be familiar with pattern

### Variations
1. **Simple strategy** - Direct algorithm switching
2. **Parameterized strategy** - Strategies accept configuration
3. **Factory + Strategy** - Creating strategies using factory pattern
4. **Strategy with state** - Strategies maintaining internal state
5. **Composite strategy** - Combining multiple strategies

### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week3/strategy_pattern.py`

Examples include:
- Payment strategies (Credit Card, PayPal, Cryptocurrency)
- Sorting algorithms (Bubble Sort, Quick Sort, Merge Sort)
- Compression algorithms (ZIP, RAR, 7z)
- Route calculation (Fastest, Shortest, Scenic)

### Key Takeaways
- Use when you have multiple implementations of same interface
- Works well with factory pattern for strategy creation
- Excellent alternative to multiple if/else chains
- Consider whether runtime switching is actually needed
- Can be combined with configuration to parameterize strategies
- Be explicit about strategy selection logic

---

## Template Method Pattern

### Intent
Define the skeleton of an algorithm in a method, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure.

### When to Use
- **Common algorithms with variations** - Base algorithm with customizable steps
- **Code reuse** - Sharing common code in inheritance hierarchy
- **Framework development** - Defining algorithm templates for users
- **Workflow processing** - Fixed workflow with customizable steps
- **Report generation** - Fixed report structure with custom content
- **Game development** - Game loop with customizable updates
- **Document processing** - Parse, process, output with custom processing

### Benefits
- **Code reuse** - Common code in base class used by all subclasses
- **Consistent structure** - Algorithm structure enforced across implementations
- **Inversion of control** - Framework controls algorithm flow
- **Easier maintenance** - Changes to algorithm affect all implementations
- **Reduced duplication** - Don't repeat common steps in subclasses
- **Flexibility in implementation** - Subclasses implement specific steps

### Drawbacks
- **Rigid structure** - Algorithm structure fixed by template
- **Inheritance overhead** - Forces inheritance which can be limiting
- **Limited flexibility** - Can't change algorithm structure in subclasses
- **Complexity** - Tight coupling between base and derived classes
- **Fragile base class problem** - Changes in base class can break subclasses
- **Hard to understand** - Need to understand base algorithm flow

### Variations
1. **Concrete template method** - Base class provides full algorithm
2. **Hook methods** - Template provides optional override points
3. **Abstract methods** - Subclasses must implement all abstract steps
4. **Default implementations** - Template provides defaults subclasses can override
5. **Strategy + Template** - Template method with pluggable strategies

### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week3/template_pattern.py`

Examples include:
- Data mining (parse, analyze, extract, output)
- Game development (initialize, render, update, input)
- Report generation (gather data, format, generate, save)
- Database migration (connect, parse, transform, save)

### Key Takeaways
- Use for algorithms with fixed structure but varying implementations
- Consider composition/strategy as alternative to inheritance
- Hook methods provide flexibility without changing template
- Good for framework development where users customize specific steps
- Can be combined with strategy pattern for maximum flexibility
- Be careful with the fragile base class problem

---

## Structural Patterns

Structural patterns deal with object composition and relationships between entities.

---

## Adapter Pattern

### Intent
Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.

### When to Use
- **Legacy system integration** - Making old systems work with new code
- **Third-party library integration** - Adapting external library to your interface
- **Multiple data sources** - Different APIs returning same data
- **Hardware drivers** - Adapting hardware interfaces to software
- **Format conversion** - Converting between different data formats
- **Interface compatibility** - Making incompatible interfaces work together
- **Version compatibility** - Supporting multiple versions of API

### Benefits
- **Compatibility** - Makes incompatible interfaces work together
- **Reusability** - Reuse existing classes with different interfaces
- **Flexibility** - Can adapt multiple implementations
- **Separation of concerns** - Keeps adaptation logic separate
- **Open/Closed Principle** - Extend without modifying original
- **Single Responsibility** - Adapter handles only interface translation
- **Easy testing** - Can mock adapters for testing

### Drawbacks
- **Extra layer** - Additional layer of indirection
- **Complexity** - Can make codebase harder to understand
- **Overhead** - Extra method calls for adaptation
- **Overuse** - Can create overly abstracted interfaces
- **Maintenance** - Need to maintain adapter as interfaces change
- **Multiple adapters** - May need many adapters for complex systems

### Variations
1. **Class adapter** - Uses inheritance (harder in single-inheritance languages)
2. **Object adapter** - Uses composition (more flexible)
3. **Two-way adapter** - Adapts both directions
4. **Pluggable adapter** - Dynamically selectable adapters
5. **Default adapter** - Provides default implementations

### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week3/adapter_pattern.py`

Examples include:
- Legacy system integration (old interface to new)
- API adapters (third-party to internal)
- Database adapters (multiple database support)
- Data format converters (JSON, XML, CSV)

### Key Takeaways
- Perfect for working with legacy systems or third-party code
- Object adapter (composition) is usually more flexible than class adapter
- Consider whether you should change the client instead of adapting
- Use sparingly to avoid over-abstraction
- Can work alongside other patterns (factory, decorator)
- Be clear about what interface you're adapting to what

---

## Decorator Pattern

### Intent
Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality.

### When to Use
- **Adding behavior to objects** - Add features without modifying original
- **Conditional features** - Enable/disable features at runtime
- **Combinations of features** - Mix and match different behaviors
- **Cross-cutting concerns** - Logging, caching, validation, authentication
- **Avoiding subclass explosion** - Alternative to creating many subclasses
- **Wrapping objects** - Layer functionality around objects
- **Stream decoration** - Decorating input/output streams

### Benefits
- **Flexible composition** - Mix and match behaviors
- **Avoids subclass explosion** - Don't need class for every combination
- **Single Responsibility** - Each decorator handles one responsibility
- **Open/Closed Principle** - Add new decorators without modifying existing code
- **Runtime composition** - Build behavior combinations at runtime
- **Easy to add/remove features** - Just decorate or undecorate
- **Cleaner than inheritance** - More flexible than deep inheritance hierarchies

### Drawbacks
- **Wrapper overhead** - Additional objects and method calls
- **Complex initialization** - Building decorator chains can be complex
- **Order matters** - Order of decorators can affect behavior
- **Debugging difficulty** - Hard to trace through decorator chain
- **Code complexity** - Can make code harder to understand
- **Performance impact** - Each decorator adds overhead
- **Identifying decorators** - Hard to tell what decorators are applied

### Variations
1. **Simple decorator** - Adds single behavior
2. **Conditional decorator** - Applies behavior based on condition
3. **Parameterized decorator** - Decorator accepts configuration
4. **Component decorator** - Decorates component hierarchy
5. **Aspect-oriented** - Using AOP frameworks for decoration

### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week3/decorator_pattern.py`

Examples include:
- Coffee shop (adding toppings to coffee)
- Text formatting (bold, italic, underline combinations)
- Caching layer (adding cache around data access)
- Security decorators (authentication, authorization)
- Logging/monitoring (adding instrumentation)

### Key Takeaways
- Excellent alternative to subclass explosion
- Consider order of decorators - order can affect results
- Can create complex behavior through composition
- Use with interfaces to ensure decorator compatibility
- Be careful with debugging - use clear naming for decorators
- Python property decorators are simplified version of pattern
- Consider whether simpler composition would work

---

## Bridge Pattern

### Intent
Decouple an abstraction from its implementation so the two can vary independently.

### When to Use
- **Multiple implementations** - Different implementations of same abstraction
- **Avoiding inheritance explosion** - Preventing deep inheritance hierarchies
- **Platform-specific code** - Different implementations for different platforms
- **Runtime implementation selection** - Choosing implementation at runtime
- **Variant hierarchies** - Handling combinations of variants
- **Refactoring deep hierarchies** - Breaking up overly complex inheritance
- **Device drivers** - Different drivers for different devices/platforms

### Benefits
- **Decoupling** - Decouples abstraction from implementation
- **Independent variation** - Can vary abstraction and implementation independently
- **Avoids inheritance explosion** - More flexible than deep hierarchies
- **Easier to change** - Can change implementation without affecting clients
- **Better encapsulation** - Implementation details hidden
- **Open/Closed Principle** - Open for extension, closed for modification
- **Multiple implementations** - Easy to support multiple implementations

### Drawbacks
- **Complexity** - More complex than simple inheritance
- **Extra abstraction layer** - Additional layer of indirection
- **Overkill for simple cases** - Over-engineering simple problems
- **Harder to understand** - Not immediately obvious why bridge is needed
- **Performance overhead** - Extra method calls through bridge
- **Requires planning** - Need to identify variation points upfront

### Variations
1. **Simple bridge** - One abstraction, multiple implementations
2. **Hierarchical bridge** - Multiple abstractions, multiple implementations
3. **Dynamic bridge** - Implementation changed at runtime
4. **Refined abstraction** - Abstraction hierarchy with shared implementation
5. **Concrete implementation** - Implementation hierarchy with shared abstraction

### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week3/bridge_pattern.py`

Examples include:
- Remote controls (abstraction) controlling different devices (implementation)
- Database drivers (abstraction) for different databases (implementation)
- Graphics shapes (abstraction) with different rendering engines (implementation)
- Payment systems (abstraction) with different providers (implementation)

### Key Takeaways
- Use when you have two independent axes of variation
- Good alternative to deep inheritance hierarchies
- Consider whether composition is simpler than bridge
- Excellent for multi-platform applications
- Works well with strategy pattern
- Helps avoid the "fragile base class" problem
- Be sure actual variation exists before using bridge

---

## Composite Pattern

### Intent
Compose objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects and compositions of objects uniformly.

### When to Use
- **Tree structures** - File systems, DOM trees, organization hierarchies
- **Part-whole hierarchies** - Objects that can contain other objects
- **Uniform treatment** - Treating individual and composite objects the same
- **UI components** - Panels containing panels containing controls
- **Graphics systems** - Shapes that contain other shapes
- **Menu systems** - Menus containing menu items and submenus
- **Directory structures** - Directories containing files and directories

### Benefits
- **Uniform interface** - Treat single and composite objects the same
- **Flexible hierarchies** - Easily create complex tree structures
- **Easy to add new elements** - Just add new leaf or composite class
- **Cleaner code** - No special cases for single vs composite
- **Natural hierarchy** - Mirrors real-world structures
- **Recursive composition** - Objects can contain objects of same type
- **Simplifies client code** - Clients don't need to distinguish types

### Drawbacks
- **Type safety** - Can't enforce what types can be children
- **Overly general** - Makes some constraints hard to express
- **Inefficient for linear structures** - Overkill for non-tree structures
- **Traversal logic** - Implementing efficient traversal can be complex
- **Memory overhead** - Extra objects for intermediate composites
- **Performance** - Deep trees can impact performance
- **Complexity** - Can make simple problems complex

### Variations
1. **Simple composite** - Leaf and composite classes
2. **Restricted composite** - Composites restrict what can be contained
3. **Transparent composite** - All objects appear same to clients
4. **Safe composite** - Client checks type before treating as composite
5. **Iterator composite** - Built-in iteration support

### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week3/composite_pattern.py`

Examples include:
- File system (directories containing files and directories)
- UI components (panels containing panels and controls)
- Organization hierarchy (departments containing departments)
- Graphic shapes (groups containing shapes and groups)
- Menu system (menus containing items and submenus)

### Key Takeaways
- Use for representing part-whole hierarchies
- Provides uniform interface for single and composite objects
- Consider whether simpler structures would work
- Be careful with type safety - composites usually allow any child
- Recursive algorithms work well with composite structure
- Good for recursive problems with tree structure
- Can combine with iterator for easy traversal

---

## Proxy Pattern

### Intent
Provide a surrogate or placeholder for another object to control access to it.

### When to Use
- **Lazy initialization** - Defer expensive object creation (virtual proxy)
- **Access control** - Control who can access objects (protection proxy)
- **Remote objects** - Access objects on remote systems (remote proxy)
- **Caching** - Cache expensive computations (caching proxy)
- **Logging/monitoring** - Log all access to objects
- **Transaction support** - Buffer changes before committing
- **Smart references** - Reference counting, garbage collection

### Benefits
- **Lazy initialization** - Defer expensive operations until needed
- **Access control** - Control access to original object
- **Transparency** - Client sees same interface as real object
- **Additional functionality** - Add logging, caching, validation
- **Remote access** - Can work with objects on different machines
- **Decoupling** - Client decoupled from real object
- **Performance** - Lazy loading improves startup performance

### Drawbacks
- **Extra layer** - Additional layer of indirection
- **Complexity** - Can make code harder to understand
- **Performance overhead** - Extra method calls and checks
- **Debugging difficulty** - Hard to trace through proxy
- **Same interface** - Proxy must match original object's interface
- **Synchronization** - Proxy and real object must stay in sync
- **Memory overhead** - Proxy objects consume memory

### Variations
1. **Virtual proxy** - Lazy initialization of expensive objects
2. **Protection proxy** - Controls access to original object
3. **Remote proxy** - Represents object on remote system
4. **Smart proxy/reference** - Reference counting, garbage collection
5. **Caching proxy** - Caches results of expensive operations

### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week3/proxy_pattern.py`

Examples include:
- Virtual proxy (lazy loading of images, heavy objects)
- Protection proxy (access control to sensitive objects)
- Remote proxy (RPC calls, network communication)
- Smart reference (reference counting, smart pointers)
- Caching proxy (memoization of function results)

### Key Takeaways
- Use when you need to control access or defer initialization
- Proxy must implement same interface as real object
- Be clear about what proxy is controlling
- Consider whether simpler approach would work
- Works well with lazy loading for performance
- Can be combined with other patterns (factory, decorator)
- Be careful about serialization and cloning proxies

---

## Facade Pattern

### Intent
Provide a unified, simplified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use.

### When to Use
- **Complex subsystems** - Simplifying complex interfaces
- **Decoupling clients from subsystems** - Isolate clients from subsystem details
- **Layered architectures** - Providing entry point to layers
- **Library design** - Simplifying library interfaces
- **Legacy system wrapping** - Making legacy systems easier to use
- **Third-party integration** - Adapting external systems
- **API simplification** - Simplifying API for common use cases

### Benefits
- **Simplification** - Hides complex subsystem behind simple interface
- **Decoupling** - Decouples client from subsystem components
- **Convenience** - Provides common-case convenience methods
- **Organization** - Groups related operations
- **Easier testing** - Can mock facade for testing
- **Single entry point** - Clear entry point to subsystem
- **Flexibility** - Clients can use subsystem directly if needed

### Drawbacks
- **Over-simplification** - Hides useful functionality
- **Inflexible** - Facade API might not fit all use cases
- **False encapsulation** - Doesn't prevent direct access to subsystem
- **God object** - Facade can become bloated with too many methods
- **Adds layer** - Additional layer of indirection
- **Maintenance** - Facade needs updating when subsystem changes
- **Misuse** - Clients bypass facade to access subsystem directly

### Variations
1. **Simple facade** - Wraps single subsystem
2. **Composite facade** - Wraps multiple subsystems
3. **Hierarchical facade** - Multiple facades at different levels
4. **Abstract facade** - Abstraction of multiple concrete facades
5. **Smart facade** - Facade with additional business logic

### Code Reference
See: `/home/user/hld-lld-course/LLD/examples/week3/facade_pattern.py`

Examples include:
- Home theater system (integrating multiple components)
- E-commerce checkout (simplifying order process)
- Database API (simplifying complex database operations)
- Graphics library (simplifying complex rendering)
- Web framework (simplifying HTTP handling)

### Key Takeaways
- Use to simplify complex interfaces
- Facade should enhance, not replace, subsystem capabilities
- Consider whether delegation to subsystem is enough
- Can have multiple facades for different use cases
- Don't hide all subsystem details - allow advanced usage
- Works well with adapter and decorator patterns
- Be careful not to create overly-complex facades

---

## Key Takeaways

### Behavioral Patterns Summary
1. **Strategy**: Choose algorithm at runtime, replace conditionals
2. **Template Method**: Define algorithm structure, vary implementation steps

### Structural Patterns Summary
1. **Adapter**: Make incompatible interfaces work together
2. **Decorator**: Add behavior to objects without subclassing
3. **Bridge**: Decouple abstraction from implementation
4. **Composite**: Create tree structures with uniform interface
5. **Proxy**: Control access or defer initialization
6. **Facade**: Simplify complex subsystems

### Pattern Selection Guide

| Problem | Solution |
|---------|----------|
| Multiple algorithm variants? | Strategy |
| Algorithm with varying steps? | Template Method |
| Incompatible interfaces? | Adapter |
| Add behavior without subclassing? | Decorator |
| Two axes of variation? | Bridge |
| Tree structures? | Composite |
| Control access/defer init? | Proxy |
| Complex subsystem? | Facade |

### Design Principle Application

- **Single Responsibility**: Each pattern isolates specific responsibility
- **Open/Closed Principle**: Open for extension, closed for modification
- **Liskov Substitution**: Implementations interchangeable with interface
- **Interface Segregation**: Clients depend on specific interfaces
- **Dependency Inversion**: Depend on abstractions, not concrete classes

### When NOT to Use

- **Over-engineering**: Don't use patterns for simple problems
- **Premature optimization**: Only optimize when needed
- **Pattern blind**: Don't force patterns where they don't fit
- **Consistency over correctness**: Choose right pattern, not trendy one

---

## Interview Tips

### Strategy Pattern Interview

1. **Problem statement** - Explain when you have multiple algorithm implementations
2. **vs. if/else** - When and why to prefer strategy over conditionals
3. **Runtime selection** - How strategy allows runtime algorithm switching
4. **Testing** - Easy to test each strategy independently
5. **Composition** - Strategy selected through composition, not inheritance
6. **Real example** - Payment processors, sorting algorithms, file compression
7. **Tradeoffs** - More classes vs. simpler logic
8. **Design** - Strategy should have well-defined interface

### Template Method Pattern Interview

1. **Intent** - Define algorithm structure, vary implementation
2. **Inheritance** - Uses inheritance for code reuse
3. **vs. Strategy** - Template Method uses inheritance, Strategy uses composition
4. **Hook methods** - Providing optional override points
5. **Abstract methods** - Forcing subclasses to implement specific steps
6. **Framework usage** - Common in frameworks (test frameworks, game engines)
7. **Extension points** - Explicitly defining where subclasses customize behavior
8. **Fragile base class** - Risk of breaking subclasses with base changes

### Adapter Pattern Interview

1. **Legacy integration** - Primary use case for working with legacy code
2. **Two-way vs one-way** - Adapting in one or both directions
3. **Class vs Object adapter** - Object adapter more flexible
4. **When not to use** - Sometimes better to change client
5. **Multiple adapters** - Can have adapters for multiple implementations
6. **Real world** - Database drivers, API adapters, hardware drivers
7. **Testing** - Easy to mock adapters
8. **Complexity** - Be careful not to over-abstract

### Decorator Pattern Interview

1. **vs. Inheritance** - More flexible alternative to subclassing
2. **Order matters** - Order of decorators affects behavior
3. **Combinations** - Building complex behavior through composition
4. **Open/Closed** - Add behavior without modifying original
5. **Transparency** - Decorator presents same interface as decorated object
6. **Real examples** - Coffee toppings, text formatting, caching
7. **Debugging** - Harder to trace through decorator chain
8. **Performance** - Each decorator adds overhead

### Bridge Pattern Interview

1. **Two hierarchies** - Separates abstraction from implementation hierarchy
2. **vs. Adapter** - Bridge designed upfront, Adapter retrofitted
3. **Decoupling** - Abstraction and implementation can vary independently
4. **Complexity** - More complex than simple inheritance
5. **When needed** - When actual variation exists on two axes
6. **Real world** - Remote controls, database drivers, platform-specific code
7. **Variant hierarchies** - Prevents explosion of subclasses
8. **Over-engineering** - Don't use bridge where inheritance works

### Composite Pattern Interview

1. **Tree structures** - Uniform treatment of single and composite objects
2. **Part-whole** - Representing hierarchies of objects
3. **Recursive composition** - Objects can contain objects of same type
4. **Type safety** - Can't enforce what types can be children
5. **Traversal** - Different traversal methods (DFS, BFS, level-order)
6. **Real examples** - File systems, DOM trees, UI components
7. **Performance** - Deep trees can impact performance
8. **Iterator** - Combining with iterator for traversal

### Proxy Pattern Interview

1. **Types of proxies** - Virtual, protection, remote, smart reference, caching
2. **Lazy loading** - Deferring expensive initialization
3. **Access control** - Protecting sensitive objects
4. **Remote proxy** - RPC, network access
5. **vs. Decorator** - Proxy controls access, Decorator adds behavior
6. **Transparent** - Proxy hides real object from client
7. **Caching** - Memoization and result caching
8. **Real world** - Image loading, database access, RPC calls

### Facade Pattern Interview

1. **Simplification** - Making complex subsystems easier to use
2. **Single entry point** - Clear, unified interface
3. **Decoupling** - Isolates clients from subsystem details
4. **Not mandatory** - Clients can access subsystem directly if needed
5. **Layered architecture** - Providing layer interface
6. **vs. Adapter** - Adapter makes interfaces compatible, Facade simplifies
7. **Real examples** - Home automation, e-commerce checkout, graphics libraries
8. **God object** - Facade shouldn't become too large

---

## Practice Problems

### Easy

1. **Payment Strategy** - Implement strategy pattern for different payment methods (credit card, PayPal, cash)
2. **Sorting Strategies** - Implement sorting with strategy pattern (bubble, quick, merge sort)
3. **Coffee Decorator** - Add toppings to coffee using decorator pattern
4. **Text Formatter** - Format text with decorators (bold, italic, underline)
5. **Simple Facade** - Create facade for pizza ordering system
6. **File System** - Implement simple composite pattern for file/directory structure

### Medium

1. **Report Generation** - Template method for different report types
2. **Database Adapter** - Adapter for different database systems
3. **Smart Home** - Bridge pattern for controlling devices
4. **UI Component Hierarchy** - Composite pattern for panels and controls
5. **Image Proxy** - Virtual proxy for lazy loading images
6. **Video Processing** - Strategy pattern for different video codecs
7. **Permission System** - Protection proxy for object access control

### Hard

1. **Configuration System** - Template method with configurable steps
2. **Event System** - Decorator pattern with event chaining
3. **Multi-DB Support** - Bridge pattern with multiple databases and drivers
4. **Complex UI** - Composite pattern with layout algorithms
5. **Remote Data Access** - Remote proxy with caching
6. **Plugin System** - Strategy pattern for dynamic plugin loading
7. **API Gateway** - Facade for multiple backend services

### Hard - Real World Scenarios

1. **Design a Payment System**
   - Multiple payment methods (credit card, wallet, crypto)
   - Use strategy pattern for algorithms
   - Support adding new payment methods
   - Handle payment processing, validation, logging

2. **Design a Game Engine**
   - Game loop using template method
   - Customizable update, render, input steps
   - Different game types (arcade, puzzle, rpg)
   - Extensible system for new game types

3. **Design a Database Connection Pool**
   - Support multiple database systems
   - Lazy initialization of connections
   - Virtual proxy for expensive connections
   - Protection proxy for access control

4. **Design a Document Format System**
   - Support multiple formats (PDF, Word, HTML)
   - Bridge pattern separating document concept from format
   - Adapter pattern for legacy format support
   - Composite pattern for document structure

5. **Design a Graphics System**
   - Shapes with different rendering engines
   - Bridge pattern for shape abstraction and rendering
   - Composite pattern for shape groups
   - Decorator pattern for styling and effects

6. **Design a Workflow Engine**
   - Template method for workflow execution
   - Customizable workflow steps
   - Strategy pattern for step implementations
   - Support branching and conditional steps

7. **Design a Caching System**
   - Proxy pattern for transparent caching
   - Different cache strategies
   - Strategy pattern for replacement policies
   - Support for cache invalidation

---

## Interview Questions Summary

### Conceptual Questions
- What problem does [pattern] solve?
- When would you use [pattern] instead of [alternative]?
- What are the tradeoffs of using [pattern]?
- How does [pattern] follow SOLID principles?
- Can you combine [pattern A] and [pattern B]?

### Implementation Questions
- Implement [pattern] for [specific scenario]
- How would you test code using [pattern]?
- What are the performance implications?
- How would you handle [edge case] with [pattern]?

### System Design Questions
- Design a [system] using patterns from this week
- How would you extend [system] with new functionality?
- What patterns would you use and why?
- How would you avoid over-engineering?

---

## Code Examples Location

All code examples are in `/home/user/hld-lld-course/LLD/examples/week3/`:

- `strategy_pattern.py` - Strategy pattern with payment, sorting, compression
- `template_pattern.py` - Template method with data mining, game, reports
- `adapter_pattern.py` - Adapter pattern with legacy, API, database adapters
- `decorator_pattern.py` - Decorator pattern with coffee, text, caching
- `bridge_pattern.py` - Bridge pattern with remote controls, database drivers
- `composite_pattern.py` - Composite pattern with file system, UI, hierarchy
- `proxy_pattern.py` - Proxy pattern with virtual, protection, remote, caching
- `facade_pattern.py` - Facade pattern with home theater, e-commerce, API

Each file contains:
- Multiple real-world examples
- Best practices and anti-patterns
- Runnable code with clear output
- Detailed comments and docstrings
- Key takeaways and learning points

---

## Comparison Matrix

| Pattern | Problem | Solution | Pros | Cons |
|---------|---------|----------|------|------|
| Strategy | Multiple algorithms | Encapsulate algorithms | Flexible, testable | Many classes |
| Template | Algorithm with variants | Define structure, vary steps | Code reuse, consistency | Inheritance-based |
| Adapter | Incompatible interfaces | Translate between interfaces | Reusability, compatibility | Extra layer |
| Decorator | Add behavior without subclassing | Wrap objects | Flexible, composable | Overhead, ordering |
| Bridge | Two axes of variation | Separate abstraction/impl | Independent variation | Complexity |
| Composite | Tree structures | Uniform component interface | Simple client code | Type safety |
| Proxy | Control access/defer init | Surrogate object | Lazy loading, access control | Transparency |
| Facade | Complex subsystems | Unified simple interface | Simplification, decoupling | Over-simplification |

---

## Next Steps

- Study pattern interactions (how patterns work together)
- Implement all patterns multiple times for fluency
- Refactor existing code to use patterns
- Think about patterns in frameworks you use
- Prepare for system design with pattern application

---

## References for Further Learning

- Design Patterns by Gang of Four (classic reference)
- Refactoring: Improving the Design of Existing Code
- Head First Design Patterns (excellent visual guide)
- Pattern-oriented Software Architecture (enterprise patterns)
- Architectural Patterns (high-level pattern thinking)
