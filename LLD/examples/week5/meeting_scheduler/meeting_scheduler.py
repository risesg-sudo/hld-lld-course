"""
Meeting Scheduler System - Low Level Design Implementation

This module implements a comprehensive meeting scheduler system with:
- Meeting creation and management
- Conflict detection with multiple strategies
- Room booking with different selection strategies
- Multi-calendar support
- Recurring meetings
- Notification system with Observer pattern

Design Patterns:
- Strategy Pattern: Conflict detection and room booking strategies
- Observer Pattern: Notification system
- Composite Pattern: Time slot finding
- Facade Pattern: MeetingScheduler main interface

Author: LLD Course
Week: 5 - Advanced System Designs
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
from collections import defaultdict
import uuid


# ============================================================================
# ENUMS AND VALUE OBJECTS
# ============================================================================

class MeetingStatus(Enum):
    """Status of a meeting"""
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"


class ResponseStatus(Enum):
    """Participant response to meeting invitation"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    TENTATIVE = "tentative"


class CalendarType(Enum):
    """Type of calendar"""
    WORK = "work"
    PERSONAL = "personal"
    SHARED = "shared"


class RecurrencePattern(Enum):
    """Pattern for recurring meetings"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class NotificationEventType(Enum):
    """Types of notification events"""
    MEETING_INVITED = "meeting_invited"
    MEETING_UPDATED = "meeting_updated"
    MEETING_CANCELLED = "meeting_cancelled"
    MEETING_REMINDER = "meeting_reminder"
    RESPONSE_RECEIVED = "response_received"


class TimeSlot:
    """Represents a time slot"""

    def __init__(self, start_time: datetime, end_time: datetime):
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")

        self.start_time = start_time
        self.end_time = end_time

    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Check if this slot overlaps with another"""
        return (self.start_time < other.end_time and
                self.end_time > other.start_time)

    def duration(self) -> timedelta:
        """Get duration of the time slot"""
        return self.end_time - self.start_time

    def contains(self, dt: datetime) -> bool:
        """Check if datetime is within this slot"""
        return self.start_time <= dt < self.end_time

    def __repr__(self) -> str:
        return f"TimeSlot({self.start_time} - {self.end_time})"


# ============================================================================
# CORE ENTITIES
# ============================================================================

class User:
    """Represents a user in the system"""

    def __init__(self, user_id: str, name: str, email: str, time_zone: str = "UTC"):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.time_zone = time_zone
        self.calendars: List['Calendar'] = []
        self.working_hours: Dict[int, Tuple[int, int]] = {
            i: (9, 17) for i in range(5)  # Monday-Friday, 9 AM - 5 PM
        }

    def add_calendar(self, calendar: 'Calendar') -> None:
        """Add a calendar to the user"""
        self.calendars.append(calendar)

    def get_availability(self, start: datetime, end: datetime) -> List[TimeSlot]:
        """Get user's available time slots in the given range"""
        # Collect all busy times from all calendars
        busy_times: List[TimeSlot] = []

        for calendar in self.calendars:
            meetings = calendar.get_meetings_in_range(start, end)
            for meeting in meetings:
                if meeting.status != MeetingStatus.CANCELLED:
                    busy_times.append(TimeSlot(meeting.start_time, meeting.end_time))

        # Find free slots (simplified - actual implementation would be more complex)
        free_slots: List[TimeSlot] = []
        current = start

        # Sort busy times
        busy_times.sort(key=lambda x: x.start_time)

        for busy in busy_times:
            if current < busy.start_time:
                free_slots.append(TimeSlot(current, busy.start_time))
            current = max(current, busy.end_time)

        if current < end:
            free_slots.append(TimeSlot(current, end))

        return free_slots

    def is_available(self, start: datetime, end: datetime) -> bool:
        """Check if user is available during the given time"""
        for calendar in self.calendars:
            meetings = calendar.get_meetings_in_range(start, end)
            for meeting in meetings:
                if meeting.status != MeetingStatus.CANCELLED:
                    slot = TimeSlot(meeting.start_time, meeting.end_time)
                    if slot.overlaps_with(TimeSlot(start, end)):
                        return False
        return True

    def __repr__(self) -> str:
        return f"User(id={self.user_id}, name={self.name})"


class Calendar:
    """Represents a calendar that contains meetings"""

    def __init__(self, calendar_id: str, name: str, owner: User,
                 calendar_type: CalendarType = CalendarType.WORK):
        self.calendar_id = calendar_id
        self.name = name
        self.owner = owner
        self.calendar_type = calendar_type
        self.meetings: List['Meeting'] = []

    def add_meeting(self, meeting: 'Meeting') -> None:
        """Add a meeting to the calendar"""
        self.meetings.append(meeting)

    def remove_meeting(self, meeting: 'Meeting') -> None:
        """Remove a meeting from the calendar"""
        if meeting in self.meetings:
            self.meetings.remove(meeting)

    def get_meetings_in_range(self, start: datetime, end: datetime) -> List['Meeting']:
        """Get all meetings within a time range"""
        return [
            meeting for meeting in self.meetings
            if (meeting.start_time < end and meeting.end_time > start)
        ]

    def find_free_slots(self, start: datetime, end: datetime,
                       duration: timedelta) -> List[TimeSlot]:
        """Find free time slots of given duration"""
        busy_times = [
            TimeSlot(m.start_time, m.end_time)
            for m in self.get_meetings_in_range(start, end)
            if m.status != MeetingStatus.CANCELLED
        ]

        busy_times.sort(key=lambda x: x.start_time)

        free_slots: List[TimeSlot] = []
        current = start

        for busy in busy_times:
            if current < busy.start_time:
                gap = busy.start_time - current
                if gap >= duration:
                    free_slots.append(TimeSlot(current, busy.start_time))
            current = max(current, busy.end_time)

        if end - current >= duration:
            free_slots.append(TimeSlot(current, end))

        return free_slots

    def __repr__(self) -> str:
        return f"Calendar(id={self.calendar_id}, name={self.name}, type={self.calendar_type})"


