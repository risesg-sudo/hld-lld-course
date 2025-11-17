# IRCTC System - Architecture

## High-Level Architecture

The IRCTC system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│              (User Interface / API)                     │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │SearchService │  │BookingManager│  │NotificationSvc│  │
│  │              │  │  (Singleton) │  │  (Observer)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Business Logic Layer                       │
│  ┌─────────┐  ┌─────────┐  ┌────────────────┐          │
│  │  Train  │  │ Booking │  │ PaymentProcessor│          │
│  │         │  │         │  │   (Strategy)    │          │
│  └─────────┘  └─────────┘  └────────────────┘          │
│  ┌─────────┐  ┌─────────┐  ┌────────────────┐          │
│  │  Seat   │  │ Ticket  │  │  TicketFactory │          │
│  │         │  │         │  │    (Factory)   │          │
│  └─────────┘  └─────────┘  └────────────────┘          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Data Layer                            │
│          (In-memory storage / Database)                 │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Domain Entities (components/train.py)

#### Station
**Responsibility**: Represents a railway station

**Key Attributes**:
- `code`: Unique station code (e.g., "NDLS")
- `name`: Station name (e.g., "New Delhi")
- `city`: City name

**Why It Exists**: Stations are fundamental entities in the railway system. Keeping them as separate objects allows for future extensions (adding coordinates, facilities, etc.)

#### Seat
**Responsibility**: Manages the state of a single seat

**Key Attributes**:
- `seat_number`: Unique identifier within a train
- `seat_type`: Enum (AC_1, AC_2, AC_3, SLEEPER, GENERAL)
- `is_booked`: Current booking status
- `price`: Base price for this seat type

**Key Operations**:
- `book()`: Mark seat as booked (with validation)
- `release()`: Free up the seat
- `get_price()`: Return seat price

**Design Note**: Single Responsibility Principle - Seat only manages its own state. It doesn't know about bookings or trains.

#### Train
**Responsibility**: Manages a train's seats and route

**Key Attributes**:
- `train_no`: Unique train number
- `name`: Train name
- `source` / `destination`: Station objects
- `seats`: Dictionary mapping SeatType to list of Seats
- `lock`: Thread lock for concurrent access

**Key Operations**:
- `add_seat()` / `add_seats_bulk()`: Add seats to train
- `get_available_seats()`: Get list of unbooked seats for a type
- `book_seats()`: Thread-safe seat booking
- `release_seats()`: Release seats back to pool
- `has_availability()`: Check if N seats available

**Why Thread Lock?**: Multiple users can book the same train simultaneously. The lock ensures that seat allocation is atomic - no two threads can book the same seat.

**Design Pattern**: Composition - Train "has" Seats rather than inheriting from some SeatContainer class.

### 2. Booking Components (components/booking.py)

#### Passenger
**Responsibility**: Represents a passenger with validation

**Key Attributes**:
- `passenger_id`: Auto-generated unique ID
- `name`, `age`, `gender`: Passenger details

**Key Operations**:
- `validate()`: Ensure passenger data is valid

**Why Separate Class?**: Even though passenger data is simple, having a separate class allows for future extensions (loyalty programs, preferences, etc.) and keeps validation logic in one place.

#### Ticket
**Responsibility**: Represents a ticket for one passenger

**Key Attributes**:
- `ticket_id`: Unique ticket ID
- `pnr`: Associated booking PNR
- `passenger`: Passenger object
- `seat`: Allocated seat (None for waiting list)
- `status`: TicketStatus enum (CONFIRMED, RAC, WAITING, CANCELLED)

**Key Operations**:
- `confirm()`: Change status to confirmed
- `cancel()`: Mark as cancelled

**Design Note**: Liskov Substitution Principle - All ticket types share the same interface, so they're interchangeable.

#### Booking
**Responsibility**: Manages a complete booking with multiple tickets

