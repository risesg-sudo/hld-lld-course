"""
Booking Management Components - IRCTC System

This module contains components for managing bookings, passengers, and tickets.
Demonstrates Singleton, Factory patterns and SOLID principles.

Classes:
    - Passenger: Represents a passenger with validation
    - Ticket: Represents a ticket for one passenger
    - Booking: Manages a complete booking with multiple tickets
    - TicketFactory: Factory for creating different ticket types
    - BookingManager: Singleton controller for all bookings
    - SearchService: Service for searching trains
"""

from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime, date
from threading import Lock
import random
import string

# Import from train module
from train import Train, Seat, SeatType, Station, BookingException, SeatNotAvailableException


# ============================================================================
# ENUMERATIONS
# ============================================================================

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

class InvalidPNRException(BookingException):
    """Raised when PNR is invalid"""
    pass


class PaymentFailedException(BookingException):
    """Raised when payment processing fails"""
    pass


# ============================================================================
# PASSENGER
# ============================================================================

class Passenger:
    """
    Represents a passenger.

    Demonstrates: SRP - manages only passenger data and validation.

    Attributes:
        passenger_id: Auto-generated unique ID
        name: Passenger name
        age: Passenger age
        gender: Gender (M/F/O)

    Design Note: Even though passenger data is simple, having a separate
    class allows for future extensions (loyalty programs, preferences, etc.)
    and keeps validation logic centralized.
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
        """
        Validate passenger data.

        Returns:
            True if data is valid, False otherwise

        Validation Rules:
            - Name must be non-empty
            - Age must be between 0 and 120
            - Gender must be M, F, or O
        """
        if not self.name or len(self.name.strip()) == 0:
            return False
        if self.age < 0 or self.age > 120:
            return False
        if self.gender not in ['M', 'F', 'O']:
            return False
        return True

    def __str__(self):
        return f"{self.name} ({self.age}{self.gender})"


# ============================================================================
# TICKET
# ============================================================================

class Ticket:
    """
    Represents a ticket for one passenger.

    Demonstrates: LSP - different ticket types are substitutable.

    Attributes:
        ticket_id: Unique ticket ID
        pnr: PNR of the booking
        passenger: Passenger object
        seat: Allocated seat (None for waiting list)
        status: Ticket status (TicketStatus enum)

    Design Note: A ticket is always associated with a booking (via PNR)
    and a passenger. The seat can be None for waiting list tickets.
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


# ============================================================================
# BOOKING
# ============================================================================

class Booking:
    """
    Represents a complete booking with multiple tickets.

    Demonstrates: SRP - manages only booking lifecycle.
    Aggregation - Booking "has" Tickets.

    Attributes:
        pnr: Unique PNR (Passenger Name Record)
        train: Train for journey
        passengers: List of passengers
        tickets: List of tickets (one per passenger)
        booking_date: When booking was made
        travel_date: Date of journey
        total_amount: Total cost
        status: Booking status

    Design Note: A booking aggregates multiple tickets. If booking is
    cancelled, all its tickets are cancelled too.
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
        """
        Add a ticket to booking.

        Also updates total amount if ticket has a seat.
        """
        self.tickets.append(ticket)
        if ticket.seat:
            self.total_amount += ticket.seat.get_price()

    def calculate_total(self) -> float:
        """Calculate total booking amount"""
        return self.total_amount

    def confirm_booking(self):
        """Confirm the booking and all its tickets"""
        self.status = BookingStatus.CONFIRMED
        for ticket in self.tickets:
            if ticket.status != TicketStatus.CANCELLED:
                ticket.confirm()

    def cancel_booking(self):
        """Cancel the booking and all its tickets"""
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
        summary += f"Total Amount: Rs. {self.total_amount}\n"
        summary += f"\nPassengers:\n"
        summary += f"{'-'*60}\n"
        for ticket in self.tickets:
            summary += f"  {ticket}\n"
        summary += f"{'='*60}\n"
        return summary

    def __str__(self):
        return f"Booking {self.pnr} - {self.status.value} - {len(self.tickets)} tickets"


# ============================================================================
# FACTORY PATTERN
# ============================================================================

class TicketFactory:
    """
    Factory pattern for creating different types of tickets.

    Demonstrates: Factory Pattern, OCP (can add new ticket types easily).

    Why Factory?:
    - Encapsulates ticket creation logic
    - Makes it easy to add new ticket types without modifying client code
    - Hides complexity of different ticket configurations

    Design Note: Static methods used as we don't need factory state.
    """

    @staticmethod
    def create_confirmed_ticket(pnr: str, passenger: Passenger, seat: Seat) -> Ticket:
        """Create a confirmed ticket with allocated seat"""
        return Ticket(pnr, passenger, seat, TicketStatus.CONFIRMED)

    @staticmethod
    def create_rac_ticket(pnr: str, passenger: Passenger, seat: Seat) -> Ticket:
        """Create a RAC (Reservation Against Cancellation) ticket"""
        return Ticket(pnr, passenger, seat, TicketStatus.RAC)

    @staticmethod
    def create_waiting_ticket(pnr: str, passenger: Passenger) -> Ticket:
        """Create a waiting list ticket (no seat allocated)"""
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
# SEARCH SERVICE
# ============================================================================

class SearchService:
    """
    Service for searching trains.

    Demonstrates: SRP - handles only search functionality.
    Doesn't modify bookings or handle payments.

    Attributes:
        trains: Dictionary of train_no to Train objects

    Design Note: Separating search from booking keeps concerns separated
    and makes the code more maintainable.
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

        Design Note: In a real system, this would query a database with
        complex route matching (intermediate stations, availability calendar).
        For this implementation, we do simple source-destination matching.
        """
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
            available = availability['available']
            total = availability['total']
            print(f"{seat_type.code:10s} | Available: {available:3d} / {total:3d}")
        print("-" * 60)
