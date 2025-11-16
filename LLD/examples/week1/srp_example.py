"""
SOLID PRINCIPLE #1: SINGLE RESPONSIBILITY PRINCIPLE (SRP)
==========================================================

Core Concept:
A class should have one, and only one, reason to change. Each class should
have a single, well-defined responsibility and should encapsulate that
responsibility completely.

Benefits:
- Classes are easier to understand
- Classes are easier to test
- Classes are easier to modify and extend
- Reduces code duplication
- Better maintainability and flexibility

Real-world analogy:
A chef's job is to cook, a waiter's job is to serve. Each has one responsibility.
Don't ask a chef to cook AND serve AND clean tables.
"""


# ============================================================================
# BAD EXAMPLE: Multiple Responsibilities (SRP Violation)
# ============================================================================

class BadUser:
    """
    This class violates SRP by having multiple responsibilities:
    1. Managing user data
    2. Validating user data
    3. Saving to database
    4. Sending emails
    5. Logging activities
    """

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def validate_email(self) -> bool:
        """Responsibility #2: Validate email."""
        if "@" not in self.email or "." not in self.email.split("@")[1]:
            return False
        return True

    def validate_name(self) -> bool:
        """Responsibility #2: Validate name."""
        if not self.name or len(self.name) < 2:
            return False
        return True

    def save_to_database(self) -> bool:
        """Responsibility #3: Database operations."""
        # Simulate database save
        print(f"Saving user {self.name} to database")
        return True

    def send_welcome_email(self) -> bool:
        """Responsibility #4: Email operations."""
        # Simulate sending email
        print(f"Sending welcome email to {self.email}")
        return True

    def log_user_creation(self) -> None:
        """Responsibility #5: Logging operations."""
        # Simulate logging
        print(f"LOG: User {self.name} created at 2024-01-15 10:00:00")

    def create_user(self) -> bool:
        """Create user with all mixed responsibilities."""
        if not self.validate_email():
            return False

        if not self.validate_name():
            return False

        if not self.save_to_database():
            return False

        if not self.send_welcome_email():
            return False

        self.log_user_creation()
        return True


def demo_bad_srp():
    """Demonstrate SRP violation."""
    print("\n" + "="*70)
    print("BAD EXAMPLE: SRP Violation - Multiple Responsibilities")
    print("="*70)

    print("\nCreating user with BadUser class:")
    user = BadUser("John Doe", "john@example.com")
    user.create_user()

    print("\nProblems:")
    print("  - Too many reasons to change this class")
    print("  - Hard to test individual functionality")
    print("  - Difficult to reuse validation logic elsewhere")
    print("  - Changes to database code affect this class")
    print("  - Changes to email code affect this class")
    print("  - Changes to logging affect this class")


# ============================================================================
# GOOD EXAMPLE: Single Responsibility (Following SRP)
# ============================================================================

class User:
    """
    Responsibility: Manage user data only.
    """

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"User(name='{self.name}', email='{self.email}')"


class UserValidator:
    """
    Responsibility: Validate user data.
    """

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email format."""
        if not email:
            return False, "Email is required"

        if "@" not in email or "." not in email.split("@")[1]:
            return False, "Invalid email format"

        return True, "Email is valid"

    @staticmethod
    def validate_name(name: str) -> tuple[bool, str]:
        """Validate name format."""
        if not name:
            return False, "Name is required"

        if len(name) < 2:
            return False, "Name must be at least 2 characters"

        return True, "Name is valid"

    @staticmethod
    def validate_user(user: User) -> tuple[bool, str]:
        """Validate complete user object."""
        is_valid, msg = UserValidator.validate_name(user.name)
        if not is_valid:
            return False, msg

        is_valid, msg = UserValidator.validate_email(user.email)
        if not is_valid:
            return False, msg

        return True, "User is valid"


class UserRepository:
    """
    Responsibility: Handle database operations.
    """

    def __init__(self):
        self.users = {}  # Simulate database
        self.next_id = 1

    def save(self, user: User) -> int:
        """Save user to database and return ID."""
        user_id = self.next_id
        self.users[user_id] = user
        self.next_id += 1
        print(f"✓ Saved user to database with ID: {user_id}")
        return user_id

    def get(self, user_id: int) -> User:
        """Retrieve user from database."""
        return self.users.get(user_id)

    def get_all(self) -> dict:
        """Get all users from database."""
        return self.users.copy()

    def delete(self, user_id: int) -> bool:
        """Delete user from database."""
        if user_id in self.users:
            del self.users[user_id]
            print(f"✓ Deleted user {user_id} from database")
            return True
        return False


class EmailService:
    """
    Responsibility: Send emails.
    """

    @staticmethod
    def send_welcome_email(user: User) -> bool:
        """Send welcome email to user."""
        print(f"✓ Sent welcome email to {user.email}")
        return True

    @staticmethod
    def send_notification(user: User, message: str) -> bool:
        """Send notification email to user."""
        print(f"✓ Sent notification to {user.email}: {message}")
        return True


class Logger:
    """
    Responsibility: Log activities.
    """

    @staticmethod
    def log(message: str) -> None:
        """Log a message."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG {timestamp}] {message}")


