# Dry Run: Singleton Pattern Execution

This document traces the step-by-step execution of singleton pattern implementations, showing exactly what happens in memory and how the single instance guarantee is maintained.

## Scenario 1: Basic Singleton - First Access

**Code:**
```python
db1 = DatabaseConnection.get_instance()
```

### Initial State
```
DatabaseConnection class:
  _instance = None
  _lock = <not used in basic version>

Memory:
  (no DatabaseConnection instances exist)
```

### Execution Steps

**Step 1: Call get_instance()**
```
Execution: DatabaseConnection.get_instance()
Action: Check if _instance is None
```

**Step 2: Check condition**
```
Condition: cls._instance is None
Result: True (no instance exists yet)
Action: Proceed to create instance
```

**Step 3: Create instance**
```
Execution: cls._instance = DatabaseConnection()
Action: Call __init__() constructor
```

**Step 4: Initialize instance**
```
Inside __init__():
  - Check if _instance is not None: False (we just set it)
  - Set self.host = "localhost"
  - Set self.port = 5432
  - Set self.database = "myapp_db"
  - Set self.connected = False
  - Set self.connection_count = 0
  - Print creation message
```

**Step 5: Store and return**
```
DatabaseConnection._instance = DatabaseConnection object at 0x7f8a1c
Return: DatabaseConnection object at 0x7f8a1c
```

### Final State After Step 5
```
DatabaseConnection class:
  _instance = DatabaseConnection@0x7f8a1c

db1 = DatabaseConnection@0x7f8a1c

Memory:
  DatabaseConnection@0x7f8a1c:
    host = "localhost"
    port = 5432
    database = "myapp_db"
    connected = False
    connection_count = 0
```

## Scenario 2: Basic Singleton - Second Access

**Code:**
```python
db2 = DatabaseConnection.get_instance()
```

### Initial State
```
DatabaseConnection class:
  _instance = DatabaseConnection@0x7f8a1c (from previous scenario)

db1 = DatabaseConnection@0x7f8a1c
```

### Execution Steps

**Step 1: Call get_instance()**
```
Execution: DatabaseConnection.get_instance()
Action: Check if _instance is None
```

**Step 2: Check condition**
```
Condition: cls._instance is None
Result: False (instance already exists!)
Action: Skip instance creation
```

**Step 3: Return existing instance**
```
Return: cls._instance (which is DatabaseConnection@0x7f8a1c)
```

### Final State After Step 3
```
DatabaseConnection class:
  _instance = DatabaseConnection@0x7f8a1c

db1 = DatabaseConnection@0x7f8a1c
db2 = DatabaseConnection@0x7f8a1c (same object!)

Memory:
  DatabaseConnection@0x7f8a1c:
    host = "localhost"
    port = 5432
    database = "myapp_db"
    connected = False
    connection_count = 0

Note: Only ONE object in memory, referenced by both db1 and db2
```

## Scenario 3: Shared State Verification

**Code:**
```python
db1.connect()
print(db2.connected)
```

### Initial State
```
db1 = DatabaseConnection@0x7f8a1c
db2 = DatabaseConnection@0x7f8a1c (same object)

DatabaseConnection@0x7f8a1c:
  connected = False
```

### Execution Steps

**Step 1: Call db1.connect()**
```
Execution: db1.connect()
Object: DatabaseConnection@0x7f8a1c
Action: Check if self.connected is False
```

**Step 2: Modify state**
```
Condition: not self.connected
Result: True
Action: Set self.connected = True
Action: Increment self.connection_count by 1
Action: Print connection message
```

**Step 3: Check state via db2**
```
Execution: print(db2.connected)
Object: DatabaseConnection@0x7f8a1c (same object!)
Value: True (changed by db1!)
```

### Final State After Step 3
```
db1 = DatabaseConnection@0x7f8a1c
db2 = DatabaseConnection@0x7f8a1c

DatabaseConnection@0x7f8a1c:
  connected = True  (modified)
  connection_count = 1  (modified)

Key insight: db1 and db2 see the same state because they ARE the same object
```

## Scenario 4: Thread-Safe Singleton - Concurrent Access

**Code:**
```python
# Thread 1 and Thread 2 call simultaneously
instance1 = ThreadSafeSingleton.get_instance()
instance2 = ThreadSafeSingleton.get_instance()
```

