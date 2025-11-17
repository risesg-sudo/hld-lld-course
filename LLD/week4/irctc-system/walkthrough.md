# IRCTC System - Complete Walkthrough

## Overview

This document provides a step-by-step execution trace of a complete booking flow, showing exactly what happens at each step, including memory state changes, method calls, and design pattern applications.

## Scenario: Booking Train Tickets

**Context**: Alice wants to book 2 train tickets from Delhi to Mumbai for tomorrow's Rajdhani Express.

## Initial Setup

### Step 1: System Initialization

```python
# Create stations
delhi = Station("NDLS", "New Delhi", "Delhi")
mumbai = Station("CSTM", "Mumbai Central", "Mumbai")
```

**Memory State**:
```
delhi = Station(code="NDLS", name="New Delhi", city="Delhi")
mumbai = Station(code="CSTM", name="Mumbai Central", city="Mumbai")
```

### Step 2: Create and Configure Train

```python
rajdhani = Train("12301", "Rajdhani Express", delhi, mumbai)
rajdhani.add_seats_bulk(SeatType.AC_3, 50)
```

**Execution Trace**:
```
1. Train.__init__() called
   - train_no = "12301"
   - name = "Rajdhani Express"
   - source = delhi
   - destination = mumbai
   - seats = {
       AC_1: [],
       AC_2: [],
       AC_3: [],
       SLEEPER: [],
       GENERAL: []
     }
   - lock = Lock()

2. add_seats_bulk(SeatType.AC_3, 50) called
   - Loop 50 times:
       - seat_number = "3A-1", "3A-2", ..., "3A-50"
       - create Seat(seat_number, SeatType.AC_3)
       - append to seats[AC_3]
```

**Memory State After**:
```
rajdhani.seats[AC_3] = [
    Seat(number="3A-1", type=AC_3, is_booked=False, price=750),
    Seat(number="3A-2", type=AC_3, is_booked=False, price=750),
    ...
    Seat(number="3A-50", type=AC_3, is_booked=False, price=750)
]
```

### Step 3: Initialize Services

```python
# Search Service
search_service = SearchService()
search_service.add_train(rajdhani)

# Booking Manager (Singleton)
booking_manager = BookingManager.get_instance()

# Setup Observers
email_observer = EmailNotificationObserver()
sms_observer = SMSNotificationObserver()
booking_manager.notification_service.subscribe(email_observer)
booking_manager.notification_service.subscribe(sms_observer)
```

**Execution Trace**:
```
1. SearchService.__init__()
   - trains = {}

2. add_train(rajdhani)
   - trains["12301"] = rajdhani

3. BookingManager.get_instance()
   Thread-safe singleton creation:
   - Check: BookingManager._instance is None? Yes
   - Acquire: BookingManager._lock
   - Check again: _instance is None? Yes (double-check)
   - Create: _instance = new BookingManager()
   - Release lock
   - Return _instance

4. BookingManager.__init__()
   - bookings = {}
   - lock = Lock()
   - notification_service = NotificationService()
   - _initialized = True

5. NotificationService subscribe operations:
   - observers = []
   - subscribe(email_observer) → observers.append(email_observer)
   - subscribe(sms_observer) → observers.append(sms_observer)
```

**Memory State**:
```
booking_manager = BookingManager {
    bookings: {},
    lock: Lock(),
    notification_service: NotificationService {
        observers: [
            EmailNotificationObserver(),
            SMSNotificationObserver()
        ]
    }
}
```

## The Booking Flow

### Step 4: Search for Trains

```python
available_trains = search_service.search_trains(delhi, mumbai, date.today())
```

**Execution Trace**:
```
1. search_trains(delhi, mumbai, date.today())
2. matching_trains = []
3. For each train in trains.values():
     - Check: train.source.code == delhi.code?
       "CSTM" == "NDLS"? Yes
     - Check: train.destination.code == mumbai.code?
       "CSTM" == "CSTM"? Yes
     - Add rajdhani to matching_trains
4. Return matching_trains
```

**Result**: `[rajdhani]`

### Step 5: Create Passengers

```python
passenger1 = Passenger("Alice Smith", 30, "F")
passenger2 = Passenger("Bob Smith", 32, "M")
passengers = [passenger1, passenger2]
```

**Execution Trace**:
```
1. Passenger.__init__("Alice Smith", 30, "F")
   - passenger_id = "P000001" (from counter)
   - Increment counter: _id_counter = 2
   - name = "Alice Smith"
   - age = 30
   - gender = "F"

2. Passenger.__init__("Bob Smith", 32, "M")
   - passenger_id = "P000002"
   - Increment counter: _id_counter = 3
   - name = "Bob Smith"
   - age = 32
   - gender = "M"
```