**Key Attributes**:
- `pnr`: Unique booking identifier
- `train`: Associated train
- `passengers`: List of passengers
- `tickets`: List of tickets (one per passenger)
- `booking_date` / `travel_date`: Dates
- `total_amount`: Total cost
- `status`: BookingStatus enum

**Key Operations**:
- `add_ticket()`: Add ticket and update total amount
- `confirm_booking()`: Confirm all tickets
- `cancel_booking()`: Cancel all tickets
- `get_booking_summary()`: Formatted booking details

**Design Note**: Aggregation - Booking "has" Tickets. If booking is deleted, tickets should also be removed.

#### TicketFactory (Factory Pattern)
**Responsibility**: Centralized ticket creation

**Key Operations**:
- `create_confirmed_ticket()`: Create ticket with confirmed status
- `create_rac_ticket()`: Create RAC ticket
- `create_waiting_ticket()`: Create waiting list ticket
- `create_ticket()`: Generic creation method

**Why Factory?**:
- Encapsulates ticket creation logic
- Makes it easy to add new ticket types (Open/Closed Principle)
- Hides complexity of different ticket configurations

#### BookingManager (Singleton Pattern)
**Responsibility**: Central controller for all booking operations

**Key Attributes**:
- `bookings`: Dictionary of all bookings (PNR → Booking)
- `notification_service`: Observer for notifications
- `lock`: Thread lock for booking operations

**Key Operations**:
- `create_booking()`: Complete booking flow with payment
- `cancel_booking()`: Cancel existing booking
- `get_booking()`: Retrieve booking by PNR

**Why Singleton?**:
- Single point of control for booking operations
- Manages shared state (booking dictionary)
- Coordinates locking for thread safety
- Ensures consistent PNR generation

**Thread Safety**:
```python
with self.lock:
    # Atomic operations:
    # 1. Check availability
    # 2. Allocate seats
    # 3. Process payment
    # 4. Store booking
```

#### SearchService
**Responsibility**: Train search and discovery

**Key Operations**:
- `add_train()`: Register a train
- `search_trains()`: Find trains by route and date
- `display_train_availability()`: Show seat availability

**Design Note**: Single Responsibility - Only handles search, doesn't modify bookings.

### 3. Payment Components (components/payment.py)

#### PaymentProcessor (Strategy Pattern)
**Responsibility**: Abstract interface for payment processing

**Key Operation**:
- `process_payment(amount, details)`: Process payment and return success/failure

**Why Abstract?**: Dependency Inversion Principle - BookingManager depends on PaymentProcessor interface, not concrete implementations.

#### Concrete Payment Strategies
- **CreditCardPayment**: Processes credit card payments
- **DebitCardPayment**: Processes debit card payments
- **UPIPayment**: Processes UPI payments

**Why Strategy Pattern?**:
- Each payment method has completely different processing logic
- New payment methods can be added without changing BookingManager
- Runtime selection of payment method
- Each strategy is independently testable

#### NotificationService (Observer Pattern)
**Responsibility**: Manages notification observers and event distribution

**Key Operations**:
- `subscribe()` / `unsubscribe()`: Manage observers
- `notify_all()`: Broadcast to all observers
- `notify_booking_confirmed()`: Booking confirmation event
- `notify_booking_cancelled()`: Cancellation event

**Observers**:
- **EmailNotificationObserver**: Sends email notifications
- **SMSNotificationObserver**: Sends SMS notifications

**Why Observer Pattern?**:
- Booking logic doesn't need to know about notification details
- Easy to add new notification channels (Push, WhatsApp)
- Notifications can happen asynchronously
- Loose coupling between booking and notification systems

## Component Interactions

### Booking Flow Sequence

