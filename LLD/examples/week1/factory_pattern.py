"""
FACTORY PATTERN
===============

Type: Creational Design Pattern

Core Concept:
The Factory Pattern is a creational design pattern that deals with object
creation mechanisms. It provides an interface for creating objects without
specifying their exact classes.

Instead of:
    obj = ConcreteClass()

We use:
    obj = Factory.create(type_name)

Benefits:
- Decouples object creation from usage
- Centralizes object creation logic
- Makes it easy to add new types
- Reduces code duplication
- Makes testing easier
- Follows Single Responsibility and Open/Closed Principles

Real-world analogy:
A car factory produces different types of cars (Toyota, Honda, BMW).
You don't go to each manufacturer's plant; you go to the factory which
handles the creation and gives you the car you want.

When to use:
- When you have multiple classes that share a common interface
- When the exact type to create depends on runtime conditions
- When object creation is complex
"""

from abc import ABC, abstractmethod
from enum import Enum


# ============================================================================
# EXAMPLE 1: Simple Factory Pattern - Vehicle Factory
# ============================================================================

class Vehicle(ABC):
    """Abstract vehicle interface."""

    @abstractmethod
    def start(self) -> None:
        """Start the vehicle."""
        pass

    @abstractmethod
    def drive(self) -> None:
        """Drive the vehicle."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the vehicle."""
        pass

    @abstractmethod
    def get_vehicle_type(self) -> str:
        """Get vehicle type."""
        pass


class Car(Vehicle):
    """Concrete car implementation."""

    def start(self) -> None:
        print("✓ Car engine started")

    def drive(self) -> None:
        print("🚗 Driving car on the road")

    def stop(self) -> None:
        print("✓ Car stopped")

    def get_vehicle_type(self) -> str:
        return "Car"


class Motorcycle(Vehicle):
    """Concrete motorcycle implementation."""

    def start(self) -> None:
        print("✓ Motorcycle engine started")

    def drive(self) -> None:
        print("🏍️ Riding motorcycle on the road")

    def stop(self) -> None:
        print("✓ Motorcycle stopped")

    def get_vehicle_type(self) -> str:
        return "Motorcycle"


class Truck(Vehicle):
    """Concrete truck implementation."""

    def start(self) -> None:
        print("✓ Truck engine started")

    def drive(self) -> None:
        print("🚚 Driving truck with cargo")

    def stop(self) -> None:
        print("✓ Truck stopped")

    def get_vehicle_type(self) -> str:
        return "Truck"


class Bus(Vehicle):
    """Concrete bus implementation."""

    def start(self) -> None:
        print("✓ Bus engine started")

    def drive(self) -> None:
        print("🚌 Driving bus with passengers")

    def stop(self) -> None:
        print("✓ Bus stopped")

    def get_vehicle_type(self) -> str:
        return "Bus"


class VehicleType(Enum):
    """Enum for vehicle types."""
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    BUS = "bus"


class VehicleFactory:
    """
    Simple Factory for creating vehicles.
    This centralizes all vehicle creation logic.
    """

    @staticmethod
    def create_vehicle(vehicle_type: VehicleType) -> Vehicle:
        """
        Create a vehicle of the specified type.

        Args:
            vehicle_type: The type of vehicle to create

        Returns:
            A Vehicle instance of the requested type

        Raises:
            ValueError: If vehicle type is not recognized
        """
        if vehicle_type == VehicleType.CAR:
            return Car()
        elif vehicle_type == VehicleType.MOTORCYCLE:
            return Motorcycle()
        elif vehicle_type == VehicleType.TRUCK:
            return Truck()
        elif vehicle_type == VehicleType.BUS:
            return Bus()
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")


def demo_simple_factory():
    """Demonstrate simple factory pattern."""
    print("\n" + "="*70)
    print("SIMPLE FACTORY PATTERN: Vehicle Factory")
    print("="*70)

    # Using factory to create vehicles
    vehicles = [
        VehicleFactory.create_vehicle(VehicleType.CAR),
        VehicleFactory.create_vehicle(VehicleType.MOTORCYCLE),
        VehicleFactory.create_vehicle(VehicleType.TRUCK),
        VehicleFactory.create_vehicle(VehicleType.BUS),
    ]

    print("\nCreating and using vehicles:")
    for vehicle in vehicles:
        print(f"\n{vehicle.get_vehicle_type()}:")
        vehicle.start()
        vehicle.drive()
        vehicle.stop()

    print("\nBenefits:")
    print("  - Client code doesn't need to know about concrete classes")
    print("  - All vehicle creation logic is in one place")
    print("  - Easy to add new vehicle types (just add new class + condition)")


