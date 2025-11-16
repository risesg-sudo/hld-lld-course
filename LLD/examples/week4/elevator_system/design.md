# Elevator System - Design Document

## Problem Statement
Design an elevator control system for a building with multiple elevators. The system should efficiently handle requests from multiple floors, optimize elevator movement, support different scheduling strategies, manage elevator states, and handle emergency situations.

---

## Requirements Analysis

### Functional Requirements
1. **External Requests**: People can call elevator from any floor (UP/DOWN buttons)
2. **Internal Requests**: People inside elevator can select destination floors
3. **Multiple Elevators**: System manages multiple elevator cars
4. **Efficient Dispatch**: Assign nearest suitable elevator to requests
5. **Elevator States**: Manage states (Idle, Moving Up, Moving Down, Maintenance)
6. **Load Capacity**: Respect maximum weight/person capacity
7. **Door Control**: Open/close doors at appropriate times
8. **Display**: Show current floor and direction
9. **Emergency Handling**: Emergency stop, fire mode
10. **Request Queue**: Maintain and process request queue

### Non-Functional Requirements
- **Performance**: Minimize average wait time
- **Efficiency**: Optimize elevator movements (fewer stops)
- **Scalability**: Support N elevators and M floors
- **Safety**: Prevent overloading, emergency handling
- **Availability**: System should be fault-tolerant
- **Fairness**: No starvation - all requests eventually served

### Out of Scope
- Hardware integration (sensors, motors)
- User authentication
- Energy optimization
- Predictive analytics
- Voice announcements
- Remote monitoring dashboard

---

## Actors

| Actor | Description | Key Actions |
|-------|-------------|-------------|
| Passenger (External) | Person outside elevator | Press UP/DOWN button on floor |
| Passenger (Internal) | Person inside elevator | Select destination floor, press door open/close |
| System Controller | Central control system | Dispatch elevators, manage queue, optimize routing |
| Maintenance | Maintenance personnel | Put elevator in/out of service, emergency override |

---

## Use Cases

### UC1: Request Elevator from Floor
**Actor**: Passenger (External)
**Preconditions**: At least one elevator is in service

**Main Flow**:
1. Passenger presses UP or DOWN button on floor
2. System creates external request
3. System identifies suitable elevators (moving in requested direction or idle)
4. System selects best elevator using scheduling algorithm
5. System adds floor to elevator's queue
6. Elevator arrives at floor
7. Doors open
8. Passenger enters

**Postconditions**: Elevator arrives at floor, passenger can board

---

### UC2: Select Destination Floor (Internal Request)
**Actor**: Passenger (Internal)
**Preconditions**: Passenger is inside elevator

**Main Flow**:
1. Passenger presses floor button inside elevator
2. System validates floor number
3. System adds floor to elevator's internal queue
4. System highlights button
5. Elevator stops at floor in sequence
6. Doors open
7. Passenger exits
8. Button highlight turns off

**Postconditions**: Elevator stops at requested floor

---

### UC3: Dispatch Elevator
**Actor**: System Controller
**Preconditions**: External request exists

**Main Flow**:
1. System receives external request (floor, direction)
2. System gets list of available elevators
3. System applies scheduling strategy (SCAN, FCFS, LOOK, etc.)
4. System selects optimal elevator
5. System assigns request to elevator
6. System updates elevator's queue
7. Elevator starts moving if idle

**Alternative Flows**:
- **Alt 1**: All elevators busy → Queue request until elevator available
- **Alt 2**: Elevator already going to that floor → Just pick up passenger

**Postconditions**: Request assigned to an elevator

---

### UC4: Handle Emergency Stop
**Actor**: Passenger or Maintenance
**Preconditions**: Elevator is in operation

**Main Flow**:
1. Emergency button pressed
2. Elevator stops immediately
3. Doors remain closed (safety)
4. Alarm triggered
5. System notifies maintenance
6. Elevator enters maintenance mode

**Postconditions**: Elevator stopped safely, maintenance notified

---

## Class Design

