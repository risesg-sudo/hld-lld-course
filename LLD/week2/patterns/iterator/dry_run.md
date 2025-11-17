# Dry Run: Iterator Pattern Execution

## Scenario: BFS Tree Traversal

**Tree:**
```
       1
      / \
     2   3
    / \
   4   5
```

**Code:**
```python
bfs = BFSIterator(root)
while bfs.has_next():
    node = bfs.next()
    print(node.value)
```

### Step 1: Create BFS Iterator

```
Execution: BFSIterator(root)

Initialize:
  self.queue = deque()
  
Check: root is not None? Yes
Action: queue.append(root)

State:
  queue = deque([TreeNode(1)])
```

### Step 2: First Iteration

```
Execution: bfs.has_next()
  Check: len(queue) > 0? Yes (length = 1)
  Returns: True

Execution: bfs.next()
  
  Step 2a: Dequeue node
    node = queue.popleft()
    node = TreeNode(1)
    queue = deque([])
  
  Step 2b: Add children to queue
    Check: node.left exists? Yes (TreeNode(2))
    Action: queue.append(TreeNode(2))
    
    Check: node.right exists? Yes (TreeNode(3))
    Action: queue.append(TreeNode(3))
  
  Step 2c: Return node
    Returns: TreeNode(1)

State after first iteration:
  queue = deque([TreeNode(2), TreeNode(3)])
  Output: 1
```

### Step 3: Second Iteration

```
Execution: bfs.has_next()
  Returns: True (queue has 2 elements)

Execution: bfs.next()
  
  Dequeue: TreeNode(2)
  queue = deque([TreeNode(3)])
  
  Add children:
    Left: TreeNode(4) -> queue.append
    Right: TreeNode(5) -> queue.append
  
  Returns: TreeNode(2)

State:
  queue = deque([TreeNode(3), TreeNode(4), TreeNode(5)])
  Output: 2
```

### Step 4: Third Iteration

```
Execution: bfs.next()
  
  Dequeue: TreeNode(3)
  queue = deque([TreeNode(4), TreeNode(5)])
  
  Add children:
    Left: None
    Right: None
  
  Returns: TreeNode(3)

State:
  queue = deque([TreeNode(4), TreeNode(5)])
  Output: 3
```

### Step 5: Fourth Iteration

```
Execution: bfs.next()
  
  Dequeue: TreeNode(4)
  No children
  Returns: TreeNode(4)

State:
  queue = deque([TreeNode(5)])
  Output: 4
```

### Step 6: Fifth Iteration

```
Execution: bfs.next()
  
  Dequeue: TreeNode(5)
  No children
  Returns: TreeNode(5)

State:
  queue = deque([])
  Output: 5
```

### Step 7: End of Iteration

```
Execution: bfs.has_next()
  Check: len(queue) > 0? No (empty)
  Returns: False

Loop terminates
```

## Complete Output Sequence

```
1 -> 2 -> 3 -> 4 -> 5

This is level-order traversal:
  Level 0: 1
  Level 1: 2, 3
  Level 2: 4, 5
```

## Key Insights

1. **Queue enables BFS:**
   - FIFO ensures level-by-level traversal
   - Process parent before children
   - Add children from left to right

2. **Iterator State:**
   - Queue maintains iteration state
   - Independent of tree structure
   - Multiple iterators possible

3. **Uniform Interface:**
   - Client uses has_next() and next()
   - Doesn't know about queue internally
   - Could swap for DFS without changing client code
