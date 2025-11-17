# IRCTC Railway Reservation System - Overview

## What Are We Building?

An online railway ticket booking system similar to IRCTC (Indian Railway Catering and Tourism Corporation). This system handles the complete lifecycle of train ticket bookings, from searching trains to payment processing, with emphasis on concurrent booking scenarios and preventing double bookings.

## The Problem

Have you ever wondered how thousands of people can simultaneously book train tickets without ending up with the same seat? When multiple users are frantically clicking "Book Now" for the last few available seats on a popular train, how does the system ensure that exactly one person gets each seat?

This is not just a simple database update problem. Consider these challenges:

1. **Race Conditions**: User A and User B both see seat 23A as available and click book at nearly the same instant. Who gets the seat?

2. **Partial Availability**: A family of 4 wants to book tickets, but only 2 confirmed seats are available. Should the system reject the entire booking or offer 2 confirmed + 2 waiting list?

3. **Payment Failures**: What happens when seats are allocated but payment processing fails? The seats should return to the pool immediately.

4. **Multiple Payment Methods**: Different users prefer different payment methods (Credit Card, Debit Card, UPI). The system should support all without duplicating code.

5. **Real-time Notifications**: Users expect instant confirmation via email and SMS. This should happen asynchronously without blocking the booking flow.

## Requirements

### Functional Requirements

1. **Train Management**
   - Maintain train schedules with source and destination stations
   - Manage multiple seat types (AC 1-Tier, AC 2-Tier, AC 3-Tier, Sleeper, General)
   - Track seat availability in real-time

2. **Search and Discovery**
   - Search trains between source and destination
   - View seat availability for different classes
   - Display pricing for each seat type

3. **Booking Management**
   - Book tickets for multiple passengers
   - Generate unique PNR for each booking
   - Handle confirmed, RAC (Reservation Against Cancellation), and waiting list tickets
   - Support booking cancellation with seat release

4. **Payment Processing**
   - Process payments through multiple methods
   - Handle payment failures gracefully
   - Rollback seat allocation if payment fails

5. **Notifications**
   - Send booking confirmation via email and SMS
   - Notify about cancellations
   - Support multiple notification channels

### Non-Functional Requirements

1. **Concurrency Handling**
   - Thread-safe booking operations
   - No double booking of seats
   - Proper locking mechanisms

2. **Data Consistency**
   - ACID properties for booking transactions
   - Atomic seat allocation and payment processing

3. **Extensibility**
   - Easy to add new seat types
   - Support for additional payment methods
   - Pluggable notification channels

4. **Performance**
   - Quick search results
   - Efficient seat allocation algorithm
   - Minimal locking duration

## Core Use Cases

### Use Case 1: Search Trains
**Actor**: User
**Flow**:
1. User enters source station, destination station, and travel date
2. System searches for available trains
3. System displays trains with seat availability for each class
4. User selects a train

**Outcome**: User sees available trains and their seat availability

### Use Case 2: Book Tickets
**Actor**: User
**Precondition**: Train and seat type selected
**Flow**:
1. User provides passenger details (name, age, gender)
2. System validates passenger data
3. System checks seat availability
4. System allocates seats (confirmed or waiting list)
5. User selects payment method and provides details
6. System processes payment
7. System confirms booking and generates PNR
8. System sends notifications (email and SMS)

**Postcondition**: Booking created, seats allocated, user notified

**Alternative Flows**:
- **Insufficient Seats**: Allocate available seats as confirmed, rest as waiting list
- **Payment Failure**: Rollback seat allocation, notify user
- **Validation Error**: Show error message, don't proceed with booking

### Use Case 3: Cancel Booking
**Actor**: User
**Precondition**: User has a confirmed booking
**Flow**:
1. User provides PNR
2. System validates PNR
3. System releases allocated seats
4. System marks booking as cancelled
5. System sends cancellation notification

**Postcondition**: Seats available again, booking cancelled

## Key Design Decisions

### 1. Singleton for Booking Manager
**Why?**: We need a single point of control for all bookings to manage concurrent access and maintain consistency. Multiple instances would lead to race conditions.

**Trade-off**: Makes testing slightly harder (need to reset singleton state), but provides essential thread-safety guarantees.

### 2. Factory Pattern for Tickets
**Why?**: Different ticket types (Confirmed, RAC, Waiting) have subtle differences in behavior but share a common interface.

**Benefit**: Easy to add new ticket types without modifying existing code (Open/Closed Principle).

### 3. Strategy Pattern for Payments
**Why?**: Payment processing logic differs completely for Credit Card, Debit Card, and UPI, but all serve the same purpose.

**Benefit**: Can add new payment methods without changing BookingManager code. Allows runtime selection of payment method.

### 4. Observer Pattern for Notifications
**Why?**: Multiple notification channels (Email, SMS, Push) need to be informed of booking events, but the booking logic shouldn't know about notification details.

**Benefit**: Adding new notification channels requires no changes to booking code. Notifications happen asynchronously.

## What Makes This Interesting?

Unlike simple CRUD applications, this system demonstrates:

1. **Concurrent Programming**: Real-world race condition handling
2. **Transaction Management**: Coordinating multiple operations atomically
3. **Design Pattern Synergy**: Multiple patterns working together
4. **Error Recovery**: Graceful handling of failures at each step
5. **Scalability Considerations**: How locking affects throughput

## Success Metrics

A well-designed system should:
- Never double-book a seat
- Complete a booking in under 2 seconds
- Handle payment failures without data corruption
- Support 100+ concurrent booking requests
- Allow adding new features without breaking existing code

## File Structure

```
irctc-system/
├── overview.md           (this file)
├── architecture.md       (component breakdown)
├── components/
│   ├── train.py         (Train, Station, Seat classes)
│   ├── booking.py       (Booking, Ticket, BookingManager)
│   └── payment.py       (Payment strategies and notifications)
└── walkthrough.md       (execution flow with dry run)
```

## Next Steps

1. Review the **architecture.md** to understand component relationships
2. Study the **components/** to see implementation details
3. Follow the **walkthrough.md** for a complete booking flow with execution trace
