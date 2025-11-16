# Requirement Analysis Template for LLD Problems

## Problem Statement
**Problem Name**: [e.g., Parking Lot System, Library Management, etc.]

**Brief Description**:
[One paragraph describing what the system does]

---

## Step 1: Clarify Requirements

### Functional Requirements
List what the system MUST do:

1.
2.
3.
4.
5.

### Non-Functional Requirements
List quality attributes and constraints:

- **Performance**:
- **Scalability**:
- **Concurrency**:
- **Data Consistency**:
- **Availability**:
- **Security**:

### Out of Scope
What the system will NOT handle:

-
-
-

### Assumptions
What we're assuming to be true:

-
-
-

---

## Step 2: Identify Actors

### Primary Actors
Main users of the system:

| Actor | Description | Key Actions |
|-------|-------------|-------------|
| | | |
| | | |

### Secondary Actors
Support users (admins, operators):

| Actor | Description | Key Actions |
|-------|-------------|-------------|
| | | |

### System Actors
External systems or automated processes:

| Actor | Description | Interactions |
|-------|-------------|--------------|
| | | |

---

## Step 3: Define Use Cases

### Use Case 1: [Name]
**Actor**:
**Preconditions**:
-

**Main Flow**:
1.
2.
3.
4.

**Alternative Flows**:
- **Alt 1**: [What can go differently]
  1.
  2.

**Exception Flows**:
- **Exception 1**: [Error condition]
  1.
  2.

**Postconditions**:
-

---

### Use Case 2: [Name]
**Actor**:
**Preconditions**:
-

**Main Flow**:
1.
2.
3.

**Alternative Flows**:
-

**Exception Flows**:
-

**Postconditions**:
-

---

### Use Case 3: [Name]
[Continue for all major use cases...]

---

## Step 4: Identify Key Entities

### Entity Brainstorm
List all nouns from requirements and use cases:

**Nouns**:

### Categorize Entities

#### Core Entities
Main domain objects that have identity and lifecycle:

| Entity | Description | Key Attributes |
|--------|-------------|----------------|
| | | |
| | | |

#### Value Objects
Objects defined by their attributes, immutable:

| Value Object | Description | Attributes |
|--------------|-------------|------------|
| | | |

#### Services
Stateless operations, business logic:

| Service | Responsibility |
|---------|----------------|
| | |

#### Enumerations
Fixed set of constants:

| Enum | Values |
|------|--------|
| | |

---

## Step 5: Define Relationships & Behaviors

### Class Relationships

#### Inheritance (is-a)
```
Parent → Child1, Child2, ...
Example: Vehicle → Car, Truck, Motorcycle
```

Your design:
```

```

#### Composition (has-a, strong ownership)
```
Container has Component (component can't exist independently)
Example: House has Rooms
```

Your design:
```

```

#### Aggregation (has-a, weak ownership)
```
Container has Component (component can exist independently)
Example: Department has Employees
```

Your design:
```

```

#### Association
```
Class1 uses/references Class2
Example: Customer places Order
```

Your design:
```

```

### Key Behaviors

#### Entity 1: [Name]
**Attributes**:
-
-

**Methods**:
- `method1(params) -> return_type`: Description
- `method2(params) -> return_type`: Description

**Responsibilities**:
-

---

#### Entity 2: [Name]
**Attributes**:
-

**Methods**:
-

**Responsibilities**:
-

---

[Continue for all entities...]

---

## Step 6: Apply Design Patterns

### Pattern Selection

| Problem/Need | Pattern | Justification |
|--------------|---------|---------------|
| Need single instance of X | Singleton | |
| Creating different types of Y | Factory | |
| Multiple algorithms for Z | Strategy | |
| Object behavior changes with state | State | |
| One-to-many notifications | Observer | |
| Undo/Redo functionality | Command | |
| | | |

### Pattern Application Details

#### Pattern 1: [Name]
**Where Applied**:

**Why**:

**Implementation Notes**:
```python
# Pseudocode or key classes involved
```

---

#### Pattern 2: [Name]
**Where Applied**:

**Why**:

**Implementation Notes**:
```python

```

---

## Step 7: Validate Design

### Requirements Coverage
Check each requirement is satisfied:

| Requirement | Covered By | Status |
|-------------|-----------|--------|
| FR1: | Class X, Method Y | ✓ |
| FR2: | | ✓ / ✗ |
| NFR1: | | ✓ / ✗ |

### SOLID Principles Check

| Principle | How Satisfied | Examples |
|-----------|---------------|----------|
| **S**RP | Each class has one responsibility | Class X only handles Y |
| **O**CP | Open for extension, closed for modification | Can add new Z without modifying existing code |
| **L**SP | Subtypes are substitutable | All W implementations work interchangeably |
| **I**SP | Interfaces are focused | Separate interfaces for A and B |
| **D**IP | Depend on abstractions | Depend on Interface, not concrete class |