### Class Diagram (ASCII)
```
┌──────────────────────────┐
│ ElevatorController       │ ← Singleton
├──────────────────────────┤
│ - elevators: List[Elev]  │
│ - strategy: Strategy     │
│ - pending_requests: []   │
├──────────────────────────┤
│ + add_elevator()         │
│ + request_elevator()     │
│ + dispatch_request()     │
│ + set_strategy()         │
└──────────┬───────────────┘
           │ manages
           │
    ┌──────▼──────────────┐
    │ Elevator            │
    ├─────────────────────┤
    │ - id: int           │
    │ - current_floor: int│
    │ - state: ElevState  │
    │ - direction: Dir    │
    │ - capacity: int     │
    │ - current_load: int │
    │ - requests: Set[int]│
    ├─────────────────────┤
    │ + move_to_floor()   │
    │ + add_request()     │
    │ + process_requests()│
    │ + open_doors()      │
    │ + close_doors()     │
    └──────────┬──────────┘
               │ has
               │
         ┌─────▼─────────┐
         │ Door          │
         ├───────────────┤
         │ - is_open: bool│
         ├───────────────┤
         │ + open()      │
         │ + close()     │
         └───────────────┘

┌───────────────────────┐
│ ElevatorState (ABC)   │ ← State Pattern
├───────────────────────┤
│ + move_up()           │
│ + move_down()         │
│ + stop()              │
│ + open_doors()        │
└──────────┬────────────┘
           △
           │ (inheritance)
    ┌──────┴──────────────────────┐
    │                             │
┌───┴────────┐  ┌──────────┐  ┌──┴──────────┐
│ IdleState  │  │ MovingUp │  │ MovingDown  │
│            │  │ State    │  │ State       │
└────────────┘  └──────────┘  └─────────────┘

┌───────────────────────┐
│ SchedulingStrategy    │ ← Strategy Pattern
├───────────────────────┤
│ + select_elevator()   │
└──────────┬────────────┘
           △
           │
    ┌──────┴─────────────────────┐
    │                            │
┌───┴──────────┐  ┌──────────────┴┐  ┌──────────┐
│ SCANStrategy │  │ FCFSStrategy  │  │ LOOK     │
│              │  │               │  │ Strategy │
└──────────────┘  └───────────────┘  └──────────┘

┌─────────────────┐         ┌──────────────────┐
│ Request         │         │ Floor            │
├─────────────────┤         ├──────────────────┤
│ - floor: int    │         │ - floor_num: int │
│ - direction: Dir│◇────────│ - up_button: bool│
│ - timestamp: dt │         │ - down_button:   │
│ - type: ReqType │         └──────────────────┘
└─────────────────┘

┌──────────────────┐
│ Display          │ ← Observer Pattern
├──────────────────┤
│ - floor: int     │
│ - direction: Dir │
├──────────────────┤
│ + update()       │
└──────────────────┘
```

### Core Classes

#### 1. Elevator
```python
class Elevator:
    - id: int                          # Unique elevator ID
    - current_floor: int               # Current position
    - state: ElevatorState             # Current state
    - direction: Direction             # Current direction
    - max_capacity: int                # Max weight/persons
    - current_load: int                # Current load
    - requests: Set[int]               # Destination floors
    - door: Door                       # Door control

    + __init__(id, max_capacity)
    + move_to_floor(floor: int)
    + add_request(floor: int)
    + process_requests()
    + open_doors()
    + close_doors()
    + can_take_request(request: Request) -> bool
    + get_current_floor() -> int
    + get_state() -> ElevatorState
    + set_state(state: ElevatorState)
    + is_idle() -> bool
    + is_moving() -> bool
```

#### 2. ElevatorState (State Pattern - Abstract)
```python
class ElevatorState(ABC):
    + move_up(elevator: Elevator)      # Abstract
    + move_down(elevator: Elevator)    # Abstract
    + stop(elevator: Elevator)         # Abstract
    + open_doors(elevator: Elevator)   # Abstract
    + close_doors(elevator: Elevator)  # Abstract
```

#### 3. Concrete States
```python
class IdleState(ElevatorState):
    + move_up(elevator)
    + move_down(elevator)
    + stop(elevator)
    + open_doors(elevator)
    + close_doors(elevator)

class MovingUpState(ElevatorState):
    + move_up(elevator)
    + move_down(elevator)
    + stop(elevator)
    + open_doors(elevator)  # Only when stopped
    + close_doors(elevator)

class MovingDownState(ElevatorState):
    + move_up(elevator)
    + move_down(elevator)
    + stop(elevator)
    + open_doors(elevator)  # Only when stopped
    + close_doors(elevator)

class MaintenanceState(ElevatorState):
    # All operations disabled except maintenance
```