**Memory State**:
```
passengers = [
    Passenger(id="P000001", name="Alice Smith", age=30, gender="F"),
    Passenger(id="P000002", name="Bob Smith", age=32, gender="M")
]
```

### Step 6: Initiate Booking

```python
payment_processor = CreditCardPayment()
payment_details = {'card_number': 'XXXX-XXXX-XXXX-1234'}
contact_info = {'email': 'alice@example.com', 'phone': '+91-9876543210'}

booking = booking_manager.create_booking(
    train=rajdhani,
    passengers=passengers,
    travel_date=date.today(),
    seat_type=SeatType.AC_3,
    payment_processor=payment_processor,
    payment_details=payment_details,
    contact_info=contact_info
)
```

Now let's trace through this complex operation step by step:

#### Step 6.1: Passenger Validation

**Code**:
```python
for passenger in passengers:
    if not passenger.validate():
        raise BookingException(...)
```

**Execution Trace**:
```
1. passenger1.validate()
   - Check: name not empty? "Alice Smith" → True
   - Check: 0 <= age <= 120? 0 <= 30 <= 120 → True
   - Check: gender in ['M','F','O']? 'F' → True
   - Return: True

2. passenger2.validate()
   - Check: name not empty? "Bob Smith" → True
   - Check: 0 <= age <= 120? 0 <= 32 <= 120 → True
   - Check: gender in ['M','F','O']? 'M' → True
   - Return: True

All passengers valid, continue...
```

#### Step 6.2: Date Validation

**Code**:
```python
if travel_date < date.today():
    raise BookingException("Cannot book for past dates")
```

**Execution Trace**:
```
1. Compare: travel_date < date.today()?
   - travel_date = 2025-11-17
   - today = 2025-11-17
   - Result: False

Validation passed, continue...
```

#### Step 6.3: Acquire Lock (Thread Safety)

**Code**:
```python
with self.lock:
    # All booking operations happen here
```

**Execution Trace**:
```
1. Attempt to acquire lock
2. Lock acquired (no other thread holds it)
3. Enter critical section
```

**Why Lock?**: If another thread tries to book at the same time, it will wait here until we complete our booking and release the lock.

#### Step 6.4: Generate PNR

**Code**:
```python
pnr = self._generate_pnr()
```

**Execution Trace**:
```
1. Generate 10 random uppercase letters and digits
2. Example result: "A7K2M9X4B1"
```

**Memory**: `pnr = "A7K2M9X4B1"`

#### Step 6.5: Create Booking Object

**Code**:
```python
booking = Booking(pnr, train, passengers, travel_date)
```

**Execution Trace**:
```
1. Booking.__init__()
   - pnr = "A7K2M9X4B1"
   - train = rajdhani
   - passengers = [passenger1, passenger2]
   - tickets = []
   - booking_date = datetime.now() → 2025-11-17 14:30:00
   - travel_date = 2025-11-17
   - total_amount = 0.0
   - status = PENDING
```

**Memory State**:
```
booking = Booking {
    pnr: "A7K2M9X4B1",
    train: rajdhani,
    passengers: [passenger1, passenger2],
    tickets: [],
    booking_date: 2025-11-17 14:30:00,
    travel_date: 2025-11-17,
    total_amount: 0.0,
    status: PENDING
}
```

#### Step 6.6: Allocate Seats

**Code**:
```python
seats = train.book_seats(seat_type, len(passengers))
```

**Execution Trace**:
```
1. rajdhani.book_seats(SeatType.AC_3, 2)

2. Inside Train.book_seats():
   a. Acquire train.lock

   b. Call get_available_seats(AC_3)
      - Iterate through seats[AC_3]
      - Filter: seat.is_booked == False
      - available_seats = [all 50 seats]

   c. Check: len(available_seats) >= count?
      - len([50 seats]) >= 2?
      - 50 >= 2? True

   d. Select seats to book:
      - booked_seats = available_seats[:2]
      - booked_seats = [
          Seat("3A-1", AC_3, is_booked=False),
          Seat("3A-2", AC_3, is_booked=False)
        ]

   e. Book each seat:
      For seat "3A-1":
        - Check: seat.is_booked? False
        - Set: seat.is_booked = True

      For seat "3A-2":
        - Check: seat.is_booked? False
        - Set: seat.is_booked = True

   f. Release train.lock

   g. Return booked_seats
```

**Memory State After**:
```
seats = [
    Seat("3A-1", AC_3, is_booked=True, price=750),
    Seat("3A-2", AC_3, is_booked=True, price=750)
]

rajdhani.seats[AC_3][0].is_booked = True
rajdhani.seats[AC_3][1].is_booked = True
rajdhani.seats[AC_3][2].is_booked = False  # still available
...
```

#### Step 6.7: Create Tickets (Factory Pattern)

