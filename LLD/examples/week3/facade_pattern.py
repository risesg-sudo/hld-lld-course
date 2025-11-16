"""
Facade Pattern - Provide a unified, simplified interface to a set of interfaces in a subsystem.

This module demonstrates various facade implementations:
1. Home theater system - integrating multiple components
2. E-commerce checkout - simplifying order process
3. Database API - simplifying complex database operations
4. Graphics library - simplifying complex rendering
5. Web framework - simplifying HTTP handling
6. Computer startup - simplifying complex subsystem initialization

Key Learning Points:
- Facade provides simple interface to complex subsystem
- Clients interact with facade, not subsystem components
- Facade coordinates subsystem components
- Facade is optional - clients can use subsystem directly
- Don't hide important functionality
- Single entry point but don't create God object
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# ============================================================================
# 1. HOME THEATER SUBSYSTEM
# ============================================================================

class Light:
    """Lighting subsystem."""

    def turn_on(self) -> None:
        print("Lights are on")

    def turn_off(self) -> None:
        print("Lights are off")

    def dim(self, level: int) -> None:
        print(f"Lights dimmed to {level}%")


class Screen:
    """Screen subsystem."""

    def up(self) -> None:
        print("Screen going up")

    def down(self) -> None:
        print("Screen going down")


class Projector:
    """Projector subsystem."""

    def __init__(self, dvd_player: "DVDPlayer"):
        self.dvd_player = dvd_player

    def on(self) -> None:
        print("Projector on")

    def off(self) -> None:
        print("Projector off")

    def wide_screen_mode(self) -> None:
        print("Projector in wide screen mode")

    def tv_mode(self) -> None:
        print("Projector in TV mode")


class DVDPlayer:
    """DVD player subsystem."""

    def __init__(self):
        self.movie = ""

    def on(self) -> None:
        print("DVD player on")

    def off(self) -> None:
        print("DVD player off")

    def play(self, movie: str) -> None:
        self.movie = movie
        print(f"Now playing '{movie}'")

    def stop(self) -> None:
        print("DVD stopped")

    def eject(self) -> None:
        print("DVD ejected")


class SoundSystem:
    """Sound system subsystem."""

    def on(self) -> None:
        print("Sound system on")

    def off(self) -> None:
        print("Sound system off")

    def set_volume(self, volume: int) -> None:
        print(f"Volume set to {volume}")


class PopcornMaker:
    """Popcorn maker subsystem."""

    def on(self) -> None:
        print("Popcorn maker warming up")

    def off(self) -> None:
        print("Popcorn maker off")

    def pop(self) -> None:
        print("Popcorn is popping!")


class HomeTheaterFacade:
    """
    Facade that simplifies home theater system.

    Coordinates multiple subsystems (lights, screen, projector, etc.)
    """

    def __init__(
        self,
        light: Light,
        screen: Screen,
        projector: Projector,
        dvd: DVDPlayer,
        sound: SoundSystem,
        popcorn: PopcornMaker
    ):
        self.light = light
        self.screen = screen
        self.projector = projector
        self.dvd = dvd
        self.sound = sound
        self.popcorn = popcorn

    def watch_movie(self, movie: str) -> None:
        """Simplified interface to watch a movie."""
        print(f"\n{'='*50}")
        print(f"Starting movie: {movie}")
        print('='*50)

        self.popcorn.on()
        self.popcorn.pop()
        self.light.dim(10)
        self.screen.down()
        self.projector.on()
        self.projector.wide_screen_mode()
        self.sound.on()
        self.sound.set_volume(75)
        self.dvd.on()
        self.dvd.play(movie)

    def end_movie(self) -> None:
        """Simplified interface to stop movie."""
        print(f"\n{'='*50}")
        print("Ending movie")
        print('='*50)

        self.dvd.stop()
        self.dvd.off()
        self.projector.off()
        self.sound.off()
        self.screen.up()
        self.light.turn_on()
        self.popcorn.off()

    def listen_to_radio(self) -> None:
        """Listen to radio through system."""
        print(f"\n{'='*50}")
        print("Radio mode")
        print('='*50)

        self.light.dim(20)
        self.sound.on()
        self.sound.set_volume(50)
        print("Radio playing...")


# ============================================================================
# 2. E-COMMERCE CHECKOUT SUBSYSTEM
# ============================================================================

class Product:
    """Product entity."""

    def __init__(self, product_id: str, name: str, price: float):
        self.product_id = product_id
        self.name = name
        self.price = price


class Inventory:
    """Inventory subsystem."""

    def __init__(self):
        self.products: Dict[str, int] = {
            "LAPTOP": 5,
            "MOUSE": 20,
            "KEYBOARD": 15
        }

    def check_stock(self, product_id: str) -> int:
        """Check if product is in stock."""
        return self.products.get(product_id, 0)

    def reserve(self, product_id: str, quantity: int) -> bool:
        """Reserve product."""
        if self.check_stock(product_id) >= quantity:
            self.products[product_id] -= quantity
            print(f"Inventory: Reserved {quantity}x {product_id}")
            return True
        return False

    def release(self, product_id: str, quantity: int) -> None:
        """Release reserved product."""
        self.products[product_id] += quantity
        print(f"Inventory: Released {quantity}x {product_id}")


class PaymentProcessor:
    """Payment processing subsystem."""

    def process(self, amount: float, method: str) -> bool:
        """Process payment."""
        if amount > 0:
            print(f"Payment: Processing ${amount:.2f} via {method}")
            return True
        return False

    def refund(self, transaction_id: str, amount: float) -> bool:
        """Refund payment."""
        print(f"Payment: Refunding ${amount:.2f} (transaction: {transaction_id})")
        return True


class Shipping:
    """Shipping subsystem."""

    def estimate_cost(self, weight: float, destination: str) -> float:
        """Estimate shipping cost."""
        base = 5.0
        per_kg = 2.0
        destination_cost = 10.0 if destination == "international" else 0
        return base + (weight * per_kg) + destination_cost

    def ship(self, order_id: str, address: str) -> str:
        """Ship order."""
        tracking_id = f"TRACK{order_id}"
        print(f"Shipping: Shipping order {order_id} to {address}")
        print(f"Shipping: Tracking ID: {tracking_id}")
        return tracking_id


class NotificationService:
    """Notification subsystem."""

    def send_order_confirmation(self, email: str, order_id: str) -> None:
        """Send order confirmation."""
        print(f"Notification: Sending order confirmation to {email}")

    def send_shipment_notification(self, email: str, tracking_id: str) -> None:
        """Send shipment notification."""
        print(f"Notification: Sending shipment update to {email}")


class CheckoutFacade:
    """
    Facade that simplifies e-commerce checkout process.

    Coordinates inventory, payment, shipping, and notifications.
    """

    def __init__(
        self,
        inventory: Inventory,
        payment: PaymentProcessor,
        shipping: Shipping,
        notification: NotificationService
    ):
        self.inventory = inventory
        self.payment = payment
        self.shipping = shipping
        self.notification = notification

    def checkout(
        self,
        products: List[tuple],  # (product_id, quantity)
        payment_method: str,
        shipping_address: str,
        email: str
    ) -> Optional[str]:
        """
        Simplified checkout process.

        Returns order ID on success, None on failure.
        """
        print(f"\n{'='*50}")
        print("Starting checkout")
        print('='*50)

        # Check inventory
        print("\n1. Checking inventory...")
        total_weight = 0
        total_price = 0
        order_id = f"ORD{datetime.now().timestamp()}"

        for product_id, quantity in products:
            if not self.inventory.check_stock(product_id) >= quantity:
                print(f"Error: {product_id} out of stock")
                return None
            print(f"✓ {product_id} available")
            total_weight += quantity * 0.5  # Assume 0.5 kg per item
            total_price += quantity * 100  # Assume $100 per item

        # Reserve inventory
        print("\n2. Reserving inventory...")
        for product_id, quantity in products:
            self.inventory.reserve(product_id, quantity)

        # Calculate shipping
        print("\n3. Calculating shipping...")
        shipping_cost = self.shipping.estimate_cost(total_weight, "domestic")
        total_price += shipping_cost
        print(f"Shipping cost: ${shipping_cost:.2f}")

        # Process payment
        print("\n4. Processing payment...")
        if not self.payment.process(total_price, payment_method):
            print("Payment failed!")
            # Release reserved inventory
            for product_id, quantity in products:
                self.inventory.release(product_id, quantity)
            return None

        # Ship order
        print("\n5. Arranging shipment...")
        tracking_id = self.shipping.ship(order_id, shipping_address)

        # Send notifications
        print("\n6. Sending notifications...")
        self.notification.send_order_confirmation(email, order_id)
        self.notification.send_shipment_notification(email, tracking_id)

        print(f"\n✓ Order {order_id} completed successfully!")
        print(f"  Total: ${total_price:.2f}")
        print(f"  Tracking: {tracking_id}")

        return order_id


# ============================================================================
# 3. DATABASE API FACADE
# ============================================================================

class Connection:
    """Database connection."""

    def open(self) -> None:
        print("Database: Opening connection")

    def close(self) -> None:
        print("Database: Closing connection")


class Query:
    """Query builder."""

    def __init__(self):
        self.sql = ""

    def select(self, columns: str) -> "Query":
        self.sql = f"SELECT {columns}"
        return self

    def from_table(self, table: str) -> "Query":
        self.sql += f" FROM {table}"
        return self

    def where(self, condition: str) -> "Query":
        self.sql += f" WHERE {condition}"
        return self

    def execute(self) -> List[Dict]:
        print(f"Database: Executing: {self.sql}")
        return [{"id": 1, "name": "John"}]


class Transaction:
    """Transaction support."""

    def begin(self) -> None:
        print("Database: BEGIN TRANSACTION")

    def commit(self) -> None:
        print("Database: COMMIT")

    def rollback(self) -> None:
        print("Database: ROLLBACK")


class DatabaseFacade:
    """
    Facade that simplifies database operations.

    Handles connection, queries, and transactions.
    """

    def __init__(self):
        self.connection = Connection()
        self.transaction = Transaction()

    def get_user(self, user_id: int) -> Dict:
        """Get user by ID."""
        print(f"\nFacade: Getting user {user_id}")
        self.connection.open()

        query = Query().select("*").from_table("users").where(f"id = {user_id}")
        results = query.execute()

        self.connection.close()
        return results[0] if results else {}

    def create_user(self, name: str, email: str) -> bool:
        """Create new user."""
        print(f"\nFacade: Creating user {name}")
        self.connection.open()
        self.transaction.begin()

        # Execute insert
        print(f"Database: INSERT INTO users VALUES ('{name}', '{email}')")

        self.transaction.commit()
        self.connection.close()
        return True

    def update_user(self, user_id: int, name: str) -> bool:
        """Update user."""
        print(f"\nFacade: Updating user {user_id}")
        self.connection.open()
        self.transaction.begin()

        print(f"Database: UPDATE users SET name = '{name}' WHERE id = {user_id}")

        self.transaction.commit()
        self.connection.close()
        return True


# ============================================================================
# 4. DEMONSTRATION
# ============================================================================

def demo_home_theater():
    """Demonstrate home theater facade."""
    print("\n" + "="*60)
    print("FACADE PATTERN - HOME THEATER EXAMPLE")
    print("="*60)

    # Create subsystems
    light = Light()
    screen = Screen()
    projector = Projector(None)
    dvd = DVDPlayer()
    sound = SoundSystem()
    popcorn = PopcornMaker()

    # Create facade
    theater = HomeTheaterFacade(light, screen, projector, dvd, sound, popcorn)

    # Use facade
    theater.watch_movie("The Matrix")
    theater.end_movie()

    print("\n" + "-"*60)
    theater.listen_to_radio()


def demo_ecommerce_checkout():
    """Demonstrate e-commerce facade."""
    print("\n" + "="*60)
    print("FACADE PATTERN - E-COMMERCE CHECKOUT EXAMPLE")
    print("="*60)

    # Create subsystems
    inventory = Inventory()
    payment = PaymentProcessor()
    shipping = Shipping()
    notification = NotificationService()

    # Create facade
    checkout = CheckoutFacade(inventory, payment, shipping, notification)

    # Use facade
    order_id = checkout.checkout(
        products=[("LAPTOP", 1), ("MOUSE", 2)],
        payment_method="credit_card",
        shipping_address="123 Main St",
        email="user@example.com"
    )

    if not order_id:
        print("Checkout failed!")


def demo_database_facade():
    """Demonstrate database facade."""
    print("\n" + "="*60)
    print("FACADE PATTERN - DATABASE FACADE EXAMPLE")
    print("="*60)

    # Create facade
    db = DatabaseFacade()

    # Use facade - simple operations
    user = db.get_user(1)
    print(f"Retrieved user: {user}")

    db.create_user("Alice", "alice@example.com")
    db.update_user(1, "Alice Updated")


def demo_facade_benefits():
    """Demonstrate facade pattern benefits."""
    print("\n" + "="*60)
    print("FACADE PATTERN - BENEFITS")
    print("="*60)

    print("""
