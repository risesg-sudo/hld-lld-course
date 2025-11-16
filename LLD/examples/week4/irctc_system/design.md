# IRCTC Railway Reservation System - Design Document

## Problem Statement
Design a railway reservation system similar to IRCTC that allows users to search for trains, book tickets, manage reservations, and handle payments. The system should prevent double booking and handle concurrent requests efficiently.

---

## Requirements Analysis

### Functional Requirements
1. **Search Trains**: Users can search for trains between two stations on a given date
2. **Check Availability**: View available seats in different classes (AC, Sleeper, General)
3. **Book Tickets**: Book one or more seats for passengers
4. **Generate PNR**: Unique identifier for each booking
5. **Ticket Types**: Confirmed, RAC (Reservation Against Cancellation), Waiting List
6. **Cancel Booking**: Cancel confirmed tickets and adjust waiting list
7. **Payment Processing**: Handle different payment methods
8. **View Booking**: Check booking status using PNR
9. **Passenger Management**: Store passenger details
10. **Seat Allocation**: Automatically allocate seats based on availability

### Non-Functional Requirements
- **Concurrency**: Handle multiple simultaneous booking requests
- **Consistency**: No double booking - atomic seat allocation
- **Availability**: System should be highly available
- **Performance**: Search and booking should be fast (<2 seconds)
- **Data Integrity**: ACID properties for booking transactions
- **Scalability**: Support millions of users

### Out of Scope
- Train scheduling and route management
- Dynamic pricing
- User authentication and authorization
- Payment gateway integration
- Notifications (email/SMS) - we'll simulate this
- Refund processing

---

## Actors

| Actor | Description | Key Actions |
|-------|-------------|-------------|
| Passenger | End user booking tickets | Search trains, book tickets, cancel booking, check status |
| Admin | System administrator | Add/remove trains, manage routes, view all bookings |
| System | Automated processes | Seat allocation, waiting list management, PNR generation |

---

## Use Cases

### UC1: Search Trains
**Actor**: Passenger
**Preconditions**: Source and destination stations exist

**Main Flow**:
1. User provides source station, destination station, and travel date
2. System searches for trains between source and destination
3. System displays list of available trains with seat availability
4. User selects a train

**Postconditions**: User sees available trains and can proceed to booking

---

### UC2: Book Ticket
**Actor**: Passenger
**Preconditions**: User has selected a train and seat class

**Main Flow**:
1. User provides passenger details (name, age, gender)
2. User selects seat class (AC, Sleeper, General)
3. User requests N seats
4. System checks seat availability
5. System allocates seats
6. System generates PNR
7. User proceeds to payment
8. System confirms booking upon successful payment

**Alternative Flows**:
- **Alt 1**: No seats available → Add to waiting list
- **Alt 2**: Limited seats (< N) → Offer available seats + RAC/Waiting
- **Alt 3**: Payment fails → Cancel booking, release seats

**Exception Flows**:
- **Ex 1**: Invalid passenger data → Return error, prompt for correction
- **Ex 2**: Train not found → Return error
- **Ex 3**: Booking timeout → Release held seats

**Postconditions**: Booking confirmed with PNR, seats allocated, payment processed

---

### UC3: Cancel Booking
**Actor**: Passenger
**Preconditions**: Valid PNR exists

**Main Flow**:
1. User provides PNR
2. System validates PNR
3. System checks booking status (only confirmed/RAC can be cancelled)
4. System releases seats
5. System promotes waiting list passengers
6. System initiates refund
7. System updates booking status to CANCELLED

**Alternative Flows**:
- **Alt 1**: Waiting list ticket → Cancel without refund

**Postconditions**: Seats released, waiting list updated, refund initiated

---

### UC4: Check Booking Status
**Actor**: Passenger
**Preconditions**: Valid PNR

**Main Flow**:
1. User provides PNR
2. System retrieves booking details
3. System displays ticket status, passenger details, and seat numbers

**Postconditions**: User sees current booking status

---

## Class Design