### Initial State
```
ThreadSafeSingleton class:
  _instance = None
  _lock = Lock (unlocked)

Thread 1: About to call get_instance()
Thread 2: About to call get_instance()
```

### Execution Timeline

**Time T0: Thread 1 starts**
```
Thread 1:
  - Execution: ThreadSafeSingleton.get_instance()
  - Action: Attempt to acquire _lock
  - Result: Lock acquired successfully
  - Status: Entering synchronized block
```

**Time T1: Thread 2 starts (overlapping with Thread 1)**
```
Thread 2:
  - Execution: ThreadSafeSingleton.get_instance()
  - Action: Attempt to acquire _lock
  - Result: Lock already held by Thread 1
  - Status: BLOCKED, waiting for lock
```

**Time T2: Thread 1 in critical section**
```
Thread 1 (inside lock):
  - Check: cls._instance is None
  - Result: True
  - Action: Create new instance
  - Execution: cls._instance = ThreadSafeSingleton()
  - Instance created at: 0x7f9b2d
  - Action: About to release lock

Thread 2:
  - Status: Still blocked, waiting
```

**Time T3: Thread 1 releases lock**
```
Thread 1:
  - Action: Exit lock context (with statement ends)
  - Lock status: Released
  - Return: ThreadSafeSingleton@0x7f9b2d

Thread 2:
  - Action: Lock becomes available
  - Status: Acquires lock, enters critical section
```

**Time T4: Thread 2 in critical section**
```
Thread 2 (inside lock):
  - Check: cls._instance is None
  - Result: False (Thread 1 already created it!)
  - Action: Skip instance creation
  - Return: cls._instance (ThreadSafeSingleton@0x7f9b2d)
  - Action: Release lock
```

### Final State After T4
```
ThreadSafeSingleton class:
  _instance = ThreadSafeSingleton@0x7f9b2d
  _lock = Lock (unlocked)

Thread 1: instance1 = ThreadSafeSingleton@0x7f9b2d
Thread 2: instance2 = ThreadSafeSingleton@0x7f9b2d

Memory:
  ThreadSafeSingleton@0x7f9b2d (ONE object, two references)
    created_by_thread = "Thread-1"
    access_count = 2
```

## Scenario 5: Double-Checked Locking Optimization

**Code:**
```python
# After instance exists
instance = DoubleCheckedLockingSingleton.get_instance()
```

### Initial State
```
DoubleCheckedLockingSingleton class:
  _instance = DoubleCheckedLockingSingleton@0x7f8c3e (already created)
  _lock = Lock (unlocked)
```

### Execution Steps (Fast Path)

**Step 1: First check (outside lock)**
```
Execution: if cls._instance is None
Check: Is None?
Result: False (instance already exists)
Action: Skip the entire lock block
Performance: No lock acquisition needed!
```

**Step 2: Increment access count and return**
```
Execution: cls._instance.access_count += 1
Action: Return cls._instance
Return: DoubleCheckedLockingSingleton@0x7f8c3e
```

### Comparison: Simple Lock vs Double-Checked

**Simple Locking Path:**
```
1. Acquire lock (expensive)
2. Check if instance exists
3. Return instance
4. Release lock
Total operations: 4 (including lock/unlock overhead)
```

**Double-Checked Locking Path (when instance exists):**
```
1. Check if instance exists (fast)
2. Return instance
Total operations: 2 (no lock overhead)
```

### Performance Impact
```
For 100,000 accesses after instance creation:
  Simple locking: 100,000 lock acquisitions
  Double-checked: 1 lock acquisition (only during creation)

Speed difference: ~2-3x faster for double-checked approach
```

## Key Insights from Dry Runs

1. **Single Instance Guarantee:**
   - Only one object created in memory
   - All variables point to same memory address
   - State changes visible through all references

2. **Thread Safety Mechanism:**
   - Lock prevents concurrent instance creation
   - Only first thread creates instance
   - Subsequent threads skip creation

3. **Performance Trade-off:**
   - Simple locking: Safe but locks every access
   - Double-checked: Safe and locks only during creation
   - Choose based on access frequency

4. **Memory Model:**
   - Class-level variable stores the instance
   - Instance lives for application lifetime
   - All callers share same object reference
