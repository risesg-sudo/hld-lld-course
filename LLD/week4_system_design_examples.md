# Week 4: System Design Examples & Requirement Analysis

## Overview
Week 4 focuses on applying LLD principles to real-world system design problems. We'll learn a systematic approach to requirement analysis and implement three classic interview problems: IRCTC Railway Reservation System, Chess Game, and Elevator System.

## Table of Contents
1. [Requirement Analysis Framework](#requirement-analysis-framework)
2. [System Design Examples](#system-design-examples)
3. [Design Patterns Reference](#design-patterns-reference)
4. [Interview Tips](#interview-tips)
5. [Common Pitfalls](#common-pitfalls)

---

## Requirement Analysis Framework

### The 7-Step LLD Approach

#### Step 1: Clarify Requirements
**Goal**: Understand what needs to be built

**Questions to Ask**:
- What are the core functionalities?
- What are the constraints (scale, performance)?
- Are there any non-functional requirements?
- What is out of scope?

**Example**: For IRCTC
```
Functional Requirements:
✓ Users can search for trains
✓ Users can book tickets
✓ Handle seat allocation
✓ Process payments

Non-Functional:
✓ System should handle concurrent bookings
✓ No double booking
✓ ACID properties for transactions
```

#### Step 2: Identify Actors/Users
**Goal**: Determine who/what interacts with the system

**Categories**:
- Primary actors (end users)
- Secondary actors (admins, operators)
- System actors (external systems, schedulers)

**Example**: For Chess Game
```
Primary Actors:
- Player (2 players)
- Spectator (optional)

System Actors:
- Game Timer
- Move Validator
```

#### Step 3: Define Use Cases
**Goal**: Capture system behavior from user perspective

**Format**:
```
Use Case: <Action Name>
Actor: <Who performs it>
Preconditions: <What must be true before>
Main Flow: <Step-by-step happy path>
Alternative Flows: <What can go differently>
Postconditions: <What is true after>
```

**Example**: For Elevator System
```
Use Case: Request Elevator
Actor: Passenger
Preconditions: Person is at a floor
Main Flow:
  1. Person presses call button (UP/DOWN)
  2. System assigns nearest suitable elevator
  3. Elevator arrives at floor
  4. Doors open
Postconditions: Passenger can enter elevator
```

#### Step 4: Identify Key Entities/Classes
**Goal**: Extract nouns from requirements and use cases

**Technique**:
1. List all nouns from requirements
2. Categorize as entities, value objects, or services
3. Identify relationships (has-a, is-a)

**Example**: IRCTC
```
Entities:
- Train, Station, Seat, Ticket, Passenger, Booking

Value Objects:
- SeatNumber, TrainNumber, PNR

Services:
- BookingService, PaymentService, SearchService
```

#### Step 5: Define Relationships & Behaviors
**Goal**: Establish how classes interact

**Relationship Types**:
- **Inheritance** (is-a): Piece → King, Queen, Knight
- **Composition** (has-a, strong): Board has Squares
- **Aggregation** (has-a, weak): Game has Players
- **Association**: Player makes Move
- **Dependency**: uses temporarily

**Behaviors**:
- Identify key methods for each class
- Define interfaces for polymorphism
- Plan for extensibility

#### Step 6: Apply Design Patterns
**Goal**: Use proven solutions for common problems

**Pattern Selection Criteria**:
- Creational: How objects are created
- Structural: How objects are composed
- Behavioral: How objects interact

**Example Applications**:
```
IRCTC:
- Singleton: BookingManager (one instance)
- Factory: TicketFactory (different ticket types)
- Observer: NotificationService (booking updates)

Chess:
- Factory: PieceFactory (create pieces)
- Strategy: MoveStrategy (different move rules)
- Command: MoveCommand (undo/redo)

Elevator:
- State: ElevatorState (Moving, Idle, etc.)
- Strategy: SchedulingStrategy (algorithms)
- Singleton: ElevatorController
```

#### Step 7: Validate Design
**Goal**: Ensure design meets requirements

**Validation Checklist**:
- [ ] All use cases covered
- [ ] SOLID principles followed
- [ ] Design patterns applied correctly
- [ ] Extensibility considered
- [ ] Edge cases handled
- [ ] Concurrency addressed (if needed)

---

## System Design Examples

### 1. IRCTC Railway Reservation System

**Location**: `/home/user/hld-lld-course/LLD/examples/week4/irctc_system/`

**Key Features**:
- Train and station management
- Seat booking with different classes (AC, Sleeper, General)
- Booking lifecycle (search → book → confirm → cancel)
- Payment processing
- Concurrent booking handling (no double booking)
- Waiting list management

**Design Patterns Used**:
- **Singleton**: `BookingManager` ensures single point of booking control
- **Factory**: `TicketFactory` creates different ticket types (Confirmed, Waiting, RAC)
- **Observer**: `NotificationService` notifies users of booking status changes
- **Strategy**: `PaymentStrategy` for different payment methods

**Core Classes**:
```python
Train, Station, Seat, Ticket, Passenger, Booking
BookingManager, SearchService, PaymentService
SeatType (Enum), TicketStatus (Enum)
```

**SOLID Principles Demonstrated**:
- **SRP**: Each class has single responsibility (Seat manages seat state, Booking manages booking lifecycle)
- **OCP**: New seat types can be added without modifying existing code
- **LSP**: Different ticket types are substitutable
- **ISP**: Separate interfaces for booking, payment, notification
- **DIP**: Depend on abstractions (PaymentProcessor interface, not concrete implementations)

**File References**:
- Design Documentation: `examples/week4/irctc_system/design.md`
- Implementation: `examples/week4/irctc_system/irctc_system.py`

**Sample Usage**:
```python
# Run the system
cd /home/user/hld-lld-course/LLD/examples/week4/irctc_system
python irctc_system.py
```

---

### 2. Chess Game System

**Location**: `/home/user/hld-lld-course/LLD/examples/week4/chess_game/`

**Key Features**:
- Complete chess board with all pieces
- Move validation for each piece type
- Game state management (active, check, checkmate, stalemate)
- Turn management
- Move history (for undo/redo)
- Special moves (castling, en passant, pawn promotion)

**Design Patterns Used**:
- **Factory**: `PieceFactory` creates different chess pieces
- **Strategy**: `MoveStrategy` for different piece movement rules
- **Command**: `MoveCommand` for move execution and undo
- **Template Method**: `Piece` abstract class with template for move validation

**Core Classes**:
```python
Board, Square, Position, Piece (abstract)
King, Queen, Rook, Bishop, Knight, Pawn
Player, Game, Move, MoveValidator
Color (Enum), PieceType (Enum), GameStatus (Enum)
```

**SOLID Principles Demonstrated**:
- **SRP**: Each piece knows only its movement rules
- **OCP**: New piece types can be added easily
- **LSP**: All piece types are substitutable for Piece
- **ISP**: Separate interfaces for Movable, Capturable
- **DIP**: Game depends on Piece abstraction, not concrete pieces

**File References**:
- Design Documentation: `examples/week4/chess_game/design.md`
- Implementation: `examples/week4/chess_game/chess_game.py`

**Sample Usage**:
```python
# Run the game
cd /home/user/hld-lld-course/LLD/examples/week4/chess_game
python chess_game.py
```

---

### 3. Elevator System

**Location**: `/home/user/hld-lld-course/LLD/examples/week4/elevator_system/`

**Key Features**:
- Multiple elevators coordination
- External requests (from floors)
- Internal requests (from inside elevator)
- Efficient scheduling algorithms (SCAN, LOOK, FCFS)
- Elevator states (Idle, Moving Up, Moving Down, Maintenance)
- Load capacity management
- Emergency handling

**Design Patterns Used**:
- **State**: `ElevatorState` for different elevator states
- **Strategy**: `SchedulingStrategy` for different dispatching algorithms
- **Singleton**: `ElevatorController` manages all elevators
- **Observer**: Floor displays observe elevator positions

**Core Classes**:
```python
Elevator, Floor, Request, ElevatorController
SchedulingStrategy (abstract), SCANStrategy, FCFSStrategy
ElevatorState (abstract), IdleState, MovingState
Direction (Enum), RequestType (Enum)
```

**SOLID Principles Demonstrated**:
- **SRP**: Request handling separate from elevator movement
- **OCP**: New scheduling strategies can be added
- **LSP**: Different strategies are substitutable
- **ISP**: Separate interfaces for internal and external requests
- **DIP**: Controller depends on strategy interface

**File References**:
- Design Documentation: `examples/week4/elevator_system/design.md`
- Implementation: `examples/week4/elevator_system/elevator_system.py`

**Sample Usage**:
```python
# Run the system
cd /home/user/hld-lld-course/LLD/examples/week4/elevator_system
python elevator_system.py
```

---

## Design Patterns Reference

### Patterns Used Across Systems

| Pattern | IRCTC | Chess | Elevator | Purpose |
|---------|-------|-------|----------|---------|
| **Singleton** | BookingManager | - | ElevatorController | Ensure single instance |
| **Factory** | TicketFactory | PieceFactory | - | Object creation |
| **Strategy** | PaymentStrategy | MoveStrategy | SchedulingStrategy | Algorithm selection |
| **Observer** | NotificationService | - | FloorDisplay | Event notification |
| **State** | - | - | ElevatorState | State management |
| **Command** | - | MoveCommand | - | Action encapsulation |

### When to Use Each Pattern

**Singleton**:
- Need exactly one instance (manager, controller)
- Global access point required
- Example: BookingManager, ElevatorController

**Factory**:
- Complex object creation logic
- Multiple variants of similar objects
- Example: Different ticket types, chess pieces

**Strategy**:
- Multiple algorithms for same task
- Algorithm selection at runtime
- Example: Payment methods, scheduling algorithms

**Observer**:
- One-to-many dependency
- Event-driven architecture
- Example: Booking notifications, elevator updates

**State**:
- Object behavior changes with state
- Many conditional statements based on state
- Example: Elevator states (idle, moving, maintenance)

**Command**:
- Parameterize objects with operations
- Support undo/redo
- Example: Chess moves

---

## Interview Tips

### 1. Start with Clarifying Questions (2-3 minutes)
```
Good Questions:
✓ "Should the system handle concurrent bookings?"
✓ "Do we need to support cancellations and refunds?"
✓ "What's the expected scale (users, transactions)?"
✓ "Are there any specific constraints?"

Avoid:
✗ Jumping directly into coding
✗ Assuming requirements without asking
✗ Asking about implementation details too early
```

### 2. Think Out Loud
- Verbalize your thought process
- Explain why you make certain decisions
- Discuss trade-offs

### 3. Start with Core Functionality
```
Prioritize:
1. Core use cases (80% of functionality)
2. Basic class structure
3. Key relationships

Later:
4. Edge cases
5. Optimizations
6. Advanced features
```

### 4. Draw Diagrams
- Quick class diagram (boxes and arrows)
- Use case diagram if helpful
- Sequence diagram for complex flows

### 5. Code Incrementally
```
Step 1: Define classes (empty or with basic attributes)
Step 2: Add key methods (signatures first)
Step 3: Implement core logic
Step 4: Handle edge cases
```

### 6. Discuss Extensions
- "How would we add feature X?"
- "To scale this, we could..."
- "For thread safety, we'd need..."

### 7. Time Management (45-60 minute interview)
```
5 min  - Clarifying requirements
10 min - High-level design (classes, relationships)
25 min - Implementation (code)
5 min  - Testing/edge cases discussion
5 min  - Extensions/optimizations
```

### 8. Communication Style
```
✓ "I'm thinking we need a Booking class to manage the booking lifecycle"
✓ "Let me use Factory pattern here for creating different ticket types"
✓ "Should I handle thread safety, or focus on the basic design first?"

✗ Silent coding for 10 minutes
✗ "I don't know"
✗ Defensive about design choices
```

---

## Common Pitfalls

### 1. Over-Engineering
**Problem**: Adding unnecessary complexity

**Example**:
```python
# Over-engineered
class AbstractFactoryForTicketCreation:
    class ConcreteFactoryA:
        class BuilderForComplexTicket:
            # Too many layers for simple ticket creation

# Better
class TicketFactory:
    @staticmethod
    def create_ticket(ticket_type, ...):
        # Simple and sufficient
```

**Solution**: Start simple, add complexity only when needed

### 2. Under-Engineering
**Problem**: Not thinking about extensibility

**Example**:
```python
# Hard to extend
class Seat:
    def __init__(self, seat_class):
        if seat_class == "AC":
            self.price = 1000
        elif seat_class == "Sleeper":
            self.price = 500
        # Adding new class requires modifying this code

# Better (OCP compliant)
class SeatPricing(ABC):
    @abstractmethod
    def get_price(self): pass

class ACSeatPricing(SeatPricing):
    def get_price(self): return 1000
```

**Solution**: Use SOLID principles, consider future extensions

### 3. Ignoring Edge Cases
**Problem**: Not handling error conditions

**Common Edge Cases**:
- Null/None values
- Empty collections
- Concurrent access
- Invalid inputs
- Resource exhaustion

**Example**:
```python
# Missing validation
def book_seat(self, seat_id):
    self.seats[seat_id].status = "booked"  # What if seat_id invalid?

# Better
def book_seat(self, seat_id):
    if seat_id not in self.seats:
        raise ValueError("Invalid seat ID")
    if self.seats[seat_id].is_booked():
        raise BookingException("Seat already booked")
    self.seats[seat_id].book()
```

### 4. Poor Class Responsibilities
**Problem**: Violating Single Responsibility Principle

**Example**:
```python
# God class - doing too much
class Game:
    def __init__(self): ...
    def make_move(self): ...
    def validate_move(self): ...
    def check_winner(self): ...
    def save_to_database(self): ...  # Not game's responsibility
    def send_notification(self): ... # Not game's responsibility

# Better - separate concerns
class Game: # Core game logic only
class GameRepository: # Database operations
class NotificationService: # Notifications
```

### 5. Tight Coupling
**Problem**: Classes too dependent on each other

**Example**:
```python
# Tightly coupled
class BookingService:
    def __init__(self):
        self.payment = CreditCardPayment()  # Hard-coded dependency

# Better - dependency injection
class BookingService:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment = payment_processor  # Flexible
```

### 6. Missing Abstractions
**Problem**: Not using interfaces/abstract classes

**Example**:
```python
# No abstraction
class SCAN_Scheduler:
    def schedule(self): ...

class FCFS_Scheduler:
    def schedule(self): ...

# Controller needs to know all implementations
# Hard to add new schedulers

# Better
class SchedulingStrategy(ABC):
    @abstractmethod
    def schedule(self, requests): pass

# Now controller depends on abstraction
```

### 7. Not Discussing Trade-offs
**Problem**: Presenting only one solution

**Better Approach**:
```
"I could use:
1. ArrayList - O(1) access, O(n) insertion
2. LinkedList - O(n) access, O(1) insertion
3. HashMap - O(1) for both, but more memory

For this use case with frequent lookups and rare insertions,
I'll go with ArrayList."
```

### 8. Ignoring Concurrency
**Problem**: Not considering thread safety when needed

**Example**:
```python
# Not thread-safe
class BookingManager:
    def book_seat(self, seat):
        if seat.is_available():  # Race condition!
            seat.book()

# Better
from threading import Lock

class BookingManager:
    def __init__(self):
        self.lock = Lock()

    def book_seat(self, seat):
        with self.lock:
            if seat.is_available():
                seat.book()
```

### 9. Incomplete Design
**Problem**: Missing critical components

**Checklist**:
- [ ] All use cases covered
- [ ] Error handling defined
- [ ] Data validation included
- [ ] State management clear
- [ ] Relationships well-defined

### 10. Poor Naming
**Problem**: Unclear or inconsistent names

**Example**:
```python
# Poor naming
class Mgr:  # What kind of manager?
    def proc(self, d):  # Process what? What is d?
        pass

# Better naming
class BookingManager:
    def process_booking(self, booking_request: BookingRequest):
        pass
```

---

## Practice Strategy

### Week 4 Learning Path

#### Day 1-2: Requirement Analysis
- Study the 7-step framework
- Practice with requirement_analysis_template.md
- Go through IRCTC design document

#### Day 3-4: Implementation Study
- Review IRCTC implementation
- Understand design pattern applications
- Run and test the code

#### Day 5-6: Chess Game
- Study chess game design
- Implement on your own first
- Compare with provided solution

#### Day 7: Elevator System
- Design elevator system yourself
- Review provided solution
- Note differences in approach

#### Day 8-9: Mock Interviews
- Pick a new problem (Parking Lot, Library System)
- Time yourself (45 minutes)
- Follow the 7-step framework
- Record what you struggled with

#### Day 10: Review and Refine
- Revisit all three examples
- Identify patterns across systems
- Practice explaining your designs

---

## Additional Resources

### Recommended Problems to Practice
1. **Parking Lot System** (similar to elevator - state management)
2. **Library Management** (similar to IRCTC - booking/reservation)
3. **ATM System** (state pattern, transaction management)
4. **Hotel Booking** (reservation system with complex rules)
5. **Stack Overflow** (voting, reputation, moderation)
6. **Movie Ticket Booking** (similar to IRCTC)
7. **Vending Machine** (state pattern)
8. **Car Rental System** (booking with inventory)
9. **Online Shopping Cart** (e-commerce basics)
10. **Snake and Ladder** (game design, simpler than chess)

### Template Location
Use `/home/user/hld-lld-course/LLD/examples/week4/requirement_analysis_template.md` as a starting point for any LLD problem.

---

## Summary

Week 4 teaches you to approach LLD systematically:

1. **Framework**: 7-step requirement analysis methodology
2. **Practice**: Three comprehensive real-world examples
3. **Patterns**: Practical application of design patterns
4. **Interview Skills**: Tips for communicating your design

**Key Takeaways**:
- Always start with requirements clarification
- Think in terms of actors, use cases, and classes
- Apply design patterns purposefully, not forcefully
- Code should be clean, extensible, and well-documented
- Practice explaining your design decisions

**Next Steps**:
- Implement each system on your own before looking at solutions
- Practice with additional problems
- Time yourself to simulate interview pressure
- Get comfortable drawing quick class diagrams

Good luck with your LLD interviews!
