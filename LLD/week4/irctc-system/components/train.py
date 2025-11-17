"""
Train Management Components - IRCTC System

This module contains components for managing trains, stations, and seats.
Demonstrates Single Responsibility Principle and Composition patterns.

Classes:
    - Station: Represents a railway station
    - Seat: Manages individual seat state
    - Train: Manages train schedule and seat inventory
"""

from enum import Enum
from typing import List, Dict
from threading import Lock


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


# ============================================================================
# EXCEPTIONS
# ============================================================================

class BookingException(Exception):
    """Base exception for booking-related errors"""
    pass


class SeatNotAvailableException(BookingException):
    """Raised when requested seats are not available"""
    pass


# ============================================================================
# STATION
# ============================================================================

class Station:
    """
    Represents a railway station.

    Attributes:
        code: Unique station code (e.g., "NDLS" for New Delhi)
        name: Full station name
        city: City where station is located

    Design Note: Keeping station as a separate entity allows for future
    extensions like adding coordinates, facilities, platform counts, etc.
    """

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


# ============================================================================
# SEAT
# ============================================================================

class Seat:
    """
    Represents a seat in a train.

    Demonstrates: Single Responsibility Principle - manages only seat state.
    The seat doesn't know about bookings or trains, just its own status.

    Attributes:
        seat_number: Unique identifier for the seat (e.g., "A1", "1A-23")
        seat_type: Type/class of seat (SeatType enum)
        is_booked: Boolean indicating if seat is currently booked
        price: Price for this seat

    Thread Safety: Seat itself is not thread-safe. Thread safety is managed
    at the Train level which owns the seats.
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
        """
        Mark seat as booked.

        Raises:
            BookingException: If seat is already booked

        Design Note: We validate state before changing it. This prevents
        double-booking at the seat level, though train level also has checks.
        """
        if self.is_booked:
            raise BookingException(f"Seat {self.seat_number} is already booked")
        self.is_booked = True

    def release(self):
        """
        Release/unbook seat.

        Design Note: No validation needed here. It's okay to release an
        already available seat (idempotent operation).
        """
        self.is_booked = False

    def get_price(self) -> float:
        """Get seat price"""
        return self.price

    def __str__(self):
        status = "Booked" if self.is_booked else "Available"
        return f"Seat {self.seat_number} ({self.seat_type.code}) - {status}"


# ============================================================================
# TRAIN
# ============================================================================

class Train:
    """
    Represents a train with multiple seat types.

    Demonstrates:
        - Composition: Train "has" seats
        - SRP: Only manages train state and seat inventory
        - Thread Safety: Uses locks for concurrent access

    Attributes:
        train_no: Unique train number
        name: Train name
        source: Starting station (Station object)
        destination: End station (Station object)
        seats: Dictionary mapping SeatType to list of Seats
        lock: Threading lock for concurrent seat operations

    Thread Safety: All operations that modify seat state are protected
    by a lock to prevent race conditions during concurrent bookings.
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
        """
        Add a seat to the train.

        Args:
            seat: Seat object to add

        Design Note: No locking needed here as this is typically done during
        initialization before the train is available for booking.
        """
        self.seats[seat.seat_type].append(seat)

    def add_seats_bulk(self, seat_type: SeatType, count: int):
        """
        Add multiple seats of same type.

        Args:
            seat_type: Type of seats to add
            count: Number of seats to add

        This is a convenience method for initialization. Generates seat
        numbers automatically in the format "{TYPE}-{NUMBER}".
        """
        for i in range(count):
            seat_number = f"{seat_type.code}-{i+1}"
            self.add_seat(Seat(seat_number, seat_type))

    def get_available_seats(self, seat_type: SeatType) -> List[Seat]:
        """
        Get list of available (unbooked) seats for given type.

        Args:
            seat_type: Type of seats to query

        Returns:
            List of available Seat objects

        Thread Safety: Locked to ensure consistent snapshot of availability
        """
        with self.lock:
            return [seat for seat in self.seats[seat_type] if not seat.is_booked]

    def has_availability(self, seat_type: SeatType, count: int) -> bool:
        """
        Check if required number of seats are available.

        Args:
            seat_type: Type of seats needed
            count: Number of seats needed

        Returns:
            True if at least 'count' seats are available
        """
        available = self.get_available_seats(seat_type)
        return len(available) >= count

    def book_seats(self, seat_type: SeatType, count: int) -> List[Seat]:
        """
        Book specified number of seats.

        This is a thread-safe, atomic operation. Either all seats are booked
        or an exception is raised with no seats booked.

        Args:
            seat_type: Type of seats to book
            count: Number of seats needed

        Returns:
            List of booked Seat objects

        Raises:
            SeatNotAvailableException: If sufficient seats not available

        Thread Safety: The entire operation is locked to prevent race
        conditions. The check-then-modify operations happen atomically:
        1. Check availability
        2. Get available seats
        3. Book each seat

        All three steps happen under the same lock, preventing another thread
        from booking seats between our check and booking operations.
        """
        with self.lock:
            available_seats = self.get_available_seats(seat_type)

            if len(available_seats) < count:
                raise SeatNotAvailableException(
                    f"Only {len(available_seats)} seats available, {count} requested"
                )

            # Book the first 'count' available seats
            booked_seats = available_seats[:count]
            for seat in booked_seats:
                seat.book()

            return booked_seats

    def release_seats(self, seats: List[Seat]):
        """
        Release booked seats back to available pool.

        Args:
            seats: List of Seat objects to release

        Thread Safety: Locked to ensure atomic release operation.
        This is crucial for rollback scenarios during payment failures.
        """
        with self.lock:
            for seat in seats:
                seat.release()

    def get_seat_availability_summary(self) -> Dict[SeatType, int]:
        """
        Get availability count for all seat types.

        Returns:
            Dictionary mapping SeatType to availability data:
            {
                SeatType.AC_1: {"available": 10, "total": 20},
                ...
            }

        Design Note: Provides a high-level view without exposing internal
        seat objects. Useful for display purposes.
        """
        summary = {}
        for seat_type in SeatType:
            available = len(self.get_available_seats(seat_type))
            total = len(self.seats[seat_type])
            summary[seat_type] = {"available": available, "total": total}
        return summary

    def __str__(self):
        return f"Train {self.train_no} - {self.name} ({self.source.code} → {self.destination.code})"


