# Dry Run: Prototype Pattern Execution

## Scenario: Deep Copy vs Shallow Copy

**Code:**
```python
original = Document("Report", "Content", {"author": "Alice"})
shallow = original.shallow_clone()
deep = original.deep_clone()
```

### Step 1: Create Original Document

```
Execution: Document("Report", "Content", {"author": "Alice"})

Memory after creation:
  Document@0x7f8a1c:
    title = "Report"
    content = "Content"
    metadata = dict@0x7f8a2d {"author": "Alice"}
    sections = list@0x7f8a3e []
    created_at = datetime@0x7f8a4f

Variables:
  original = Document@0x7f8a1c
```

### Step 2: Shallow Clone

```
Execution: copy.copy(original)

Process:
  1. Create new Document object at 0x7f9b1c
  2. Copy primitive attributes (title, content) - NEW values
  3. Copy object references (metadata, sections) - SAME references
  
Memory after shallow copy:
  Document@0x7f9b1c:  (NEW object)
    title = "Report"  (NEW string)
    content = "Content"  (NEW string)
    metadata = dict@0x7f8a2d  (SAME dict reference!)
    sections = list@0x7f8a3e  (SAME list reference!)
    created_at = datetime@0x7f8a4f  (SAME datetime)
    
  dict@0x7f8a2d:  (SHARED by both documents)
    {"author": "Alice"}

Variables:
  original = Document@0x7f8a1c
  shallow = Document@0x7f9b1c  (different object)
  
Note: original.metadata is shallow.metadata → True (same object!)
```

### Step 3: Deep Clone

```
Execution: copy.deepcopy(original)

Process:
  1. Create new Document object at 0x7fac1c
  2. Recursively copy ALL nested objects
  3. Handle circular references using memo dict
  
Memory after deep copy:
  Document@0xfac1c:  (NEW object)
    title = "Report"  (NEW string)
    content = "Content"  (NEW string)
    metadata = dict@0x7fac2d  (NEW dict!)
    sections = list@0x7fac3e  (NEW list!)
    created_at = datetime@0x7fac4f  (NEW datetime!)
    
  dict@0x7fac2d:  (INDEPENDENT copy)
    {"author": "Alice"}

Variables:
  original = Document@0x7f8a1c
  shallow = Document@0x7f9b1c
  deep = Document@0x7fac1c

Note: original.metadata is deep.metadata → False (different objects!)
```

### Step 4: Modify Shallow Copy's Metadata

```
Code: shallow.metadata["version"] = "2.0"

Memory before modification:
  dict@0x7f8a2d (shared by original and shallow):
    {"author": "Alice"}

Execution:
  Access shallow.metadata → dict@0x7f8a2d
  Add key "version" with value "2.0"
  
Memory after modification:
  dict@0x7f8a2d (STILL shared!):
    {"author": "Alice", "version": "2.0"}

Effect on documents:
  original.metadata["version"] → "2.0" (AFFECTED!)
  shallow.metadata["version"] → "2.0"
  
Reason: Both reference the SAME dict object
```

### Step 5: Modify Deep Copy's Metadata

```
Code: deep.metadata["version"] = "3.0"

Memory before modification:
  dict@0x7f8a2d (original and shallow):
    {"author": "Alice", "version": "2.0"}
  dict@0x7fac2d (deep copy only):
    {"author": "Alice", "version": "2.0"}

Execution:
  Access deep.metadata → dict@0x7fac2d (DIFFERENT dict)
  Add key "version" with value "3.0"
  
Memory after modification:
  dict@0x7f8a2d (unchanged):
    {"author": "Alice", "version": "2.0"}
  dict@0x7fac2d (modified):
    {"author": "Alice", "version": "3.0"}

Effect on documents:
  original.metadata["version"] → "2.0" (NOT affected)
  deep.metadata["version"] → "3.0"
  
Reason: Each has SEPARATE dict object
```

## Key Insights

1. **Shallow Copy:**
   - Creates new object
   - Copies primitive values
   - SHARES references to nested objects
   - Fast but dangerous

2. **Deep Copy:**
   - Creates new object
   - Recursively copies nested objects
   - Complete independence
   - Slower but safe

3. **When to Use Each:**
   - Shallow: When nested objects are immutable or intentionally shared
   - Deep: When you need complete independence (most common)