class Participant:
    """Represents a participant in a meeting"""

    def __init__(self, user: User, is_optional: bool = False):
        self.user = user
        self.response = ResponseStatus.PENDING
        self.is_optional = is_optional
        self.responded_at: Optional[datetime] = None

    def accept(self) -> None:
        """Accept the meeting invitation"""
        self.response = ResponseStatus.ACCEPTED
        self.responded_at = datetime.now()

    def decline(self) -> None:
        """Decline the meeting invitation"""
        self.response = ResponseStatus.DECLINED
        self.responded_at = datetime.now()

    def tentative(self) -> None:
        """Mark response as tentative"""
        self.response = ResponseStatus.TENTATIVE
        self.responded_at = datetime.now()

    def __repr__(self) -> str:
        return f"Participant(user={self.user.name}, response={self.response.value})"


class Room:
    """Represents a meeting room"""

    def __init__(self, room_id: str, name: str, capacity: int,
                 floor: int, building: str = "Main"):
        self.room_id = room_id
        self.name = name
        self.capacity = capacity
        self.floor = floor
        self.building = building
        self.amenities: List[str] = []
        self.bookings: List[TimeSlot] = []

    def add_amenity(self, amenity: str) -> None:
        """Add an amenity to the room"""
        self.amenities.append(amenity)

    def is_available(self, start: datetime, end: datetime) -> bool:
        """Check if room is available during the given time"""
        requested_slot = TimeSlot(start, end)
        return not any(booking.overlaps_with(requested_slot) for booking in self.bookings)

    def book(self, start: datetime, end: datetime) -> bool:
        """Book the room for the given time"""
        if self.is_available(start, end):
            self.bookings.append(TimeSlot(start, end))
            return True
        return False

    def release(self, start: datetime, end: datetime) -> None:
        """Release a booking"""
        self.bookings = [
            booking for booking in self.bookings
            if not (booking.start_time == start and booking.end_time == end)
        ]

    def __repr__(self) -> str:
        return f"Room(id={self.room_id}, name={self.name}, capacity={self.capacity})"


class Recurrence:
    """Represents recurrence pattern for meetings"""

    def __init__(self, pattern: RecurrencePattern, frequency: int = 1,
                 end_date: Optional[datetime] = None, occurrences: Optional[int] = None):
        self.pattern = pattern
        self.frequency = frequency
        self.end_date = end_date
        self.occurrences = occurrences
        self.days_of_week: Optional[List[int]] = None  # For weekly pattern

    def generate_instances(self, base_start: datetime,
                          base_end: datetime) -> List[Tuple[datetime, datetime]]:
        """Generate all meeting instances based on recurrence pattern"""
        instances: List[Tuple[datetime, datetime]] = []
        duration = base_end - base_start

        current_start = base_start
        count = 0

        while True:
            # Check termination conditions
            if self.end_date and current_start > self.end_date:
                break
            if self.occurrences and count >= self.occurrences:
                break

            instances.append((current_start, current_start + duration))
            count += 1

            # Calculate next occurrence
            if self.pattern == RecurrencePattern.DAILY:
                current_start += timedelta(days=self.frequency)
            elif self.pattern == RecurrencePattern.WEEKLY:
                current_start += timedelta(weeks=self.frequency)
            elif self.pattern == RecurrencePattern.MONTHLY:
                # Simplified monthly recurrence
                month = current_start.month + self.frequency
                year = current_start.year
                while month > 12:
                    month -= 12
                    year += 1
                current_start = current_start.replace(year=year, month=month)
            elif self.pattern == RecurrencePattern.YEARLY:
                current_start = current_start.replace(year=current_start.year + self.frequency)

        return instances

    def get_next_occurrence(self, after: datetime) -> Optional[datetime]:
        """Get next occurrence after given datetime"""
        # Simplified implementation
        if self.pattern == RecurrencePattern.DAILY:
            return after + timedelta(days=self.frequency)
        elif self.pattern == RecurrencePattern.WEEKLY:
            return after + timedelta(weeks=self.frequency)
        return None


class Meeting:
    """Represents a meeting"""

    def __init__(self, title: str, organizer: User, start_time: datetime,
                 end_time: datetime, description: str = ""):
        self.meeting_id = str(uuid.uuid4())
        self.title = title
        self.organizer = organizer
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.participants: List[Participant] = []
        self.room: Optional[Room] = None
        self.recurrence: Optional[Recurrence] = None
        self.status = MeetingStatus.SCHEDULED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_participant(self, participant: Participant) -> None:
        """Add a participant to the meeting"""
        self.participants.append(participant)

    def remove_participant(self, user_id: str) -> None:
        """Remove a participant from the meeting"""
        self.participants = [
            p for p in self.participants if p.user.user_id != user_id
        ]

    def update_time(self, start_time: datetime, end_time: datetime) -> None:
        """Update meeting time"""
        self.start_time = start_time
        self.end_time = end_time
        self.updated_at = datetime.now()

    def cancel(self) -> None:
        """Cancel the meeting"""
        self.status = MeetingStatus.CANCELLED
        self.updated_at = datetime.now()

        # Release room booking
        if self.room:
            self.room.release(self.start_time, self.end_time)

    def is_conflicting(self, other: 'Meeting') -> bool:
        """Check if this meeting conflicts with another"""
        # Check time overlap
        time_overlap = (self.start_time < other.end_time and
                       self.end_time > other.start_time)

        if not time_overlap:
            return False

        # Check if any participant is in both meetings
        self_participants = {p.user.user_id for p in self.participants}
        other_participants = {p.user.user_id for p in other.participants}

        return bool(self_participants & other_participants)

    def get_accepted_participants(self) -> List[Participant]:
        """Get list of participants who accepted"""
        return [p for p in self.participants if p.response == ResponseStatus.ACCEPTED]

    def get_required_capacity(self) -> int:
        """Get required room capacity"""
        return len(self.participants) + 1  # participants + organizer

    def __repr__(self) -> str:
        return f"Meeting(id={self.meeting_id}, title={self.title}, time={self.start_time})"