#### 4. Direction
```python
class Direction(Enum):
    UP = 1
    DOWN = -1
    IDLE = 0
```

#### 5. Request
```python
class Request:
    - floor: int                       # Floor number
    - direction: Direction             # UP or DOWN
    - timestamp: datetime              # When request was made
    - request_type: RequestType        # EXTERNAL or INTERNAL

    + __init__(floor, direction, request_type)
    + get_floor() -> int
    + get_direction() -> Direction
    + get_timestamp() -> datetime
```

#### 6. Floor
```python
class Floor:
    - floor_number: int
    - up_button_pressed: bool
    - down_button_pressed: bool

    + __init__(floor_number)
    + press_up_button()
    + press_down_button()
    + reset_buttons()
```

#### 7. Door
```python
class Door:
    - is_open: bool
    - elevator_id: int

    + __init__(elevator_id)
    + open()
    + close()
    + is_open() -> bool
```

#### 8. ElevatorController (Singleton)
```python
class ElevatorController:
    - _instance: ElevatorController    # Singleton instance
    - elevators: List[Elevator]
    - strategy: SchedulingStrategy
    - pending_requests: Queue[Request]
    - floors: List[Floor]

    + get_instance() -> ElevatorController  # Static
    + add_elevator(elevator: Elevator)
    + request_elevator(floor: int, direction: Direction) -> Request
    + dispatch_request(request: Request)
    + set_strategy(strategy: SchedulingStrategy)
    + process_pending_requests()
    + get_elevator_status(elevator_id: int) -> dict
```

#### 9. SchedulingStrategy (Strategy Pattern - Abstract)
```python
class SchedulingStrategy(ABC):
    + select_elevator(elevators: List[Elevator], request: Request) -> Elevator
```

#### 10. Concrete Strategies
```python
class SCANStrategy(SchedulingStrategy):
    """
    SCAN (Elevator Algorithm):
    Elevator continues in one direction until no more requests,
    then reverses direction
    """
    + select_elevator(elevators, request) -> Elevator

class FCFSStrategy(SchedulingStrategy):
    """
    First Come First Served:
    Nearest elevator regardless of direction
    """
    + select_elevator(elevators, request) -> Elevator

class LOOKStrategy(SchedulingStrategy):
    """
    LOOK Algorithm:
    Like SCAN but reverses at last request, not at end
    """
    + select_elevator(elevators, request) -> Elevator

class ShortestSeekTimeFirst(SchedulingStrategy):
    """
    SSTF: Select elevator with shortest seek time to request
    """
    + select_elevator(elevators, request) -> Elevator
```

#### 11. Display (Observer Pattern)
```python
class Display:
    - elevator_id: int
    - current_floor: int
    - direction: Direction

    + update(floor: int, direction: Direction)
    + show_status()
```

### Enumerations

```python
class Direction(Enum):
    UP = 1
    DOWN = -1
    IDLE = 0

class RequestType(Enum):
    EXTERNAL = "external"  # From floor panel
    INTERNAL = "internal"  # From inside elevator

class ElevatorStatus(Enum):
    IDLE = "idle"
    MOVING_UP = "moving_up"
    MOVING_DOWN = "moving_down"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"
```

---

## Design Patterns Applied

### 1. Singleton Pattern
**Where**: `ElevatorController`

**Why**:
- Need single point of control for all elevators
- Centralized request management
- Global access to controller

**Implementation**:
```python
class ElevatorController:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. State Pattern
**Where**: `ElevatorState` hierarchy

**Why**:
- Elevator behavior changes significantly based on state
- Different actions valid in different states
- Clean state transitions
- Avoid complex if-else chains

**Implementation**:
```python
class Elevator:
    def move_up(self):
        self.state.move_up(self)  # Delegate to state

class IdleState:
    def move_up(self, elevator):
        elevator.state = MovingUpState()
        # Start moving

class MovingUpState:
    def move_up(self, elevator):
        # Already moving up, continue
        pass
