"""
SOLID PRINCIPLE #5: DEPENDENCY INVERSION PRINCIPLE (DIP)
==========================================================

Core Concept:
High-level modules should not depend on low-level modules.
Both should depend on abstractions.
Abstractions should not depend on details.
Details should depend on abstractions.

In simpler terms: Depend on interfaces/abstractions, not on concrete implementations.

Benefits:
- Decouples high-level and low-level modules
- Makes code more flexible and maintainable
- Easier to test with mock objects
- Easier to swap implementations
- Makes code more resilient to changes

Real-world analogy:
A light switch doesn't need to know the details of how the bulb works.
It just needs an interface to turn things on/off.
The bulb and switch both depend on a common electrical interface.
"""

from abc import ABC, abstractmethod
from typing import List


# ============================================================================
# BAD EXAMPLE: High-Level Depends on Low-Level (DIP Violation)
# ============================================================================

class BadEmailSender:
    """Low-level: Concrete email implementation."""

    def send_email(self, to: str, message: str) -> bool:
        print(f"✓ Sending email to {to}: {message}")
        return True


class BadSMSSender:
    """Low-level: Concrete SMS implementation."""

    def send_sms(self, phone: str, message: str) -> bool:
        print(f"✓ Sending SMS to {phone}: {message}")
        return True


class BadNotificationService:
    """
    High-level module that DIRECTLY depends on low-level concrete classes.
    This violates DIP because:
    1. It imports BadEmailSender and BadSMSSender directly
    2. It's tightly coupled to specific implementations
    3. Changing EmailSender or SMSSender breaks this class
    4. Hard to test with mock objects
    5. Can't easily add new notification types
    """

    def __init__(self):
        self.email_sender = BadEmailSender()  # Direct dependency
        self.sms_sender = BadSMSSender()      # Direct dependency

    def send_notification(self, to: str, message: str, type: str) -> bool:
        """Send notification using specific concrete classes."""
        if type == "email":
            return self.email_sender.send_email(to, message)
        elif type == "sms":
            return self.sms_sender.send_sms(to, message)
        else:
            raise ValueError(f"Unknown notification type: {type}")

    def notify_users(self, users: List[dict], message: str):
        """Notify multiple users."""
        for user in users:
            if user.get("email"):
                self.send_notification(user["email"], message, "email")
            if user.get("phone"):
                self.send_notification(user["phone"], message, "sms")


def demo_bad_dip():
    """Demonstrate DIP violation."""
    print("\n" + "="*70)
    print("BAD EXAMPLE: DIP Violation - High-Level Depends on Low-Level")
    print("="*70)

    service = BadNotificationService()

    users = [
        {"email": "john@example.com", "phone": "555-1234"},
        {"email": "jane@example.com", "phone": "555-5678"}
    ]

    print("\nSending notifications:")
    service.notify_users(users, "Important: Your account needs attention")

    print("\nProblems:")
    print("  - NotificationService is tightly coupled to EmailSender and SMSSender")
    print("  - If EmailSender changes, NotificationService might break")
    print("  - Can't easily add new notification types (Slack, Teams, etc.)")
    print("  - Hard to test with mock objects")
    print("  - Direct instantiation of dependencies makes testing difficult")


# ============================================================================
# GOOD EXAMPLE: Following DIP - Depend on Abstractions
# ============================================================================

class NotificationSender(ABC):
    """
    Abstraction: Both high-level and low-level modules depend on this.
    This is the interface that decouples them.
    """

    @abstractmethod
    def send(self, to: str, message: str) -> bool:
        """Send notification."""
        pass

    @abstractmethod
    def get_type(self) -> str:
        """Get notification type."""
        pass


class EmailNotificationSender(NotificationSender):
    """Low-level: Email implementation of NotificationSender."""

    def send(self, to: str, message: str) -> bool:
        print(f"✓ Sending email to {to}: {message}")
        return True

    def get_type(self) -> str:
        return "email"


class SMSNotificationSender(NotificationSender):
    """Low-level: SMS implementation of NotificationSender."""

    def send(self, phone: str, message: str) -> bool:
        print(f"✓ Sending SMS to {phone}: {message}")
        return True

    def get_type(self) -> str:
        return "sms"


class SlackNotificationSender(NotificationSender):
    """Low-level: Slack implementation of NotificationSender."""

    def send(self, channel: str, message: str) -> bool:
        print(f"✓ Sending Slack message to {channel}: {message}")
        return True

    def get_type(self) -> str:
        return "slack"