# ============================================================================
# CONFLICT DETECTION STRATEGIES (Strategy Pattern)
# ============================================================================

class Conflict:
    """Represents a scheduling conflict"""

    def __init__(self, meeting1: Meeting, meeting2: Meeting,
                 conflicting_users: Set[str]):
        self.meeting1 = meeting1
        self.meeting2 = meeting2
        self.conflicting_users = conflicting_users

    def __repr__(self) -> str:
        return (f"Conflict({self.meeting1.title} conflicts with {self.meeting2.title} "
               f"for {len(self.conflicting_users)} users)")


class ConflictDetectionStrategy(ABC):
    """Abstract strategy for conflict detection"""

    @abstractmethod
    def detect_conflicts(self, meeting: Meeting,
                        calendars: List[Calendar]) -> List[Conflict]:
        """Detect conflicts for a meeting"""
        pass

    @abstractmethod
    def suggest_alternatives(self, meeting: Meeting,
                           conflicts: List[Conflict]) -> List[TimeSlot]:
        """Suggest alternative time slots"""
        pass


class StrictConflictDetection(ConflictDetectionStrategy):
    """Strict conflict detection - no overlaps allowed"""

    def detect_conflicts(self, meeting: Meeting,
                        calendars: List[Calendar]) -> List[Conflict]:
        """Detect any time overlaps"""
        conflicts: List[Conflict] = []

        meeting_participants = {p.user.user_id for p in meeting.participants}
        meeting_slot = TimeSlot(meeting.start_time, meeting.end_time)

        for calendar in calendars:
            existing_meetings = calendar.get_meetings_in_range(
                meeting.start_time, meeting.end_time
            )

            for existing in existing_meetings:
                if existing.status == MeetingStatus.CANCELLED:
                    continue

                existing_slot = TimeSlot(existing.start_time, existing.end_time)
                if meeting_slot.overlaps_with(existing_slot):
                    existing_participants = {p.user.user_id for p in existing.participants}
                    conflicting = meeting_participants & existing_participants

                    if conflicting:
                        conflicts.append(Conflict(meeting, existing, conflicting))

        return conflicts

    def suggest_alternatives(self, meeting: Meeting,
                           conflicts: List[Conflict]) -> List[TimeSlot]:
        """Suggest alternative time slots"""
        duration = meeting.end_time - meeting.start_time

        # Look for slots in the next week
        search_start = meeting.start_time
        search_end = search_start + timedelta(days=7)

        # Simple suggestion: slots right after conflicts
        alternatives: List[TimeSlot] = []
        for conflict in conflicts[:3]:  # Top 3 conflicts
            alt_start = conflict.meeting2.end_time
            alt_end = alt_start + duration
            if alt_end <= search_end:
                alternatives.append(TimeSlot(alt_start, alt_end))

        return alternatives


class FlexibleConflictDetection(ConflictDetectionStrategy):
    """Flexible conflict detection - allow tentative meetings"""

    def detect_conflicts(self, meeting: Meeting,
                        calendars: List[Calendar]) -> List[Conflict]:
        """Detect conflicts but allow tentative meetings"""
        conflicts: List[Conflict] = []

        meeting_participants = {p.user.user_id for p in meeting.participants}
        meeting_slot = TimeSlot(meeting.start_time, meeting.end_time)

        for calendar in calendars:
            existing_meetings = calendar.get_meetings_in_range(
                meeting.start_time, meeting.end_time
            )

            for existing in existing_meetings:
                # Skip cancelled and tentative meetings
                if existing.status == MeetingStatus.CANCELLED:
                    continue

                # Check if all participants are tentative
                all_tentative = all(
                    p.response == ResponseStatus.TENTATIVE
                    for p in existing.participants
                )
                if all_tentative:
                    continue

                existing_slot = TimeSlot(existing.start_time, existing.end_time)
                if meeting_slot.overlaps_with(existing_slot):
                    existing_participants = {p.user.user_id for p in existing.participants}
                    conflicting = meeting_participants & existing_participants

                    # Only count as conflict if participants have accepted
                    accepted_conflicting = set()
                    for p in existing.participants:
                        if (p.user.user_id in conflicting and
                            p.response == ResponseStatus.ACCEPTED):
                            accepted_conflicting.add(p.user.user_id)

                    if accepted_conflicting:
                        conflicts.append(Conflict(meeting, existing, accepted_conflicting))

        return conflicts

    def suggest_alternatives(self, meeting: Meeting,
                           conflicts: List[Conflict]) -> List[TimeSlot]:
        """Suggest alternatives considering optional participants"""
        duration = meeting.end_time - meeting.start_time
        search_start = meeting.start_time
        search_end = search_start + timedelta(days=7)

        # Consider dropping optional participants
        alternatives: List[TimeSlot] = []

        # Suggestion 1: Same time, different day
        for days in range(1, 8):
            alt_start = meeting.start_time + timedelta(days=days)
            alt_end = alt_start + duration
            if alt_end <= search_end:
                alternatives.append(TimeSlot(alt_start, alt_end))

        return alternatives[:5]


# ============================================================================
# ROOM BOOKING STRATEGIES (Strategy Pattern)
# ============================================================================

