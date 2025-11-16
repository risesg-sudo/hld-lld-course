# Meeting Scheduler System - Low Level Design

## Overview
A comprehensive meeting scheduler system that manages meeting creation, scheduling, conflict detection, room booking, and participant management across multiple calendars. The system handles complex scenarios like recurring meetings, availability checking, and automatic room assignment.

## Requirements

### Functional Requirements
1. **User Management**
   - Register and manage users
   - Track user availability
   - Support multiple calendars per user
   - Set working hours and time zones

2. **Meeting Management**
   - Create one-time meetings
   - Create recurring meetings (daily, weekly, monthly)
   - Send meeting invitations
   - Accept/decline/tentative responses
   - Update and cancel meetings
   - Track meeting participants

3. **Calendar Management**
   - Multiple calendars per user (work, personal)
   - View calendar by day/week/month
   - Check availability across calendars
   - Block time slots
   - Sync external calendars

4. **Room Management**
   - Book meeting rooms
   - Check room availability
   - Room capacity management
   - Room amenities tracking
   - Room release on meeting cancellation

5. **Conflict Detection**
   - Detect scheduling conflicts
   - Check participant availability
   - Suggest alternative time slots
   - Handle double-booking prevention

6. **Notifications**
   - Meeting invitations
   - Reminder notifications
   - Update notifications
   - Cancellation notifications

### Non-Functional Requirements
1. **Performance**
   - Fast availability checking (< 100ms)
   - Support thousands of concurrent users
   - Efficient conflict detection

2. **Reliability**
   - No double booking
   - ACID properties for bookings
   - Data consistency across calendars

3. **Scalability**
   - Handle large organizations
   - Support high meeting volume
   - Distributed calendar access

4. **Usability**
   - Intuitive scheduling interface
   - Clear conflict resolution
   - Easy time zone handling

5. **Extensibility**
   - Add new calendar types
   - Integrate external calendar systems
   - Support custom meeting types

## Use Cases

### Use Case 1: Create Meeting
**Actor**: User (Organizer)
**Preconditions**: User is authenticated, participants exist
**Main Flow**:
1. User specifies meeting details (title, time, duration)
2. User adds participants
3. System checks participant availability
4. System detects conflicts and suggests alternatives
5. User confirms meeting details
6. System books room if required
7. System creates meeting
8. System sends invitations to participants

**Alternative Flow**:
- If conflicts exist: User can override or choose alternative time
- If no room available: System suggests rooms or allows virtual meeting

**Postconditions**: Meeting created, invitations sent, room booked

---

### Use Case 2: Accept/Decline Meeting Invitation
**Actor**: Participant
**Preconditions**: User received invitation
**Main Flow**:
1. User reviews meeting invitation
2. User checks personal calendar
3. User responds (Accept/Decline/Tentative)
4. System updates meeting status
5. System notifies organizer
6. If accepted, system blocks time on user's calendar

**Postconditions**: Response recorded, organizer notified

---

### Use Case 3: Find Available Time Slot
**Actor**: User
**Preconditions**: List of participants provided
**Main Flow**:
1. User specifies participants and duration
2. System retrieves all participant calendars
3. System analyzes availability
4. System identifies free time slots
5. System ranks slots by preference
6. System presents available options

**Postconditions**: Available time slots identified

---

### Use Case 4: Book Meeting Room
**Actor**: System/User
**Preconditions**: Meeting time confirmed
**Main Flow**:
1. System determines room requirements
2. System queries available rooms
3. System filters by capacity and amenities
4. System selects best room
5. System books room for meeting duration
6. System updates room calendar

**Alternative Flow**:
- If no room available: Suggest alternative times or virtual meeting

**Postconditions**: Room booked and assigned to meeting

---

### Use Case 5: Handle Recurring Meeting
**Actor**: User (Organizer)
**Preconditions**: User authenticated
**Main Flow**:
1. User creates meeting with recurrence pattern
2. System validates recurrence rules
3. System generates meeting instances
4. System checks conflicts for each instance
5. System books rooms for all instances
6. System sends invitations

**Alternative Flow**:
- Skip instances with conflicts (if configured)
- Notify about conflict instances

**Postconditions**: Recurring meeting series created

---

### Use Case 6: Cancel Meeting
**Actor**: User (Organizer)
**Preconditions**: User owns the meeting
**Main Flow**:
1. User selects meeting to cancel
2. User confirms cancellation
3. System releases meeting room
4. System updates all participant calendars
5. System sends cancellation notifications
6. System marks meeting as cancelled

**Alternative Flow**:
- If recurring: Option to cancel single instance or entire series