class UserService:
    """
    Orchestrates user creation using separate classes with single responsibilities.
    This class coordinates the different services.
    """

    def __init__(self, repository: UserRepository, email_service: EmailService):
        self.repository = repository
        self.email_service = email_service
        self.validator = UserValidator()

    def create_user(self, name: str, email: str) -> tuple[bool, int]:
        """Create a new user using coordinated services."""
        # Create user object
        user = User(name, email)

        # Validate user
        is_valid, message = self.validator.validate_user(user)
        if not is_valid:
            Logger.log(f"Validation failed: {message}")
            return False, -1

        # Save to database
        user_id = self.repository.save(user)

        # Send welcome email
        self.email_service.send_welcome_email(user)

        # Log the activity
        Logger.log(f"User '{name}' created successfully with ID {user_id}")

        return True, user_id


def demo_good_srp():
    """Demonstrate proper SRP implementation."""
    print("\n" + "="*70)
    print("GOOD EXAMPLE: Following SRP - Single Responsibilities")
    print("="*70)

    # Initialize services
    repository = UserRepository()
    email_service = EmailService()
    user_service = UserService(repository, email_service)

    print("\n1. Creating first user:")
    success, user_id = user_service.create_user("Alice Johnson", "alice@example.com")

    print("\n2. Creating second user:")
    success, user_id = user_service.create_user("Bob Smith", "bob@example.com")

    print("\n3. Attempting to create invalid user:")
    success, user_id = user_service.create_user("X", "invalid-email")

    print("\n4. Retrieving users from database:")
    all_users = repository.get_all()
    for uid, user in all_users.items():
        print(f"   User {uid}: {user}")

    print("\nBenefits of SRP:")
    print("  ✓ Each class has ONE reason to change")
    print("  ✓ Easy to test each component independently")
    print("  ✓ Easy to reuse validators, email service, logging elsewhere")
    print("  ✓ Easy to swap implementations (e.g., different database)")
    print("  ✓ Code is more maintainable and flexible")


# ============================================================================
# REAL-WORLD EXAMPLE: E-Commerce Order Processing
# ============================================================================

class Order:
    """Responsibility: Represent an order."""

    def __init__(self, order_id: int, items: list, total: float):
        self.order_id = order_id
        self.items = items
        self.total = total


class PaymentProcessor:
    """Responsibility: Process payments."""

    @staticmethod
    def process_payment(order: Order, card_number: str) -> bool:
        """Process payment for order."""
        print(f"✓ Processing payment of ${order.total} for order {order.order_id}")
        return True


class ShippingService:
    """Responsibility: Handle shipping."""

    @staticmethod
    def create_shipment(order: Order) -> str:
        """Create shipment for order."""
        tracking_number = f"SHIP-{order.order_id}-2024"
        print(f"✓ Created shipment with tracking number: {tracking_number}")
        return tracking_number


class NotificationService:
    """Responsibility: Send notifications."""

    @staticmethod
    def notify_order_confirmed(order: Order, customer_email: str) -> bool:
        """Notify customer of order confirmation."""
        print(f"✓ Sent order confirmation to {customer_email}")
        return True

    @staticmethod
    def notify_order_shipped(order: Order, tracking_number: str, customer_email: str) -> bool:
        """Notify customer of shipment."""
        print(f"✓ Sent shipping notification to {customer_email}")
        print(f"  Tracking: {tracking_number}")
        return True


class OrderProcessor:
    """
    Coordinates order processing using separate services.
    Orchestrates the workflow but doesn't handle individual responsibilities.
    """

    def __init__(self, payment_processor: PaymentProcessor, shipping_service: ShippingService,
                 notification_service: NotificationService):
        self.payment_processor = payment_processor
        self.shipping_service = shipping_service
        self.notification_service = notification_service

    def process_order(self, order: Order, card_number: str, customer_email: str) -> bool:
        """Process complete order workflow."""
        # Process payment
        if not self.payment_processor.process_payment(order, card_number):
            return False

        # Notify confirmation
        self.notification_service.notify_order_confirmed(order, customer_email)

        # Create shipment
        tracking_number = self.shipping_service.create_shipment(order)

        # Notify shipment
        self.notification_service.notify_order_shipped(order, tracking_number, customer_email)

        return True


def demo_real_world():
    """Demonstrate real-world SRP usage."""
    print("\n" + "="*70)
    print("REAL-WORLD EXAMPLE: E-Commerce Order Processing")
    print("="*70)

    # Initialize services
    payment_processor = PaymentProcessor()
    shipping_service = ShippingService()
    notification_service = NotificationService()
    order_processor = OrderProcessor(payment_processor, shipping_service, notification_service)

    print("\nProcessing order:")
    order = Order(order_id=1001, items=["Laptop", "Mouse"], total=1050.00)
    order_processor.process_order(order, "4532-1234-5678-9012", "customer@example.com")

    print("\nWhy SRP helps here:")
    print("  - Can change payment processing without affecting shipping")
    print("  - Can swap email with SMS notification service")
    print("  - Can test each service independently")
    print("  - Easy to add new services like inventory management")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SINGLE RESPONSIBILITY PRINCIPLE (SRP) EXAMPLES")
    print("="*70)

    # Bad example
    demo_bad_srp()

    # Good example
    demo_good_srp()

    # Real-world example
    demo_real_world()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. A class should have only ONE reason to change
2. Identify all responsibilities a class has
3. Extract each responsibility into a separate class
4. Use composition to combine services
5. A class should do one thing and do it well
6. Single responsibility makes classes reusable
7. Easier to test and maintain
8. Follows the principle: Separation of Concerns
    """)