class RoomRequirements:
    """Requirements for a meeting room"""

    def __init__(self, min_capacity: int, required_amenities: List[str] = None,
                 preferred_floor: Optional[int] = None,
                 preferred_building: str = "Main"):
        self.min_capacity = min_capacity
        self.required_amenities = required_amenities or []
        self.preferred_floor = preferred_floor
        self.preferred_building = preferred_building


class RoomBookingStrategy(ABC):
    """Abstract strategy for room booking"""

    @abstractmethod
    def select_room(self, available_rooms: List[Room],
                   requirements: RoomRequirements) -> Optional[Room]:
        """Select the best room from available options"""
        pass


class NearestRoomStrategy(RoomBookingStrategy):
    """Select the nearest room (by floor)"""

    def select_room(self, available_rooms: List[Room],
                   requirements: RoomRequirements) -> Optional[Room]:
        """Select room on preferred floor or nearest"""
        if not available_rooms:
            return None

        # Filter by requirements
        suitable = [
            room for room in available_rooms
            if room.capacity >= requirements.min_capacity and
            all(amenity in room.amenities for amenity in requirements.required_amenities)
        ]

        if not suitable:
            return None

        # Prefer requested floor
        if requirements.preferred_floor is not None:
            on_floor = [r for r in suitable if r.floor == requirements.preferred_floor]
            if on_floor:
                return on_floor[0]

            # Find nearest floor
            suitable.sort(key=lambda r: abs(r.floor - requirements.preferred_floor))

        return suitable[0]


class LargestRoomStrategy(RoomBookingStrategy):
    """Select the largest available room"""

    def select_room(self, available_rooms: List[Room],
                   requirements: RoomRequirements) -> Optional[Room]:
        """Select largest room that meets requirements"""
        if not available_rooms:
            return None

        # Filter by requirements
        suitable = [
            room for room in available_rooms
            if room.capacity >= requirements.min_capacity and
            all(amenity in room.amenities for amenity in requirements.required_amenities)
        ]

        if not suitable:
            return None

        # Sort by capacity (descending)
        suitable.sort(key=lambda r: r.capacity, reverse=True)
        return suitable[0]


class SmallestSuitableRoomStrategy(RoomBookingStrategy):
    """Select the smallest room that fits requirements (most efficient)"""

    def select_room(self, available_rooms: List[Room],
                   requirements: RoomRequirements) -> Optional[Room]:
        """Select smallest room that meets requirements"""
        if not available_rooms:
            return None

        # Filter by requirements
        suitable = [
            room for room in available_rooms
            if room.capacity >= requirements.min_capacity and
            all(amenity in room.amenities for amenity in requirements.required_amenities)
        ]

        if not suitable:
            return None

        # Sort by capacity (ascending)
        suitable.sort(key=lambda r: r.capacity)
        return suitable[0]


# ============================================================================
# ROOM MANAGER
# ============================================================================

class RoomManager:
    """Manages room booking and selection"""

    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.booking_strategy: RoomBookingStrategy = SmallestSuitableRoomStrategy()

    def add_room(self, room: Room) -> None:
        """Add a room to the system"""
        self.rooms[room.room_id] = room

    def set_booking_strategy(self, strategy: RoomBookingStrategy) -> None:
        """Set the room booking strategy"""
        self.booking_strategy = strategy

    def find_available_rooms(self, start: datetime, end: datetime,
                            requirements: RoomRequirements) -> List[Room]:
        """Find all available rooms matching requirements"""
        available = []

        for room in self.rooms.values():
            if room.is_available(start, end):
                # Check capacity and amenities
                if (room.capacity >= requirements.min_capacity and
                    all(amenity in room.amenities
                        for amenity in requirements.required_amenities)):
                    available.append(room)

        return available

    def book_room(self, meeting: Meeting,
                 requirements: RoomRequirements) -> Optional[Room]:
        """Book a room for a meeting"""
        available = self.find_available_rooms(
            meeting.start_time, meeting.end_time, requirements
        )

        if not available:
            return None

        # Use strategy to select best room
        selected = self.booking_strategy.select_room(available, requirements)

        if selected and selected.book(meeting.start_time, meeting.end_time):
            meeting.room = selected
            return selected

        return None

    def release_room(self, meeting: Meeting) -> None:
        """Release room booking"""
        if meeting.room:
            meeting.room.release(meeting.start_time, meeting.end_time)


# ============================================================================
# TIME SLOT FINDER (Composite Pattern)
# ============================================================================

class SlotFinder(ABC):
    """Abstract component for finding time slots"""

    @abstractmethod
    def find_slots(self, participants: List[User], duration: timedelta,
                  search_range: Tuple[datetime, datetime]) -> List[TimeSlot]:
        """Find available time slots"""
        pass


class WorkingHoursSlotFinder(SlotFinder):
    """Find slots within working hours"""

    def find_slots(self, participants: List[User], duration: timedelta,
                  search_range: Tuple[datetime, datetime]) -> List[TimeSlot]:
        """Find slots within all participants' working hours"""
        start, end = search_range
        slots: List[TimeSlot] = []

        current = start
        while current < end:
            # Check if time is within working hours for all
            hour = current.hour
            weekday = current.weekday()

            within_hours = all(
                weekday in user.working_hours and
                user.working_hours[weekday][0] <= hour < user.working_hours[weekday][1]
                for user in participants
            )

            if within_hours:
                slot_end = current + duration
                if slot_end <= end:
                    slots.append(TimeSlot(current, slot_end))

            current += timedelta(hours=1)

        return slots


