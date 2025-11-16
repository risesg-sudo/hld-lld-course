"""
Elevator System - Complete Implementation
Demonstrates: Singleton, State, Strategy, Observer patterns
SOLID Principles: All five principles demonstrated
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Set, Optional
from datetime import datetime
from threading import Lock
import time


# ============================================================================
# ENUMERATIONS
# ============================================================================

class Direction(Enum):
    """Direction of elevator movement"""
    UP = 1
    DOWN = -1
    IDLE = 0


class RequestType(Enum):
    """Type of elevator request"""
    EXTERNAL = "external"  # From floor panel (outside elevator)
    INTERNAL = "internal"  # From elevator panel (inside elevator)


class ElevatorStatus(Enum):
    """Status of elevator"""
    IDLE = "idle"
    MOVING_UP = "moving_up"
    MOVING_DOWN = "moving_down"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"


# ============================================================================
# CORE ENTITIES
# ============================================================================

class Request:
    """
    Represents an elevator request.
    Demonstrates: SRP - manages only request data
    """

    def __init__(self, floor: int, direction: Direction, request_type: RequestType):
        """
        Initialize a request.

        Args:
            floor: Floor number
            direction: Direction (UP/DOWN for external, IDLE for internal)
            request_type: EXTERNAL or INTERNAL
        """
        self.floor = floor
        self.direction = direction
        self.request_type = request_type
        self.timestamp = datetime.now()

    def get_floor(self) -> int:
        """Get requested floor"""
        return self.floor

    def get_direction(self) -> Direction:
        """Get requested direction"""
        return self.direction

    def get_age(self) -> float:
        """Get request age in seconds"""
        return (datetime.now() - self.timestamp).total_seconds()

    def __str__(self):
        return f"Request(floor={self.floor}, dir={self.direction.name}, type={self.request_type.value})"


class Door:
    """
    Represents elevator door.
    Demonstrates: SRP - manages only door operations
    """

    def __init__(self, elevator_id: int):
        """
        Initialize door.

        Args:
            elevator_id: ID of elevator this door belongs to
        """
        self.elevator_id = elevator_id
        self.is_open = False

    def open(self):
        """Open the door"""
        if not self.is_open:
            print(f"  [Elevator {self.elevator_id}] Doors opening...")
            self.is_open = True
            time.sleep(0.5)  # Simulate door opening time
            print(f"  [Elevator {self.elevator_id}] Doors open")

    def close(self):
        """Close the door"""
        if self.is_open:
            print(f"  [Elevator {self.elevator_id}] Doors closing...")
            self.is_open = False
            time.sleep(0.5)  # Simulate door closing time
            print(f"  [Elevator {self.elevator_id}] Doors closed")

    def is_door_open(self) -> bool:
        """Check if door is open"""
        return self.is_open


# ============================================================================
# STATE PATTERN
# ============================================================================

class ElevatorState(ABC):
    """
    Abstract base class for elevator states.
    Demonstrates: State Pattern, OCP
    """

    @abstractmethod
    def move_up(self, elevator: 'Elevator'):
        """Handle move up action"""
        pass

    @abstractmethod
    def move_down(self, elevator: 'Elevator'):
        """Handle move down action"""
        pass

    @abstractmethod
    def stop(self, elevator: 'Elevator'):
        """Handle stop action"""
        pass

    @abstractmethod
    def get_status(self) -> ElevatorStatus:
        """Get status of this state"""
        pass


class IdleState(ElevatorState):
    """Elevator is idle (not moving)"""

    def move_up(self, elevator: 'Elevator'):
        """Start moving up"""
        print(f"  [Elevator {elevator.id}] Starting to move UP")
        elevator.set_state(MovingUpState())
        elevator.direction = Direction.UP

    def move_down(self, elevator: 'Elevator'):
        """Start moving down"""
        print(f"  [Elevator {elevator.id}] Starting to move DOWN")
        elevator.set_state(MovingDownState())
        elevator.direction = Direction.DOWN

    def stop(self, elevator: 'Elevator'):
        """Already stopped"""
        pass

    def get_status(self) -> ElevatorStatus:
        return ElevatorStatus.IDLE


class MovingUpState(ElevatorState):
    """Elevator is moving up"""

    def move_up(self, elevator: 'Elevator'):
        """Continue moving up"""
        elevator.current_floor += 1
        print(f"  [Elevator {elevator.id}] Moving UP → Floor {elevator.current_floor}")
        time.sleep(0.3)  # Simulate travel time

    def move_down(self, elevator: 'Elevator'):
        """Change direction to down"""
        print(f"  [Elevator {elevator.id}] Changing direction to DOWN")
        elevator.set_state(MovingDownState())
        elevator.direction = Direction.DOWN

    def stop(self, elevator: 'Elevator'):
        """Stop at current floor"""
        print(f"  [Elevator {elevator.id}] Stopping at floor {elevator.current_floor}")
        elevator.set_state(IdleState())
        elevator.direction = Direction.IDLE

    def get_status(self) -> ElevatorStatus:
        return ElevatorStatus.MOVING_UP


class MovingDownState(ElevatorState):
    """Elevator is moving down"""

    def move_up(self, elevator: 'Elevator'):
        """Change direction to up"""
        print(f"  [Elevator {elevator.id}] Changing direction to UP")
        elevator.set_state(MovingUpState())
        elevator.direction = Direction.UP

    def move_down(self, elevator: 'Elevator'):
        """Continue moving down"""
        elevator.current_floor -= 1
        print(f"  [Elevator {elevator.id}] Moving DOWN → Floor {elevator.current_floor}")
        time.sleep(0.3)  # Simulate travel time

    def stop(self, elevator: 'Elevator'):
        """Stop at current floor"""
        print(f"  [Elevator {elevator.id}] Stopping at floor {elevator.current_floor}")
        elevator.set_state(IdleState())
        elevator.direction = Direction.IDLE

    def get_status(self) -> ElevatorStatus:
        return ElevatorStatus.IDLE


class MaintenanceState(ElevatorState):
    """Elevator is in maintenance mode"""

    def move_up(self, elevator: 'Elevator'):
        """Cannot move in maintenance"""
        print(f"  [Elevator {elevator.id}] Cannot move - in MAINTENANCE mode")

    def move_down(self, elevator: 'Elevator'):
        """Cannot move in maintenance"""
        print(f"  [Elevator {elevator.id}] Cannot move - in MAINTENANCE mode")

    def stop(self, elevator: 'Elevator'):
        """Already stopped"""
        pass

    def get_status(self) -> ElevatorStatus:
        return ElevatorStatus.MAINTENANCE


# ============================================================================
# ELEVATOR
# ============================================================================

class Elevator:
    """
    Represents an elevator car.
    Demonstrates: State Pattern usage, SRP
    """

    def __init__(self, elevator_id: int, max_capacity: int = 10, total_floors: int = 10):
        """
        Initialize elevator.

        Args:
            elevator_id: Unique elevator ID
            max_capacity: Maximum number of passengers
            total_floors: Total floors in building (0 to total_floors-1)
        """
        self.id = elevator_id
        self.current_floor = 0
        self.state: ElevatorState = IdleState()
        self.direction = Direction.IDLE
        self.max_capacity = max_capacity
        self.current_load = 0
        self.total_floors = total_floors

        # Request queues
        self.requests: Set[int] = set()  # All destination floors
        self.up_requests: Set[int] = set()  # Floors to stop while going up
        self.down_requests: Set[int] = set()  # Floors to stop while going down

        self.door = Door(elevator_id)
        self.observers: List['Display'] = []

    def add_request(self, floor: int):
        """
        Add a floor request.

        Args:
            floor: Destination floor
        """
        if floor < 0 or floor >= self.total_floors:
            print(f"  [Elevator {self.id}] Invalid floor: {floor}")
            return

        if floor == self.current_floor:
            print(f"  [Elevator {self.id}] Already at floor {floor}")
            return

        self.requests.add(floor)

        # Categorize request
        if floor > self.current_floor:
            self.up_requests.add(floor)
        else:
            self.down_requests.add(floor)

        print(f"  [Elevator {self.id}] Added request for floor {floor}")

    def process_requests(self):
        """Process all requests using SCAN algorithm"""
        while self.requests:
            # Determine next move based on current direction
            if self.direction == Direction.IDLE:
                # Choose direction based on available requests
                if self.up_requests:
                    self.direction = Direction.UP
                elif self.down_requests:
                    self.direction = Direction.DOWN
                else:
                    break

            # Move in current direction
            if self.direction == Direction.UP:
                if self.up_requests:
                    next_floor = min(self.up_requests)
                    self._move_to_floor(next_floor)
                else:
                    # No more up requests, switch to down
                    if self.down_requests:
                        self.direction = Direction.DOWN
                    else:
                        self.state.stop(self)
                        break

            elif self.direction == Direction.DOWN:
                if self.down_requests:
                    next_floor = max(self.down_requests)
                    self._move_to_floor(next_floor)
                else:
                    # No more down requests, switch to up
                    if self.up_requests:
                        self.direction = Direction.UP
                    else:
                        self.state.stop(self)
                        break

    def _move_to_floor(self, target_floor: int):
        """
        Move elevator to target floor.

        Args:
            target_floor: Destination floor
        """
        # Move floor by floor
        while self.current_floor != target_floor:
            if self.current_floor < target_floor:
                self.state.move_up(self)
            else:
                self.state.move_down(self)

            self.notify_observers()

            # Check if we should stop at current floor
            if self.should_stop_at_current_floor():
                self._stop_at_floor()

        # Final stop at target floor
        if target_floor in self.requests:
            self._stop_at_floor()

    def should_stop_at_current_floor(self) -> bool:
        """Check if elevator should stop at current floor"""
        if self.direction == Direction.UP:
            return self.current_floor in self.up_requests
        elif self.direction == Direction.DOWN:
            return self.current_floor in self.down_requests
        return self.current_floor in self.requests

    def _stop_at_floor(self):
        """Stop at current floor and open doors"""
        print(f"\n  [Elevator {self.id}] === Arriving at floor {self.current_floor} ===")

        # Remove from request queues
        self.requests.discard(self.current_floor)
        self.up_requests.discard(self.current_floor)
        self.down_requests.discard(self.current_floor)

        # Open doors
        self.door.open()
        time.sleep(1)  # Time for passengers to enter/exit
        self.door.close()

        print(f"  [Elevator {self.id}] Remaining requests: {sorted(self.requests)}\n")

    def get_current_floor(self) -> int:
        """Get current floor"""
        return self.current_floor

    def get_state(self) -> ElevatorState:
        """Get current state"""
        return self.state

    def set_state(self, state: ElevatorState):
        """Set elevator state"""
        self.state = state

    def is_idle(self) -> bool:
        """Check if elevator is idle"""
        return isinstance(self.state, IdleState)

    def is_moving(self) -> bool:
        """Check if elevator is moving"""
        return isinstance(self.state, (MovingUpState, MovingDownState))

    def can_take_request(self, request: Request) -> bool:
        """
        Check if elevator can take this request.

        Args:
            request: Request to evaluate

        Returns:
            True if elevator can handle this request
        """
        # Can't take requests in maintenance
        if isinstance(self.state, MaintenanceState):
            return False

        # If idle, can take any request
        if self.is_idle():
            return True

        # If moving in same direction and haven't passed the floor
        if request.direction == Direction.UP and self.direction == Direction.UP:
            return request.floor >= self.current_floor

        if request.direction == Direction.DOWN and self.direction == Direction.DOWN:
            return request.floor <= self.current_floor

        return False

    def add_observer(self, observer: 'Display'):
        """Add display observer"""
        self.observers.append(observer)

    def notify_observers(self):
        """Notify all observers of state change"""
        for observer in self.observers:
            observer.update(self.current_floor, self.direction)

    def get_status_summary(self) -> dict:
        """Get elevator status summary"""
        return {
            'id': self.id,
            'current_floor': self.current_floor,
            'state': self.state.get_status().value,
            'direction': self.direction.name,
            'requests': sorted(self.requests),
            'load': f"{self.current_load}/{self.max_capacity}"
        }

    def __str__(self):
        return f"Elevator {self.id} @ Floor {self.current_floor} ({self.state.get_status().value})"


# ============================================================================
# STRATEGY PATTERN (Scheduling)
# ============================================================================

class SchedulingStrategy(ABC):
    """
    Abstract scheduling strategy.
    Demonstrates: Strategy Pattern, OCP
    """

    @abstractmethod
    def select_elevator(self, elevators: List[Elevator], request: Request) -> Optional[Elevator]:
        """
        Select best elevator for request.

        Args:
            elevators: Available elevators
            request: Elevator request

        Returns:
            Selected elevator or None
        """
        pass


class SCANStrategy(SchedulingStrategy):
    """
    SCAN (Elevator) Algorithm.
    Select elevator already moving in requested direction or nearest idle elevator.
    """

    def select_elevator(self, elevators: List[Elevator], request: Request) -> Optional[Elevator]:
        """Select elevator using SCAN algorithm"""
        available = [e for e in elevators if e.can_take_request(request)]

        if not available:
            # No suitable elevator, get nearest idle
            idle_elevators = [e for e in elevators if e.is_idle()]
            if idle_elevators:
                return min(idle_elevators, key=lambda e: abs(e.current_floor - request.floor))
            return None

        # Prefer elevator already moving in same direction
        same_direction = [
            e for e in available
            if e.direction == request.direction and e.is_moving()
        ]

        if same_direction:
            # Get closest one
            return min(same_direction, key=lambda e: abs(e.current_floor - request.floor))

        # Otherwise, get nearest available
        return min(available, key=lambda e: abs(e.current_floor - request.floor))


class FCFSStrategy(SchedulingStrategy):
    """
    First Come First Served.
    Simply select nearest elevator.
    """

    def select_elevator(self, elevators: List[Elevator], request: Request) -> Optional[Elevator]:
        """Select nearest elevator"""
        available = [e for e in elevators if not isinstance(e.state, MaintenanceState)]

        if not available:
            return None

        return min(available, key=lambda e: abs(e.current_floor - request.floor))


class LOOKStrategy(SchedulingStrategy):
    """
    LOOK Algorithm.
    Like SCAN but reverses at last request, not at end of building.
    """

    def select_elevator(self, elevators: List[Elevator], request: Request) -> Optional[Elevator]:
        """Select elevator using LOOK algorithm"""
        # Similar to SCAN for selection purposes
        # The difference is in how elevator processes its queue (handled in Elevator.process_requests)
        scan = SCANStrategy()
        return scan.select_elevator(elevators, request)


# ============================================================================
# OBSERVER PATTERN (Display)
# ============================================================================

class Display:
    """
    Elevator display.
    Demonstrates: Observer Pattern
    """

    def __init__(self, elevator_id: int):
        """
        Initialize display.

        Args:
            elevator_id: ID of elevator this display belongs to
        """
        self.elevator_id = elevator_id
        self.current_floor = 0
        self.direction = Direction.IDLE

    def update(self, floor: int, direction: Direction):
        """
        Update display with new information.

        Args:
            floor: Current floor
            direction: Current direction
        """
        self.current_floor = floor
        self.direction = direction
        # In real system, this would update physical display
        # For now, we just track the state

    def show_status(self):
        """Show current status"""
        arrow = "↑" if self.direction == Direction.UP else "↓" if self.direction == Direction.DOWN else "•"
        print(f"  Display {self.elevator_id}: Floor {self.current_floor} {arrow}")


class Floor:
    """Represents a floor with call buttons"""

    def __init__(self, floor_number: int):
        """
        Initialize floor.

        Args:
            floor_number: Floor number
        """
        self.floor_number = floor_number
        self.up_button_pressed = False
        self.down_button_pressed = False

    def press_up_button(self):
        """Press UP button"""
        self.up_button_pressed = True

    def press_down_button(self):
        """Press DOWN button"""
        self.down_button_pressed = True

    def reset_buttons(self):
        """Reset both buttons"""
        self.up_button_pressed = False
        self.down_button_pressed = False


# ============================================================================
# SINGLETON PATTERN (Controller)
# ============================================================================

class ElevatorController:
    """
    Central elevator controller.
    Demonstrates: Singleton Pattern, Facade Pattern
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        """Ensure only one instance exists (thread-safe)"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize controller"""
        if self._initialized:
            return

        self.elevators: List[Elevator] = []
        self.strategy: SchedulingStrategy = SCANStrategy()  # Default strategy
        self.pending_requests: List[Request] = []
        self.floors: List[Floor] = []
        self._initialized = True

    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        return cls()

    def initialize_building(self, num_floors: int, num_elevators: int):
        """
        Initialize building with elevators and floors.

        Args:
            num_floors: Number of floors
            num_elevators: Number of elevators
        """
        # Create floors
        self.floors = [Floor(i) for i in range(num_floors)]

        # Create elevators
        for i in range(num_elevators):
            elevator = Elevator(i + 1, max_capacity=10, total_floors=num_floors)
            display = Display(i + 1)
            elevator.add_observer(display)
            self.elevators.append(elevator)

        print(f"✓ Building initialized: {num_floors} floors, {num_elevators} elevators")

    def add_elevator(self, elevator: Elevator):
        """Add an elevator to the system"""
        self.elevators.append(elevator)

    def request_elevator(self, floor: int, direction: Direction) -> Request:
        """
        Request an elevator from a floor.

        Args:
            floor: Floor number
            direction: Direction (UP or DOWN)

        Returns:
            Created request
        """
        request = Request(floor, direction, RequestType.EXTERNAL)
        print(f"\n>>> New request: Floor {floor}, Direction: {direction.name}")

        # Try to dispatch immediately
        elevator = self.dispatch_request(request)

        if elevator:
            print(f"✓ Request assigned to Elevator {elevator.id}")
        else:
            print(f"⚠ No suitable elevator available, request queued")
            self.pending_requests.append(request)

        return request

    def dispatch_request(self, request: Request) -> Optional[Elevator]:
        """
        Dispatch request to an elevator.

        Args:
            request: Request to dispatch

        Returns:
            Selected elevator or None
        """
        # Use strategy to select elevator
        elevator = self.strategy.select_elevator(self.elevators, request)

        if elevator:
            elevator.add_request(request.floor)

        return elevator

    def set_strategy(self, strategy: SchedulingStrategy):
        """
        Set scheduling strategy.

        Args:
            strategy: New scheduling strategy
        """
        self.strategy = strategy
        print(f"✓ Scheduling strategy changed to {strategy.__class__.__name__}")

    def process_pending_requests(self):
        """Process queued requests"""
        if not self.pending_requests:
            return

        print(f"\nProcessing {len(self.pending_requests)} pending requests...")

        # Try to dispatch each pending request
        still_pending = []
        for request in self.pending_requests:
            elevator = self.dispatch_request(request)
            if elevator:
                print(f"✓ Pending request (floor {request.floor}) assigned to Elevator {elevator.id}")
            else:
                still_pending.append(request)

        self.pending_requests = still_pending

    def get_elevator_status(self, elevator_id: int) -> Optional[dict]:
        """Get status of specific elevator"""
        for elevator in self.elevators:
            if elevator.id == elevator_id:
                return elevator.get_status_summary()
        return None

    def get_all_statuses(self):
        """Get status of all elevators"""
        print("\n" + "="*70)
        print(" ELEVATOR SYSTEM STATUS ".center(70))
        print("="*70)

        for elevator in self.elevators:
            status = elevator.get_status_summary()
            requests_str = str(status['requests']) if status['requests'] else "none"
            print(f"Elevator {status['id']}: Floor {status['current_floor']:2d} | "
                  f"{status['state']:12s} | {status['direction']:4s} | "
                  f"Requests: {requests_str}")

        print("="*70 + "\n")