# ============================================================================
# EXAMPLE 2: Factory Method Pattern - Multi-Level Factory
# ============================================================================

class Logger(ABC):
    """Abstract logger interface."""

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


class DatabaseLogger(Logger):
    """Log to database."""

    def log(self, message: str) -> None:
        print(f"[DATABASE] {message}")


class LoggerFactory:
    """
    Factory for creating loggers based on type.
    Demonstrates factory method pattern where the factory is responsible
    for deciding which logger to create.
    """

    @staticmethod
    def create_logger(logger_type: str) -> Logger:
        """
        Create a logger of the specified type.

        Args:
            logger_type: Type of logger ('console', 'file', 'database')

        Returns:
            A Logger instance
        """
        if logger_type.lower() == "console":
            return ConsoleLogger()
        elif logger_type.lower() == "file":
            return FileLogger()
        elif logger_type.lower() == "database":
            return DatabaseLogger()
        else:
            raise ValueError(f"Unknown logger type: {logger_type}")


class Application:
    """
    Application that uses loggers created by factory.
    Application depends on abstraction (Logger), not concrete classes.
    """

    def __init__(self, logger_type: str):
        self.logger = LoggerFactory.create_logger(logger_type)

    def run(self) -> None:
        """Run the application."""
        self.logger.log("Application started")
        self.logger.log("Processing data...")
        self.logger.log("Application stopped")


def demo_factory_method():
    """Demonstrate factory method pattern."""
    print("\n" + "="*70)
    print("FACTORY METHOD PATTERN: Logger Factory")
    print("="*70)

    print("\n1. Application with console logger:")
    app1 = Application("console")
    app1.run()

    print("\n2. Application with file logger:")
    app2 = Application("file")
    app2.run()

    print("\n3. Application with database logger:")
    app3 = Application("database")
    app3.run()

    print("\nBenefits:")
    print("  - Application doesn't care which logger is used")
    print("  - Factory handles logger creation")
    print("  - Easy to add new logger types")


# ============================================================================
# EXAMPLE 3: Factory with Configuration
# ============================================================================

class Database(ABC):
    """Abstract database interface."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to database."""
        pass

    @abstractmethod
    def query(self, sql: str) -> list:
        """Execute a query."""
        pass


class MySQLDatabase(Database):
    """MySQL database."""

    def connect(self) -> None:
        print("✓ Connected to MySQL")

    def query(self, sql: str) -> list:
        print(f"Executing MySQL query: {sql}")
        return [{"id": 1, "name": "John"}]


class PostgreSQLDatabase(Database):
    """PostgreSQL database."""

    def connect(self) -> None:
        print("✓ Connected to PostgreSQL")

    def query(self, sql: str) -> list:
        print(f"Executing PostgreSQL query: {sql}")
        return [{"id": 1, "name": "Jane"}]


class MongoDB(Database):
    """MongoDB database."""

    def connect(self) -> None:
        print("✓ Connected to MongoDB")

    def query(self, sql: str) -> list:
        print(f"Executing MongoDB query: {sql}")
        return [{"_id": "507f1f77bcf86cd799439011", "name": "Bob"}]


class DatabaseFactory:
    """
    Database factory that creates databases based on configuration.
    This pattern is useful when the type is determined by configuration files.
    """

    @staticmethod
    def create_database(config: dict) -> Database:
        """
        Create a database based on configuration.

        Args:
            config: Configuration dictionary with 'type' key

        Returns:
            A Database instance
        """
        db_type = config.get("type", "mysql").lower()

        if db_type == "mysql":
            return MySQLDatabase()
        elif db_type == "postgresql":
            return PostgreSQLDatabase()
        elif db_type == "mongodb":
            return MongoDB()
        else:
            raise ValueError(f"Unknown database type: {db_type}")