### Edge Cases Handled

| Edge Case | How Handled |
|-----------|-------------|
| Null/empty input | Validation in constructor/methods |
| Concurrent access | Thread synchronization / locks |
| Resource exhaustion | Capacity checks, exceptions |
| Invalid state transitions | State validation |
| Duplicate entries | Uniqueness checks |

### Extensibility

**Future Extensions**:
1. **Add Feature X**: Would require creating new class Y implementing interface Z
2. **Support Type W**: Would extend existing hierarchy without modification
3. **Change Algorithm**: Would swap strategy implementation

---

## Class Diagram

### ASCII Art Diagram
```
┌─────────────────────┐
│   ClassName         │
├─────────────────────┤
│ - attribute1: Type  │
│ - attribute2: Type  │
├─────────────────────┤
│ + method1(): Type   │
│ + method2(): Type   │
└─────────────────────┘
         △
         │ (inheritance)
         │
┌────────┴────────┐
│                 │
┌───────────┐ ┌──────────┐
│  Child1   │ │ Child2   │
└───────────┘ └──────────┘
```

Your design:
```




```

### Detailed Class Diagram
```
[Draw a more detailed diagram showing all classes and relationships]




```

---

## Implementation Plan

### Phase 1: Core Classes
**Priority**: High
**Classes**:
-
-

**Deliverable**: Basic structure with key attributes

---

### Phase 2: Core Functionality
**Priority**: High
**Features**:
-
-

**Deliverable**: Main use cases working

---

### Phase 3: Edge Cases & Validation
**Priority**: Medium
**Tasks**:
- Input validation
- Error handling
- State validation

**Deliverable**: Robust error handling

---

### Phase 4: Design Patterns
**Priority**: Medium
**Patterns**:
-
-

**Deliverable**: Clean, extensible design

---

### Phase 5: Advanced Features
**Priority**: Low
**Features**:
-
-

**Deliverable**: Complete system with bells and whistles

---

## Testing Strategy

### Unit Tests
- Test each class in isolation
- Mock dependencies
- Cover edge cases

**Key Test Cases**:
1.
2.
3.

### Integration Tests
- Test interactions between classes
- Test complete use cases
- Test error propagation

**Key Scenarios**:
1.
2.
3.

### Concurrency Tests (if applicable)
- Test race conditions
- Test deadlocks
- Test data consistency

---

## Interview Talking Points

### Design Decisions
1. **Decision**:
   - **Reason**:
   - **Alternative**:
   - **Trade-off**:

2. **Decision**:
   - **Reason**:
   - **Alternative**:
   - **Trade-off**:

### Complexity Analysis
- **Time Complexity**:
  - Operation X: O(?)
  - Operation Y: O(?)

- **Space Complexity**:
  - Overall: O(?)

### Scalability Considerations
-
-

### Potential Improvements
1.
2.
3.

---

## Code Structure

### Directory Layout
```
project_name/
├── entities/
│   ├── entity1.py
│   ├── entity2.py
│   └── ...
├── services/
│   ├── service1.py
│   └── service2.py
├── enums/
│   └── enums.py
├── exceptions/
│   └── exceptions.py
├── patterns/
│   ├── factories.py
│   ├── strategies.py
│   └── ...
├── tests/
│   └── test_*.py
└── main.py
```

### Sample Code Template
```python
"""
Module: entity_name.py
Description: Brief description of what this module contains
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from enum import Enum


class EntityName:
    """
    Description of the entity.

    Attributes:
        attribute1: Description
        attribute2: Description
    """

    def __init__(self, param1: Type, param2: Type):
        """
        Initialize EntityName.

        Args:
            param1: Description
            param2: Description
        """
        self._attribute1 = param1
        self._attribute2 = param2

    def method1(self, param: Type) -> ReturnType:
        """
        Description of what this method does.

        Args:
            param: Description

        Returns:
            Description of return value

        Raises:
            ExceptionType: When this exception is raised
        """
        pass


# Continue with other classes...
```

---

## Notes & Observations

### Challenges Identified


### Questions to Ask Interviewer


### Assumptions Made


---

## Revision History

| Date | Changes | Author |
|------|---------|--------|
| | Initial template | |
| | | |

---

## References

- Similar problems:
- Design patterns used:
- Articles/resources:

---

**Remember**:
1. Start simple, add complexity incrementally
2. Think out loud during interviews
3. Draw diagrams to communicate
4. Discuss trade-offs
5. Validate against requirements
6. Consider extensibility
7. Handle edge cases
8. Follow SOLID principles

Good luck with your design!