class AvailabilitySlotFinder(SlotFinder):
    """Find slots when all participants are available"""

    def find_slots(self, participants: List[User], duration: timedelta,
                  search_range: Tuple[datetime, datetime]) -> List[TimeSlot]:
        """Find common free slots"""
        start, end = search_range

        if not participants:
            return []

        # Get availability for all participants
        all_availability = [
            user.get_availability(start, end) for user in participants
        ]

        # Find intersection of all availabilities
        common_slots: List[TimeSlot] = []

        # Start with first user's availability
        for slot in all_availability[0]:
            # Check if this slot works for all other participants
            works_for_all = True

            for user_slots in all_availability[1:]:
                # Check if there's an overlapping slot
                has_overlap = any(
                    slot.overlaps_with(user_slot) for user_slot in user_slots
                )
                if not has_overlap:
                    works_for_all = False
                    break

            if works_for_all and slot.duration() >= duration:
                common_slots.append(slot)

        return common_slots


class PreferenceSlotFinder(SlotFinder):
    """Find slots based on preferences (e.g., morning/afternoon)"""

    def __init__(self, prefer_morning: bool = True):
        self.prefer_morning = prefer_morning

    def find_slots(self, participants: List[User], duration: timedelta,
                  search_range: Tuple[datetime, datetime]) -> List[TimeSlot]:
        """Find slots in preferred time"""
        start, end = search_range
        slots: List[TimeSlot] = []

        current = start
        while current < end:
            hour = current.hour

            if self.prefer_morning:
                in_preference = 8 <= hour < 12
            else:
                in_preference = 13 <= hour < 17

            if in_preference:
                slot_end = current + duration
                if slot_end <= end:
                    slots.append(TimeSlot(current, slot_end))

            current += timedelta(hours=1)

        return slots


class TimeSlotFinderComposite(SlotFinder):
    """Composite slot finder combining multiple strategies"""

    def __init__(self):
        self.finders: List[SlotFinder] = []

    def add_finder(self, finder: SlotFinder) -> None:
        """Add a slot finder"""
        self.finders.append(finder)

    def find_slots(self, participants: List[User], duration: timedelta,
                  search_range: Tuple[datetime, datetime]) -> List[TimeSlot]:
        """Find slots using all finders and intersect results"""
        if not self.finders:
            return []

        # Get results from all finders
        all_results = [
            finder.find_slots(participants, duration, search_range)
            for finder in self.finders
        ]

        # Find intersection (slots that appear in all results)
        if not all_results:
            return []

        # Start with first result
        common = set((slot.start_time, slot.end_time) for slot in all_results[0])

        # Intersect with all other results
        for results in all_results[1:]:
            result_set = set((slot.start_time, slot.end_time) for slot in results)
            common &= result_set

        # Convert back to TimeSlot objects
        return [TimeSlot(start, end) for start, end in sorted(common)]


# ============================================================================
# NOTIFICATION SYSTEM (Observer Pattern)
# ============================================================================

class NotificationEvent:
    """Event for notifications"""

    def __init__(self, event_type: NotificationEventType, data: Dict):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()


class NotificationObserver(ABC):
    """Abstract observer for notifications"""

    @abstractmethod
    def update(self, event: NotificationEvent) -> None:
        """Handle notification event"""
        pass


class EmailNotifier(NotificationObserver):
    """Email notification observer"""

    def __init__(self):
        self.sent_emails: List[str] = []

    def update(self, event: NotificationEvent) -> None:
        """Send email notification"""
        if event.event_type == NotificationEventType.MEETING_INVITED:
            to = event.data.get('to')
            meeting = event.data.get('meeting')
            email = f"Email to {to}: You're invited to '{meeting.title}' at {meeting.start_time}"
            self.sent_emails.append(email)
            print(f"[EMAIL] {email}")

        elif event.event_type == NotificationEventType.MEETING_CANCELLED:
            meeting = event.data.get('meeting')
            participants = event.data.get('participants', [])
            for participant in participants:
                email = f"Email to {participant}: Meeting '{meeting.title}' has been cancelled"
                self.sent_emails.append(email)
                print(f"[EMAIL] {email}")

        elif event.event_type == NotificationEventType.MEETING_REMINDER:
            to = event.data.get('to')
            meeting = event.data.get('meeting')
            email = f"Email to {to}: Reminder - '{meeting.title}' in 15 minutes"
            self.sent_emails.append(email)
            print(f"[EMAIL] {email}")


class SMSNotifier(NotificationObserver):
    """SMS notification observer"""

    def __init__(self):
        self.sent_sms: List[str] = []

    def update(self, event: NotificationEvent) -> None:
        """Send SMS notification"""
        if event.event_type == NotificationEventType.MEETING_REMINDER:
            to = event.data.get('to')
            meeting = event.data.get('meeting')
            sms = f"SMS to {to}: Meeting '{meeting.title}' starts in 15 min"
            self.sent_sms.append(sms)
            print(f"[SMS] {sms}")


class PushNotifier(NotificationObserver):
    """Push notification observer"""

    def __init__(self):
        self.sent_push: List[str] = []

    def update(self, event: NotificationEvent) -> None:
        """Send push notification"""
        if event.event_type in [NotificationEventType.MEETING_INVITED,
                               NotificationEventType.MEETING_UPDATED]:
            to = event.data.get('to')
            meeting = event.data.get('meeting')
            push = f"Push to {to}: Meeting update - {meeting.title}"
            self.sent_push.append(push)
            print(f"[PUSH] {push}")