def demo_factory_with_config():
    """Demonstrate factory with configuration."""
    print("\n" + "="*70)
    print("FACTORY WITH CONFIGURATION: Database Factory")
    print("="*70)

    # Different configurations
    configs = [
        {"type": "mysql", "host": "localhost"},
        {"type": "postgresql", "host": "db.example.com"},
        {"type": "mongodb", "host": "mongo.example.com"},
    ]

    print("\nCreating databases from configuration:")
    for config in configs:
        print(f"\nConfiguration: {config}")
        db = DatabaseFactory.create_database(config)
        db.connect()
        db.query("SELECT * FROM users")


# ============================================================================
# REAL-WORLD EXAMPLE: Payment Gateway Factory
# ============================================================================

class PaymentGateway(ABC):
    """Abstract payment gateway."""

    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        """Process payment."""
        pass

    @abstractmethod
    def get_gateway_name(self) -> str:
        """Get gateway name."""
        pass


class StripePayment(PaymentGateway):
    """Stripe payment gateway."""

    def process_payment(self, amount: float) -> bool:
        print(f"✓ Processing ${amount} via Stripe")
        return True

    def get_gateway_name(self) -> str:
        return "Stripe"


class PayPalPayment(PaymentGateway):
    """PayPal payment gateway."""

    def process_payment(self, amount: float) -> bool:
        print(f"✓ Processing ${amount} via PayPal")
        return True

    def get_gateway_name(self) -> str:
        return "PayPal"


class SquarePayment(PaymentGateway):
    """Square payment gateway."""

    def process_payment(self, amount: float) -> bool:
        print(f"✓ Processing ${amount} via Square")
        return True

    def get_gateway_name(self) -> str:
        return "Square"


class PaymentGatewayFactory:
    """
    Payment gateway factory.
    In real-world, this would be configured by environment or user preference.
    """

    _gateways = {
        "stripe": StripePayment,
        "paypal": PayPalPayment,
        "square": SquarePayment,
    }

    @staticmethod
    def create_gateway(gateway_name: str) -> PaymentGateway:
        """Create payment gateway."""
        gateway_class = PaymentGatewayFactory._gateways.get(gateway_name.lower())
        if not gateway_class:
            raise ValueError(f"Unknown payment gateway: {gateway_name}")
        return gateway_class()

    @staticmethod
    def register_gateway(name: str, gateway_class):
        """Register a new payment gateway - extensible!"""
        PaymentGatewayFactory._gateways[name.lower()] = gateway_class

    @staticmethod
    def available_gateways() -> list[str]:
        """Get list of available gateways."""
        return list(PaymentGatewayFactory._gateways.keys())


class ECommerceStore:
    """E-commerce store that uses payment gateway factory."""

    def __init__(self, preferred_gateway: str):
        self.gateway = PaymentGatewayFactory.create_gateway(preferred_gateway)

    def checkout(self, amount: float) -> bool:
        """Checkout using configured payment gateway."""
        print(f"Checking out ${amount}")
        return self.gateway.process_payment(amount)


def demo_real_world():
    """Demonstrate real-world factory pattern."""
    print("\n" + "="*70)
    print("REAL-WORLD EXAMPLE: Payment Gateway Factory")
    print("="*70)

    print("\nAvailable gateways:", PaymentGatewayFactory.available_gateways())

    print("\n1. Store using Stripe:")
    store1 = ECommerceStore("stripe")
    store1.checkout(99.99)

    print("\n2. Store using PayPal:")
    store2 = ECommerceStore("paypal")
    store2.checkout(49.99)

    print("\n3. Store using Square:")
    store3 = ECommerceStore("square")
    store3.checkout(199.99)

    print("\nBenefit: Easy to add new payment gateways or switch between them.")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("FACTORY PATTERN EXAMPLES")
    print("="*70)

    # Simple factory example
    demo_simple_factory()

    # Factory method example
    demo_factory_method()

    # Factory with configuration
    demo_factory_with_config()

    # Real-world example
    demo_real_world()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. Factory pattern centralizes object creation
2. Decouples client code from concrete classes
3. Makes adding new types easier (just add new class)
4. Uses abstraction and polymorphism
5. Types of factories:
   - Simple Factory: Single method that creates objects
   - Factory Method: Subclasses decide which class to instantiate
   - Abstract Factory: Creates families of related objects
6. Useful when:
   - Object creation is complex
   - Many similar classes exist
   - The type to create depends on runtime conditions
7. Follows SOLID principles (OCP, DIP, SRP)
8. Improves testability with mock objects
    """)
