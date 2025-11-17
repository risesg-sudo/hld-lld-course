# Iterator Pattern

## The Hook: Traversing Different Collections

How do you iterate through a list, a tree, and a graph using the same approach? Each has different internal structures. Lists are linear, trees are hierarchical, graphs have cycles. Yet you want uniform iteration.

This is the Iterator pattern: provide a way to access collection elements sequentially without exposing underlying structure.

## The Problem: Collection-Specific Traversal

Different collections need different traversal logic:
- Arrays: index-based access
- Linked lists: node-by-node traversal
- Trees: DFS, BFS, in-order, pre-order, post-order
- Graphs: cycle-aware traversal

**Without Iterator:**
- Client code knows collection internals
- Different traversal code for each collection
- Can't change internal structure without breaking clients
- Hard to traverse same collection multiple ways

## The Solution: Abstract Iteration

Separate traversal logic into iterator objects with uniform interface.

**Key Components:**
- Iterator: Interface with has_next() and next()
- Concrete Iterators: Implement traversal for specific collection
- Collection: Creates appropriate iterator

**When to Use:**
- Need uniform access to different collections
- Want to hide collection structure
- Support multiple traversal algorithms
- Enable concurrent iteration

**Common Applications:**
- Tree traversal (DFS, BFS, in-order)
- Database result sets
- File system navigation
- Graph traversal
- Stream processing

## Trade-offs

**Gains:**
- Uniform interface for different collections
- Hides collection internals
- Multiple iterators on same collection
- Can change collection without breaking clients

**Losses:**
- Additional iterator classes needed
- Overhead for simple collections
- State management complexity
- Concurrent modification issues

## The Verdict

Iterator is fundamental to modern languages (Python's for loop, Java's Iterator). It provides clean, uniform collection access. Essential for complex traversals like tree/graph algorithms. Python generators make iterators trivial to implement.