class TeamsNotificationSender(NotificationSender):
    """Low-level: Teams implementation - added without changing NotificationService!"""

    def send(self, channel: str, message: str) -> bool:
        print(f"✓ Sending Teams message to {channel}: {message}")
        return True

    def get_type(self) -> str:
        return "teams"


class GoodNotificationService:
    """
    High-level module that depends on abstractions (NotificationSender),
    NOT on concrete implementations.

    This class doesn't know or care about EmailSender, SMSSender, etc.
    It only knows about NotificationSender interface.
    """

    def __init__(self):
        self.senders: dict[str, NotificationSender] = {}

    def register_sender(self, type: str, sender: NotificationSender) -> None:
        """Register a notification sender."""
        self.senders[type] = sender
        print(f"✓ Registered {type} notification sender")

    def send_notification(self, to: str, message: str, type: str) -> bool:
        """Send notification using registered sender."""
        if type not in self.senders:
            raise ValueError(f"No sender registered for type: {type}")

        sender = self.senders[type]
        return sender.send(to, message)

    def notify_users(self, users: List[dict], message: str):
        """Notify multiple users using their preferred methods."""
        for user in users:
            if "email" in user and "email" in self.senders:
                self.send_notification(user["email"], message, "email")
            if "phone" in user and "sms" in self.senders:
                self.send_notification(user["phone"], message, "sms")
            if "slack" in user and "slack" in self.senders:
                self.send_notification(user["slack"], message, "slack")


def demo_good_dip():
    """Demonstrate proper DIP implementation."""
    print("\n" + "="*70)
    print("GOOD EXAMPLE: Following DIP - Depend on Abstractions")
    print("="*70)

    service = GoodNotificationService()

    # Register different notification senders
    print("\n1. Registering notification senders:")
    service.register_sender("email", EmailNotificationSender())
    service.register_sender("sms", SMSNotificationSender())
    service.register_sender("slack", SlackNotificationSender())

    # Users with different contact preferences
    users = [
        {"email": "john@example.com", "phone": "555-1234", "slack": "@john"},
        {"email": "jane@example.com", "slack": "@jane"}
    ]

    print("\n2. Sending notifications:")
    service.notify_users(users, "System maintenance scheduled for tonight")

    # Add new notification type without modifying NotificationService!
    print("\n3. Adding new notification type (Teams) at runtime:")
    service.register_sender("teams", TeamsNotificationSender())

    print("\nBenefits:")
    print("  ✓ NotificationService depends on abstraction, not concrete classes")
    print("  ✓ New senders can be added without modifying NotificationService")
    print("  ✓ Easy to register different implementations")
    print("  ✓ Easy to test with mock NotificationSender objects")
    print("  ✓ Loose coupling between high-level and low-level modules")


# ============================================================================
# REAL-WORLD EXAMPLE: Database Access
# ============================================================================

class Database(ABC):
    """Abstraction for database operations."""

    @abstractmethod
    def connect(self) -> bool:
        """Connect to database."""
        pass

    @abstractmethod
    def query(self, sql: str) -> List[dict]:
        """Execute a query."""
        pass

    @abstractmethod
    def execute(self, sql: str) -> bool:
        """Execute a command."""
        pass


class MySQLDatabase(Database):
    """MySQL implementation."""

    def connect(self) -> bool:
        print("✓ Connected to MySQL database")
        return True

    def query(self, sql: str) -> List[dict]:
        print(f"✓ Executing MySQL query: {sql}")
        return [{"id": 1, "name": "John"}]

    def execute(self, sql: str) -> bool:
        print(f"✓ Executing MySQL command: {sql}")
        return True


class PostgreSQLDatabase(Database):
    """PostgreSQL implementation."""

    def connect(self) -> bool:
        print("✓ Connected to PostgreSQL database")
        return True

    def query(self, sql: str) -> List[dict]:
        print(f"✓ Executing PostgreSQL query: {sql}")
        return [{"id": 1, "name": "Jane"}]

    def execute(self, sql: str) -> bool:
        print(f"✓ Executing PostgreSQL command: {sql}")
        return True