class NotificationService:
    """Notification service managing observers"""

    def __init__(self):
        self._observers: List[NotificationObserver] = []

    def attach(self, observer: NotificationObserver) -> None:
        """Attach an observer"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: NotificationObserver) -> None:
        """Detach an observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: NotificationEvent) -> None:
        """Notify all observers"""
        for observer in self._observers:
            observer.update(event)

    def send_invitation(self, meeting: Meeting, participant: User) -> None:
        """Send meeting invitation"""
        event = NotificationEvent(
            NotificationEventType.MEETING_INVITED,
            {'meeting': meeting, 'to': participant.email}
        )
        self.notify(event)

    def send_reminder(self, meeting: Meeting, participant: User) -> None:
        """Send meeting reminder"""
        event = NotificationEvent(
            NotificationEventType.MEETING_REMINDER,
            {'meeting': meeting, 'to': participant.email}
        )
        self.notify(event)

    def send_cancellation(self, meeting: Meeting) -> None:
        """Send cancellation notification"""
        participants = [p.user.email for p in meeting.participants]
        event = NotificationEvent(
            NotificationEventType.MEETING_CANCELLED,
            {'meeting': meeting, 'participants': participants}
        )
        self.notify(event)

    def send_update(self, meeting: Meeting, participant: User) -> None:
        """Send update notification"""
        event = NotificationEvent(
            NotificationEventType.MEETING_UPDATED,
            {'meeting': meeting, 'to': participant.email}
        )
        self.notify(event)


# ============================================================================
# MEETING SCHEDULER (Facade Pattern)
# ============================================================================