KEY BENEFITS:

1. SIMPLIFICATION
   - Complex subsystem appears simple to client
   - Hides complexity behind simple interface
   - Reduces learning curve

2. DECOUPLING
   - Client decoupled from subsystem details
   - Changes to subsystem don't affect client
   - Easier to maintain and evolve

3. SINGLE ENTRY POINT
   - Clear interface to subsystem
   - Easier to understand how to use system
   - Coordinates related operations

4. COMMON USE CASES
   - Simplifying common workflows
   - Bundling related operations
   - Reducing parameter lists

5. LAYERED ARCHITECTURE
   - Provides layer interface
   - Separates concerns
   - Clean architecture

FACADE vs OTHER PATTERNS:
- Facade: Simplifies complex subsystem
- Adapter: Makes incompatible interfaces compatible
- Bridge: Decouples abstraction from implementation
- Decorator: Adds behavior to objects
- Proxy: Controls access to object

NOT THE SAME AS:
- Facade doesn't prevent access to subsystem components
- Client can use subsystem directly if needed
- Facade is optional convenience, not mandatory
    """)


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

"""
KEY TAKEAWAYS - FACADE PATTERN:

1. WHEN TO USE:
   - Complex subsystems with many components
   - Want simple interface for common use cases
   - Need layered architecture
   - Coordinating multiple related operations
   - Simplifying API for library users