```
User → BookingManager.create_booking()
                │
                ├─→ Validate passengers
                │
                ├─→ Train.book_seats() [with lock]
                │       │
                │       ├─→ Check availability
                │       ├─→ Seat.book() for each seat
                │       └─→ Return booked seats
                │
                ├─→ TicketFactory.create_ticket() for each passenger
                │       │
                │       └─→ Create Ticket objects
                │
                ├─→ Booking.add_ticket() for each ticket
                │
                ├─→ PaymentProcessor.process_payment()
                │       │
                │       ├─→ [If Success] Continue
                │       └─→ [If Failure] Rollback seats and throw exception
                │
                ├─→ Booking.confirm_booking()
                │
                ├─→ NotificationService.notify_booking_confirmed()
                │       │
                │       ├─→ EmailObserver.update()
                │       └─→ SMSObserver.update()
                │
                └─→ Return Booking
```

## Design Patterns Summary

| Pattern | Component | Purpose |
|---------|-----------|---------|
| **Singleton** | BookingManager | Single point of booking control, thread safety |
| **Factory** | TicketFactory | Encapsulate ticket creation, easy to extend |
| **Strategy** | PaymentProcessor | Interchangeable payment methods |
| **Observer** | NotificationService | Decouple booking from notifications |

## SOLID Principles in Action

### Single Responsibility Principle (SRP)
- `Seat`: Only manages seat state
- `SearchService`: Only handles search
- `BookingManager`: Only handles booking orchestration
- `NotificationService`: Only handles notifications

### Open/Closed Principle (OCP)
- **Open for extension**: Can add new seat types, payment methods, notification channels
- **Closed for modification**: Adding new features doesn't require changing existing classes

Example: Adding a new payment method requires creating a new class implementing PaymentProcessor, not modifying BookingManager.

### Liskov Substitution Principle (LSP)
- All `PaymentProcessor` implementations are interchangeable
- All `Ticket` types can substitute for base Ticket class
- All `Observer` implementations can substitute for base Observer

### Interface Segregation Principle (ISP)
- `PaymentProcessor`: Focused interface with single method
- `Observer`: Simple interface for event handling
- Clients depend only on methods they use

### Dependency Inversion Principle (DIP)
- `BookingManager` depends on `PaymentProcessor` abstraction, not concrete classes
- `NotificationService` depends on `Observer` abstraction
- High-level booking logic doesn't depend on low-level payment/notification details

## Concurrency Considerations

### Race Condition Prevention

**Problem**: Two users book the last seat simultaneously

**Solution**: Thread lock at Train level
```python
with self.lock:  # Atomic operations
    if seat.is_available():
        seat.book()
```

### Booking Transaction

The booking operation is NOT database-transactional in this implementation, but follows a transaction-like pattern:

1. **Check**: Verify availability
2. **Modify**: Allocate seats
3. **Verify**: Process payment
4. **Commit**: Confirm booking
5. **Notify**: Send notifications

If payment fails at step 3, seats are released (rollback).

## Scalability Considerations

### Current Limitations
- In-memory storage (doesn't persist across restarts)
- Single-server locks (won't work in distributed system)
- No database transactions

### How to Scale
1. **Database**: Replace in-memory dicts with database
2. **Distributed Locks**: Use Redis or database-level locks for distributed deployment
3. **Message Queue**: Use async queue for notifications
4. **Caching**: Cache search results and seat availability
5. **Sharding**: Partition trains by route or date

## Error Handling Strategy

### Exceptions
- `BookingException`: Base exception for all booking errors
- `SeatNotAvailableException`: Seats not available
- `InvalidPNRException`: PNR not found
- `PaymentFailedException`: Payment processing failed

### Error Recovery
- **Payment Failure**: Release allocated seats immediately
- **Partial Availability**: Allocate what's available, put rest on waiting list
- **Invalid Input**: Validate early, fail fast

## Testing Strategy

### Unit Tests
- Test each component independently
- Mock dependencies (PaymentProcessor, NotificationService)
- Test edge cases (no seats, payment failure)

### Integration Tests
- Test complete booking flow
- Test concurrent bookings
- Test rollback scenarios

### Concurrency Tests
- Simulate multiple threads booking same seats
- Verify no double booking occurs
- Test lock timeout scenarios