**Postconditions**: Meeting cancelled, room released, participants notified

## Class Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Class Diagram                                │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│      User            │
├──────────────────────┤
│ - user_id: str       │
│ - name: str          │
│ - email: str         │
│ - time_zone: str     │
│ - calendars: List    │
│ - working_hours: Dict│
├──────────────────────┤
│ + add_calendar()     │
│ + get_availability() │
│ + is_available()     │
└──────────────────────┘
          │
          │ owns
          ▼
┌──────────────────────┐
│     Calendar         │
├──────────────────────┤
│ - calendar_id: str   │
│ - name: str          │
│ - type: CalendarType │
│ - owner_id: str      │
│ - meetings: List     │
├──────────────────────┤
│ + add_meeting()      │
│ + remove_meeting()   │
│ + get_events()       │
│ + find_free_slots()  │
└──────────────────────┘
          │
          │ contains
          ▼
┌──────────────────────────────────────┐
│          Meeting                     │
├──────────────────────────────────────┤
│ - meeting_id: str                    │
│ - title: str                         │
│ - organizer: User                    │
│ - start_time: DateTime               │
│ - end_time: DateTime                 │
│ - participants: List[Participant]    │
│ - room: Optional[Room]               │
│ - recurrence: Optional[Recurrence]   │
│ - status: MeetingStatus              │
│ - description: str                   │
├──────────────────────────────────────┤
│ + add_participant()                  │
│ + remove_participant()               │
│ + update_time()                      │
│ + cancel()                           │
│ + is_conflicting(other): bool        │
└──────────────────────────────────────┘
          │                    │
          │                    │ uses
          ▼                    ▼
┌──────────────────────┐    ┌──────────────────────┐
│   Participant        │    │      Room            │
├──────────────────────┤    ├──────────────────────┤
│ - user: User         │    │ - room_id: str       │
│ - response: Response │    │ - name: str          │
│ - is_optional: bool  │    │ - capacity: int      │
├──────────────────────┤    │ - floor: int         │
│ + accept()           │    │ - amenities: List    │
│ + decline()          │    │ - bookings: List     │
│ + tentative()        │    ├──────────────────────┤
└──────────────────────┘    │ + is_available()     │
                            │ + book()             │
                            │ + release()          │
                            └──────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│               MeetingScheduler (Facade)                          │
├──────────────────────────────────────────────────────────────────┤
│ - users: Dict[str, User]                                         │
│ - calendars: Dict[str, Calendar]                                 │
│ - meetings: Dict[str, Meeting]                                   │
│ - rooms: Dict[str, Room]                                         │
│ - conflict_detector: ConflictDetector                            │
│ - room_manager: RoomManager                                      │
│ - notification_service: NotificationService                      │
├──────────────────────────────────────────────────────────────────┤
│ + create_meeting(details): Meeting                               │
│ + update_meeting(meeting_id, details)                            │
│ + cancel_meeting(meeting_id)                                     │
│ + find_available_slots(participants, duration): List[TimeSlot]   │
│ + send_invitation(meeting, participant)                          │
│ + respond_to_meeting(meeting_id, user_id, response)              │
└──────────────────────────────────────────────────────────────────┘
                    │
                    │ uses
                    ▼
┌──────────────────────────────────────────────────────────────────┐
│              <<interface>> ConflictDetectionStrategy             │
├──────────────────────────────────────────────────────────────────┤
│ + detect_conflicts(meeting, calendars): List[Conflict]           │
│ + suggest_alternatives(meeting, conflicts): List[TimeSlot]       │
└──────────────────────────────────────────────────────────────────┘
                    ▲
                    │
      ┌─────────────┴─────────────┐
      │                           │
┌─────┴───────────┐    ┌─────────┴──────────┐
│  Strict         │    │  Flexible          │
│  Detection      │    │  Detection         │
├─────────────────┤    ├────────────────────┤
│+ detect()       │    │+ detect()          │
│                 │    │+ allow_partial()   │
└─────────────────┘    └────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                   RoomManager                                    │
├──────────────────────────────────────────────────────────────────┤
│ - rooms: Dict[str, Room]                                         │
│ - booking_strategy: RoomBookingStrategy                          │
├──────────────────────────────────────────────────────────────────┤
│ + find_available_rooms(start, end, requirements): List[Room]    │
│ + book_room(room, meeting): bool                                 │
│ + release_room(room, meeting)                                    │
│ + set_booking_strategy(strategy)                                 │
└──────────────────────────────────────────────────────────────────┘
                    │
                    │ uses
                    ▼