### Class Diagram (ASCII)
```
┌─────────────────────┐         ┌──────────────────┐
│   Station           │         │   Train          │
├─────────────────────┤         ├──────────────────┤
│ - code: str         │         │ - train_no: str  │
│ - name: str         │         │ - name: str      │
│ - city: str         │◇────────│ - source: Station│
└─────────────────────┘         │ - dest: Station  │
                                │ - seats: Dict    │
                                └────────┬─────────┘
                                         │ has
                                         │
                                    ┌────▼─────────────┐
                                    │   Seat           │
                                    ├──────────────────┤
                                    │ - seat_no: str   │
                                    │ - type: SeatType │
                                    │ - status: Status │
                                    │ - price: float   │
                                    └──────────────────┘

┌──────────────────┐         ┌──────────────────────┐
│   Passenger      │         │   Booking            │
├──────────────────┤         ├──────────────────────┤
│ - name: str      │         │ - pnr: str           │
│ - age: int       │         │ - train: Train       │
│ - gender: str    │◇────────│ - passengers: List   │
│ - id: str        │         │ - seats: List        │
└──────────────────┘         │ - status: Status     │
                             │ - booking_date: Date │
                             │ - travel_date: Date  │
                             └──────────┬───────────┘
                                        │
                                        │ creates
                                        │
                                  ┌─────▼─────────────┐
                                  │   Ticket          │
                                  ├───────────────────┤
                                  │ - ticket_id: str  │
                                  │ - pnr: str        │
                                  │ - passenger: Pass │
                                  │ - seat: Seat      │
                                  │ - status: Status  │
                                  └───────────────────┘

┌──────────────────────────┐
│ BookingManager           │ ← Singleton
├──────────────────────────┤
│ - instance: Self         │
│ - bookings: Dict         │
│ - lock: Lock             │
├──────────────────────────┤
│ + get_instance()         │
│ + create_booking()       │
│ + cancel_booking()       │
│ + get_booking()          │
└────────┬─────────────────┘
         │ uses
         │
    ┌────▼──────────────┐         ┌─────────────────┐
    │ TicketFactory     │         │ SearchService   │
    ├───────────────────┤         ├─────────────────┤
    │ + create_ticket() │         │ + search_trains()│
    └───────────────────┘         └─────────────────┘

┌───────────────────────┐
│ PaymentProcessor      │ ← Interface
├───────────────────────┤
│ + process_payment()   │
└──────────┬────────────┘
           △
           │ implements
     ┌─────┴─────────────┐
     │                   │
┌────┴─────────┐  ┌──────┴────────┐
│ CreditCard   │  │ DebitCard     │
│ Payment      │  │ Payment       │
└──────────────┘  └───────────────┘

┌──────────────────────┐
│ NotificationService  │ ← Observer Pattern
├──────────────────────┤
│ + notify()           │
│ + subscribe()        │
└──────────────────────┘
```

### Core Classes

#### 1. Station
```python
class Station:
    - code: str          # Station code (e.g., "NDLS")
    - name: str          # Station name (e.g., "New Delhi")
    - city: str          # City name

    + __init__(code, name, city)
    + __str__()
```

#### 2. Train
```python
class Train:
    - train_no: str               # Train number
    - name: str                   # Train name
    - source: Station             # Starting station
    - destination: Station        # End station
    - seats: Dict[SeatType, List[Seat]]  # Seats by class

    + __init__(train_no, name, source, destination)
    + add_seat(seat: Seat)
    + get_available_seats(seat_type: SeatType) -> List[Seat]
    + has_availability(seat_type: SeatType, count: int) -> bool
```

#### 3. Seat
```python
class Seat:
    - seat_number: str
    - seat_type: SeatType      # AC, Sleeper, General
    - price: float
    - is_booked: bool

    + __init__(seat_number, seat_type, price)
    + book()
    + release()
    + get_price() -> float
```

#### 4. Passenger
```python
class Passenger:
    - passenger_id: str
    - name: str
    - age: int
    - gender: str

    + __init__(name, age, gender)
    + validate() -> bool
```

#### 5. Ticket
```python
class Ticket:
    - ticket_id: str
    - pnr: str
    - passenger: Passenger
    - seat: Seat
    - status: TicketStatus    # CONFIRMED, RAC, WAITING, CANCELLED

    + __init__(pnr, passenger, seat, status)
    + confirm()
    + cancel()
    + get_status() -> TicketStatus
```

#### 6. Booking
```python
class Booking:
    - pnr: str                # Unique booking identifier
    - train: Train
    - passengers: List[Passenger]
    - tickets: List[Ticket]
    - booking_date: datetime
    - travel_date: date
    - total_amount: float
    - status: BookingStatus   # CONFIRMED, CANCELLED, PENDING

    + __init__(train, passengers, travel_date)
    + add_ticket(ticket: Ticket)
    + calculate_total() -> float
    + confirm_booking()
    + cancel_booking()
```

