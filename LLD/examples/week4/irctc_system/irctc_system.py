"""
IRCTC Railway Reservation System - Complete Implementation
Demonstrates: Singleton, Factory, Strategy, Observer patterns
SOLID Principles: All five principles demonstrated
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime, date
from threading import Lock
import random
import string


# ============================================================================
# ENUMERATIONS
# ============================================================================

class SeatType(Enum):
    """Different classes of seats available in trains"""
    AC_1 = ("1A", 1500)
    AC_2 = ("2A", 1000)
    AC_3 = ("3A", 750)
    SLEEPER = ("SL", 400)
    GENERAL = ("GEN", 200)

    def __init__(self, code, base_price):
        self.code = code
        self.base_price = base_price


class TicketStatus(Enum):
    """Status of a ticket"""
    CONFIRMED = "CNF"
    RAC = "RAC"
    WAITING = "WL"
    CANCELLED = "CAN"


class BookingStatus(Enum):
    """Status of a booking"""
    CONFIRMED = "CONFIRMED"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"


# ============================================================================
# EXCEPTIONS
# ============================================================================

class BookingException(Exception):
    """Base exception for booking-related errors"""
    pass


class SeatNotAvailableException(BookingException):
    """Raised when requested seats are not available"""
    pass


class InvalidPNRException(BookingException):
    """Raised when PNR is invalid"""
    pass


class PaymentFailedException(BookingException):
    """Raised when payment processing fails"""
    pass


# ============================================================================
# CORE ENTITIES
# ============================================================================

class Station:
    """Represents a railway station"""

    def __init__(self, code: str, name: str, city: str):
        """
        Initialize a station.

        Args:
            code: Station code (e.g., "NDLS")
            name: Station name (e.g., "New Delhi")
            city: City name
        """
        self.code = code
        self.name = name
        self.city = city

    def __str__(self):
        return f"{self.name} ({self.code})"

    def __repr__(self):
        return f"Station({self.code}, {self.name})"


class Seat:
    """
    Represents a seat in a train.
    Demonstrates: Single Responsibility Principle - manages only seat state
    """

    def __init__(self, seat_number: str, seat_type: SeatType):
        """
        Initialize a seat.

        Args:
            seat_number: Unique seat identifier (e.g., "A1", "B23")
            seat_type: Type/class of seat
        """
        self.seat_number = seat_number
        self.seat_type = seat_type
        self.is_booked = False
        self.price = seat_type.base_price

    def book(self):
        """Mark seat as booked"""
        if self.is_booked:
            raise BookingException(f"Seat {self.seat_number} is already booked")
        self.is_booked = True

    def release(self):
        """Release/unbook seat"""
        self.is_booked = False

    def get_price(self) -> float:
        """Get seat price"""
        return self.price

    def __str__(self):
        status = "Booked" if self.is_booked else "Available"
        return f"Seat {self.seat_number} ({self.seat_type.code}) - {status}"


class Train:
    """
    Represents a train with multiple seat types.
    Demonstrates: Composition (has seats), SRP (manages train state)
    """

    def __init__(self, train_no: str, name: str, source: Station, destination: Station):
        """
        Initialize a train.

        Args:
            train_no: Unique train number
            name: Train name
            source: Starting station
            destination: End station
        """
        self.train_no = train_no
        self.name = name
        self.source = source
        self.destination = destination
        self.seats: Dict[SeatType, List[Seat]] = {seat_type: [] for seat_type in SeatType}
        self.lock = Lock()  # For thread-safe seat operations

    def add_seat(self, seat: Seat):
        """Add a seat to the train"""
        self.seats[seat.seat_type].append(seat)

    def add_seats_bulk(self, seat_type: SeatType, count: int):
        """Add multiple seats of same type"""
        for i in range(count):
            seat_number = f"{seat_type.code}-{i+1}"
            self.add_seat(Seat(seat_number, seat_type))

    def get_available_seats(self, seat_type: SeatType) -> List[Seat]:
        """Get list of available seats for given type"""
        with self.lock:
            return [seat for seat in self.seats[seat_type] if not seat.is_booked]

    def has_availability(self, seat_type: SeatType, count: int) -> bool:
        """Check if required number of seats are available"""
        available = self.get_available_seats(seat_type)
        return len(available) >= count

    def book_seats(self, seat_type: SeatType, count: int) -> List[Seat]:
        """
        Book specified number of seats.
        Thread-safe operation.

        Args:
            seat_type: Type of seats to book
            count: Number of seats needed

        Returns:
            List of booked seats

        Raises:
            SeatNotAvailableException: If seats not available
        """
        with self.lock:
            available_seats = self.get_available_seats(seat_type)
            if len(available_seats) < count:
                raise SeatNotAvailableException(
                    f"Only {len(available_seats)} seats available, {count} requested"
                )

            booked_seats = available_seats[:count]
            for seat in booked_seats:
                seat.book()

            return booked_seats

    def release_seats(self, seats: List[Seat]):
        """Release booked seats"""
        with self.lock:
            for seat in seats:
                seat.release()

    def get_seat_availability_summary(self) -> Dict[SeatType, int]:
        """Get availability count for all seat types"""
        summary = {}
        for seat_type in SeatType:
            available = len(self.get_available_seats(seat_type))
            total = len(self.seats[seat_type])
            summary[seat_type] = {"available": available, "total": total}
        return summary

    def __str__(self):
        return f"Train {self.train_no} - {self.name} ({self.source.code} → {self.destination.code})"


class Passenger:
    """
    Represents a passenger.
    Demonstrates: SRP - manages only passenger data
    """

    _id_counter = 1

    def __init__(self, name: str, age: int, gender: str):
        """
        Initialize a passenger.

        Args:
            name: Passenger name
            age: Passenger age
            gender: Gender (M/F/O)
        """
        self.passenger_id = f"P{Passenger._id_counter:06d}"
        Passenger._id_counter += 1
        self.name = name
        self.age = age
        self.gender = gender.upper()

    def validate(self) -> bool:
        """Validate passenger data"""
        if not self.name or len(self.name.strip()) == 0:
            return False
        if self.age < 0 or self.age > 120:
            return False
        if self.gender not in ['M', 'F', 'O']:
            return False
        return True

    def __str__(self):
        return f"{self.name} ({self.age}{self.gender})"


class Ticket:
    """
    Represents a ticket for one passenger.
    Base class for different ticket types.
    Demonstrates: LSP - different ticket types are substitutable
    """

    def __init__(self, pnr: str, passenger: Passenger, seat: Optional[Seat], status: TicketStatus):
        """
        Initialize a ticket.

        Args:
            pnr: PNR of the booking
            passenger: Passenger for this ticket
            seat: Seat allocated (None for waiting list)
            status: Ticket status
        """
        self.ticket_id = f"T{random.randint(100000, 999999)}"
        self.pnr = pnr
        self.passenger = passenger
        self.seat = seat
        self.status = status

    def confirm(self):
        """Confirm the ticket"""
        self.status = TicketStatus.CONFIRMED

    def cancel(self):
        """Cancel the ticket"""
        self.status = TicketStatus.CANCELLED

    def get_status(self) -> TicketStatus:
        """Get ticket status"""
        return self.status

    def __str__(self):
        seat_info = f"Seat: {self.seat.seat_number}" if self.seat else "No seat"
        return f"Ticket {self.ticket_id} - {self.passenger.name} - {self.status.value} - {seat_info}"


class Booking:
    """
    Represents a complete booking with multiple tickets.
    Demonstrates: SRP - manages booking lifecycle
    """

    def __init__(self, pnr: str, train: Train, passengers: List[Passenger], travel_date: date):
        """
        Initialize a booking.

        Args:
            pnr: Unique PNR
            train: Train for journey
            passengers: List of passengers
            travel_date: Date of journey
        """
        self.pnr = pnr
        self.train = train
        self.passengers = passengers
        self.tickets: List[Ticket] = []
        self.booking_date = datetime.now()
        self.travel_date = travel_date
        self.total_amount = 0.0
        self.status = BookingStatus.PENDING

    def add_ticket(self, ticket: Ticket):
        """Add a ticket to booking"""
        self.tickets.append(ticket)
        if ticket.seat:
            self.total_amount += ticket.seat.get_price()

    def calculate_total(self) -> float:
        """Calculate total booking amount"""
        return self.total_amount

    def confirm_booking(self):
        """Confirm the booking"""
        self.status = BookingStatus.CONFIRMED
        for ticket in self.tickets:
            if ticket.status != TicketStatus.CANCELLED:
                ticket.confirm()

    def cancel_booking(self):
        """Cancel the booking"""
        self.status = BookingStatus.CANCELLED
        for ticket in self.tickets:
            ticket.cancel()

    def get_booking_summary(self) -> str:
        """Get formatted booking summary"""
        summary = f"\n{'='*60}\n"
        summary += f"PNR: {self.pnr}\n"
        summary += f"Status: {self.status.value}\n"
        summary += f"Train: {self.train}\n"
        summary += f"Travel Date: {self.travel_date}\n"
        summary += f"Booking Date: {self.booking_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"Total Amount: ₹{self.total_amount}\n"
        summary += f"\nPassengers:\n"
        summary += f"{'-'*60}\n"
        for ticket in self.tickets:
            summary += f"  {ticket}\n"
        summary += f"{'='*60}\n"
        return summary

    def __str__(self):
        return f"Booking {self.pnr} - {self.status.value} - {len(self.tickets)} tickets"


# ============================================================================
# DESIGN PATTERNS: FACTORY
# ============================================================================

class TicketFactory:
    """
    Factory pattern for creating different types of tickets.
    Demonstrates: Factory Pattern, OCP (can add new ticket types easily)
    """

    @staticmethod
    def create_confirmed_ticket(pnr: str, passenger: Passenger, seat: Seat) -> Ticket:
        """Create a confirmed ticket"""
        return Ticket(pnr, passenger, seat, TicketStatus.CONFIRMED)

    @staticmethod
    def create_rac_ticket(pnr: str, passenger: Passenger, seat: Seat) -> Ticket:
        """Create a RAC (Reservation Against Cancellation) ticket"""
        return Ticket(pnr, passenger, seat, TicketStatus.RAC)

    @staticmethod
    def create_waiting_ticket(pnr: str, passenger: Passenger) -> Ticket:
        """Create a waiting list ticket (no seat)"""
        return Ticket(pnr, passenger, None, TicketStatus.WAITING)

    @staticmethod
    def create_ticket(pnr: str, passenger: Passenger, seat: Optional[Seat],
                     status: TicketStatus) -> Ticket:
        """
        General factory method to create any ticket type.

        Args:
            pnr: PNR of booking
            passenger: Passenger for ticket
            seat: Seat allocated (can be None)
            status: Ticket status

        Returns:
            Created ticket
        """
        return Ticket(pnr, passenger, seat, status)


# ============================================================================
# DESIGN PATTERNS: STRATEGY (Payment Processing)
# ============================================================================

class PaymentProcessor(ABC):
    """
    Abstract payment processor interface.
    Demonstrates: Strategy Pattern, DIP (depend on abstraction)
    """

    @abstractmethod
    def process_payment(self, amount: float, details: dict) -> bool:
        """
        Process payment.

        Args:
            amount: Amount to charge
            details: Payment details (card number, etc.)

        Returns:
            True if payment successful, False otherwise
        """
        pass


class CreditCardPayment(PaymentProcessor):
    """Credit card payment implementation"""

    def process_payment(self, amount: float, details: dict) -> bool:
        """Process credit card payment"""
        print(f"Processing Credit Card payment of ₹{amount}")
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
        """Process debit card payment"""
        print(f"Processing Debit Card payment of ₹{amount}")
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
        """Process UPI payment"""
        print(f"Processing UPI payment of ₹{amount}")
        upi_id = details.get('upi_id', 'user@upi')
        print(f"UPI ID: {upi_id}")

        # Simulate payment processing
        if amount > 0:
            print("Payment successful!")
            return True
        return False


# ============================================================================
# DESIGN PATTERNS: OBSERVER (Notification)
# ============================================================================

class Observer(ABC):
    """Observer interface for notifications"""

    @abstractmethod
    def update(self, event: str, data: dict):
        """Handle notification"""
        pass


class EmailNotificationObserver(Observer):
    """Email notification implementation"""

    def update(self, event: str, data: dict):
        """Send email notification"""
        if event == "BOOKING_CONFIRMED":
            pnr = data.get('pnr')
            email = data.get('email', 'user@example.com')
            print(f"📧 Sending email to {email}: Booking {pnr} confirmed!")
        elif event == "BOOKING_CANCELLED":
            pnr = data.get('pnr')
            email = data.get('email', 'user@example.com')
            print(f"📧 Sending email to {email}: Booking {pnr} cancelled!")


class SMSNotificationObserver(Observer):
    """SMS notification implementation"""

    def update(self, event: str, data: dict):
        """Send SMS notification"""
        if event == "BOOKING_CONFIRMED":
            pnr = data.get('pnr')
            phone = data.get('phone', '+91-XXXXXXXXXX')
            print(f"📱 Sending SMS to {phone}: Your PNR {pnr} is confirmed!")
        elif event == "BOOKING_CANCELLED":
            pnr = data.get('pnr')
            phone = data.get('phone', '+91-XXXXXXXXXX')
            print(f"📱 Sending SMS to {phone}: Your PNR {pnr} is cancelled!")


class NotificationService:
    """
    Notification service using Observer pattern.
    Demonstrates: Observer Pattern, OCP (can add new observers)
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
        """Notify all observers"""
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
# DESIGN PATTERNS: SINGLETON (Booking Manager)
# ============================================================================