class MeetingScheduler:
    """
    Main facade for the meeting scheduler system
    Provides simplified interface to complex subsystems
    """

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.calendars: Dict[str, Calendar] = {}
        self.meetings: Dict[str, Meeting] = {}
        self.room_manager = RoomManager()
        self.notification_service = NotificationService()
        self.conflict_detector: ConflictDetectionStrategy = StrictConflictDetection()

    # ========================================================================
    # User Management
    # ========================================================================

    def add_user(self, user: User) -> None:
        """Add a user to the system"""
        self.users[user.user_id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)

    # ========================================================================
    # Calendar Management
    # ========================================================================

    def create_calendar(self, user_id: str, name: str,
                       calendar_type: CalendarType = CalendarType.WORK) -> Optional[Calendar]:
        """Create a calendar for a user"""
        user = self.get_user(user_id)
        if not user:
            return None

        calendar_id = str(uuid.uuid4())
        calendar = Calendar(calendar_id, name, user, calendar_type)
        self.calendars[calendar_id] = calendar
        user.add_calendar(calendar)

        return calendar

    # ========================================================================
    # Room Management
    # ========================================================================

    def add_room(self, room: Room) -> None:
        """Add a room to the system"""
        self.room_manager.add_room(room)

    def set_room_booking_strategy(self, strategy: RoomBookingStrategy) -> None:
        """Set room booking strategy"""
        self.room_manager.set_booking_strategy(strategy)

    # ========================================================================
    # Conflict Detection
    # ========================================================================

    def set_conflict_detection_strategy(self,
                                       strategy: ConflictDetectionStrategy) -> None:
        """Set conflict detection strategy"""
        self.conflict_detector = strategy

    # ========================================================================
    # Meeting Management
    # ========================================================================

    def create_meeting(self, title: str, organizer_id: str,
                      start_time: datetime, end_time: datetime,
                      participant_ids: List[str],
                      description: str = "",
                      room_requirements: Optional[RoomRequirements] = None,
                      calendar_id: Optional[str] = None) -> Optional[Meeting]:
        """
        Create a new meeting

        Args:
            title: Meeting title
            organizer_id: User ID of organizer
            start_time: Meeting start time
            end_time: Meeting end time
            participant_ids: List of participant user IDs
            description: Meeting description
            room_requirements: Room requirements
            calendar_id: Calendar to add meeting to (default: first calendar)

        Returns:
            Created meeting or None if creation failed
        """
        # Get organizer
        organizer = self.get_user(organizer_id)
        if not organizer:
            print(f"Error: Organizer {organizer_id} not found")
            return None

        # Create meeting
        meeting = Meeting(title, organizer, start_time, end_time, description)

        # Add participants
        for participant_id in participant_ids:
            user = self.get_user(participant_id)
            if user:
                participant = Participant(user)
                meeting.add_participant(participant)

        # Check conflicts
        all_calendars = [cal for user in self.users.values() for cal in user.calendars]
        conflicts = self.conflict_detector.detect_conflicts(meeting, all_calendars)

        if conflicts:
            print(f"Warning: {len(conflicts)} conflicts detected")
            for conflict in conflicts[:3]:  # Show first 3
                print(f"  - {conflict}")

        # Book room if required
        if room_requirements:
            room = self.room_manager.book_room(meeting, room_requirements)
            if room:
                print(f"Room booked: {room.name}")
            else:
                print("Warning: No room available")

        # Add to calendar
        if calendar_id:
            calendar = self.calendars.get(calendar_id)
        else:
            calendar = organizer.calendars[0] if organizer.calendars else None

        if calendar:
            calendar.add_meeting(meeting)

        # Store meeting
        self.meetings[meeting.meeting_id] = meeting

        # Send invitations
        for participant in meeting.participants:
            self.notification_service.send_invitation(meeting, participant.user)

        return meeting

    def update_meeting(self, meeting_id: str, start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> bool:
        """Update a meeting"""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return False

        if start_time and end_time:
            # Release old room booking
            if meeting.room:
                self.room_manager.release_room(meeting)

            # Update time
            meeting.update_time(start_time, end_time)

            # Re-book room
            if meeting.room:
                requirements = RoomRequirements(
                    min_capacity=meeting.get_required_capacity()
                )
                self.room_manager.book_room(meeting, requirements)

            # Notify participants
            for participant in meeting.participants:
                self.notification_service.send_update(meeting, participant.user)

        return True

    def cancel_meeting(self, meeting_id: str) -> bool:
        """Cancel a meeting"""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return False

        meeting.cancel()

        # Send notifications
        self.notification_service.send_cancellation(meeting)

        return True

    def respond_to_meeting(self, meeting_id: str, user_id: str,
                          response: ResponseStatus) -> bool:
        """Respond to a meeting invitation"""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return False

        # Find participant
        for participant in meeting.participants:
            if participant.user.user_id == user_id:
                if response == ResponseStatus.ACCEPTED:
                    participant.accept()
                elif response == ResponseStatus.DECLINED:
                    participant.decline()
                elif response == ResponseStatus.TENTATIVE:
                    participant.tentative()

                print(f"{participant.user.name} {response.value} meeting '{meeting.title}'")
                return True

        return False

    # ========================================================================
    # Time Slot Finding
    # ========================================================================

    def find_available_slots(self, participant_ids: List[str],
                           duration: timedelta,
                           search_days: int = 7) -> List[TimeSlot]:
        """Find available time slots for participants"""
        # Get participants
        participants = [self.get_user(uid) for uid in participant_ids]
        participants = [p for p in participants if p is not None]

        if not participants:
            return []

        # Create composite finder
        finder = TimeSlotFinderComposite()
        finder.add_finder(WorkingHoursSlotFinder())
        finder.add_finder(AvailabilitySlotFinder())
        finder.add_finder(PreferenceSlotFinder(prefer_morning=True))

        # Search range
        search_start = datetime.now()
        search_end = search_start + timedelta(days=search_days)

        # Find slots
        slots = finder.find_slots(participants, duration, (search_start, search_end))

        return slots[:10]  # Return top 10 slots

    # ========================================================================
    # Notification Management
    # ========================================================================

    def attach_notifier(self, observer: NotificationObserver) -> None:
        """Attach a notification observer"""
        self.notification_service.attach(observer)

    # ========================================================================
    # Statistics and Reporting
    # ========================================================================

    def get_statistics(self) -> Dict:
        """Get system statistics"""
        total_meetings = len(self.meetings)
        scheduled = sum(1 for m in self.meetings.values()
                       if m.status == MeetingStatus.SCHEDULED)
        cancelled = sum(1 for m in self.meetings.values()
                       if m.status == MeetingStatus.CANCELLED)

        return {
            'total_users': len(self.users),
            'total_calendars': len(self.calendars),
            'total_meetings': total_meetings,
            'scheduled_meetings': scheduled,
            'cancelled_meetings': cancelled,
            'total_rooms': len(self.room_manager.rooms)
        }


# ============================================================================
# DEMO AND TEST SCENARIOS
# ============================================================================

def demo_meeting_scheduler():
    """Comprehensive demo of the meeting scheduler system"""

    print("=" * 80)
    print("MEETING SCHEDULER SYSTEM DEMO")
    print("=" * 80)
    print()

    # ========================================================================
    # 1. Initialize System
    # ========================================================================
    print("1. Initializing Meeting Scheduler...")
    scheduler = MeetingScheduler()

    # Attach notification observers
    email_notifier = EmailNotifier()
    sms_notifier = SMSNotifier()
    push_notifier = PushNotifier()

    scheduler.attach_notifier(email_notifier)
    scheduler.attach_notifier(sms_notifier)
    scheduler.attach_notifier(push_notifier)
    print("   ✓ Notification observers attached")
    print()

    # ========================================================================
    # 2. Create Users
    # ========================================================================
    print("2. Creating Users...")
    users_data = [
        ("u1", "Alice Smith", "alice@company.com", "US/Pacific"),
        ("u2", "Bob Johnson", "bob@company.com", "US/Pacific"),
        ("u3", "Charlie Brown", "charlie@company.com", "US/Eastern"),
        ("u4", "Diana Prince", "diana@company.com", "US/Pacific"),
        ("u5", "Eve Wilson", "eve@company.com", "US/Pacific"),
    ]

    for user_id, name, email, timezone in users_data:
        user = User(user_id, name, email, timezone)
        scheduler.add_user(user)
        print(f"   ✓ Added {user}")
    print()

    # ========================================================================
    # 3. Create Calendars
    # ========================================================================
    print("3. Creating Calendars...")
    for user_id in ["u1", "u2", "u3", "u4", "u5"]:
        work_cal = scheduler.create_calendar(user_id, "Work", CalendarType.WORK)
        personal_cal = scheduler.create_calendar(user_id, "Personal", CalendarType.PERSONAL)
        user = scheduler.get_user(user_id)
        print(f"   ✓ Created calendars for {user.name}")
    print()

    # ========================================================================
    # 4. Add Meeting Rooms
    # ========================================================================
    print("4. Adding Meeting Rooms...")
    rooms_data = [
        ("r1", "Conference Room A", 10, 1, ["projector", "whiteboard"]),
        ("r2", "Conference Room B", 6, 1, ["projector"]),
        ("r3", "Board Room", 20, 2, ["projector", "whiteboard", "videoconf"]),
        ("r4", "Small Meeting Room", 4, 1, []),
        ("r5", "Training Room", 30, 3, ["projector", "whiteboard", "computers"]),
    ]

    for room_id, name, capacity, floor, amenities in rooms_data:
        room = Room(room_id, name, capacity, floor)
        for amenity in amenities:
            room.add_amenity(amenity)
        scheduler.add_room(room)
        print(f"   ✓ Added {room}")
    print()

    # ========================================================================
    # 5. Create a Simple Meeting
    # ========================================================================
    print("5. Creating a Simple Meeting...")
    print("-" * 80)

    start_time = datetime.now() + timedelta(hours=2)
    end_time = start_time + timedelta(hours=1)

    meeting1 = scheduler.create_meeting(
        title="Weekly Standup",
        organizer_id="u1",
        start_time=start_time,
        end_time=end_time,
        participant_ids=["u2", "u3"],
        description="Weekly team standup meeting",
        room_requirements=RoomRequirements(min_capacity=4, required_amenities=["projector"])
    )

    if meeting1:
        print(f"   ✓ Created: {meeting1}")
        print(f"     Room: {meeting1.room.name if meeting1.room else 'None'}")
        print(f"     Participants: {len(meeting1.participants)}")
    print()

    # ========================================================================
    # 6. Test Participant Responses
    # ========================================================================
    print("6. Testing Participant Responses...")
    print("-" * 80)

    scheduler.respond_to_meeting(meeting1.meeting_id, "u2", ResponseStatus.ACCEPTED)
    scheduler.respond_to_meeting(meeting1.meeting_id, "u3", ResponseStatus.TENTATIVE)
    print()

    # ========================================================================
    # 7. Create Conflicting Meeting (Test Conflict Detection)
    # ========================================================================
    print("7. Creating Conflicting Meeting...")
    print("-" * 80)

    meeting2 = scheduler.create_meeting(
        title="Project Review",
        organizer_id="u4",
        start_time=start_time,  # Same time as meeting1
        end_time=end_time,
        participant_ids=["u2", "u5"],  # u2 is in meeting1
        description="Review project progress",
        room_requirements=RoomRequirements(min_capacity=3)
    )

    if meeting2:
        print(f"   ✓ Created: {meeting2}")
    print()

    # ========================================================================
    # 8. Find Available Slots
    # ========================================================================
    print("8. Finding Available Time Slots...")
    print("-" * 80)

    available_slots = scheduler.find_available_slots(
        participant_ids=["u1", "u2", "u3"],
        duration=timedelta(hours=1),
        search_days=7
    )

    print(f"   Found {len(available_slots)} available slots:")
    for i, slot in enumerate(available_slots[:5], 1):
        print(f"   {i}. {slot}")
    print()

    # ========================================================================
    # 9. Test Different Room Booking Strategies
    # ========================================================================
    print("9. Testing Room Booking Strategies...")
    print("-" * 80)

    strategies = [
        ("Nearest Room", NearestRoomStrategy()),
        ("Largest Room", LargestRoomStrategy()),
        ("Smallest Suitable", SmallestSuitableRoomStrategy()),
    ]

    for strategy_name, strategy in strategies:
        print(f"\n   Testing {strategy_name}:")
        scheduler.set_room_booking_strategy(strategy)

        test_time = datetime.now() + timedelta(days=1, hours=10)
        meeting = scheduler.create_meeting(
            title=f"Test Meeting - {strategy_name}",
            organizer_id="u1",
            start_time=test_time,
            end_time=test_time + timedelta(hours=1),
            participant_ids=["u2"],
            room_requirements=RoomRequirements(min_capacity=6, required_amenities=["projector"])
        )

        if meeting and meeting.room:
            print(f"      Selected: {meeting.room.name} (capacity: {meeting.room.capacity})")
    print()

    # ========================================================================
    # 10. Test Flexible Conflict Detection
    # ========================================================================
    print("10. Testing Flexible Conflict Detection...")
    print("-" * 80)

    scheduler.set_conflict_detection_strategy(FlexibleConflictDetection())

    test_time = datetime.now() + timedelta(days=2, hours=14)
    meeting3 = scheduler.create_meeting(
        title="Team Brainstorming",
        organizer_id="u1",
        start_time=test_time,
        end_time=test_time + timedelta(hours=1),
        participant_ids=["u2", "u3", "u4"],
        description="Brainstorm new features",
        room_requirements=RoomRequirements(min_capacity=5)
    )

    if meeting3:
        print(f"   ✓ Created: {meeting3} (using flexible detection)")
    print()

    # ========================================================================
    # 11. Update Meeting
    # ========================================================================
    print("11. Updating Meeting...")
    print("-" * 80)

    new_start = start_time + timedelta(hours=1)
    new_end = new_start + timedelta(hours=1)

    success = scheduler.update_meeting(meeting1.meeting_id, new_start, new_end)
    if success:
        print(f"   ✓ Updated meeting to {new_start}")
    print()

    # ========================================================================
    # 12. Cancel Meeting
    # ========================================================================
    print("12. Cancelling Meeting...")
    print("-" * 80)

    success = scheduler.cancel_meeting(meeting2.meeting_id)
    if success:
        print(f"   ✓ Cancelled meeting: {meeting2.title}")
        print(f"     Status: {meeting2.status.value}")
    print()

    # ========================================================================
    # 13. Display Statistics
    # ========================================================================
    print("13. System Statistics:")
    print("-" * 80)
    stats = scheduler.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()

    # ========================================================================
    # 14. Display Notification Summary
    # ========================================================================
    print("14. Notification Summary:")
    print("-" * 80)
    print(f"   Emails sent: {len(email_notifier.sent_emails)}")
    print(f"   SMS sent: {len(sms_notifier.sent_sms)}")
    print(f"   Push notifications: {len(push_notifier.sent_push)}")
    print()

    print("=" * 80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nDesign Patterns Demonstrated:")
    print("✓ Strategy Pattern: Conflict detection and room booking strategies")
    print("✓ Observer Pattern: Notification system (Email, SMS, Push)")
    print("✓ Composite Pattern: Time slot finding with multiple criteria")
    print("✓ Facade Pattern: MeetingScheduler providing simplified interface")
    print("\nSOLID Principles Followed:")
    print("✓ Single Responsibility: Each class has one clear purpose")
    print("✓ Open/Closed: Easy to add new strategies without modifying existing code")
    print("✓ Liskov Substitution: All strategies are interchangeable")
    print("✓ Interface Segregation: Clean, focused interfaces")
    print("✓ Dependency Inversion: Depend on abstractions, not concretions")
    print()


if __name__ == "__main__":
    demo_meeting_scheduler()