#### 7. BookingManager (Singleton)
```python
class BookingManager:
    - _instance: BookingManager     # Singleton instance
    - bookings: Dict[str, Booking]  # PNR -> Booking
    - lock: Lock                    # Thread safety

    + get_instance() -> BookingManager     # Static
    + create_booking(train, passengers, travel_date, seat_type) -> Booking
    + cancel_booking(pnr: str) -> bool
    + get_booking(pnr: str) -> Booking
    - generate_pnr() -> str                # Private
    - allocate_seats(train, seat_type, count) -> List[Seat]
```

#### 8. TicketFactory
```python
class TicketFactory:
    + create_ticket(pnr, passenger, seat, status) -> Ticket     # Static

    # Can create different ticket types
    + create_confirmed_ticket(...) -> Ticket
    + create_rac_ticket(...) -> Ticket
    + create_waiting_ticket(...) -> Ticket
```

#### 9. SearchService
```python
class SearchService:
    - trains: List[Train]

    + search_trains(source: Station, destination: Station, date: date) -> List[Train]
    + get_train_by_number(train_no: str) -> Train
    + add_train(train: Train)
```

#### 10. PaymentProcessor (Interface)
```python
class PaymentProcessor(ABC):
    + process_payment(amount: float, details: dict) -> bool    # Abstract
```

#### 11. CreditCardPayment, DebitCardPayment
```python
class CreditCardPayment(PaymentProcessor):
    + process_payment(amount, details) -> bool

class DebitCardPayment(PaymentProcessor):
    + process_payment(amount, details) -> bool
```

#### 12. NotificationService (Observer)
```python
class NotificationService:
    - observers: List[Observer]

    + subscribe(observer: Observer)
    + unsubscribe(observer: Observer)
    + notify_booking_confirmed(booking: Booking)
    + notify_booking_cancelled(booking: Booking)
```

### Enumerations

```python
class SeatType(Enum):
    AC_1 = "1A"
    AC_2 = "2A"
    AC_3 = "3A"
    SLEEPER = "SL"
    GENERAL = "GEN"

class TicketStatus(Enum):
    CONFIRMED = "CNF"
    RAC = "RAC"
    WAITING = "WL"
    CANCELLED = "CAN"

class BookingStatus(Enum):
    CONFIRMED = "CONFIRMED"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
```

---

## Design Patterns Applied

### 1. Singleton Pattern
**Where**: `BookingManager`

**Why**:
- Need single point of control for all bookings
- Ensures consistent state across system
- Manages thread-safe booking operations

**Implementation**:
```python
class BookingManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. Factory Pattern
**Where**: `TicketFactory`

**Why**:
- Different ticket types (Confirmed, RAC, Waiting) have different creation logic
- Centralizes ticket creation
- Easy to add new ticket types

**Implementation**:
```python
class TicketFactory:
    @staticmethod
    def create_ticket(ticket_type, pnr, passenger, seat=None):
        if ticket_type == TicketStatus.CONFIRMED:
            return ConfirmedTicket(pnr, passenger, seat)
        elif ticket_type == TicketStatus.RAC:
            return RACTicket(pnr, passenger, seat)
        elif ticket_type == TicketStatus.WAITING:
            return WaitingTicket(pnr, passenger)
```

### 3. Strategy Pattern
**Where**: `PaymentProcessor` hierarchy

**Why**:
- Multiple payment methods (Credit Card, Debit Card, UPI, etc.)
- Payment algorithm can change at runtime
- Easy to add new payment methods

**Implementation**:
```python
class BookingService:
    def __init__(self, payment_strategy: PaymentProcessor):
        self.payment_strategy = payment_strategy

    def process_payment(self, amount):
        return self.payment_strategy.process_payment(amount)
```

### 4. Observer Pattern
**Where**: `NotificationService`

**Why**:
- Notify users when booking status changes
- Decouple notification logic from booking logic
- Support multiple notification channels (Email, SMS, Push)

**Implementation**:
```python
class NotificationService:
    def __init__(self):
        self.observers = []

    def notify_all(self, event, data):
        for observer in self.observers:
            observer.update(event, data)
