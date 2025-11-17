# Prototype Pattern

## The Hook: The Cost of Creation

What if creating an object from scratch takes 5 seconds because it requires database queries, file I/O, and complex calculations? What if you need to create 1000 similar objects? That's 5000 seconds, or over an hour of waiting.

Now imagine you could clone an existing, pre-configured object in milliseconds. That's the promise of the Prototype pattern.

## The Problem: Expensive Object Creation

Creating objects can be expensive when they require:
- Database queries to fetch initialization data
- Network calls to remote services  
- Complex calculations or data processing
- File I/O operations
- Resource allocation (connections, handles)

Repeating this initialization for similar objects wastes time and resources.

## The Solution: Clone Instead of Create

The Prototype pattern specifies object creation using a prototypical instance. Instead of creating from scratch, you clone an existing object.

**Key Mechanism:**
- Shallow Copy: Copies object's own attributes, shares nested objects
- Deep Copy: Recursively copies all nested objects

**When to Use:**
- Object creation is expensive
- Need many variations of similar objects
- Want to avoid subclass explosion
- Object pool implementations

## Trade-offs

**Gains:**
- Faster than creating from scratch (sometimes)
- Avoid repeating expensive initialization
- Reduce subclass proliferation

**Losses:**
- Deep cloning complexity with circular references
- Not always faster (measure first!)
- Shallow vs deep copy confusion
- Memory overhead during cloning

## The Verdict

Prototype is valuable when object initialization is genuinely expensive. But measure before optimizing - cloning isn't always faster than construction. Use for caching, templates, and object pools where you've verified the performance benefit.