```

### 3. Strategy Pattern
**Where**: `SchedulingStrategy` hierarchy

**Why**:
- Multiple scheduling algorithms (SCAN, FCFS, LOOK, SSTF)
- Algorithm can be changed at runtime
- Easy to add new scheduling algorithms
- Separate algorithm from controller

**Implementation**:
```python
class ElevatorController:
    def set_strategy(self, strategy):
        self.strategy = strategy

    def dispatch_request(self, request):
        elevator = self.strategy.select_elevator(
            self.elevators, request
        )
        elevator.add_request(request.floor)
```

### 4. Observer Pattern
**Where**: `Display` observes elevator state

**Why**:
- Displays need to update when elevator moves
- Decouple display from elevator logic
- Multiple displays can observe same elevator

**Implementation**:
```python
class Elevator:
    def __init__(self):
        self.observers = []

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self.current_floor, self.direction)

class Display:
    def update(self, floor, direction):
        self.current_floor = floor
        self.direction = direction
        self.show_status()
```

---

## SOLID Principles Demonstrated

### Single Responsibility Principle (SRP)
- `Elevator`: Manages only elevator movement and state
- `ElevatorController`: Manages only elevator coordination
- `SchedulingStrategy`: Handles only scheduling logic
- `Door`: Manages only door operations
- Each class has one reason to change

### Open/Closed Principle (OCP)
- New scheduling strategies can be added without modifying controller
- New elevator states can be added without changing elevator class
- System is open for extension, closed for modification

### Liskov Substitution Principle (LSP)
- Any `SchedulingStrategy` can be used interchangeably
- Any `ElevatorState` can be substituted for another
- Clients work correctly with any subtype

### Interface Segregation Principle (ISP)
- `SchedulingStrategy` has focused interface (just `select_elevator`)
- `ElevatorState` has only relevant methods
- No fat interfaces forcing unnecessary implementations

### Dependency Inversion Principle (DIP)
- `ElevatorController` depends on `SchedulingStrategy` abstraction
- `Elevator` depends on `ElevatorState` abstraction
- High-level modules don't depend on low-level details

---

## Scheduling Algorithms

### 1. SCAN (Elevator Algorithm)
**Description**: Elevator continues in current direction until no more requests in that direction, then reverses.

**Advantages**:
- Fair - no starvation
- Good throughput
- Predictable

**Disadvantages**:
- May not minimize individual wait times

**Implementation**:
```
1. Get elevator's current direction
2. If going UP:
   - Serve all requests above current floor first
   - Then reverse and serve requests below
3. If going DOWN:
   - Serve all requests below current floor first
   - Then reverse and serve requests above
4. If IDLE:
   - Choose nearest request
```

### 2. FCFS (First Come First Served)
**Description**: Nearest available elevator, regardless of direction.

**Advantages**:
- Simple
- Fair in terms of request order

**Disadvantages**:
- Inefficient movement
- Higher average wait time

### 3. LOOK Algorithm
**Description**: Like SCAN but reverses at last request, not at end.

**Advantages**:
- More efficient than SCAN
- Avoids unnecessary movement to ends

### 4. SSTF (Shortest Seek Time First)
**Description**: Select elevator with shortest distance to request.

**Advantages**:
- Minimizes seek time
- Good average wait time

**Disadvantages**:
- Can cause starvation
- Unfair to distant requests

---

## State Transitions

```
IDLE ──────────> MOVING_UP ────────> IDLE
  │                   │                 │
  │                   ↓                 │
  │             MOVING_DOWN ────────────┘
  │
  └──────────> MAINTENANCE
                     ↓
                 EMERGENCY
```

**Transition Rules**:
- `IDLE → MOVING_UP`: When request above current floor
- `IDLE → MOVING_DOWN`: When request below current floor
- `MOVING_UP → IDLE`: When no more requests
- `MOVING_UP → MOVING_DOWN`: When no more up requests, have down requests
- `Any → MAINTENANCE`: Manual trigger
- `Any → EMERGENCY`: Emergency button pressed

---

## Request Processing Algorithm

### Main Loop
```
1. Check for new requests
2. For each elevator:
   a. Get elevator's current state
   b. Get elevator's request queue
   c. Determine next floor based on strategy
   d. Move to next floor
   e. Check if should stop at current floor
   f. If yes:
      - Stop elevator
      - Open doors
      - Remove floor from queue
      - Wait for passengers
      - Close doors
   g. Update direction based on remaining requests
   h. If no more requests, set to IDLE