**Code**:
```python
for passenger, seat in zip(passengers, seats):
    ticket = TicketFactory.create_confirmed_ticket(pnr, passenger, seat)
    booking.add_ticket(ticket)
```

**Execution Trace**:
```
Iteration 1:
1. TicketFactory.create_confirmed_ticket("A7K2M9X4B1", passenger1, seat1)
   - Create Ticket object:
     - ticket_id = random → "T123456"
     - pnr = "A7K2M9X4B1"
     - passenger = passenger1
     - seat = seat1 (3A-1)
     - status = CONFIRMED

2. booking.add_ticket(ticket)
   - tickets.append(ticket)
   - total_amount += seat.get_price()
   - total_amount += 750
   - total_amount = 750

Iteration 2:
3. TicketFactory.create_confirmed_ticket("A7K2M9X4B1", passenger2, seat2)
   - ticket_id = "T789012"
   - (same PNR, passenger2, seat2, CONFIRMED)

4. booking.add_ticket(ticket)
   - tickets.append(ticket)
   - total_amount += 750
   - total_amount = 1500
```

**Memory State**:
```
booking.tickets = [
    Ticket(id="T123456", pnr="A7K2M9X4B1", passenger=passenger1,
           seat=Seat("3A-1"), status=CONFIRMED),
    Ticket(id="T789012", pnr="A7K2M9X4B1", passenger=passenger2,
           seat=Seat("3A-2"), status=CONFIRMED)
]
booking.total_amount = 1500
```

#### Step 6.8: Process Payment (Strategy Pattern)

**Code**:
```python
total_amount = booking.calculate_total()
payment_success = payment_processor.process_payment(total_amount, payment_details)
```

**Execution Trace**:
```
1. booking.calculate_total()
   - Return: 1500

2. payment_processor.process_payment(1500, payment_details)

   Strategy Pattern in Action:
   - payment_processor is CreditCardPayment instance
   - Calls CreditCardPayment.process_payment()

   Inside CreditCardPayment.process_payment():
   a. Print: "Processing Credit Card payment of Rs. 1500"
   b. Extract: card_number = payment_details.get('card_number')
      - card_number = "XXXX-XXXX-XXXX-1234"
   c. Print: "Card: XXXX-XXXX-XXXX-1234"
   d. Simulate payment: amount > 0? 1500 > 0? True
   e. Print: "Payment successful!"
   f. Return: True

3. payment_success = True
```

**What if payment failed?**:
```python
if not payment_success:
    # Rollback - release seats
    for ticket in booking.tickets:
        if ticket.seat:
            ticket.seat.release()  # Set is_booked = False
    raise PaymentFailedException("Payment processing failed")
```

This ensures transaction-like behavior: either everything succeeds or nothing changes.

#### Step 6.9: Confirm Booking

**Code**:
```python
booking.confirm_booking()
```

**Execution Trace**:
```
1. Set: booking.status = CONFIRMED

2. For each ticket in tickets:
     - Check: ticket.status != CANCELLED?
     - If yes: ticket.confirm()
       - Set: ticket.status = CONFIRMED
```

**Memory State**:
```
booking.status = CONFIRMED
booking.tickets[0].status = CONFIRMED
booking.tickets[1].status = CONFIRMED
```

#### Step 6.10: Store Booking

**Code**:
```python
self.bookings[pnr] = booking
```

**Execution Trace**:
```
1. Add to dictionary:
   bookings["A7K2M9X4B1"] = booking
```

**Memory State**:
```
booking_manager.bookings = {
    "A7K2M9X4B1": booking
}
```

#### Step 6.11: Send Notifications (Observer Pattern)

**Code**:
```python
self.notification_service.notify_booking_confirmed(booking, contact_info)
```

**Execution Trace**:
```
1. notification_service.notify_booking_confirmed(booking, contact_info)

2. Prepare data:
   data = {
       'pnr': "A7K2M9X4B1",
       'email': "alice@example.com",
       'phone': "+91-9876543210",
       'amount': 1500
   }

3. Call notify_all("BOOKING_CONFIRMED", data)

4. For each observer in observers:

   Observer 1: EmailNotificationObserver
   a. email_observer.update("BOOKING_CONFIRMED", data)
   b. Extract: pnr = "A7K2M9X4B1"
   c. Extract: email = "alice@example.com"
   d. Print: "Email sent to alice@example.com: Booking A7K2M9X4B1 confirmed!"

   Observer 2: SMSNotificationObserver
   a. sms_observer.update("BOOKING_CONFIRMED", data)
   b. Extract: pnr = "A7K2M9X4B1"
   c. Extract: phone = "+91-9876543210"
   d. Print: "SMS sent to +91-9876543210: Your PNR A7K2M9X4B1 is confirmed!"
```

**Output**:
```
Email sent to alice@example.com: Booking A7K2M9X4B1 confirmed!
SMS sent to +91-9876543210: Your PNR A7K2M9X4B1 is confirmed!
```

