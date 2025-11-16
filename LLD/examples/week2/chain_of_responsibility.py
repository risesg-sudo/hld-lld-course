"""
Chain of Responsibility Pattern - Pass request along chain until handled.

This module demonstrates various chain of responsibility implementations:
1. Simple handler chain
2. Logging system with levels
3. Support ticket routing system
4. HTTP middleware chain
5. Approval workflow
6. Event handling chain

Key Learning Points:
- Chain decouples sender from receiver
- Handlers decide whether to handle request or pass it on
- Multiple handlers can process same request
- Order of handlers matters
- Request might not be handled (need default handler)
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, List
from datetime import datetime
from enum import Enum


# ============================================================================
# 1. SIMPLE HANDLER CHAIN
# ============================================================================

class Request:
    """Request to be handled."""

    def __init__(self, request_id: str, data: str):
        self.request_id = request_id
        self.data = data
        self.created_at = datetime.now()

    def __str__(self):
        return f"Request({self.request_id}, {self.data})"


class Handler(ABC):
    """
    Abstract handler in chain.

    Each handler:
    1. Can handle request or pass to next handler
    2. Knows next handler in chain
    3. Can process request before/after passing to next handler
    """

    def __init__(self, name: str):
        self.name = name
        self.next_handler: Optional[Handler] = None

    def set_next(self, handler: "Handler") -> "Handler":
        """Set next handler in chain."""
        self.next_handler = handler
        return handler  # Return next handler to allow chaining

    @abstractmethod
    def handle(self, request: Request) -> bool:
        """
        Handle request or pass to next handler.

        Returns:
            True if handled, False if passed to next handler
        """
        if self.next_handler:
            return self.next_handler.handle(request)
        return False


class ConcreteHandlerA(Handler):
    """Handler that processes certain requests."""

    def handle(self, request: Request) -> bool:
        """Handle request if it starts with 'A'."""
        if request.data.startswith('A'):
            print(f"{self.name} handled: {request}")
            return True
        else:
            print(f"{self.name} passed request to next handler")
            return super().handle(request)


class ConcreteHandlerB(Handler):
    """Handler that processes certain requests."""

    def handle(self, request: Request) -> bool:
        """Handle request if it starts with 'B'."""
        if request.data.startswith('B'):
            print(f"{self.name} handled: {request}")
            return True
        else:
            print(f"{self.name} passed request to next handler")
            return super().handle(request)


class DefaultHandler(Handler):
    """Default handler - always handles request."""

    def handle(self, request: Request) -> bool:
        """Handle any request (default)."""
        print(f"{self.name} handled (default): {request}")
        return True


# ============================================================================
# 2. LOGGING SYSTEM WITH LEVELS
# ============================================================================

class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class LogRecord:
    """Represents a log record."""

    def __init__(self, level: LogLevel, message: str):
        self.level = level
        self.message = message
        self.timestamp = datetime.now()

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.level.name}: {self.message}"


class Logger(ABC):
    """Abstract logger handler."""

    def __init__(self, name: str, level: LogLevel):
        self.name = name
        self.level = level
        self.next_logger: Optional[Logger] = None

    def set_next(self, logger: "Logger") -> "Logger":
        """Set next logger in chain."""
        self.next_logger = logger
        return logger

    def log_message(self, record: LogRecord):
        """Log message or pass to next handler."""
        if record.level.value >= self.level.value:
            self.write(record)

        if self.next_logger:
            self.next_logger.log_message(record)

    @abstractmethod
    def write(self, record: LogRecord):
        """Write log record."""
        pass


class ConsoleLogger(Logger):
    """Logs to console."""

    def write(self, record: LogRecord):
        """Write to console."""
        print(f"[CONSOLE] {record}")


class FileLogger(Logger):
    """Logs to file."""

    def __init__(self, name: str, level: LogLevel, filename: str):
        super().__init__(name, level)
        self.filename = filename
        self.logs: List[str] = []

    def write(self, record: LogRecord):
        """Write to file (simulated)."""
        self.logs.append(str(record))
        print(f"[FILE] {record}")

    def get_logs(self) -> List[str]:
        """Get logged messages."""
        return self.logs.copy()


class EmailLogger(Logger):
    """Logs critical errors via email."""

    def write(self, record: LogRecord):
        """Send email for critical errors."""
        if record.level == LogLevel.CRITICAL:
            print(f"[EMAIL] Sending critical alert: {record.message}")


class DatabaseLogger(Logger):
    """Logs to database."""

    def __init__(self, name: str, level: LogLevel):
        super().__init__(name, level)
        self.db_logs: List[str] = []

    def write(self, record: LogRecord):
        """Write to database (simulated)."""
        self.db_logs.append(str(record))
        print(f"[DATABASE] Stored: {record}")

    def get_logs(self) -> List[str]:
        """Get logged messages."""
        return self.db_logs.copy()


# ============================================================================
# 3. SUPPORT TICKET ROUTING SYSTEM
# ============================================================================

class SupportTicket:
    """Support ticket to be routed."""

    def __init__(self, ticket_id: str, issue: str, priority: int):
        self.ticket_id = ticket_id
        self.issue = issue
        self.priority = priority  # 1=low, 5=high
        self.assigned_to = None
        self.status = "OPEN"
        self.created_at = datetime.now()

    def __str__(self):
        return f"Ticket({self.ticket_id}, priority={self.priority}, {self.issue})"


class SupportHandler(ABC):
    """Abstract support handler."""

    def __init__(self, name: str, max_priority: int):
        self.name = name
        self.max_priority = max_priority
        self.next_handler: Optional[SupportHandler] = None
        self.handled_tickets: List[SupportTicket] = []

    def set_next(self, handler: "SupportHandler") -> "SupportHandler":
        """Set next handler."""
        self.next_handler = handler
        return handler

    def handle_ticket(self, ticket: SupportTicket):
        """Handle ticket or pass to next handler."""
        if ticket.priority <= self.max_priority:
            self.process_ticket(ticket)
            self.handled_tickets.append(ticket)
        elif self.next_handler:
            self.next_handler.handle_ticket(ticket)
        else:
            print(f"ERROR: No handler available for {ticket}")

    @abstractmethod
    def process_ticket(self, ticket: SupportTicket):
        """Process the ticket."""
        pass


class BasicSupportHandler(SupportHandler):
    """Handles basic support tickets (priority 1-2)."""

    def process_ticket(self, ticket: SupportTicket):
        """Process basic ticket."""
        print(f"{self.name} handling: {ticket}")
        ticket.assigned_to = self.name
        ticket.status = "IN_PROGRESS"
        print(f"  Resolving: {ticket.issue}")
        ticket.status = "RESOLVED"


class TechnicianHandler(SupportHandler):
    """Handles technical tickets (priority 2-3)."""

    def process_ticket(self, ticket: SupportTicket):
        """Process technical ticket."""
        print(f"{self.name} handling: {ticket}")
        ticket.assigned_to = self.name
        ticket.status = "INVESTIGATING"
        print(f"  Investigating technical issue: {ticket.issue}")
        ticket.status = "RESOLVED"


class ManagerHandler(SupportHandler):
    """Handles critical tickets (priority 4-5)."""

    def process_ticket(self, ticket: SupportTicket):
        """Process critical ticket."""
        print(f"{self.name} handling: {ticket}")
        ticket.assigned_to = self.name
        ticket.status = "CRITICAL"
        print(f"  Escalating to management: {ticket.issue}")
        print(f"  Engaging specialized team...")
        ticket.status = "RESOLVED"


# ============================================================================
# 4. HTTP MIDDLEWARE CHAIN
# ============================================================================

class HTTPRequest:
    """HTTP request object."""

    def __init__(self, url: str, method: str = "GET"):
        self.url = url
        self.method = method
        self.headers: dict = {}
        self.body: Optional[str] = None
        self.user_id: Optional[str] = None
        self.is_authenticated = False
        self.is_authorized = False

    def __str__(self):
        return f"HTTPRequest({self.method} {self.url})"


class HTTPResponse:
    """HTTP response object."""

    def __init__(self, status_code: int = 200, body: str = ""):
        self.status_code = status_code
        self.body = body

    def __str__(self):
        return f"HTTPResponse({self.status_code}, {len(self.body)} bytes)"


class Middleware(ABC):
    """Abstract middleware."""

    def __init__(self, name: str):
        self.name = name
        self.next_middleware: Optional[Middleware] = None

    def set_next(self, middleware: "Middleware") -> "Middleware":
        """Set next middleware."""
        self.next_middleware = middleware
        return middleware

    def process(self, request: HTTPRequest) -> Optional[HTTPResponse]:
        """
        Process request or pass to next middleware.

        Returns:
            HTTPResponse if should stop chain, None to continue
        """
        print(f"{self.name} processing {request}")
        result = self.handle(request)

        if result:
            return result  # Stop chain
        elif self.next_middleware:
            return self.next_middleware.process(request)

        return HTTPResponse(200, "OK")

    @abstractmethod
    def handle(self, request: HTTPRequest) -> Optional[HTTPResponse]:
        """Handle request."""
        pass


class LoggingMiddleware(Middleware):
    """Logs HTTP requests."""

    def handle(self, request: HTTPRequest) -> Optional[HTTPResponse]:
        """Log request."""
        print(f"  [LOGGING] {request.method} {request.url}")
        return None  # Continue to next middleware


class AuthenticationMiddleware(Middleware):
    """Authenticates user."""

    def handle(self, request: HTTPRequest) -> Optional[HTTPResponse]:
        """Authenticate request."""
        # Check if request has authentication header
        if "Authorization" not in request.headers:
            print(f"  [AUTH] No authentication provided")
            return HTTPResponse(401, "Unauthorized")

        print(f"  [AUTH] User authenticated")
        request.is_authenticated = True
        request.user_id = "user123"
        return None  # Continue


class AuthorizationMiddleware(Middleware):
    """Checks if user is authorized."""

    def handle(self, request: HTTPRequest) -> Optional[HTTPResponse]:
        """Check authorization."""
        if not request.is_authenticated:
            print(f"  [AUTHZ] User not authenticated")
            return HTTPResponse(401, "Unauthorized")

        if request.method == "DELETE" and request.user_id != "admin":
            print(f"  [AUTHZ] User not authorized for DELETE")
            return HTTPResponse(403, "Forbidden")

        print(f"  [AUTHZ] User authorized")
        request.is_authorized = True
        return None  # Continue


class CORSMiddleware(Middleware):
    """Handles CORS."""

    def handle(self, request: HTTPRequest) -> Optional[HTTPResponse]:
        """Check CORS."""
        print(f"  [CORS] Checking CORS headers")
        request.headers["Access-Control-Allow-Origin"] = "*"
        return None  # Continue


# ============================================================================
# 5. APPROVAL WORKFLOW
# ============================================================================

class ExpenseReport:
    """Expense report to be approved."""

    def __init__(self, report_id: str, amount: float):
        self.report_id = report_id
        self.amount = amount
        self.approvals: List[str] = []
        self.status = "PENDING"

    def __str__(self):
        return f"ExpenseReport({self.report_id}, ${self.amount:.2f})"


class ApprovalHandler(ABC):
    """Abstract approval handler."""

    def __init__(self, name: str, approval_limit: float):
        self.name = name
        self.approval_limit = approval_limit
        self.next_handler: Optional[ApprovalHandler] = None

    def set_next(self, handler: "ApprovalHandler") -> "ApprovalHandler":
        """Set next handler."""
        self.next_handler = handler
        return handler

    def approve(self, report: ExpenseReport):
        """Approve report or pass to next handler."""
        if report.amount <= self.approval_limit:
            print(f"{self.name} approving: {report}")
            report.approvals.append(self.name)
            report.status = "APPROVED"
        elif self.next_handler:
            print(f"{self.name} cannot approve (amount too high), passing to {self.next_handler.name}")
            self.next_handler.approve(report)
        else:
            print(f"ERROR: No one can approve ${report.amount:.2f}")
            report.status = "REJECTED"


class TeamLeadApprover(ApprovalHandler):
    """Team lead can approve up to $500."""
    pass


class ManagerApprover(ApprovalHandler):
    """Manager can approve up to $2000."""
    pass


class DirectorApprover(ApprovalHandler):
    """Director can approve up to $10000."""
    pass


class CFOApprover(ApprovalHandler):
    """CFO can approve any amount."""
    pass


# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

def test_simple_chain():
    """Test simple handler chain."""
    print("\n" + "="*70)
    print("TEST 1: SIMPLE HANDLER CHAIN")
    print("="*70)

    # Create chain
    handler_a = ConcreteHandlerA("Handler A")
    handler_b = ConcreteHandlerB("Handler B")
    default = DefaultHandler("Default Handler")

    handler_a.set_next(handler_b).set_next(default)

    # Process requests
    handler_a.handle(Request("1", "A Request"))
    handler_a.handle(Request("2", "B Request"))
    handler_a.handle(Request("3", "C Request"))


def test_logging_chain():
    """Test logging system with chain."""
    print("\n" + "="*70)
    print("TEST 2: LOGGING SYSTEM WITH CHAIN")
    print("="*70)

    # Create logger chain
    console = ConsoleLogger("Console", LogLevel.DEBUG)
    file = FileLogger("File", LogLevel.INFO, "app.log")
    email = EmailLogger("Email", LogLevel.CRITICAL)
    database = DatabaseLogger("Database", LogLevel.WARNING)

    # Set up chain: Console -> File -> Database -> Email
    console.set_next(file).set_next(database).set_next(email)

    # Log messages at different levels
    console.log_message(LogRecord(LogLevel.DEBUG, "Debug information"))
    console.log_message(LogRecord(LogLevel.INFO, "Application started"))
    console.log_message(LogRecord(LogLevel.WARNING, "Low memory available"))
    console.log_message(LogRecord(LogLevel.ERROR, "Failed to connect to database"))
    console.log_message(LogRecord(LogLevel.CRITICAL, "System failure!"))


def test_support_routing():
    """Test support ticket routing."""
    print("\n" + "="*70)
    print("TEST 3: SUPPORT TICKET ROUTING")
    print("="*70)

    # Create handler chain
    basic = BasicSupportHandler("Basic Support", 2)
    technician = TechnicianHandler("Technician", 3)
    manager = ManagerHandler("Manager", 5)

    basic.set_next(technician).set_next(manager)

    # Route tickets
    basic.handle_ticket(SupportTicket("T001", "Password reset", 1))
    basic.handle_ticket(SupportTicket("T002", "Software crash", 3))
    basic.handle_ticket(SupportTicket("T003", "System down", 5))


def test_http_middleware():
    """Test HTTP middleware chain."""
    print("\n" + "="*70)
    print("TEST 4: HTTP MIDDLEWARE CHAIN")
    print("="*70)

    # Create middleware chain
    logging = LoggingMiddleware("Logging")
    auth = AuthenticationMiddleware("Authentication")
    authz = AuthorizationMiddleware("Authorization")
    cors = CORSMiddleware("CORS")

    # Set up chain
    logging.set_next(cors).set_next(auth).set_next(authz)

    # Request 1: Authenticated, authorized
    print("\nRequest 1: DELETE with auth")
    req1 = HTTPRequest("/api/users/123", "DELETE")
    req1.headers["Authorization"] = "Bearer token123"
    req1.user_id = "admin"
    response1 = logging.process(req1)
    print(f"Response: {response1}")

    # Request 2: No auth
    print("\nRequest 2: GET without auth")
    req2 = HTTPRequest("/api/public", "GET")
    response2 = logging.process(req2)
    print(f"Response: {response2}")

    # Request 3: Authenticated but not authorized
    print("\nRequest 3: DELETE without admin privileges")
    req3 = HTTPRequest("/api/admin", "DELETE")
    req3.headers["Authorization"] = "Bearer token456"
    req3.user_id = "user"
    response3 = logging.process(req3)
    print(f"Response: {response3}")


def test_approval_workflow():
    """Test approval workflow."""
    print("\n" + "="*70)
    print("TEST 5: APPROVAL WORKFLOW")
    print("="*70)

    # Create approval chain
    lead = TeamLeadApprover("Team Lead", 500)
    manager = ManagerApprover("Manager", 2000)
    director = DirectorApprover("Director", 10000)
    cfo = CFOApprover("CFO", float('inf'))

    lead.set_next(manager).set_next(director).set_next(cfo)

    # Request approvals
    lead.approve(ExpenseReport("EXP001", 300))
    lead.approve(ExpenseReport("EXP002", 1500))
    lead.approve(ExpenseReport("EXP003", 5000))
    lead.approve(ExpenseReport("EXP004", 50000))


def test_event_handling():
    """Test event handling chain."""
    print("\n" + "="*70)
    print("TEST 6: EVENT HANDLING CHAIN")
    print("="*70)

    class Event:
        def __init__(self, event_type: str, data: Any):
            self.event_type = event_type
            self.data = data
            self.handled = False

    class EventHandler(ABC):
        def __init__(self, event_type: str):
            self.event_type = event_type
            self.next_handler: Optional[EventHandler] = None

        def set_next(self, handler: "EventHandler") -> "EventHandler":
            self.next_handler = handler
            return handler

        def handle(self, event: Event):
            if event.event_type == self.event_type and not event.handled:
                self.process(event)
                event.handled = True
            elif self.next_handler:
                self.next_handler.handle(event)

        @abstractmethod
        def process(self, event: Event):
            pass

    class ClickHandler(EventHandler):
        def __init__(self):
            super().__init__("click")

        def process(self, event: Event):
            print(f"  Processing CLICK event: {event.data}")

    class HoverHandler(EventHandler):
        def __init__(self):
            super().__init__("hover")

        def process(self, event: Event):
            print(f"  Processing HOVER event: {event.data}")

    class KeyPressHandler(EventHandler):
        def __init__(self):
            super().__init__("keypress")

        def process(self, event: Event):
            print(f"  Processing KEYPRESS event: {event.data}")

    # Create handler chain
    click = ClickHandler()
    hover = HoverHandler()
    keypress = KeyPressHandler()

    click.set_next(hover).set_next(keypress)

    # Handle events
    click.handle(Event("click", "button clicked"))
    click.handle(Event("hover", "mouse hovered"))
    click.handle(Event("keypress", "key pressed"))


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

def print_key_takeaways():
    """Print key learning points."""
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. CHAIN DECOUPLES SENDER AND RECEIVER
   - Sender doesn't know who will handle request
   - Receiver doesn't know who sent request
   - Multiple handlers possible
   - Easy to add/remove handlers at runtime

2. HANDLER RESPONSIBILITIES
   Each handler:
   - Decides whether to handle request
   - Passes to next if can't handle
   - Can process before/after passing
   - Knows about next handler (not others)

3. CHAIN CONSTRUCTION
   Benefits:
   - Flexible ordering
   - Add/remove handlers dynamically
   - Different chains for different scenarios
   - Can reuse handlers in multiple chains

4. REQUEST FLOW
   Pattern:
   1. Handler receives request
   2. Checks if can handle
   3. If yes: process and stop (or continue)
   4. If no: pass to next handler
   5. If no next: request unhandled (ERROR!)

5. IMPORTANT: HANDLE UNHANDLED REQUESTS
   - Always have default/final handler
   - Or explicitly handle unhandled case
   - Silently dropping requests is bug
   - Log unhandled requests

6. REAL-WORLD APPLICATIONS
   - HTTP middleware (logging, auth, CORS)
   - Approval workflows (expense, leave requests)
   - Event handling systems
   - Logging with multiple outputs
   - Support ticket routing
   - Exception handling
   - UI event propagation
   - Request validation pipeline
   - Processing pipelines

7. HANDLER ORDER MATTERS
   - Authentication before authorization
   - Validation before processing
   - Logging first (catch all)
   - Critical handlers first
   - Order can affect results!

8. VARIATIONS
   Linear Chain:
   - Simple single path
   - Handler decides: handle or skip

   Tree-based Chain:
   - Multiple branches
   - Different paths based on condition

   Parallel Processing:
   - Multiple handlers process same request
   - Request not consumed by first handler

9. PERFORMANCE CONSIDERATIONS
   - Chain length affects latency
   - Each handler adds overhead
   - Avoid deep chains (> 10 levels)
   - Consider caching for repeated checks
   - Profile to find bottlenecks

10. DEBUGGING CHAIN ISSUES
    - Add logging at each handler
    - Log which handler handled request
    - Log when request passes to next
    - Use middleware to wrap handlers
    - Test each handler independently
    - Test full chain
    """)


if __name__ == "__main__":
    test_simple_chain()
    test_logging_chain()
    test_support_routing()
    test_http_middleware()
    test_approval_workflow()
    test_event_handling()
    print_key_takeaways()