# ============================================================================
# DEMO
# ============================================================================

def demo_elevator_system():
    """Demonstrate elevator system with sample requests"""

    print("\n" + "="*80)
    print(" ELEVATOR SYSTEM - DEMO ".center(80))
    print("="*80 + "\n")

    # Initialize controller (Singleton)
    controller = ElevatorController.get_instance()

    # Verify singleton
    controller2 = ElevatorController.get_instance()
    print(f"✓ Singleton verified: {controller is controller2}\n")

    # Initialize building
    NUM_FLOORS = 10
    NUM_ELEVATORS = 3
    controller.initialize_building(NUM_FLOORS, NUM_ELEVATORS)

    # Display initial status
    controller.get_all_statuses()

    # Set strategy
    print("Using SCAN scheduling strategy")
    controller.set_strategy(SCANStrategy())

    # Scenario 1: Multiple requests
    print("\n" + "="*80)
    print(" SCENARIO 1: Multiple Floor Requests ".center(80))
    print("="*80)

    # Person at floor 0 wants to go up
    controller.request_elevator(0, Direction.UP)
    elevator1 = controller.elevators[0]
    elevator1.add_request(7)  # Going to floor 7

    # Person at floor 5 wants to go down
    controller.request_elevator(5, Direction.DOWN)
    elevator2 = controller.elevators[1]
    elevator2.add_request(0)  # Going to ground floor

    # Person at floor 9 wants to go down
    controller.request_elevator(9, Direction.DOWN)

    controller.get_all_statuses()

    # Process elevator 1's requests
    print("\n--- Elevator 1 Processing Requests ---")
    elevator1.process_requests()

    # Process elevator 2's requests
    print("\n--- Elevator 2 Processing Requests ---")
    elevator2.process_requests()

    # Final status
    controller.get_all_statuses()

    # Scenario 2: Strategy Comparison
    print("\n" + "="*80)
    print(" SCENARIO 2: Testing FCFS Strategy ".center(80))
    print("="*80)

    # Reset elevators to ground floor
    for elevator in controller.elevators:
        elevator.current_floor = 0
        elevator.state = IdleState()
        elevator.direction = Direction.IDLE
        elevator.requests.clear()
        elevator.up_requests.clear()
        elevator.down_requests.clear()

    # Change to FCFS strategy
    controller.set_strategy(FCFSStrategy())

    # Make same requests
    controller.request_elevator(5, Direction.UP)
    controller.request_elevator(3, Direction.DOWN)
    controller.request_elevator(8, Direction.DOWN)

    controller.get_all_statuses()

    # Scenario 3: Complex Journey
    print("\n" + "="*80)
    print(" SCENARIO 3: Complex Multi-Stop Journey ".center(80))
    print("="*80)

    # Reset
    for elevator in controller.elevators:
        elevator.current_floor = 0
        elevator.state = IdleState()
        elevator.direction = Direction.IDLE
        elevator.requests.clear()
        elevator.up_requests.clear()
        elevator.down_requests.clear()

    controller.set_strategy(SCANStrategy())

    # Elevator serving multiple floors
    test_elevator = controller.elevators[0]
    test_elevator.add_request(3)
    test_elevator.add_request(5)
    test_elevator.add_request(8)
    test_elevator.add_request(2)
    test_elevator.add_request(6)

    print(f"\nElevator {test_elevator.id} requests: {sorted(test_elevator.requests)}")
    print("Processing with SCAN algorithm (should go up first, then down)...\n")

    test_elevator.process_requests()

    controller.get_all_statuses()

    print("\n" + "="*80)
    print(" DEMO COMPLETED ".center(80))
    print("="*80 + "\n")

    print("DESIGN PATTERNS DEMONSTRATED:")
    print("  ✓ Singleton: ElevatorController (single instance)")
    print("  ✓ State: ElevatorState (Idle, MovingUp, MovingDown, Maintenance)")
    print("  ✓ Strategy: SchedulingStrategy (SCAN, FCFS, LOOK)")
    print("  ✓ Observer: Display observes elevator state changes")
    print("\nSOLID PRINCIPLES DEMONSTRATED:")
    print("  ✓ SRP: Each class has single responsibility")
    print("  ✓ OCP: Open for extension (new strategies, states)")
    print("  ✓ LSP: All strategies/states are substitutable")
    print("  ✓ ISP: Focused interfaces (SchedulingStrategy, ElevatorState)")
    print("  ✓ DIP: Depend on abstractions (Strategy, State interfaces)")

    print("\nKEY FEATURES:")
    print("  • SCAN Algorithm: Elevator serves requests in current direction first")
    print("  • State Management: Clean state transitions (Idle ↔ Moving)")
    print("  • Multiple Strategies: Easy to switch between scheduling algorithms")
    print("  • Observer Pattern: Displays automatically update when elevator moves")
    print("  • Extensible: Easy to add new states, strategies, or features")


if __name__ == "__main__":
    demo_elevator_system()
