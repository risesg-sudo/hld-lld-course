"""
Iterator Pattern - Provide sequential access to collection elements without exposing structure.

This module demonstrates various iterator implementations:
1. Custom iterator for simple list
2. Bidirectional iterator
3. Tree traversal iterators (DFS, BFS)
4. Generator-based iterators (Pythonic)
5. Lazy iterators (compute on-demand)
6. Filtering and mapping iterators

Key Learning Points:
- Iterator provides uniform interface for different collections
- Encapsulates traversal logic
- Collection structure hidden from client
- Multiple iterators can exist simultaneously
- Python generators provide simple iterator implementation
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Iterator as IteratorType, Callable
from collections import deque


# ============================================================================
# 1. CUSTOM ITERATOR FOR SIMPLE LIST
# ============================================================================

class Iterator(ABC):
    """Abstract iterator interface."""

    @abstractmethod
    def has_next(self) -> bool:
        """Check if more elements exist."""
        pass

    @abstractmethod
    def next(self) -> Any:
        """Get next element."""
        pass

    @abstractmethod
    def reset(self):
        """Reset iterator to beginning."""
        pass


class Collection(ABC):
    """Abstract collection interface."""

    @abstractmethod
    def create_iterator(self) -> Iterator:
        """Create iterator for collection."""
        pass


class ArrayCollection(Collection):
    """
    Collection implemented as array/list.
    """

    def __init__(self):
        self.items: List[Any] = []

    def add_item(self, item: Any):
        """Add item to collection."""
        self.items.append(item)

    def create_iterator(self) -> "ArrayIterator":
        """Create iterator for array."""
        return ArrayIterator(self)

    def __len__(self):
        return len(self.items)


class ArrayIterator(Iterator):
    """
    Iterator for array collection.

    Maintains internal state (current position) separately from collection.
    Multiple iterators can iterate simultaneously without interfering.
    """

    def __init__(self, collection: ArrayCollection):
        self.collection = collection
        self.index = 0

    def has_next(self) -> bool:
        """Check if more elements."""
        return self.index < len(self.collection.items)

    def next(self) -> Any:
        """Get next element."""
        if self.has_next():
            item = self.collection.items[self.index]
            self.index += 1
            return item
        raise StopIteration("No more items")

    def reset(self):
        """Reset to beginning."""
        self.index = 0

    def __iter__(self):
        """Make iterator iterable."""
        return self

    def __next__(self):
        """Python iterator protocol."""
        if self.has_next():
            return self.next()
        raise StopIteration()


# ============================================================================
# 2. BIDIRECTIONAL ITERATOR
# ============================================================================

class BidirectionalIterator(Iterator):
    """
    Iterator that can move forward and backward.
    """

    def __init__(self, collection: ArrayCollection):
        self.collection = collection
        self.index = 0

    def has_next(self) -> bool:
        """Check if next element exists."""
        return self.index < len(self.collection.items)

    def has_previous(self) -> bool:
        """Check if previous element exists."""
        return self.index > 0

    def next(self) -> Any:
        """Get next element and advance."""
        if self.has_next():
            item = self.collection.items[self.index]
            self.index += 1
            return item
        raise StopIteration()

    def previous(self) -> Any:
        """Get previous element and move back."""
        if self.has_previous():
            self.index -= 1
            return self.collection.items[self.index]
        raise StopIteration()

    def reset(self):
        """Reset to beginning."""
        self.index = 0

    def reset_to_end(self):
        """Reset to end (for backward iteration)."""
        self.index = len(self.collection.items)


# ============================================================================
# 3. TREE TRAVERSAL ITERATORS
# ============================================================================

class TreeNode:
    """Binary tree node."""

    def __init__(self, value: Any):
        self.value = value
        self.left: Optional[TreeNode] = None
        self.right: Optional[TreeNode] = None

    def __str__(self):
        return f"TreeNode({self.value})"


class Tree:
    """Binary tree with different traversal iterators."""

    def __init__(self, root: TreeNode):
        self.root = root

    def create_dfs_iterator(self) -> "DFSIterator":
        """Create depth-first search iterator."""
        return DFSIterator(self.root)

    def create_bfs_iterator(self) -> "BFSIterator":
        """Create breadth-first search iterator."""
        return BFSIterator(self.root)

    def create_inorder_iterator(self) -> "InorderIterator":
        """Create in-order traversal iterator."""
        return InorderIterator(self.root)

    def create_preorder_iterator(self) -> "PreorderIterator":
        """Create pre-order traversal iterator."""
        return PreorderIterator(self.root)

    def create_postorder_iterator(self) -> "PostorderIterator":
        """Create post-order traversal iterator."""
        return PostorderIterator(self.root)


class DFSIterator(Iterator):
    """
    Depth-first search iterator using stack.

    Traversal order: Root -> Left -> Right (and depth first)
    """

    def __init__(self, root: Optional[TreeNode]):
        self.stack: List[TreeNode] = []
        if root:
            self.stack.append(root)

    def has_next(self) -> bool:
        """Check if more nodes."""
        return len(self.stack) > 0

    def next(self) -> TreeNode:
        """Get next node (DFS order)."""
        if not self.has_next():
            raise StopIteration()

        node = self.stack.pop()
        # Push right then left (so left is popped first)
        if node.right:
            self.stack.append(node.right)
        if node.left:
            self.stack.append(node.left)
        return node

    def reset(self):
        """Reset iterator."""
        self.__init__(self.stack[0] if self.stack else None)


class BFSIterator(Iterator):
    """
    Breadth-first search iterator using queue.

    Traversal level by level.
    """

    def __init__(self, root: Optional[TreeNode]):
        self.queue: deque = deque()
        if root:
            self.queue.append(root)

    def has_next(self) -> bool:
        """Check if more nodes."""
        return len(self.queue) > 0

    def next(self) -> TreeNode:
        """Get next node (BFS order)."""
        if not self.has_next():
            raise StopIteration()

        node = self.queue.popleft()
        if node.left:
            self.queue.append(node.left)
        if node.right:
            self.queue.append(node.right)
        return node

    def reset(self):
        """Reset iterator."""
        self.__init__(self.queue[0] if self.queue else None)


class InorderIterator(Iterator):
    """In-order traversal: Left -> Root -> Right."""

    def __init__(self, root: Optional[TreeNode]):
        self.stack: List[TreeNode] = []
        self.current = root
        self._build_stack()

    def _build_stack(self):
        """Build stack for in-order traversal."""
        while self.current:
            self.stack.append(self.current)
            self.current = self.current.left

    def has_next(self) -> bool:
        """Check if more nodes."""
        return len(self.stack) > 0

    def next(self) -> TreeNode:
        """Get next node."""
        if not self.has_next():
            raise StopIteration()

        node = self.stack.pop()
        if node.right:
            self.current = node.right
            self._build_stack()
        return node

    def reset(self):
        """Reset iterator."""
        self.__init__(self.stack[0] if self.stack else None)


class PreorderIterator(Iterator):
    """Pre-order traversal: Root -> Left -> Right."""

    def __init__(self, root: Optional[TreeNode]):
        self.stack: List[TreeNode] = []
        if root:
            self.stack.append(root)

    def has_next(self) -> bool:
        """Check if more nodes."""
        return len(self.stack) > 0

    def next(self) -> TreeNode:
        """Get next node."""
        if not self.has_next():
            raise StopIteration()

        node = self.stack.pop()
        if node.right:
            self.stack.append(node.right)
        if node.left:
            self.stack.append(node.left)
        return node

    def reset(self):
        """Reset iterator."""
        pass


class PostorderIterator(Iterator):
    """Post-order traversal: Left -> Right -> Root."""

    def __init__(self, root: Optional[TreeNode]):
        self.stack: List[TreeNode] = []
        self.last_visited: Optional[TreeNode] = None
        self.current = root
        self._build_stack()

    def _build_stack(self):
        """Build stack for post-order traversal."""
        while self.current:
            self.stack.append(self.current)
            self.current = self.current.left

    def has_next(self) -> bool:
        """Check if more nodes."""
        return len(self.stack) > 0

    def next(self) -> TreeNode:
        """Get next node."""
        if not self.has_next():
            raise StopIteration()

        current = self.stack[-1]

        # If right child exists and not yet visited
        if current.right and self.last_visited != current.right:
            self.current = current.right
            self._build_stack()
        else:
            node = self.stack.pop()
            self.last_visited = node
            return node

    def reset(self):
        """Reset iterator."""
        pass


# ============================================================================
# 4. GENERATOR-BASED ITERATORS (Pythonic)
# ============================================================================

class GeneratorCollection:
    """Collection using Python generators (most Pythonic way)."""

    def __init__(self):
        self.items: List[Any] = []

    def add_item(self, item: Any):
        """Add item."""
        self.items.append(item)

    def __iter__(self):
        """Make collection iterable (generator)."""
        for item in self.items:
            yield item

    def reverse_iter(self) -> IteratorType:
        """Reverse iterator using generator."""
        for item in reversed(self.items):
            yield item

    def filter_iter(self, predicate: Callable) -> IteratorType:
        """Filter iterator using generator."""
        for item in self.items:
            if predicate(item):
                yield item


# ============================================================================
# 5. LAZY ITERATORS (Compute on-demand)
# ============================================================================

class LazyIterator:
    """
    Iterator that computes elements on-demand.

    Useful for:
    - Large datasets (don't load all in memory)
    - Expensive computations
    - Infinite sequences
    - Remote data sources
    """

    def __init__(self, data_source: Callable):
        """
        Create lazy iterator.

        Args:
            data_source: Function that returns next element
        """
        self.data_source = data_source
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            value = self.data_source(self.index)
            self.index += 1
            return value
        except StopIteration:
            raise


class RangeIterator:
    """
    Iterator for range of numbers (lazy).

    Similar to Python's range() - doesn't store all numbers in memory.
    """

    def __init__(self, start: int, end: int, step: int = 1):
        self.current = start
        self.end = end
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        if (self.step > 0 and self.current >= self.end) or \
           (self.step < 0 and self.current <= self.end):
            raise StopIteration()

        value = self.current
        self.current += self.step
        return value


class FibonacciIterator:
    """Iterator for Fibonacci sequence (lazy, infinite)."""

    def __init__(self, limit: Optional[int] = None):
        self.a, self.b = 0, 1
        self.count = 0
        self.limit = limit

    def __iter__(self):
        return self

    def __next__(self):
        if self.limit and self.count >= self.limit:
            raise StopIteration()

        value = self.a
        self.a, self.b = self.b, self.a + self.b
        self.count += 1
        return value


# ============================================================================
# 6. FILTERING AND MAPPING ITERATORS
# ============================================================================

class FilterIterator:
    """Iterator that filters elements based on predicate."""

    def __init__(self, iterator: IteratorType, predicate: Callable):
        self.iterator = iterator
        self.predicate = predicate

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            value = next(self.iterator)
            if self.predicate(value):
                return value


class MapIterator:
    """Iterator that transforms elements."""

    def __init__(self, iterator: IteratorType, transform: Callable):
        self.iterator = iterator
        self.transform = transform

    def __iter__(self):
        return self

    def __next__(self):
        value = next(self.iterator)
        return self.transform(value)


# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

def test_simple_iterator():
    """Test simple custom iterator."""
    print("\n" + "="*70)
    print("TEST 1: SIMPLE CUSTOM ITERATOR")
    print("="*70)

    # Create collection
    collection = ArrayCollection()
    for i in range(1, 6):
        collection.add_item(f"Item {i}")

    # Create iterator
    iterator = collection.create_iterator()

    print("Iterating forward:")
    while iterator.has_next():
        print(f"  {iterator.next()}")

    # Reset and iterate again
    print("\nIterating again after reset:")
    iterator.reset()
    while iterator.has_next():
        print(f"  {iterator.next()}")

    # Multiple iterators simultaneously
    print("\nMultiple iterators simultaneously:")
    iter1 = collection.create_iterator()
    iter2 = collection.create_iterator()

    print(f"  Iter1: {iter1.next()}, Iter2: {iter2.next()}")
    print(f"  Iter1: {iter1.next()}, Iter2: {iter2.next()}")


def test_bidirectional_iterator():
    """Test bidirectional iterator."""
    print("\n" + "="*70)
    print("TEST 2: BIDIRECTIONAL ITERATOR")
    print("="*70)

    collection = ArrayCollection()
    for i in range(1, 6):
        collection.add_item(f"Item {i}")

    iterator = BidirectionalIterator(collection)

    print("Forward iteration:")
    while iterator.has_next():
        print(f"  {iterator.next()}")

    print("\nBackward iteration:")
    while iterator.has_previous():
        print(f"  {iterator.previous()}")


def test_tree_dfs_bfs():
    """Test tree traversal iterators."""
    print("\n" + "="*70)
    print("TEST 3: TREE TRAVERSAL (DFS vs BFS)")
    print("="*70)

    # Create tree:
    #        1
    #       / \
    #      2   3
    #     / \
    #    4   5

    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)

    tree = Tree(root)

    print("DFS (Depth-First):")
    dfs = tree.create_dfs_iterator()
    while dfs.has_next():
        print(f"  {dfs.next().value}")

    print("\nBFS (Breadth-First):")
    bfs = tree.create_bfs_iterator()
    while bfs.has_next():
        print(f"  {bfs.next().value}")


def test_tree_inorder_preorder_postorder():
    """Test different tree traversals."""
    print("\n" + "="*70)
    print("TEST 4: TREE TRAVERSAL ORDERS")
    print("="*70)

    # Create tree:
    #        1
    #       / \
    #      2   3
    #     / \
    #    4   5

    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)

    tree = Tree(root)

    print("In-order (Left -> Root -> Right):")
    inorder = tree.create_inorder_iterator()
    result = []
    while inorder.has_next():
        node = inorder.next()
        result.append(node.value)
        print(f"  {node.value}")
    print(f"Sequence: {result}")

    print("\nPre-order (Root -> Left -> Right):")
    preorder = tree.create_preorder_iterator()
    result = []
    while preorder.has_next():
        node = preorder.next()
        result.append(node.value)
        print(f"  {node.value}")
    print(f"Sequence: {result}")

    print("\nPost-order (Left -> Right -> Root):")
    postorder = tree.create_postorder_iterator()
    result = []
    while postorder.has_next():
        node = postorder.next()
        result.append(node.value)
        print(f"  {node.value}")
    print(f"Sequence: {result}")


def test_generator_iterator():
    """Test Pythonic generator-based iterators."""
    print("\n" + "="*70)
    print("TEST 5: GENERATOR-BASED ITERATORS (Pythonic)")
    print("="*70)

    collection = GeneratorCollection()
    for i in range(1, 6):
        collection.add_item(f"Item {i}")

    print("Forward (using for loop):")
    for item in collection:
        print(f"  {item}")

    print("\nReverse:")
    for item in collection.reverse_iter():
        print(f"  {item}")

    print("\nFiltered (only even indices):")
    for i, item in enumerate(collection.filter_iter(lambda x: int(x.split()[1]) % 2 == 0)):
        print(f"  {item}")


def test_lazy_iterator():
    """Test lazy iterators."""
    print("\n" + "="*70)
    print("TEST 6: LAZY ITERATORS")
    print("="*70)

    # Lazy range iterator
    print("Lazy range (1-10):")
    for num in RangeIterator(1, 10):
        print(f"  {num}")

    # Fibonacci iterator
    print("\nFibonacci (first 10 numbers):")
    fib = FibonacciIterator(limit=10)
    for num in fib:
        print(f"  {num}")

    # Lazy data source
    print("\nLazy computation (squares of 1-5):")
    def data_source(index):
        if index >= 5:
            raise StopIteration()
        return (index + 1) ** 2

    lazy = LazyIterator(data_source)
    for value in lazy:
        print(f"  {value}")


def test_chaining_iterators():
    """Test chaining filter and map iterators."""
    print("\n" + "="*70)
    print("TEST 7: CHAINING ITERATORS")
    print("="*70)

    # Create base range iterator
    base_iter = RangeIterator(1, 10)

    # Filter: keep only even numbers
    filtered = FilterIterator(base_iter, lambda x: x % 2 == 0)

    # Map: square the numbers
    mapped = MapIterator(filtered, lambda x: x ** 2)

    print("Chain: Range(1-10) -> Filter(even) -> Map(square):")
    for value in mapped:
        print(f"  {value}")


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

def print_key_takeaways():
    """Print key learning points."""
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. ITERATOR ENCAPSULATES TRAVERSAL LOGIC
   Benefits:
   - Collection structure hidden
   - Uniform interface for different collections
   - Traversal logic in one place
   - Client code simplified

2. MULTIPLE ITERATORS SIMULTANEOUSLY
   - Different iterators on same collection
   - Each maintains own state (position)
   - No interference between iterators
   - Useful for nested loops

3. GENERATOR-BASED ITERATORS (Pythonic)
   Most Pythonic approach:
   - Use Python generators (yield)
   - Implements __iter__ and __next__
   - Works with for loops
   - Simpler than custom iterator classes

4. TREE TRAVERSAL ITERATORS
   Different orders:
   - DFS (depth-first) - explores deep first
   - BFS (breadth-first) - explores level by level
   - In-order - Left, Root, Right (binary search tree)
   - Pre-order - Root, Left, Right (clone tree)
   - Post-order - Left, Right, Root (delete tree)

5. LAZY ITERATORS (Compute on-demand)
   Benefits:
   - Don't load all data in memory
   - Compute elements when needed
   - Infinite sequences possible
   - Good for large datasets

6. FILTERING AND MAPPING ITERATORS
   Functional approach:
   - Filter: keep elements matching predicate
   - Map: transform elements
   - Can chain together
   - Lazy evaluation (modern frameworks)

7. WHEN TO USE ITERATOR PATTERN
   - Different traversal orders for same collection
   - Hide internal data structure
   - Multiple concurrent iterations
   - Lazy evaluation needed
   - Custom iteration logic

8. PYTHON ALTERNATIVES
   - For loops on __iter__
   - Generator functions (yield)
   - itertools module
   - List comprehensions
   - map() and filter() built-ins

9. BIDIRECTIONAL ITERATION
   Use cases:
   - Back navigation (browser)
   - Undo/redo systems
   - Cursor-based navigation
   - Requires: previous(), has_previous()

10. PERFORMANCE CONSIDERATIONS
    - Each iterator has memory overhead
    - Tree traversal efficiency varies
    - BFS uses queue (more memory)
    - DFS uses stack (less memory)
    - Lazy iterators save memory
    - Caching can improve performance

11. REAL-WORLD EXAMPLES
    - Database cursors (lazy loading)
    - File readers (read line by line)
    - API pagination (lazy loading pages)
    - Tree/graph traversal
    - Directory traversal
    - Stream processing
    - Event streams
    """)


if __name__ == "__main__":
    test_simple_iterator()
    test_bidirectional_iterator()
    test_tree_dfs_bfs()
    test_tree_inorder_preorder_postorder()
    test_generator_iterator()
    test_lazy_iterator()
    test_chaining_iterators()
    print_key_takeaways()