┌──────────────────────────────────────────────────────────────────┐
│            <<interface>> RoomBookingStrategy                     │
├──────────────────────────────────────────────────────────────────┤
│ + select_room(available_rooms, requirements): Room              │
└──────────────────────────────────────────────────────────────────┘
                    ▲
                    │
      ┌─────────────┴─────────────┬───────────────┐
      │                           │               │
┌─────┴───────────┐    ┌─────────┴──────┐   ┌───┴──────────┐
│  Nearest        │    │  Largest       │   │  Cheapest    │
│  Room           │    │  Room          │   │  Room        │
├─────────────────┤    ├────────────────┤   ├──────────────┤
│+ select_room()  │    │+ select_room() │   │+ select_room()│
└─────────────────┘    └────────────────┘   └──────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                  NotificationService (Observer)                  │
├──────────────────────────────────────────────────────────────────┤
│ - observers: List[NotificationObserver]                          │
├──────────────────────────────────────────────────────────────────┤
│ + attach(observer)                                               │
│ + detach(observer)                                               │
│ + notify(event)                                                  │
│ + send_invitation(meeting, participant)                          │
│ + send_reminder(meeting)                                         │
│ + send_cancellation(meeting)                                     │
└──────────────────────────────────────────────────────────────────┘
                    │
                    │ notifies
                    ▼
┌──────────────────────────────────────────────────────────────────┐
│          <<interface>> NotificationObserver                      │
├──────────────────────────────────────────────────────────────────┤
│ + update(event: NotificationEvent)                               │
└──────────────────────────────────────────────────────────────────┘
                    ▲
                    │
      ┌─────────────┴─────────────┬───────────────┐
      │                           │               │
┌─────┴───────────┐    ┌─────────┴──────┐   ┌───┴──────────┐
│  Email          │    │  SMS           │   │  Push        │
│  Notifier       │    │  Notifier      │   │  Notifier    │
├─────────────────┤    ├────────────────┤   ├──────────────┤
│+ update()       │    │+ update()      │   │+ update()    │
└─────────────────┘    └────────────────┘   └──────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                    Recurrence                                    │
├──────────────────────────────────────────────────────────────────┤
│ - pattern: RecurrencePattern                                     │
│ - frequency: int                                                 │
│ - end_date: Optional[DateTime]                                   │
│ - occurrences: Optional[int]                                     │
│ - days_of_week: Optional[List[int]]                              │
├──────────────────────────────────────────────────────────────────┤
│ + generate_instances(start, end): List[DateTime]                 │
│ + get_next_occurrence(after): DateTime                           │
└──────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                  TimeSlotFinder (Composite)                      │
├──────────────────────────────────────────────────────────────────┤
│ - slot_finders: List[SlotFinder]                                 │
├──────────────────────────────────────────────────────────────────┤
│ + add_finder(finder)                                             │
│ + find_slots(participants, duration): List[TimeSlot]             │
└──────────────────────────────────────────────────────────────────┘
                    │
                    │ composed of
                    ▼
┌──────────────────────────────────────────────────────────────────┐
│             <<interface>> SlotFinder                             │
├──────────────────────────────────────────────────────────────────┤
│ + find_slots(participants, duration): List[TimeSlot]             │
└──────────────────────────────────────────────────────────────────┘
                    ▲
                    │
      ┌─────────────┴─────────────┬───────────────┐
      │                           │               │
┌─────┴──────────┐    ┌──────────┴────────┐  ┌──┴─────────────┐
│WorkingHours    │    │  Preference       │  │  Availability  │
│SlotFinder      │    │  SlotFinder       │  │  SlotFinder    │
├────────────────┤    ├───────────────────┤  ├────────────────┤
│+ find_slots()  │    │+ find_slots()     │  │+ find_slots()  │
└────────────────┘    └───────────────────┘  └────────────────┘

