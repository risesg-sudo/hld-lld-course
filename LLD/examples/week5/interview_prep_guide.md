# LLD Interview Preparation Guide

## Overview
This comprehensive guide provides 50+ commonly asked Low-Level Design (LLD) interview questions across different categories, along with approaches, sample answers, and company-specific tips.

## Table of Contents
1. [System Design Questions](#system-design-questions)
2. [Design Pattern Questions](#design-pattern-questions)
3. [SOLID Principles Questions](#solid-principles-questions)
4. [Scenario-Based Questions](#scenario-based-questions)
5. [Company-Specific Tips](#company-specific-tips)
6. [Interview Approach Framework](#interview-approach-framework)

---

## System Design Questions

### 1. Design a Parking Lot System

**Difficulty**: Medium
**Companies**: Amazon, Google, Microsoft, Uber

**Requirements to Clarify**:
- Types of vehicles (motorcycle, car, truck, bus)?
- Parking spot types (handicapped, compact, large, motorcycle)?
- Pricing model (hourly, daily, monthly pass)?
- Payment methods?
- Features needed (find nearest spot, reserve spot)?

**Key Classes**:
```python
ParkingLot, Level, ParkingSpot, Vehicle, Ticket, PaymentProcessor
```

**Design Patterns**:
- **Singleton**: ParkingLot (single instance)
- **Factory**: VehicleFactory, SpotFactory
- **Strategy**: PricingStrategy, ParkingStrategy
- **State**: SpotState (available, occupied, reserved)

**Sample Code Snippet**:
```python
class ParkingLot:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.levels: List[Level] = []
        self.entry_panels: List[EntryPanel] = []
        self.exit_panels: List[ExitPanel] = []

    def park_vehicle(self, vehicle: Vehicle) -> Optional[Ticket]:
        for level in self.levels:
            spot = level.find_available_spot(vehicle.type)
            if spot:
                spot.assign_vehicle(vehicle)
                return self._generate_ticket(vehicle, spot)
        return None
```

**Key Points to Discuss**:
- Thread safety for concurrent parking/exiting
- Efficient spot finding algorithm
- Handling different vehicle sizes
- Payment processing flow

---

### 2. Design a Library Management System

**Difficulty**: Medium
**Companies**: Amazon, Adobe, Microsoft

**Requirements to Clarify**:
- User roles (member, librarian, admin)?
- Book lending period?
- Late fee calculation?
- Book reservation system?
- Multiple copies of same book?

**Key Classes**:
```python
Library, Book, BookItem, Member, Librarian, Lending, Reservation
```

**Design Patterns**:
- **Singleton**: Library
- **Factory**: NotificationFactory
- **Observer**: Notification system for overdue books
- **Strategy**: FineCalculationStrategy

**Sample Approach**:
```
1. Core entities:
   - Book (metadata) vs BookItem (physical copy)
   - Member with borrowing history
   - Lending transaction

2. Key operations:
   - Search books (by title, author, ISBN, category)
   - Check out / return books
   - Renew lending
   - Reserve books
   - Calculate and pay fines

3. Business rules:
   - Max books per member (e.g., 5)
   - Lending period (e.g., 14 days)
   - Late fee calculation
   - Reservation expires after N days
```

---

### 3. Design an ATM System

**Difficulty**: Medium
**Companies**: Amazon, Microsoft, Intuit

**Requirements to Clarify**:
- Operations supported (withdraw, deposit, check balance, transfer)?
- Cash denominations?
- Daily withdrawal limits?
- Multiple accounts per card?
- Failed transaction handling?

**Key Classes**:
```python
ATM, Card, Account, Transaction, CashDispenser, CardReader, Screen
```

**Design Patterns**:
- **State**: ATMState (idle, card inserted, PIN verified, transaction in progress)
- **Strategy**: TransactionStrategy (withdraw, deposit, transfer)
- **Chain of Responsibility**: CashDispenser (different denominations)
- **Singleton**: ATM

**State Diagram**:
```
Idle → CardInserted → PINVerified → TransactionInProgress → Idle
       ↓                ↓                ↓
    CardEjected    InvalidPIN      TransactionFailed
```

**Critical Edge Cases**:
- Insufficient funds in account
- Insufficient cash in ATM
- Card gets stuck
- Network failure during transaction
- Concurrent transactions

---

### 4. Design a Hotel Booking System

**Difficulty**: Medium-Hard
**Companies**: Booking.com, Airbnb, Expedia

**Requirements to Clarify**:
- Room types (single, double, suite)?
- Pricing variations (season, demand)?
- Booking modifications and cancellations?
- Payment and refund policies?
- Amenities and services?

**Key Classes**:
```python
Hotel, Room, RoomType, Booking, Guest, Payment, Amenity
```

**Design Patterns**:
- **Factory**: RoomFactory
- **Strategy**: PricingStrategy (dynamic pricing)
- **Observer**: BookingNotifications
- **State**: BookingState (pending, confirmed, checked-in, completed, cancelled)

**Complex Scenarios**:
```python
# Double booking prevention
def book_room(room_id: str, check_in: Date, check_out: Date) -> Booking:
    with transaction():
        if room.is_available(check_in, check_out):
            booking = create_booking(room, check_in, check_out)
            room.block_dates(check_in, check_out)
            return booking
        raise RoomNotAvailableException()
```

---

### 5. Design a Movie Ticket Booking System

**Difficulty**: Medium
**Companies**: BookMyShow, Fandango

**Requirements to Clarify**:
- Multiple cities, theaters, screens?
- Seat selection (premium, normal)?
- Show timings and pricing?
- Concurrent booking handling?
- Cancellation policy?

**Key Classes**:
```python
Theater, Screen, Show, Movie, Seat, Booking, Payment
```

**Design Patterns**:
- **Singleton**: BookingManager
- **Factory**: NotificationFactory
- **Observer**: Seat availability notifications
- **State**: SeatState, BookingState

**Concurrency Handling**:
```python
class BookingManager:
    def book_seats(self, show_id: str, seat_ids: List[str]) -> Booking:
        with lock:  # Database lock or optimistic locking
            # Check all seats available
            if all(seat.is_available() for seat in seats):
                # Create temporary reservation (expires in 10 min)
                reservation = create_temp_reservation(seats, ttl=600)
                return reservation
            raise SeatsNotAvailableException()
```

---

### 6. Design a Car Rental System

**Difficulty**: Medium
**Companies**: Zipcar, Hertz, Enterprise

**Key Classes**:
```python
Vehicle, VehicleType, Rental, Customer, Location, Insurance, Payment
```

**Design Patterns**:
- **Factory**: VehicleFactory
- **Strategy**: PricingStrategy (hourly, daily, weekly)
- **Observer**: Rental notifications
- **State**: VehicleState (available, rented, maintenance, reserved)

---

### 7. Design an Online Shopping Cart

**Difficulty**: Easy-Medium
**Companies**: Amazon, Flipkart, eBay

**Key Classes**:
```python
Cart, CartItem, Product, User, Order, Payment, Inventory
```

**Design Patterns**:
- **Singleton**: Cart per session
- **Observer**: Price change notifications
- **Strategy**: DiscountStrategy, PaymentStrategy
- **Decorator**: Gift wrapping, express shipping

**Sample Implementation**:
```python
class ShoppingCart:
    def __init__(self, user: User):
        self.user = user
        self.items: Dict[str, CartItem] = {}
        self.discount_strategy: Optional[DiscountStrategy] = None

    def add_item(self, product: Product, quantity: int):
        if product.id in self.items:
            self.items[product.id].quantity += quantity
        else:
            self.items[product.id] = CartItem(product, quantity)

    def calculate_total(self) -> float:
        subtotal = sum(item.get_price() for item in self.items.values())
        if self.discount_strategy:
            return self.discount_strategy.apply_discount(subtotal)
        return subtotal
```

---

### 8. Design a Vending Machine

**Difficulty**: Medium
**Companies**: Amazon, Google

**Key Classes**:
```python
VendingMachine, Product, Inventory, Payment, State
```

**Design Patterns**:
- **State**: VendingMachineState (idle, payment pending, dispensing)
- **Factory**: ProductFactory
- **Singleton**: VendingMachine

**State Transitions**:
```
Idle → SelectProduct → PaymentPending → Dispensing → Idle
         ↓                  ↓                ↓
    InvalidSelection    CancelPayment    DispenseFailed
```

---

### 9. Design a Stack Overflow Clone

**Difficulty**: Hard
**Companies**: Stack Overflow, Reddit, Quora

**Requirements to Clarify**:
- User reputation system?
- Voting mechanism?
- Comment threading?
- Search functionality?
- Tags and categorization?

**Key Classes**:
```python
User, Question, Answer, Comment, Tag, Vote, Badge, Reputation
```

**Design Patterns**:
- **Observer**: Notification system (answer posted, comment added)
- **Strategy**: ReputationCalculationStrategy
- **Composite**: CommentTree (nested comments)
- **Factory**: BadgeFactory

**Sample Reputation System**:
```python
class ReputationManager:
    REPUTATION_RULES = {
        'question_upvote': 5,
        'answer_upvote': 10,
        'answer_accepted': 15,
        'question_downvote': -2,
    }

    def update_reputation(self, user: User, action: str):
        points = self.REPUTATION_RULES.get(action, 0)
        user.reputation += points
        self._check_badge_eligibility(user)
```

---

### 10. Design a Social Network (Facebook/Twitter)

**Difficulty**: Hard
**Companies**: Facebook, Twitter, LinkedIn

**Key Classes**:
```python
User, Post, Comment, Like, Follow, Feed, Notification
```

**Design Patterns**:
- **Observer**: Feed updates, notifications
- **Strategy**: FeedRankingStrategy
- **Composite**: CommentTree
- **Factory**: PostFactory (text, image, video)

**Feed Generation**:
```python
class FeedGenerator:
    def __init__(self, ranking_strategy: FeedRankingStrategy):
        self.ranking_strategy = ranking_strategy

    def generate_feed(self, user: User, limit: int) -> List[Post]:
        # Get posts from friends
        friend_posts = self._get_friend_posts(user)

        # Rank posts
        ranked_posts = self.ranking_strategy.rank(friend_posts, user)

        return ranked_posts[:limit]
```

---

## Design Pattern Questions

### 11. Implement Singleton Pattern (Thread-Safe)

**Difficulty**: Easy
**Companies**: All

**Sample Answer**:
```python
from threading import Lock

class Singleton:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

**Key Points**:
- Double-checked locking
- Thread safety
- Lazy initialization
- When to use: Database connection, Logger, Configuration

---

### 12. Implement Factory Pattern

**Difficulty**: Easy
**Companies**: All

**Sample Answer**:
```python
class ShapeFactory:
    @staticmethod
    def create_shape(shape_type: str) -> Shape:
        if shape_type == "circle":
            return Circle()
        elif shape_type == "square":
            return Square()
        elif shape_type == "triangle":
            return Triangle()
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")
```

**When to Use**:
- Object creation logic is complex
- Need to create different types based on input
- Want to centralize creation logic

---

### 13. Implement Observer Pattern

**Difficulty**: Medium
**Companies**: All

**Sample Answer**:
```python
class Subject:
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self, event: Event):
        for observer in self._observers:
            observer.update(event)

class Observer(ABC):
    @abstractmethod
    def update(self, event: Event):
        pass
```

**Use Cases**:
- Event handling
- Notification systems
- MVC architecture
- Publish-subscribe systems

---

### 14. Implement Strategy Pattern

**Difficulty**: Medium
**Companies**: All

**Sample Answer**:
```python
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        # Process credit card payment
        return True

class PayPalPayment(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        # Process PayPal payment
        return True

class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def process_payment(self, amount: float):
        return self.strategy.pay(amount)
```

**Benefits**:
- Runtime algorithm selection
- Easy to add new strategies
- Follows Open/Closed Principle

---

### 15. Implement Decorator Pattern

**Difficulty**: Medium
**Companies**: All

**Sample Answer**:
```python
class Coffee:
    def cost(self) -> float:
        return 5.0

    def description(self) -> str:
        return "Simple coffee"

class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self._coffee = coffee

    def cost(self) -> float:
        return self._coffee.cost()

    def description(self) -> str:
        return self._coffee.description()

class MilkDecorator(CoffeeDecorator):
    def cost(self) -> float:
        return self._coffee.cost() + 1.5

    def description(self) -> str:
        return self._coffee.description() + ", milk"

# Usage
coffee = Coffee()
coffee_with_milk = MilkDecorator(coffee)
coffee_with_milk_and_sugar = SugarDecorator(coffee_with_milk)
```

---

### 16. Implement Builder Pattern

**Difficulty**: Medium
**Companies**: Amazon, Google

**Sample Answer**:
```python
class House:
    def __init__(self):
        self.foundation = None
        self.walls = None
        self.roof = None
        self.windows = None

class HouseBuilder:
    def __init__(self):
        self.house = House()

    def build_foundation(self, foundation_type: str):
        self.house.foundation = foundation_type
        return self

    def build_walls(self, wall_type: str):
        self.house.walls = wall_type
        return self

    def build_roof(self, roof_type: str):
        self.house.roof = roof_type
        return self

    def build_windows(self, window_count: int):
        self.house.windows = window_count
        return self

    def build(self) -> House:
        return self.house

# Usage
house = (HouseBuilder()
         .build_foundation("concrete")
         .build_walls("brick")
         .build_roof("tiles")
         .build_windows(6)
         .build())
```

---

### 17. Implement Adapter Pattern

**Difficulty**: Medium
**Companies**: Microsoft, Oracle

**Sample Answer**:
```python
# Legacy interface
class OldPaymentGateway:
    def make_payment(self, amount: int):
        print(f"Processing ${amount} via old gateway")

# New interface
class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float):
        pass

# Adapter
class PaymentGatewayAdapter(PaymentProcessor):
    def __init__(self, old_gateway: OldPaymentGateway):
        self.old_gateway = old_gateway

    def process_payment(self, amount: float):
        # Convert float to int (cents)
        amount_cents = int(amount * 100)
        self.old_gateway.make_payment(amount_cents)
```

---

### 18. Implement Command Pattern

**Difficulty**: Medium
**Companies**: Amazon, Adobe

**Sample Answer**:
```python
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class Light:
    def turn_on(self):
        print("Light is ON")

    def turn_off(self):
        print("Light is OFF")

class LightOnCommand(Command):
    def __init__(self, light: Light):
        self.light = light

    def execute(self):
        self.light.turn_on()

    def undo(self):
        self.light.turn_off()

class RemoteControl:
    def __init__(self):
        self.history: List[Command] = []

    def execute_command(self, command: Command):
        command.execute()
        self.history.append(command)

    def undo_last(self):
        if self.history:
            command = self.history.pop()
            command.undo()
```

---

### 19. Implement Template Method Pattern

**Difficulty**: Medium
**Companies**: Google, Microsoft

**Sample Answer**:
```python
class DataProcessor(ABC):
    def process(self, data):
        # Template method
        raw_data = self.read_data(data)
        validated = self.validate_data(raw_data)
        processed = self.transform_data(validated)
        self.save_data(processed)

    @abstractmethod
    def read_data(self, source):
        pass

    def validate_data(self, data):
        # Default implementation
        return data

    @abstractmethod
    def transform_data(self, data):
        pass

    @abstractmethod
    def save_data(self, data):
        pass

class CSVDataProcessor(DataProcessor):
    def read_data(self, source):
        return read_csv(source)

    def transform_data(self, data):
        return data.upper()

    def save_data(self, data):
        write_to_database(data)
```

---

### 20. Implement Chain of Responsibility

**Difficulty**: Medium
**Companies**: Amazon, Google

**Sample Answer**:
```python
class Handler(ABC):
    def __init__(self):
        self._next_handler: Optional[Handler] = None

    def set_next(self, handler: 'Handler'):
        self._next_handler = handler
        return handler

    def handle(self, request):
        if self._can_handle(request):
            return self._process(request)
        elif self._next_handler:
            return self._next_handler.handle(request)
        return None

    @abstractmethod
    def _can_handle(self, request) -> bool:
        pass

    @abstractmethod
    def _process(self, request):
        pass

class SmallAmountHandler(Handler):
    def _can_handle(self, amount: float) -> bool:
        return amount < 100

    def _process(self, amount: float):
        print(f"Clerk approved: ${amount}")
        return True

class LargeAmountHandler(Handler):
    def _can_handle(self, amount: float) -> bool:
        return amount >= 100

    def _process(self, amount: float):
        print(f"Manager approved: ${amount}")
        return True
```

---

## SOLID Principles Questions

### 21. Explain Single Responsibility Principle with Example

**Answer**:
The Single Responsibility Principle states that a class should have only one reason to change.

**Bad Example**:
```python
class UserManager:
    def create_user(self, data):
        # User creation logic
        user = User(data)

        # Database logic (second responsibility!)
        database.save(user)

        # Email logic (third responsibility!)
        send_email(user.email, "Welcome!")

        return user
```

**Good Example**:
```python
class UserManager:
    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service

    def create_user(self, data):
        user = User(data)
        self.user_repo.save(user)
        self.email_service.send_welcome_email(user)
        return user

class UserRepository:
    def save(self, user: User):
        database.save(user)

class EmailService:
    def send_welcome_email(self, user: User):
        send_email(user.email, "Welcome!")
```

---

### 22. Explain Open/Closed Principle with Example

**Answer**:
Classes should be open for extension but closed for modification.

**Bad Example**:
```python
class AreaCalculator:
    def calculate_area(self, shape):
        if shape.type == "circle":
            return 3.14 * shape.radius ** 2
        elif shape.type == "square":
            return shape.side ** 2
        # Need to modify this class to add new shapes!
```

**Good Example**:
```python
class Shape(ABC):
    @abstractmethod
    def calculate_area(self) -> float:
        pass

class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def calculate_area(self) -> float:
        return 3.14 * self.radius ** 2

class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def calculate_area(self) -> float:
        return self.side ** 2

# Can add new shapes without modifying existing code
class Triangle(Shape):
    def calculate_area(self) -> float:
        return 0.5 * self.base * self.height
```

---

### 23. Explain Liskov Substitution Principle

**Answer**:
Objects of a superclass should be replaceable with objects of its subclasses without breaking the application.

**Bad Example**:
```python
class Bird:
    def fly(self):
        print("Flying...")

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins can't fly!")  # Violates LSP!
```

**Good Example**:
```python
class Bird:
    def move(self):
        pass

class FlyingBird(Bird):
    def move(self):
        self.fly()

    def fly(self):
        print("Flying...")

class Penguin(Bird):
    def move(self):
        self.swim()

    def swim(self):
        print("Swimming...")
```

---

### 24. Explain Interface Segregation Principle

**Answer**:
Clients should not be forced to depend on interfaces they don't use.

**Bad Example**:
```python
class Worker(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass

class Robot(Worker):
    def work(self):
        print("Working...")

    def eat(self):
        # Robots don't eat! Forced to implement unnecessary method
        raise NotImplementedError()
```

**Good Example**:
```python
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Human(Workable, Eatable):
    def work(self):
        print("Working...")

    def eat(self):
        print("Eating...")

class Robot(Workable):
    def work(self):
        print("Working...")
```

---

### 25. Explain Dependency Inversion Principle

**Answer**:
High-level modules should not depend on low-level modules. Both should depend on abstractions.

**Bad Example**:
```python
class MySQLDatabase:
    def save(self, data):
        print("Saving to MySQL...")

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Tight coupling!

    def save_user(self, user):
        self.db.save(user)
```

**Good Example**:
```python
class Database(ABC):
    @abstractmethod
    def save(self, data):
        pass

class MySQLDatabase(Database):
    def save(self, data):
        print("Saving to MySQL...")

class MongoDatabase(Database):
    def save(self, data):
        print("Saving to MongoDB...")

class UserService:
    def __init__(self, db: Database):
        self.db = db  # Depends on abstraction!

    def save_user(self, user):
        self.db.save(user)
```

---

## Scenario-Based Questions

### 26. How Would You Design a Rate Limiter?

**Difficulty**: Medium-Hard
**Companies**: Google, Amazon, Twitter

**Approach**:
```python
class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window  # in seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        window_start = now - self.time_window

        # Remove old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > window_start
        ]

        # Check if under limit
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True

        return False
```

**Algorithms**:
1. **Token Bucket**: Refill tokens at fixed rate
2. **Sliding Window**: Track requests in time window
3. **Fixed Window Counter**: Reset counter every window
4. **Leaky Bucket**: Process requests at constant rate

---

### 27. How to Handle Concurrent Bookings?

**Answer**:
Use one of these approaches:

1. **Pessimistic Locking**:
```python
def book_seat(seat_id: str):
    with database.transaction():
        seat = database.select_for_update(seat_id)
        if seat.is_available:
            seat.status = "BOOKED"
            database.commit()
            return True
        return False
```

2. **Optimistic Locking**:
```python
def book_seat(seat_id: str):
    seat = database.get(seat_id)
    old_version = seat.version

    seat.status = "BOOKED"
    seat.version += 1

    rows_updated = database.update_where(
        seat_id=seat_id,
        version=old_version,
        new_data=seat
    )

    return rows_updated > 0  # False if version changed
```

3. **Distributed Lock** (Redis):
```python
def book_seat(seat_id: str):
    lock_key = f"lock:seat:{seat_id}"
    if redis.set(lock_key, "1", nx=True, ex=10):  # 10 sec TTL
        try:
            # Perform booking
            return book_seat_internal(seat_id)
        finally:
            redis.delete(lock_key)
    return False
```

---

### 28. Design a Cache with LRU Eviction

**Difficulty**: Medium
**Companies**: Google, Facebook, Amazon

**Answer**:
```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: Any):
        if key in self.cache:
            # Update and move to end
            self.cache.move_to_end(key)

        self.cache[key] = value

        if len(self.cache) > self.capacity:
            # Remove least recently used (first item)
            self.cache.popitem(last=False)
```

**Using Doubly Linked List + HashMap**:
```python
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict[str, Node] = {}
        self.head = Node(0, 0)  # Dummy head
        self.tail = Node(0, 0)  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head

    def _add_to_head(self, node: Node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: Node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            node = self.cache[key]
            self._remove_node(node)
            self._add_to_head(node)
            return node.value
        return None

    def put(self, key: str, value: Any):
        if key in self.cache:
            self._remove_node(self.cache[key])

        node = Node(key, value)
        self.cache[key] = node
        self._add_to_head(node)

        if len(self.cache) > self.capacity:
            # Remove LRU
            lru = self.tail.prev
            self._remove_node(lru)
            del self.cache[lru.key]
```

---

### 29. How to Implement Undo/Redo Functionality?

**Answer**:
Use Command Pattern with two stacks:

```python
class TextEditor:
    def __init__(self):
        self.text = ""
        self.undo_stack: List[Command] = []
        self.redo_stack: List[Command] = []

    def execute_command(self, command: Command):
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()  # Clear redo stack on new action

    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)

class InsertCommand(Command):
    def __init__(self, editor: TextEditor, text: str, position: int):
        self.editor = editor
        self.text = text
        self.position = position

    def execute(self):
        self.editor.text = (
            self.editor.text[:self.position] +
            self.text +
            self.editor.text[self.position:]
        )

    def undo(self):
        self.editor.text = (
            self.editor.text[:self.position] +
            self.editor.text[self.position + len(self.text):]
        )
```

---

### 30. Design a Notification System

**Difficulty**: Medium
**Companies**: Facebook, LinkedIn, Twitter

**Requirements**:
- Multiple notification types (email, SMS, push, in-app)
- User preferences (opt-in/opt-out)
- Priority levels
- Batching and throttling
- Retry mechanism

**Design**:
```python
class NotificationSystem:
    def __init__(self):
        self.channels: Dict[str, NotificationChannel] = {}
        self.queue: PriorityQueue = PriorityQueue()
        self.preferences: UserPreferencesStore = UserPreferencesStore()

    def send_notification(self, notification: Notification):
        # Check user preferences
        if not self.preferences.is_enabled(
            notification.user_id,
            notification.type
        ):
            return

        # Add to priority queue
        self.queue.put((notification.priority, notification))

    def process_notifications(self):
        while not self.queue.empty():
            priority, notification = self.queue.get()

            # Get appropriate channel
            channel = self.channels.get(notification.channel_type)
            if channel:
                try:
                    channel.send(notification)
                except Exception as e:
                    # Retry logic
                    self._retry(notification)
```

---

## More Essential Questions (31-60)

### 31. Design a URL Shortener (TinyURL)
### 32. Design a Web Crawler
### 33. Design a Distributed ID Generator
### 34. Design a File Storage System (Dropbox/Google Drive)
### 35. Design a Chat Application (WhatsApp/Slack)
### 36. Design a News Feed System
### 37. Design a Notification System
### 38. Design a Search Autocomplete
### 39. Design a Ride-Sharing Service (Uber/Lyft)
### 40. Design a Food Delivery System (DoorDash/UberEats)
### 41. Design a Music Streaming Service (Spotify)
### 42. Design a Video Streaming Service (Netflix)
### 43. Design a Payment System
### 44. Design a Logging Framework
### 45. Design a Task Scheduler
### 46. Design a Pub-Sub System
### 47. Design a Proximity Service (Nearby)
### 48. Design a Collaborative Editor (Google Docs)
### 49. Design an Analytics System
### 50. Design a Metrics Collection System

### 51. What's the difference between Composition and Inheritance?
**Answer**:
- **Inheritance** (is-a): Car is a Vehicle
- **Composition** (has-a): Car has an Engine

Prefer composition over inheritance for flexibility.

### 52. How to design for extensibility?
**Answer**:
- Use interfaces and abstract classes
- Dependency injection
- Plugin architecture
- Configuration over hard-coding

### 53. How to handle versioning in APIs?
**Answer**:
- URL versioning: `/api/v1/users`
- Header versioning: `API-Version: 1.0`
- Accept header: `Accept: application/vnd.company.v1+json`

### 54. Thread Safety Strategies
**Answer**:
1. Immutability
2. Synchronization (locks)
3. Thread-local storage
4. Lock-free data structures

### 55. Design Anti-Patterns to Avoid
**Answer**:
- God Object (one class does everything)
- Spaghetti Code (tangled dependencies)
- Golden Hammer (using one pattern everywhere)
- Copy-Paste Programming

---

## Company-Specific Tips

### Google
**Focus Areas**:
- Scalability and performance
- Clean code and design patterns
- Edge case handling
- Time/space complexity analysis

**Common Questions**:
- Design Google Calendar
- Design Google Maps
- Design YouTube

**Tips**:
- Discuss distributed systems aspects
- Consider caching strategies
- Think about data partitioning

---

### Amazon
**Focus Areas**:
- Customer-centric design
- Operational excellence
- Ownership and leadership principles

**Common Questions**:
- Design Amazon Shopping Cart
- Design Inventory Management
- Design Order Fulfillment System

**Tips**:
- Think about availability and reliability
- Discuss failure scenarios
- Consider cost optimization

---

### Microsoft
**Focus Areas**:
- Enterprise software design
- Windows/Office integrations
- Security considerations

**Common Questions**:
- Design Meeting Scheduler (Outlook)
- Design File Sync (OneDrive)
- Design Collaborative Editing

**Tips**:
- Consider backward compatibility
- Think about user experience
- Discuss security measures

---

### Facebook/Meta
**Focus Areas**:
- Social features
- Real-time updates
- Feed ranking algorithms

**Common Questions**:
- Design News Feed
- Design Messenger
- Design Friend Suggestions

**Tips**:
- Consider real-time requirements
- Discuss notification systems
- Think about privacy

---

### Uber
**Focus Areas**:
- Location-based services
- Real-time matching
- High availability

**Common Questions**:
- Design Ride Matching
- Design Surge Pricing
- Design ETA Calculation

**Tips**:
- Consider geospatial indexing
- Think about latency
- Discuss failure handling

---

## Interview Approach Framework

### Step 1: Clarify Requirements (5 minutes)
```
Ask questions:
✓ Who are the users?
✓ What are the core features?
✓ What's the scale (users, QPS)?
✓ Any constraints or assumptions?
✓ What's in/out of scope?
```

### Step 2: High-Level Design (10 minutes)
```
1. Identify actors/users
2. List use cases
3. Define core classes
4. Draw relationships
5. Discuss APIs
```

### Step 3: Detailed Design (20 minutes)
```
1. Define class attributes and methods
2. Apply design patterns
3. Code key methods
4. Handle edge cases
5. Discuss thread safety if needed
```

### Step 4: Validate and Extend (5 minutes)
```
1. Walk through use cases
2. Discuss trade-offs
3. Mention possible improvements
4. Talk about scalability
```

### Communication Tips
```
✓ Think out loud
✓ Draw diagrams
✓ Start simple, then extend
✓ Ask for feedback
✓ Discuss alternatives
✓ Be open to suggestions
```

### Red Flags to Avoid
```
✗ Jumping to code immediately
✗ Not asking clarifying questions
✗ Ignoring edge cases
✗ Poor variable naming
✗ Over-engineering
✗ Not explaining thought process
```

---

## Practice Strategy

### Week 1-2: Fundamentals
- Master SOLID principles
- Understand all major design patterns
- Practice 10 easy problems

### Week 3-4: Intermediate
- Practice 15 medium problems
- Focus on system design examples
- Time yourself (45 minutes per problem)

### Week 5-6: Advanced
- Practice 10 hard problems
- Mock interviews with peers
- Review and refine approach

### Week 7-8: Company-Specific
- Study company-specific questions
- Practice relevant problems
- Fine-tune communication skills

---

## Quick Reference Cheat Sheet

### When to Use Which Pattern

| Pattern | Use When |
|---------|----------|
| Singleton | Need exactly one instance |
| Factory | Complex object creation |
| Builder | Many optional parameters |
| Prototype | Cloning expensive objects |
| Adapter | Integrate incompatible interfaces |
| Decorator | Add behavior dynamically |
| Facade | Simplify complex subsystem |
| Strategy | Multiple algorithms for same task |
| Observer | One-to-many notifications |
| Command | Undo/redo, queue operations |
| State | Behavior changes with state |
| Template Method | Algorithm skeleton with variations |

### SOLID Quick Reference

| Principle | Rule | Example |
|-----------|------|---------|
| SRP | One class, one responsibility | UserManager only manages users |
| OCP | Open for extension, closed for modification | New shapes without changing calculator |
| LSP | Subclass substitutable for parent | All Birds can move (not all can fly) |
| ISP | No fat interfaces | Workable and Eatable separate |
| DIP | Depend on abstractions | UserService depends on Database interface |

---

## Additional Resources

1. **Books**:
   - "Design Patterns" by Gang of Four
   - "Head First Design Patterns"
   - "Clean Code" by Robert Martin

2. **Online Practice**:
   - LeetCode (System Design section)
   - Educative.io (Grokking courses)
   - InterviewBit

3. **YouTube Channels**:
   - Gaurav Sen
   - Tech Dummies
   - System Design Interview

---

## Conclusion

Success in LLD interviews requires:
1. **Strong fundamentals** in OOP and design patterns
2. **Practice** with diverse problems
3. **Clear communication** of thought process
4. **Systematic approach** to problem-solving
5. **Flexibility** to handle different scenarios

Remember: The interviewer is evaluating your problem-solving approach, not expecting a perfect solution. Show your thinking, discuss trade-offs, and be open to feedback.

Good luck with your interviews!