#### Step 6.12: Release Lock and Return

**Code**:
```python
return booking
```

**Execution Trace**:
```
1. Exit critical section (with block ends)
2. Release lock (allows other threads to proceed)
3. Return booking object to caller
```

## Final Memory State

```
booking = Booking {
    pnr: "A7K2M9X4B1",
    train: rajdhani,
    passengers: [passenger1, passenger2],
    tickets: [
        Ticket(id="T123456", passenger="Alice Smith", seat="3A-1", status=CONFIRMED),
        Ticket(id="T789012", passenger="Bob Smith", seat="3A-2", status=CONFIRMED)
    ],
    booking_date: 2025-11-17 14:30:00,
    travel_date: 2025-11-17,
    total_amount: 1500,
    status: CONFIRMED
}

rajdhani.seats[AC_3]:
    - Seat "3A-1": is_booked = True
    - Seat "3A-2": is_booked = True
    - Seat "3A-3" to "3A-50": is_booked = False

booking_manager.bookings:
    "A7K2M9X4B1" → booking
```

## Design Patterns Summary

| Pattern | Where Used | Benefit in This Flow |
|---------|------------|---------------------|
| **Singleton** | BookingManager | Single point of control, prevents multiple instances managing bookings |
| **Factory** | TicketFactory.create_confirmed_ticket() | Encapsulates ticket creation, easy to add new types |
| **Strategy** | CreditCardPayment.process_payment() | Can swap payment method without changing booking code |
| **Observer** | NotificationService notifies Email and SMS | Adding WhatsApp notifications requires no booking code changes |

## SOLID Principles in Action

1. **SRP**: Each class has one job
   - Seat: manages seat state
   - Booking: manages booking lifecycle
   - PaymentProcessor: handles payment
   - NotificationService: handles notifications

2. **OCP**: Open for extension
   - Can add new PaymentProcessor (e.g., NetBanking) without modifying BookingManager
   - Can add new Observer (e.g., PushNotification) without modifying booking logic

3. **LSP**: Substitutability
   - Any PaymentProcessor can replace CreditCardPayment
   - Any Observer can replace EmailNotificationObserver

4. **ISP**: Focused interfaces
   - PaymentProcessor has single method: process_payment()
   - Observer has single method: update()

5. **DIP**: Depend on abstractions
   - BookingManager depends on PaymentProcessor interface, not CreditCardPayment
   - NotificationService depends on Observer interface, not concrete observers

## Thread Safety Analysis

What happens if two users try to book the last 2 seats simultaneously?

**Thread 1**: Trying to book 2 seats
**Thread 2**: Trying to book 1 seat

```
Time  | Thread 1                          | Thread 2
------|-----------------------------------|----------------------------------
T1    | create_booking() called           |
T2    | Validate passengers ✓             |
T3    | Enter: with booking_manager.lock |
T4    | Lock acquired                     | create_booking() called
T5    | PNR = "AAA"                       | Validate passengers ✓
T6    | Create booking object             | Enter: with booking_manager.lock
T7    |                                   | WAITING (lock held by Thread 1)
T8    | Call train.book_seats(AC_3, 2)    |
T9    | Enter: with train.lock            |
T10   | Get available: [3A-1, 3A-2]       |
T11   | Check: 2 >= 2? Yes                |
T12   | Book 3A-1 and 3A-2                |
T13   | 3A-1.is_booked = True             |
T14   | 3A-2.is_booked = True             |
T15   | Exit: train.lock released         |
T16   | Create tickets                    |
T17   | Process payment ✓                 |
T18   | Confirm booking                   |
T19   | Store in bookings dict            |
T20   | Exit: booking_manager.lock        | Lock acquired!
T21   |                                   | PNR = "BBB"
T22   |                                   | Create booking object
T23   |                                   | Call train.book_seats(AC_3, 1)
T24   |                                   | Enter: with train.lock
T25   |                                   | Get available: [] (all booked!)
T26   |                                   | Check: 0 >= 1? No
T27   |                                   | Raise SeatNotAvailableException
T28   |                                   | Handle exception: waiting list
```

**Result**: Thread 1 succeeds with 2 confirmed seats. Thread 2 gets waiting list because seats are no longer available. No double booking occurs.

## What We Learned

1. **Locking is Critical**: Without locks, both threads could see 2 available seats and both would try to book them, leading to double booking.

2. **Transaction-like Behavior**: Payment failure triggers rollback (seat release), ensuring data consistency.

3. **Pattern Synergy**: Multiple patterns work together seamlessly - Singleton manages state, Factory creates objects, Strategy handles algorithms, Observer notifies listeners.

4. **Separation of Concerns**: Each component has a clear responsibility, making the system maintainable and testable.