2. FACADE vs ADAPTER:
   - Facade: Simplifies (many to one)
   - Adapter: Makes compatible (incompatible to compatible)
   - Facade for complexity, Adapter for incompatibility

3. FACADE vs DECORATOR:
   - Facade: Simplifies complex system
   - Decorator: Adds behavior to objects
   - Facade is structural, Decorator is behavioral

4. DESIGN GUIDELINES:
   - Keep facade simple
   - Don't expose all subsystem functionality
   - Provide common use case methods
   - Allow advanced usage directly
   - Avoid God object (too many methods)

5. COMMON PITFALLS:
   - Making facade too complex
   - Hiding important functionality
   - Making facade mandatory (should be optional)
   - Over-generalizing interface
   - Facade becomes bottleneck

6. REAL WORLD EXAMPLES:
   - Spring Framework (simplified Java configuration)
   - Django ORM (database abstraction)
   - Requests library (HTTP simplified)
   - jQuery (DOM manipulation)
   - Operating systems (system calls)
   - Web frameworks (routing, middleware)
   - Third-party service SDKs
   - Game engines (physics, graphics, audio APIs)

7. MULTIPLE FACADES:
   - Can have multiple facades for different use cases
   - Different clients, different facades
   - Advanced and simple interfaces
   - Specialized facades for special cases

8. TESTING:
   - Easy to test facade
   - Can mock subsystem components
   - Facade simplifies testing client code
   - Test subsystem separately
"""


if __name__ == "__main__":
    demo_home_theater()
    demo_ecommerce_checkout()
    demo_database_facade()
    demo_facade_benefits()

    print("\n" + "="*60)
    print("All Facade Pattern examples completed!")
    print("="*60)