class MongoDBDatabase(Database):
    """MongoDB implementation."""

    def connect(self) -> bool:
        print("✓ Connected to MongoDB")
        return True

    def query(self, sql: str) -> List[dict]:
        print(f"✓ Executing MongoDB query: {sql}")
        return [{"_id": "507f1f77bcf86cd799439011", "name": "Bob"}]

    def execute(self, sql: str) -> bool:
        print(f"✓ Executing MongoDB command: {sql}")
        return True


class UserRepository:
    """
    High-level module that depends on Database abstraction,
    not on specific database implementations.
    """

    def __init__(self, database: Database):
        self.database = database
        self.database.connect()

    def get_user(self, user_id: int) -> dict:
        """Get user from database."""
        results = self.database.query(f"SELECT * FROM users WHERE id = {user_id}")
        return results[0] if results else {}

    def create_user(self, name: str, email: str) -> bool:
        """Create user in database."""
        sql = f"INSERT INTO users (name, email) VALUES ('{name}', '{email}')"
        return self.database.execute(sql)

    def update_user(self, user_id: int, name: str) -> bool:
        """Update user in database."""
        sql = f"UPDATE users SET name = '{name}' WHERE id = {user_id}"
        return self.database.execute(sql)


def demo_real_world():
    """Demonstrate real-world DIP usage."""
    print("\n" + "="*70)
    print("REAL-WORLD EXAMPLE: Database Abstraction with DIP")
    print("="*70)

    # Can use any database implementation without changing UserRepository
    print("\n1. Using MySQL database:")
    mysql_repo = UserRepository(MySQLDatabase())
    mysql_repo.get_user(1)
    mysql_repo.create_user("Alice", "alice@example.com")

    print("\n2. Switching to PostgreSQL (no changes to UserRepository):")
    postgres_repo = UserRepository(PostgreSQLDatabase())
    postgres_repo.get_user(1)
    postgres_repo.create_user("Bob", "bob@example.com")

    print("\n3. Switching to MongoDB (no changes to UserRepository):")
    mongo_repo = UserRepository(MongoDBDatabase())
    mongo_repo.get_user(1)
    mongo_repo.create_user("Charlie", "charlie@example.com")

    print("\nBenefit: UserRepository doesn't care which database is used.")
    print("We can switch databases without modifying UserRepository code.")


# ============================================================================
# DEPENDENCY INJECTION PATTERNS
# ============================================================================

class Logger(ABC):
    """Logger abstraction."""

    @abstractmethod
    def log(self, message: str) -> None:
        """Log a message."""
        pass


class ConsoleLogger(Logger):
    """Log to console."""

    def log(self, message: str) -> None:
        print(f"[CONSOLE] {message}")


class FileLogger(Logger):
    """Log to file."""

    def log(self, message: str) -> None:
        print(f"[FILE] {message}")


class Service:
    """
    Service that depends on Logger abstraction.
    Dependencies are injected, not created internally.
    This is Dependency Injection - a technique to follow DIP.
    """

    def __init__(self, logger: Logger):
        self.logger = logger  # Injected dependency

    def do_work(self) -> None:
        """Do some work and log it."""
        self.logger.log("Starting work...")
        # Do work
        self.logger.log("Work completed!")


def demo_dependency_injection():
    """Demonstrate dependency injection."""
    print("\n" + "="*70)
    print("DEPENDENCY INJECTION: A Technique to Implement DIP")
    print("="*70)

    print("\n1. Injecting ConsoleLogger:")
    service1 = Service(ConsoleLogger())
    service1.do_work()

    print("\n2. Injecting FileLogger:")
    service2 = Service(FileLogger())
    service2.do_work()

    print("\nBenefit: We control which Logger implementation is used.")
    print("Easy to test with mock loggers.")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DEPENDENCY INVERSION PRINCIPLE (DIP) EXAMPLES")
    print("="*70)

    # Bad example
    demo_bad_dip()

    # Good example
    demo_good_dip()

    # Real-world example
    demo_real_world()

    # Dependency injection
    demo_dependency_injection()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. Depend on abstractions, not on concrete implementations
2. Create interfaces/abstract classes for dependencies
3. Inject dependencies from outside (Constructor Injection)
4. High-level modules should not depend on low-level details
5. Use Dependency Injection to implement DIP
6. Makes code flexible and testable
7. Easy to swap implementations
8. Reduces coupling between modules
9. Makes adding new features easier
10. Use Design Patterns like Factory, Strategy, etc. with DIP
    """)