3. Dispatch pending external requests
4. Sleep/wait
5. Repeat
```

### Request Dispatch Logic
```
1. Get external request (floor, direction)
2. Get list of available elevators (not in maintenance)
3. Apply scheduling strategy:
   - Filter suitable elevators
   - Rank by strategy criteria
   - Select best elevator
4. Add request to selected elevator's queue
5. If elevator is IDLE, start moving
6. Return selected elevator
```

---

## Edge Cases Handled

1. **No elevators available**: Queue request until elevator becomes available
2. **Overload**: Prevent boarding if capacity exceeded
3. **Emergency stop**: Immediate halt, enter emergency state
4. **Maintenance mode**: Remove elevator from service
5. **Multiple requests same floor**: Deduplicate
6. **Door obstruction**: Keep doors open, retry close
7. **Invalid floor**: Reject invalid floor numbers
8. **Conflicting requests**: Prioritize based on strategy
9. **All elevators busy**: Queue and wait
10. **Elevator stuck**: Timeout detection, emergency mode

---

## Sample Usage Flow

```
Scenario: Person on floor 5 wants to go down to ground floor

1. Person at floor 5 presses DOWN button
   └─> ElevatorController.request_elevator(5, DOWN)
   └─> External request created

2. Controller dispatches request
   └─> strategy.select_elevator(elevators, request)
   └─> SCAN strategy selects Elevator #2 (at floor 3, moving up)

3. Elevator #2 continues up to floor 7 (has internal request)
   └─> Stops at floor 7
   └─> Passenger exits
   └─> Reverses direction to DOWN

4. Elevator #2 moves down
   └─> Stops at floor 5
   └─> Opens doors
   └─> Person enters

5. Person presses button for floor 0 (ground)
   └─> Internal request added to Elevator #2
   └─> Elevator continues down

6. Elevator #2 reaches floor 0
   └─> Stops
   └─> Opens doors
   └─> Person exits
   └─> No more requests → state changes to IDLE
```

---

## Testing Considerations

### Unit Tests
1. Test elevator state transitions
2. Test each scheduling strategy
3. Test request queue management
4. Test capacity checks
5. Test emergency handling

### Integration Tests
1. Test complete request flow (external → dispatch → pickup → delivery)
2. Test multiple concurrent requests
3. Test elevator coordination
4. Test strategy switching

### Load Tests
1. Test with many elevators
2. Test with high request rate
3. Test performance of strategies
4. Measure average wait time

---

## Potential Enhancements

1. **Energy Optimization**: Minimize power consumption
2. **Predictive Dispatch**: Use ML to predict request patterns
3. **Express Elevators**: Some elevators skip certain floors
4. **Group Control**: Coordinate multiple elevator banks
5. **Priority Handling**: VIP passengers, emergency services
6. **Load Balancing**: Distribute load evenly across elevators
7. **Destination Dispatch**: Enter destination before boarding
8. **Smart Scheduling**: Consider time of day, building usage patterns
9. **Real-time Monitoring**: Dashboard with elevator positions
10. **Maintenance Scheduling**: Predictive maintenance based on usage

---

## Complexity Analysis

### Time Complexity
- **Request dispatch**: O(n) where n = number of elevators
- **Select elevator (SCAN)**: O(n)
- **Select elevator (SSTF)**: O(n)
- **Process requests**: O(m) where m = floors in queue

### Space Complexity
- **Controller**: O(n) for n elevators
- **Elevator**: O(m) for m floor requests
- **Overall**: O(n × m)

---

## Performance Metrics

Key metrics to evaluate system:
1. **Average Wait Time**: Time from request to pickup
2. **Average Travel Time**: Time from pickup to destination
3. **Throughput**: Requests handled per unit time
4. **Elevator Utilization**: % time elevators are in use
5. **Fairness**: Variance in wait times
6. **Energy Consumption**: Total distance traveled

---

## Conclusion

This elevator system design demonstrates:
- Sophisticated state management using State pattern
- Flexible scheduling using Strategy pattern
- Centralized control using Singleton pattern
- Event notification using Observer pattern
- Clean separation of concerns (SOLID principles)
- Multiple scheduling algorithms for optimization
- Comprehensive request handling
- Safety and edge case handling

The system is production-ready for simulation and can be extended with hardware integration, advanced algorithms, and real-time monitoring.