```

---

## SOLID Principles Demonstrated

### Single Responsibility Principle (SRP)
- `Seat`: Only manages seat state (booked/available)
- `Booking`: Only manages booking lifecycle
- `PaymentProcessor`: Only handles payment
- `SearchService`: Only handles train search
- Each class has one reason to change

### Open/Closed Principle (OCP)
- New seat types can be added without modifying `Seat` class
- New payment methods extend `PaymentProcessor` without modification
- New ticket types can be added via factory

### Liskov Substitution Principle (LSP)
- Any `PaymentProcessor` implementation can be used interchangeably
- Different ticket types (Confirmed, RAC, Waiting) are substitutable

### Interface Segregation Principle (ISP)
- `PaymentProcessor` has focused interface (just `process_payment`)
- Clients depend only on methods they use
- No fat interfaces

### Dependency Inversion Principle (DIP)
- `BookingManager` depends on `PaymentProcessor` interface, not concrete implementations
- High-level booking logic doesn't depend on low-level payment details
- Depend on abstractions, not concretions

---

## Concurrency Handling

### Problem: Race Conditions
Two users trying to book the last seat simultaneously.

### Solution: Locking
```python
class BookingManager:
    def create_booking(self, ...):
        with self.lock:  # Acquire lock
            # Check availability
            if train.has_availability(seat_type, num_passengers):
                # Allocate seats
                seats = self.allocate_seats(...)
                # Create booking
                booking = Booking(...)
            # Release lock automatically
        return booking
```

### Granular Locking
Instead of locking entire booking manager, lock specific train:
```python
class Train:
    def __init__(self, ...):
        self.lock = Lock()

    def book_seats(self, seat_type, count):
        with self.lock:
            # Check and allocate seats for this train only
```

---

## Edge Cases Handled

1. **No seats available**: Add to waiting list
2. **Partial availability**: Offer available seats + RAC/waiting for rest
3. **Payment failure**: Rollback booking, release seats
4. **Invalid PNR**: Return error
5. **Cancellation of already cancelled booking**: Return error
6. **Concurrent booking**: Thread-safe seat allocation
7. **Invalid passenger data**: Validation before booking
8. **Booking timeout**: Release held seats after timeout
9. **Train not found**: Return error
10. **Past date booking**: Validation to prevent

---

## Sample Usage Flow

```
1. User searches for trains: Delhi → Mumbai on 2025-11-20
   └─> SearchService.search_trains(delhi, mumbai, date)
   └─> Returns list of available trains

2. User selects train and seat class
   └─> Check availability: train.has_availability(AC_3, 2)

3. User provides passenger details
   └─> Create Passenger objects
   └─> Validate passenger data

4. System creates booking
   └─> BookingManager.create_booking(train, passengers, date, AC_3)
   └─> Generate PNR
   └─> Allocate seats (with lock)
   └─> Create tickets via TicketFactory
   └─> Calculate total amount

5. User makes payment
   └─> PaymentProcessor.process_payment(amount, details)
   └─> If successful: Confirm booking
   └─> If failed: Cancel booking, release seats

6. System confirms booking
   └─> Update booking status to CONFIRMED
   └─> NotificationService.notify_booking_confirmed(booking)
   └─> Return PNR to user

7. User can check status
   └─> BookingManager.get_booking(pnr)
   └─> Display ticket details
```

---

## Testing Considerations

### Unit Tests
1. Test seat booking and release
2. Test PNR generation uniqueness
3. Test ticket creation via factory
4. Test payment processing
5. Test booking cancellation and refund

### Integration Tests
1. Test complete booking flow
2. Test concurrent booking scenarios
3. Test waiting list promotion
4. Test search functionality

### Concurrency Tests
1. Test race condition handling
2. Test deadlock prevention
3. Test data consistency under load

---

## Potential Enhancements

1. **Dynamic Pricing**: Adjust prices based on demand
2. **Route Management**: Handle trains with multiple stops
3. **Seat Preferences**: Allow users to select specific seats
4. **Partial Cancellation**: Cancel some tickets, not entire booking
5. **Tatkal Booking**: Special quota with different rules
6. **Chart Preparation**: Final seat allocation before departure
7. **Refund Rules**: Complex refund calculation based on cancellation time
8. **Waiting List Auto-upgrade**: Automatic promotion to confirmed
9. **User Profiles**: Save passenger details for quick booking
10. **Seat Map**: Visual representation of seat availability

---

## Complexity Analysis

### Time Complexity
- **Search trains**: O(n) where n = number of trains
- **Book ticket**: O(1) with proper indexing, O(m) for m seats
- **Check availability**: O(k) where k = seats in class
- **Cancel booking**: O(1) to find booking, O(m) to release seats

### Space Complexity
- **Overall**: O(T × S + B) where:
  - T = number of trains
  - S = seats per train
  - B = number of bookings

---

## Conclusion

This IRCTC system design demonstrates:
- Systematic requirement analysis
- Clean class design with clear responsibilities
- Appropriate use of design patterns
- SOLID principles in action
- Handling of concurrency and edge cases
- Extensibility for future enhancements

The implementation is production-ready for the core functionality and can be extended with additional features as needed.
