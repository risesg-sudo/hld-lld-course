"""
Tree Traversal using Iterator Pattern

Demonstrates different traversal strategies for same tree structure.
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import Optional, List


class TreeNode:
    """Binary tree node."""
    
    def __init__(self, value: int):
        self.value = value
        self.left: Optional[TreeNode] = None
        self.right: Optional[TreeNode] = None


class Iterator(ABC):
    """Abstract iterator interface."""
    
    @abstractmethod
    def has_next(self) -> bool:
        """Check if more elements exist."""
        pass
    
    @abstractmethod
    def next(self) -> TreeNode:
        """Get next element."""
        pass


class BFSIterator(Iterator):
    """
    Breadth-First Search iterator.
    
    Traverses tree level by level using a queue.
    """
    
    def __init__(self, root: Optional[TreeNode]):
        self.queue = deque()
        if root:
            self.queue.append(root)
    
    def has_next(self) -> bool:
        """Check if more nodes exist."""
        return len(self.queue) > 0
    
    def next(self) -> TreeNode:
        """Get next node in BFS order."""
        if not self.has_next():
            raise StopIteration()
        
        node = self.queue.popleft()
        
        # Add children to queue
        if node.left:
            self.queue.append(node.left)
        if node.right:
            self.queue.append(node.right)
        
        return node


class DFSIterator(Iterator):
    """
    Depth-First Search iterator.
    
    Traverses tree depth-first using a stack.
    """
    
    def __init__(self, root: Optional[TreeNode]):
        self.stack: List[TreeNode] = []
        if root:
            self.stack.append(root)
    
    def has_next(self) -> bool:
        """Check if more nodes exist."""
        return len(self.stack) > 0
    
    def next(self) -> TreeNode:
        """Get next node in DFS order."""
        if not self.has_next():
            raise StopIteration()
        
        node = self.stack.pop()
        
        # Add children to stack (right first so left is popped first)
        if node.right:
            self.stack.append(node.right)
        if node.left:
            self.stack.append(node.left)
        
        return node


class InOrderIterator(Iterator):
    """
    In-order iterator: Left -> Root -> Right.
    
    For binary search trees, yields values in sorted order.
    """
    
    def __init__(self, root: Optional[TreeNode]):
        self.stack: List[TreeNode] = []
        self.current = root
        self._build_left_stack()
    
    def _build_left_stack(self):
        """Push all left children onto stack."""
        while self.current:
            self.stack.append(self.current)
            self.current = self.current.left
    
    def has_next(self) -> bool:
        """Check if more nodes exist."""
        return len(self.stack) > 0
    
    def next(self) -> TreeNode:
        """Get next node in in-order."""
        if not self.has_next():
            raise StopIteration()
        
        node = self.stack.pop()
        
        # Move to right subtree
        if node.right:
            self.current = node.right
            self._build_left_stack()
        
        return node


def demonstrate():
    """Demonstrate different tree traversals."""
    print("="*70)
    print("TREE TRAVERSAL ITERATORS")
    print("="*70)
    
    # Create tree:
    #       1
    #      / \
    #     2   3
    #    / \
    #   4   5
    
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)
    
    print("\nTree structure:")
    print("       1")
    print("      / \\")
    print("     2   3")
    print("    / \\")
    print("   4   5")
    
    # BFS traversal
    print("\n1. BFS (level by level):")
    bfs = BFSIterator(root)
    result = []
    while bfs.has_next():
        node = bfs.next()
        result.append(node.value)
        print(f"   {node.value}")
    print(f"   Sequence: {result}")
    
    # DFS traversal
    print("\n2. DFS (depth first):")
    dfs = DFSIterator(root)
    result = []
    while dfs.has_next():
        node = dfs.next()
        result.append(node.value)
        print(f"   {node.value}")
    print(f"   Sequence: {result}")
    
    # In-order traversal
    print("\n3. In-order (Left-Root-Right):")
    inorder = InOrderIterator(root)
    result = []
    while inorder.has_next():
        node = inorder.next()
        result.append(node.value)
        print(f"   {node.value}")
    print(f"   Sequence: {result}")


if __name__ == "__main__":
    demonstrate()
    print("\n" + "="*70)
    print("KEY POINTS")
    print("="*70)
    print("""
1. Same tree, different traversal strategies
2. Each iterator encapsulates traversal logic
3. Client uses uniform interface (has_next/next)
4. Tree structure hidden from client
5. Can create custom iterators for any traversal order
    """)