```

## Design Patterns Used

### 1. Strategy Pattern
**Purpose**: Enable different strategies for conflict detection and room booking

**Implementation**:
- `ConflictDetectionStrategy` interface with concrete implementations
  - `StrictDetectionStrategy`: No overlaps allowed
  - `FlexibleDetectionStrategy`: Allow partial overlaps or tentative meetings
- `RoomBookingStrategy` interface with concrete implementations
  - `NearestRoomStrategy`: Select closest room
  - `LargestRoomStrategy`: Select largest available room
  - `CheapestRoomStrategy`: Select most cost-effective room

**Benefits**:
- Easy to switch between different strategies
- Add new strategies without modifying existing code
- Different organizations can use different policies

### 2. Observer Pattern
**Purpose**: Notify participants about meeting events

**Implementation**:
- `NotificationService` as subject
- `NotificationObserver` interface
- Concrete observers: `EmailNotifier`, `SMSNotifier`, `PushNotifier`
- Observers get notified on meeting creation, updates, cancellations

**Benefits**:
- Decoupled notification mechanism
- Easy to add new notification channels
- Event-driven architecture

### 3. Composite Pattern
**Purpose**: Combine multiple slot-finding algorithms

**Implementation**:
- `TimeSlotFinder` as composite
- `SlotFinder` interface for components
- Concrete finders: `WorkingHoursSlotFinder`, `PreferenceSlotFinder`, `AvailabilitySlotFinder`
- Composite combines results from all finders

**Benefits**:
- Flexible combination of finding strategies
- Treat individual and composite finders uniformly
- Easy to add new finding criteria

### 4. Facade Pattern
**Purpose**: Provide simplified interface to complex subsystem

**Implementation**:
- `MeetingScheduler` as facade
- Hides complexity of calendars, rooms, conflicts, notifications
- Provides simple methods like `create_meeting()`, `find_available_slots()`

**Benefits**:
- Simplified API for clients
- Reduces coupling between clients and subsystems
- Easy to use and understand

### 5. Template Method Pattern (Implicit)
**Purpose**: Define skeleton of conflict detection algorithm

**Implementation**:
- Base conflict detection flow
- Subclasses override specific steps
- Common preprocessing/postprocessing

## Core Algorithms

### 1. Conflict Detection Algorithm
```
Algorithm: Detect Meeting Conflicts
Input: New meeting, List of calendars
Output: List of conflicts

1. For each calendar in calendars:
   a. Get all meetings in the time range
   b. For each existing meeting:
      - Check if time overlaps with new meeting
      - Check if same participant in both
      - If yes, add to conflicts list

2. Group conflicts by participant

3. Return conflicts

Time Complexity: O(N × M)
where N = number of calendars, M = average meetings per calendar
```

### 2. Find Available Time Slots Algorithm
```
Algorithm: Find Available Slots
Input: List of participants, Duration, Search range
Output: List of available time slots

1. Initialize free_slots = all slots in search range

2. For each participant:
   a. Get participant's calendars
   b. Get all meetings in search range
   c. Remove occupied slots from free_slots

3. Filter slots that are:
   - Within working hours of all participants
   - Long enough for the meeting duration
   - Not during blackout periods

4. Rank slots by preferences:
   - Prefer morning/afternoon based on preferences
   - Prefer slots with all participants available
   - Prefer slots with room availability

5. Return top N ranked slots

Time Complexity: O(P × C × M)
where P = participants, C = calendars per participant, M = meetings
```

### 3. Room Booking Algorithm
```
Algorithm: Book Meeting Room
Input: Meeting details, Room requirements
Output: Booked room or null

1. Get time range from meeting

2. Query all rooms matching requirements:
   - Minimum capacity
   - Required amenities
   - Location preferences

3. Filter available rooms:
   - Not booked in the time range
   - Not under maintenance

4. Apply booking strategy to select best room

5. Book the selected room:
   - Add booking to room calendar
   - Update meeting with room info
   - Return room

Time Complexity: O(R × B)
where R = number of rooms, B = bookings per room
```

### 4. Recurring Meeting Generation
```
Algorithm: Generate Recurring Meetings
Input: Base meeting, Recurrence pattern
Output: List of meeting instances

1. Validate recurrence pattern

2. Calculate series end date:
   - Use explicit end date if provided
   - Or calculate from occurrence count

3. Generate instances:
   start_date = base_meeting.start_time
   instances = []

   while start_date <= end_date:
      a. Create meeting instance
      b. Check conflicts for this instance
      c. Add to instances list
      d. Calculate next occurrence based on pattern

4. Return instances