# ============================================================================
# DRY RUN EXAMPLE
# ============================================================================

def dry_run_train_booking():
    """
    Demonstrate train and seat operations with execution trace.

    This shows the step-by-step flow of creating a train, adding seats,
    and booking seats with state changes at each step.
    """
    print("\n" + "="*70)
    print(" DRY RUN: Train Booking Operations ".center(70))
    print("="*70 + "\n")

    # Step 1: Create stations
    print("Step 1: Create Stations")
    print("-" * 70)
    delhi = Station("NDLS", "New Delhi", "Delhi")
    mumbai = Station("CSTM", "Mumbai Central", "Mumbai")
    print(f"Created: {delhi}")
    print(f"Created: {mumbai}")
    print(f"\nState: 2 station objects in memory")
    print()

    # Step 2: Create train
    print("Step 2: Create Train")
    print("-" * 70)
    rajdhani = Train("12301", "Rajdhani Express", delhi, mumbai)
    print(f"Created: {rajdhani}")
    print(f"\nState: Train object with empty seat dictionary")
    print(f"  seats = {{")
    for seat_type in SeatType:
        print(f"    {seat_type.code}: []")
    print(f"  }}")
    print()

    # Step 3: Add seats
    print("Step 3: Add Seats")
    print("-" * 70)
    print("Adding 5 AC-3 seats...")
    rajdhani.add_seats_bulk(SeatType.AC_3, 5)
    print(f"\nState after adding seats:")
    print(f"  seats[AC_3] = [")
    for seat in rajdhani.seats[SeatType.AC_3]:
        print(f"    {seat}")
    print(f"  ]")
    print()

    # Step 4: Check availability
    print("Step 4: Check Availability")
    print("-" * 70)
    has_seats = rajdhani.has_availability(SeatType.AC_3, 3)
    print(f"Query: rajdhani.has_availability(AC_3, 3)")
    print(f"Process:")
    print(f"  1. Get available seats for AC_3")
    print(f"  2. Count = {len(rajdhani.get_available_seats(SeatType.AC_3))}")
    print(f"  3. Compare: 5 >= 3")
    print(f"Result: {has_seats}")
    print()

    # Step 5: Book seats
    print("Step 5: Book 3 Seats")
    print("-" * 70)
    print("Calling: rajdhani.book_seats(AC_3, 3)")
    print("\nExecution trace:")
    print("  1. Acquire lock")
    print("  2. Get available seats: [3A-1, 3A-2, 3A-3, 3A-4, 3A-5]")
    print("  3. Check: len(available) >= 3? True")
    print("  4. Select first 3: [3A-1, 3A-2, 3A-3]")
    print("  5. For each seat:")
    print("       - Check seat.is_booked == False")
    print("       - Set seat.is_booked = True")
    print("  6. Release lock")
    print("  7. Return booked seats")

    booked_seats = rajdhani.book_seats(SeatType.AC_3, 3)

    print(f"\nReturned seats: {[s.seat_number for s in booked_seats]}")
    print(f"\nState after booking:")
    print(f"  seats[AC_3] = [")
    for seat in rajdhani.seats[SeatType.AC_3]:
        print(f"    {seat}")
    print(f"  ]")
    print()

    # Step 6: Check availability again
    print("Step 6: Check Availability Again")
    print("-" * 70)
    available = rajdhani.get_available_seats(SeatType.AC_3)
    print(f"Available seats: {[s.seat_number for s in available]}")
    print(f"Count: {len(available)}")
    print()

    # Step 7: Try to overbook
    print("Step 7: Attempt to Overbook")
    print("-" * 70)
    print("Calling: rajdhani.book_seats(AC_3, 3)")
    print("Available: 2, Requested: 3")
    print("\nExecution trace:")
    print("  1. Acquire lock")
    print("  2. Get available seats: [3A-4, 3A-5]")
    print("  3. Check: len(available) >= 3? False")
    print("  4. Raise SeatNotAvailableException")
    print("  5. Release lock (via context manager)")

    try:
        rajdhani.book_seats(SeatType.AC_3, 3)
    except SeatNotAvailableException as e:
        print(f"\nException caught: {e}")

    print(f"\nState remains unchanged (no partial booking)")
    print()

    # Step 8: Release seats
    print("Step 8: Release Seats (Cancellation)")
    print("-" * 70)
    print(f"Releasing seats: {[s.seat_number for s in booked_seats]}")
    print("\nExecution trace:")
    print("  1. Acquire lock")
    print("  2. For each seat:")
    print("       - Set seat.is_booked = False")
    print("  3. Release lock")

    rajdhani.release_seats(booked_seats)

    print(f"\nState after release:")
    available = rajdhani.get_available_seats(SeatType.AC_3)
    print(f"Available seats: {[s.seat_number for s in available]}")
    print(f"Count: {len(available)}")
    print()

    print("="*70)
    print(" DRY RUN COMPLETE ".center(70))
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run dry run example
    dry_run_train_booking()