class BookingManager:
    """
    Singleton class to manage all bookings.
    Demonstrates: Singleton Pattern, Thread Safety
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
        """Generate unique PNR"""
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
        Create a new booking.
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
            Created booking

        Raises:
            SeatNotAvailableException: If seats not available
            PaymentFailedException: If payment fails
        """
        # Validate passengers
        for passenger in passengers:
            if not passenger.validate():
                raise BookingException(f"Invalid passenger data: {passenger.name}")

        # Validate travel date
        if travel_date < date.today():
            raise BookingException("Cannot book for past dates")

        with self.lock:
            # Generate PNR
            pnr = self._generate_pnr()

            # Create booking
            booking = Booking(pnr, train, passengers, travel_date)

            # Try to allocate seats
            try:
                seats = train.book_seats(seat_type, len(passengers))

                # Create tickets
                for passenger, seat in zip(passengers, seats):
                    ticket = TicketFactory.create_confirmed_ticket(pnr, passenger, seat)
                    booking.add_ticket(ticket)

            except SeatNotAvailableException as e:
                # Handle partial availability or waiting list
                available_count = len(train.get_available_seats(seat_type))

                if available_count > 0:
                    # Book available seats as confirmed
                    seats = train.book_seats(seat_type, available_count)
                    for i, (passenger, seat) in enumerate(zip(passengers[:available_count], seats)):
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

            # Process payment
            total_amount = booking.calculate_total()
            payment_success = payment_processor.process_payment(total_amount, payment_details)

            if not payment_success:
                # Rollback - release seats
                for ticket in booking.tickets:
                    if ticket.seat:
                        ticket.seat.release()
                raise PaymentFailedException("Payment processing failed")

            # Confirm booking
            booking.confirm_booking()

            # Store booking
            self.bookings[pnr] = booking

            # Notify
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
        """
        with self.lock:
            if pnr not in self.bookings:
                raise InvalidPNRException(f"PNR {pnr} not found")

            booking = self.bookings[pnr]

            if booking.status == BookingStatus.CANCELLED:
                raise BookingException("Booking already cancelled")

            # Release seats
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


# ============================================================================
# SEARCH SERVICE
# ============================================================================

class SearchService:
    """
    Service for searching trains.
    Demonstrates: SRP - handles only search functionality
    """

    def __init__(self):
        self.trains: Dict[str, Train] = {}

    def add_train(self, train: Train):
        """Add a train to the system"""
        self.trains[train.train_no] = train

    def get_train_by_number(self, train_no: str) -> Optional[Train]:
        """Get train by train number"""
        return self.trains.get(train_no)

    def search_trains(self, source: Station, destination: Station, travel_date: date) -> List[Train]:
        """
        Search trains between source and destination.

        Args:
            source: Source station
            destination: Destination station
            travel_date: Date of travel

        Returns:
            List of available trains
        """
        # In real system, this would query database with route matching
        # For now, simple matching
        matching_trains = []
        for train in self.trains.values():
            if train.source.code == source.code and train.destination.code == destination.code:
                matching_trains.append(train)

        return matching_trains

    def display_train_availability(self, train: Train):
        """Display train availability summary"""
        print(f"\n{train}")
        print("-" * 60)
        summary = train.get_seat_availability_summary()
        for seat_type, availability in summary.items():
            print(f"{seat_type.code:10s} | Available: {availability['available']:3d} / {availability['total']:3d}")
        print("-" * 60)


# ============================================================================
# DEMO/TESTING
# ============================================================================

def demo_irctc_system():
    """Demonstrate the IRCTC system with sample usage"""

    print("\n" + "="*80)
    print(" IRCTC RAILWAY RESERVATION SYSTEM - DEMO ".center(80))
    print("="*80 + "\n")

    # Step 1: Create stations
    print("Step 1: Creating Stations...")
    delhi = Station("NDLS", "New Delhi", "Delhi")
    mumbai = Station("CSTM", "Mumbai Central", "Mumbai")
    print(f"  ✓ Created: {delhi}")
    print(f"  ✓ Created: {mumbai}")

    # Step 2: Create train
    print("\nStep 2: Creating Train...")
    rajdhani = Train("12301", "Rajdhani Express", delhi, mumbai)

    # Add seats
    rajdhani.add_seats_bulk(SeatType.AC_1, 20)
    rajdhani.add_seats_bulk(SeatType.AC_2, 30)
    rajdhani.add_seats_bulk(SeatType.AC_3, 50)
    rajdhani.add_seats_bulk(SeatType.SLEEPER, 100)
    rajdhani.add_seats_bulk(SeatType.GENERAL, 200)
    print(f"  ✓ Created: {rajdhani}")

    # Step 3: Setup search service
    print("\nStep 3: Setting up Search Service...")
    search_service = SearchService()
    search_service.add_train(rajdhani)
    print("  ✓ Search service initialized")

    # Step 4: Setup booking manager (Singleton)
    print("\nStep 4: Initializing Booking Manager (Singleton)...")
    booking_manager = BookingManager.get_instance()

    # Verify singleton
    booking_manager2 = BookingManager.get_instance()
    print(f"  ✓ Singleton verified: {booking_manager is booking_manager2}")

    # Step 5: Setup notification service (Observer pattern)
    print("\nStep 5: Setting up Notification Service (Observer Pattern)...")
    email_observer = EmailNotificationObserver()
    sms_observer = SMSNotificationObserver()
    booking_manager.notification_service.subscribe(email_observer)
    booking_manager.notification_service.subscribe(sms_observer)
    print("  ✓ Email and SMS observers subscribed")

    # Step 6: Search for trains
    print("\nStep 6: Searching for Trains...")
    available_trains = search_service.search_trains(delhi, mumbai, date.today())
    print(f"  ✓ Found {len(available_trains)} train(s)")

    for train in available_trains:
        search_service.display_train_availability(train)

    # Step 7: Create passengers
    print("\nStep 7: Creating Passengers...")
    passenger1 = Passenger("Rahul Kumar", 30, "M")
    passenger2 = Passenger("Priya Sharma", 28, "F")
    passengers = [passenger1, passenger2]
    for p in passengers:
        print(f"  ✓ {p}")

    # Step 8: Book tickets (Strategy pattern for payment)
    print("\nStep 8: Booking Tickets...")
    print("Payment Method: Credit Card (Strategy Pattern)")

    payment_processor = CreditCardPayment()  # Can swap with DebitCardPayment or UPIPayment
    payment_details = {'card_number': 'XXXX-XXXX-XXXX-1234'}
    contact_info = {'email': 'rahul@example.com', 'phone': '+91-9876543210'}

    try:
        booking = booking_manager.create_booking(
            train=rajdhani,
            passengers=passengers,
            travel_date=date.today(),
            seat_type=SeatType.AC_3,
            payment_processor=payment_processor,
            payment_details=payment_details,
            contact_info=contact_info
        )

        print("\n✓ BOOKING SUCCESSFUL!")
        print(booking.get_booking_summary())

    except BookingException as e:
        print(f"\n✗ BOOKING FAILED: {e}")

    # Step 9: Check booking status
    print("\nStep 9: Checking Booking Status...")
    pnr = booking.pnr
    retrieved_booking = booking_manager.get_booking(pnr)
    print(f"  ✓ Retrieved booking for PNR: {pnr}")
    print(f"  Status: {retrieved_booking.status.value}")

    # Step 10: Display updated availability
    print("\nStep 10: Updated Train Availability...")
    search_service.display_train_availability(rajdhani)

    # Step 11: Try booking when limited seats available
    print("\nStep 11: Testing Partial Availability (3 passengers, 1 seat left)...")
    # Book more seats to reduce availability
    dummy_passengers = [Passenger(f"Passenger{i}", 25, "M") for i in range(47)]
    for i in range(0, len(dummy_passengers), 2):
        batch = dummy_passengers[i:i+2]
        try:
            booking_manager.create_booking(
                train=rajdhani,
                passengers=batch,
                travel_date=date.today(),
                seat_type=SeatType.AC_3,
                payment_processor=CreditCardPayment(),
                payment_details={'card_number': 'XXXX'},
                contact_info=contact_info
            )
        except:
            pass

    print("Current AC_3 Availability:")
    available_ac3 = len(rajdhani.get_available_seats(SeatType.AC_3))
    print(f"  Available AC_3 seats: {available_ac3}")

    # Now book 3 passengers
    test_passengers = [
        Passenger("Alice", 25, "F"),
        Passenger("Bob", 30, "M"),
        Passenger("Charlie", 35, "M")
    ]

    try:
        partial_booking = booking_manager.create_booking(
            train=rajdhani,
            passengers=test_passengers,
            travel_date=date.today(),
            seat_type=SeatType.AC_3,
            payment_processor=UPIPayment(),  # Different payment method
            payment_details={'upi_id': 'alice@upi'},
            contact_info={'email': 'alice@example.com', 'phone': '+91-1234567890'}
        )

        print("\n✓ PARTIAL BOOKING CREATED!")
        print(partial_booking.get_booking_summary())

    except BookingException as e:
        print(f"\n✗ BOOKING FAILED: {e}")

    # Step 12: Cancel a booking
    print("\nStep 12: Cancelling a Booking...")
    try:
        booking_manager.cancel_booking(pnr, contact_info)
        cancelled_booking = booking_manager.get_booking(pnr)
        print(f"  ✓ Booking {pnr} status: {cancelled_booking.status.value}")

    except BookingException as e:
        print(f"  ✗ Cancellation failed: {e}")

    # Step 13: Final availability
    print("\nStep 13: Final Train Availability...")
    search_service.display_train_availability(rajdhani)

    print("\n" + "="*80)
    print(" DEMO COMPLETED ".center(80))
    print("="*80 + "\n")

    # Summary of patterns demonstrated
    print("DESIGN PATTERNS DEMONSTRATED:")
    print("  ✓ Singleton: BookingManager (single instance)")
    print("  ✓ Factory: TicketFactory (creating different ticket types)")
    print("  ✓ Strategy: PaymentProcessor (CreditCard, DebitCard, UPI)")
    print("  ✓ Observer: NotificationService (Email and SMS notifications)")
    print("\nSOLID PRINCIPLES DEMONSTRATED:")
    print("  ✓ SRP: Each class has single responsibility")
    print("  ✓ OCP: Open for extension (new payment methods, ticket types)")
    print("  ✓ LSP: Different payment strategies are substitutable")
    print("  ✓ ISP: Focused interfaces (PaymentProcessor, Observer)")
    print("  ✓ DIP: Depend on abstractions (PaymentProcessor interface)")


if __name__ == "__main__":
    demo_irctc_system()