Time Complexity: O(N)
where N = number of occurrences
```

## Edge Cases and Error Handling

### 1. Double Booking Prevention
- Use optimistic locking or database transactions
- Check availability immediately before booking
- Lock calendar during booking operation
- Rollback on conflict detection

### 2. Time Zone Handling
- Store all times in UTC
- Convert to user's time zone for display
- Handle daylight saving time transitions
- Validate time zones

### 3. Concurrent Bookings
- Use database-level locks
- Implement retry mechanism
- Return error if booking fails
- Suggest alternative slots

### 4. Meeting Conflicts
- **Total conflict**: All participants unavailable
  - Suggest alternative times
  - Allow force booking with notification
- **Partial conflict**: Some participants unavailable
  - Mark as tentative
  - Suggest alternatives
  - Allow proceeding with available participants

### 5. Room Unavailability
- **No rooms available**: Suggest alternative times or virtual meeting
- **Room too small**: Suggest larger room or split meeting
- **Room booking fails**: Retry with next best room

### 6. Recurring Meeting Issues
- **Conflict in some instances**: Skip or mark as tentative
- **Pattern changes**: Update future instances only
- **Cancellation**: Option to cancel single or all instances

### 7. Invalid Input
- Validate meeting duration (not negative, not too long)
- Validate time range (start before end)
- Validate participants (exist in system)
- Validate room capacity (sufficient for participants)

## SOLID Principles

### Single Responsibility Principle (SRP)
- `Meeting`: Manages meeting data and state
- `Calendar`: Manages events in a calendar
- `ConflictDetector`: Only detects conflicts
- `RoomManager`: Only manages rooms
- `NotificationService`: Only handles notifications

### Open/Closed Principle (OCP)
- New conflict detection strategies can be added without modifying core
- New room booking strategies can be added
- New notification channels can be added
- New slot finding algorithms can be added

### Liskov Substitution Principle (LSP)
- All `ConflictDetectionStrategy` implementations are interchangeable
- All `RoomBookingStrategy` implementations are interchangeable
- All `NotificationObserver` implementations are interchangeable

### Interface Segregation Principle (ISP)
- `ConflictDetectionStrategy`: Only conflict detection methods
- `RoomBookingStrategy`: Only room selection methods
- `NotificationObserver`: Only update method
- No fat interfaces with unused methods

### Dependency Inversion Principle (DIP)
- `MeetingScheduler` depends on strategy interfaces, not concrete strategies
- `RoomManager` depends on `RoomBookingStrategy` interface
- High-level scheduling logic doesn't depend on low-level notification details

## Performance Considerations

### Time Complexity
- **Create Meeting**: O(P × M) where P=participants, M=meetings per participant
- **Find Available Slots**: O(P × C × M) where C=calendars per participant
- **Conflict Detection**: O(N × M) where N=number of calendars
- **Room Booking**: O(R × B) where R=rooms, B=bookings per room

### Space Complexity
- **Calendar Storage**: O(U × C × M) where U=users
- **Room Bookings**: O(R × B)
- **Notification Queue**: O(N) where N=pending notifications

### Optimizations
1. **Indexing**: Index meetings by time range for fast queries
2. **Caching**: Cache frequently accessed calendars
3. **Lazy Loading**: Load meetings only for required time range
4. **Batch Operations**: Batch notification sending
5. **Database Queries**: Use efficient queries with proper indexes

## Testing Strategy

### Unit Tests
- Meeting conflict detection
- Time slot finding
- Room booking logic
- Recurrence pattern generation
- Notification sending

### Integration Tests
- End-to-end meeting creation
- Multi-calendar conflict detection
- Room booking with actual database
- Notification delivery

### Test Scenarios
1. **Simple meeting creation** with no conflicts
2. **Meeting with conflicts** requiring resolution
3. **Recurring meeting** with weekly pattern
4. **Multi-participant meeting** across time zones
5. **Room booking** with capacity constraints
6. **Meeting cancellation** and notification
7. **Concurrent booking attempts** (race condition)
8. **Edge times** (midnight, daylight saving transitions)
9. **Large meetings** (100+ participants)
10. **Long-running series** (1 year recurring meeting)

## Extensions and Future Enhancements

1. **AI-Powered Scheduling**
   - Smart time suggestions based on past meetings
   - Predict best meeting times
   - Auto-suggest optimal meeting duration

2. **Integration with External Calendars**
   - Google Calendar sync
   - Outlook Calendar sync
   - iCal support

3. **Advanced Room Features**
   - Equipment booking (projector, whiteboard)
   - Catering requests
   - Room setup preferences

4. **Meeting Analytics**
   - Meeting frequency analysis
   - Time utilization reports
   - Room utilization metrics

5. **Virtual Meeting Integration**
   - Auto-generate Zoom/Teams links
   - Hybrid meeting support
   - Virtual room booking

6. **Delegation and Proxies**
   - Delegate scheduling authority
   - Assistant can book on behalf
   - Proxy attendees

7. **Resource Management**
   - Book shared resources (cars, equipment)
   - Resource availability tracking
   - Resource conflict detection

## Implementation Notes

- Use proper datetime library (Python's `datetime` with `pytz` for time zones)
- Implement database transactions for booking operations
- Use message queue for asynchronous notifications
- Add comprehensive logging for debugging
- Implement audit trail for all changes
- Use type hints for better code clarity
- Include detailed docstrings
- Consider using dataclasses for value objects
