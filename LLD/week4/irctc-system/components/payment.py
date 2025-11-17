"""
Payment and Notification Components - IRCTC System

This module contains components for payment processing and notifications.
Demonstrates Strategy Pattern (Payment), Observer Pattern (Notifications),
and Singleton Pattern (BookingManager).

Classes:
    Payment Strategy:
        - PaymentProcessor: Abstract payment interface
        - CreditCardPayment, DebitCardPayment, UPIPayment: Concrete implementations

    Observer Pattern:
        - Observer: Abstract observer interface
        - EmailNotificationObserver, SMSNotificationObserver: Concrete observers
        - NotificationService: Subject managing observers

    Singleton:
        - BookingManager: Central booking controller
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import date
from threading import Lock
import random
import string

# Import from other modules
from train import Train, Seat, SeatType, BookingException, SeatNotAvailableException
from booking import (
    Passenger, Ticket, Booking, TicketFactory,
    TicketStatus, BookingStatus, InvalidPNRException, PaymentFailedException
)


# ============================================================================
# STRATEGY PATTERN (Payment Processing)
# ============================================================================

class PaymentProcessor(ABC):
    """
    Abstract payment processor interface.

    Demonstrates: Strategy Pattern, DIP (depend on abstraction).

    Why Strategy?:
    - Each payment method has completely different processing logic
    - New payment methods can be added without changing BookingManager
    - Runtime selection of payment method
    - Each strategy is independently testable

    Design Note: This is the abstraction that BookingManager depends on.
    It doesn't care about CreditCard vs UPI details.
    """

    @abstractmethod
    def process_payment(self, amount: float, details: dict) -> bool:
        """
        Process payment.

        Args:
            amount: Amount to charge
            details: Payment details (card number, UPI ID, etc.)

        Returns:
            True if payment successful, False otherwise

        Design Note: Returns bool rather than raising exceptions to allow
        caller to handle failures gracefully (e.g., retry logic).
        """
        pass


class CreditCardPayment(PaymentProcessor):
    """Credit card payment implementation"""

    def process_payment(self, amount: float, details: dict) -> bool:
        """
        Process credit card payment.

        In a real system, this would:
        1. Validate card number (Luhn algorithm)
        2. Check expiry date
        3. Verify CVV
        4. Call payment gateway API
        5. Handle 3D Secure authentication
        6. Return transaction ID
        """
        print(f"Processing Credit Card payment of Rs. {amount}")
        card_number = details.get('card_number', 'XXXX-XXXX-XXXX-XXXX')
        print(f"Card: {card_number}")

        # Simulate payment processing
        if amount > 0:
            print("Payment successful!")
            return True
        return False


class DebitCardPayment(PaymentProcessor):
    """Debit card payment implementation"""

    def process_payment(self, amount: float, details: dict) -> bool:
        """
        Process debit card payment.

        Similar to credit card but with additional balance check.
        """
        print(f"Processing Debit Card payment of Rs. {amount}")
        card_number = details.get('card_number', 'XXXX-XXXX-XXXX-XXXX')
        print(f"Card: {card_number}")

        # Simulate payment processing
        if amount > 0:
            print("Payment successful!")
            return True
        return False


class UPIPayment(PaymentProcessor):
    """UPI payment implementation"""

    def process_payment(self, amount: float, details: dict) -> bool:
        """
        Process UPI payment.

        In a real system, this would:
        1. Validate UPI ID format
        2. Send payment request to UPI server
        3. Wait for user authorization on phone
        4. Receive callback with status
        5. Return transaction reference
        """
        print(f"Processing UPI payment of Rs. {amount}")
        upi_id = details.get('upi_id', 'user@upi')
        print(f"UPI ID: {upi_id}")

        # Simulate payment processing
        if amount > 0:
            print("Payment successful!")
            return True
        return False


# ============================================================================
# OBSERVER PATTERN (Notification)
# ============================================================================

class Observer(ABC):
    """
    Observer interface for notifications.

    Demonstrates: Observer Pattern.

    Why Observer?:
    - Booking logic doesn't need to know about notification details
    - Easy to add new notification channels
    - Notifications can happen asynchronously
    - Loose coupling between booking and notification systems
    """

    @abstractmethod
    def update(self, event: str, data: dict):
        """
        Handle notification.

        Args:
            event: Event type (e.g., "BOOKING_CONFIRMED")
            data: Event data
        """
        pass


class EmailNotificationObserver(Observer):
    """Email notification implementation"""

    def update(self, event: str, data: dict):
        """
        Send email notification.

        In a real system, this would:
        1. Compose email from template
        2. Attach booking details/ticket PDF
        3. Send via SMTP or email service API
        4. Handle delivery failures
        5. Log sent emails
        """
        if event == "BOOKING_CONFIRMED":
            pnr = data.get('pnr')
            email = data.get('email', 'user@example.com')
            print(f"Email sent to {email}: Booking {pnr} confirmed!")

        elif event == "BOOKING_CANCELLED":
            pnr = data.get('pnr')
            email = data.get('email', 'user@example.com')
            print(f"Email sent to {email}: Booking {pnr} cancelled!")


class SMSNotificationObserver(Observer):
    """SMS notification implementation"""

    def update(self, event: str, data: dict):
        """
        Send SMS notification.

        In a real system, this would:
        1. Format message (160 char limit)
        2. Call SMS gateway API
        3. Handle delivery status
        4. Retry on failure
        """
        if event == "BOOKING_CONFIRMED":
            pnr = data.get('pnr')
            phone = data.get('phone', '+91-XXXXXXXXXX')
            print(f"SMS sent to {phone}: Your PNR {pnr} is confirmed!")

        elif event == "BOOKING_CANCELLED":
            pnr = data.get('pnr')
            phone = data.get('phone', '+91-XXXXXXXXXX')
            print(f"SMS sent to {phone}: Your PNR {pnr} is cancelled!")


class NotificationService:
    """
    Notification service using Observer pattern.

    Demonstrates: Observer Pattern, OCP (can add new observers).

    Attributes:
        observers: List of registered observers

    Design Note: This is the Subject in Observer pattern. It maintains
    a list of observers and notifies them of events.
    """

    def __init__(self):
        self.observers: List[Observer] = []

    def subscribe(self, observer: Observer):
        """Add an observer"""
        if observer not in self.observers:
            self.observers.append(observer)

    def unsubscribe(self, observer: Observer):
        """Remove an observer"""
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_all(self, event: str, data: dict):
        """Notify all observers of an event"""
        for observer in self.observers:
            observer.update(event, data)

    def notify_booking_confirmed(self, booking: Booking, contact_info: dict):
        """Notify about confirmed booking"""
        data = {
            'pnr': booking.pnr,
            'email': contact_info.get('email'),
            'phone': contact_info.get('phone'),
            'amount': booking.total_amount
        }
        self.notify_all("BOOKING_CONFIRMED", data)

    def notify_booking_cancelled(self, booking: Booking, contact_info: dict):
        """Notify about cancelled booking"""
        data = {
            'pnr': booking.pnr,
            'email': contact_info.get('email'),
            'phone': contact_info.get('phone')
        }
        self.notify_all("BOOKING_CANCELLED", data)


# ============================================================================
# SINGLETON PATTERN (Booking Manager)
# ============================================================================

class BookingManager:
    """
    Singleton class to manage all bookings.

    Demonstrates: Singleton Pattern, Thread Safety.

    Why Singleton?:
    - Single point of control for booking operations
    - Manages shared state (booking dictionary)
    - Coordinates locking for thread safety
    - Ensures consistent PNR generation

    Thread Safety: Double-checked locking for instance creation.
    Each booking operation is also locked to prevent race conditions.

    Attributes:
        bookings: Dictionary mapping PNR to Booking objects
        notification_service: NotificationService instance
        lock: Threading lock for booking operations
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        """
        Ensure only one instance exists (thread-safe).

        Uses double-checked locking pattern:
        1. Check if instance exists (without lock) - fast path
        2. If not, acquire lock
        3. Check again inside lock - handles race condition
        4. Create instance if still None
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the booking manager"""
        if self._initialized:
            return

        self.bookings: Dict[str, Booking] = {}
        self.lock = Lock()
        self.notification_service = NotificationService()
        self._initialized = True

    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        return cls()

    def _generate_pnr(self) -> str:
        """
        Generate unique PNR.

        Returns:
            10-character alphanumeric PNR

        Design Note: In production, this would check database for uniqueness.
        Random generation is acceptable for demo as collision probability is low.
        """
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def create_booking(
        self,
        train: Train,
        passengers: List[Passenger],
        travel_date: date,
        seat_type: SeatType,
        payment_processor: PaymentProcessor,
        payment_details: dict,
        contact_info: dict
    ) -> Booking:
        """
        Create a new booking - the complete booking flow.

        This is the main method that orchestrates:
        1. Validation
        2. Seat allocation
        3. Payment processing
        4. Confirmation
        5. Notifications

        Thread-safe operation with proper locking.

        Args:
            train: Train to book
            passengers: List of passengers
            travel_date: Date of travel
            seat_type: Type of seats to book
            payment_processor: Payment strategy to use
            payment_details: Payment details
            contact_info: Contact information for notifications

        Returns:
            Created Booking object

        Raises:
            BookingException: If validation fails
            SeatNotAvailableException: If seats not available
            PaymentFailedException: If payment fails

        Transaction Guarantee:
        - Either booking succeeds completely, or nothing is changed
        - On payment failure, seats are released (rollback)
        """
        # Step 1: Validate passengers
        for passenger in passengers:
            if not passenger.validate():
                raise BookingException(f"Invalid passenger data: {passenger.name}")

        # Step 2: Validate travel date
        if travel_date < date.today():
            raise BookingException("Cannot book for past dates")

        # Step 3: Atomic booking operation
        with self.lock:
            # Generate unique PNR
            pnr = self._generate_pnr()

            # Create booking object
            booking = Booking(pnr, train, passengers, travel_date)

            # Step 4: Try to allocate seats
            try:
                seats = train.book_seats(seat_type, len(passengers))

                # Create confirmed tickets
                for passenger, seat in zip(passengers, seats):
                    ticket = TicketFactory.create_confirmed_ticket(pnr, passenger, seat)
                    booking.add_ticket(ticket)

            except SeatNotAvailableException:
                # Handle partial availability
                available_count = len(train.get_available_seats(seat_type))

                if available_count > 0:
                    # Book available seats as confirmed
                    seats = train.book_seats(seat_type, available_count)
                    for passenger, seat in zip(passengers[:available_count], seats):
                        ticket = TicketFactory.create_confirmed_ticket(pnr, passenger, seat)
                        booking.add_ticket(ticket)

                    # Rest go to waiting list
                    for passenger in passengers[available_count:]:
                        ticket = TicketFactory.create_waiting_ticket(pnr, passenger)
                        booking.add_ticket(ticket)
                else:
                    # All go to waiting list
                    for passenger in passengers:
                        ticket = TicketFactory.create_waiting_ticket(pnr, passenger)
                        booking.add_ticket(ticket)

            # Step 5: Process payment
            total_amount = booking.calculate_total()
            payment_success = payment_processor.process_payment(total_amount, payment_details)

            if not payment_success:
                # Rollback - release all allocated seats
                for ticket in booking.tickets:
                    if ticket.seat:
                        ticket.seat.release()
                raise PaymentFailedException("Payment processing failed")

            # Step 6: Confirm booking
            booking.confirm_booking()

            # Step 7: Store booking
            self.bookings[pnr] = booking

            # Step 8: Notify
            self.notification_service.notify_booking_confirmed(booking, contact_info)

            return booking

    def cancel_booking(self, pnr: str, contact_info: dict) -> bool:
        """
        Cancel a booking.

        Args:
            pnr: PNR to cancel
            contact_info: Contact information for notifications

        Returns:
            True if cancellation successful

        Raises:
            InvalidPNRException: If PNR not found
            BookingException: If booking already cancelled
        """
        with self.lock:
            if pnr not in self.bookings:
                raise InvalidPNRException(f"PNR {pnr} not found")

            booking = self.bookings[pnr]

            if booking.status == BookingStatus.CANCELLED:
                raise BookingException("Booking already cancelled")

            # Release all allocated seats
            for ticket in booking.tickets:
                if ticket.seat:
                    ticket.seat.release()

            # Cancel booking
            booking.cancel_booking()

            # Notify
            self.notification_service.notify_booking_cancelled(booking, contact_info)

            print(f"Booking {pnr} cancelled successfully")
            return True

    def get_booking(self, pnr: str) -> Booking:
        """
        Get booking by PNR.

        Args:
            pnr: PNR to search

        Returns:
            Booking object

        Raises:
            InvalidPNRException: If PNR not found
        """
        if pnr not in self.bookings:
            raise InvalidPNRException(f"PNR {pnr} not found")
        return self.bookings[pnr]
