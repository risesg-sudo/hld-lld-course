"""
SOLID PRINCIPLE #3: LISKOV SUBSTITUTION PRINCIPLE (LSP)
========================================================

Core Concept:
Objects of a superclass should be replaceable with objects of its subclasses
without breaking the application. In other words, derived classes must be
substitutable for their base classes without altering the correctness of
the program.

Benefits:
- Enables polymorphism to work correctly
- Prevents unexpected behavior when using inheritance
- Makes code more reliable and predictable
- Ensures contracts defined by parent classes are honored
- Allows safe use of base class references

Real-world analogy:
If you hire a person for a job, you expect them to fulfill the contract.
All employees should be able to do basic work tasks without surprising you.
A manager should not break when you ask them to do what a regular employee does.
"""

from abc import ABC, abstractmethod
import math


# ============================================================================
# BAD EXAMPLE: LSP Violation - Rectangle and Square Problem
# ============================================================================

class BadRectangle:
    """
    This class represents a rectangle with width and height.
    Subclasses are expected to maintain the rectangle contract.
    """

    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def set_width(self, width: float) -> None:
        self._width = width

    def set_height(self, height: float) -> None:
        self._height = height

    def get_area(self) -> float:
        return self._width * self._height

    def __repr__(self):
        return f"Rectangle({self._width}x{self._height}, area={self.get_area()})"


class BadSquare(BadRectangle):
    """
    This class VIOLATES LSP. A square IS-A rectangle mathematically,
    but this implementation breaks the Rectangle contract.

    When you set width or height on a square, both should change.
    This violates the expectation of a Rectangle where width and height
    are independent.
    """

    def __init__(self, side: float):
        super().__init__(side, side)

    def set_width(self, width: float) -> None:
        """Override to maintain square invariant - BREAKS RECTANGLE CONTRACT."""
        self._width = width
        self._height = width  # Force height to match (unexpected!)

    def set_height(self, height: float) -> None:
        """Override to maintain square invariant - BREAKS RECTANGLE CONTRACT."""
        self._width = height  # Force width to match (unexpected!)
        self._height = height

    def __repr__(self):
        return f"Square({self._width}x{self._height}, area={self.get_area()})"


def demo_bad_lsp():
    """Demonstrate LSP violation."""
    print("\n" + "="*70)
    print("BAD EXAMPLE: LSP Violation - Rectangle/Square Problem")
    print("="*70)

    # Using Rectangle as expected
    print("\n1. Using a proper Rectangle:")
    rect = BadRectangle(10, 5)
    print(f"   Created: {rect}")

    rect.set_width(20)
    print(f"   After set_width(20): {rect}")

    rect.set_height(8)
    print(f"   After set_height(8): {rect}")

    # Using Square - breaks the Rectangle contract!
    print("\n2. Using Square (which extends Rectangle):")
    square = BadSquare(5)
    print(f"   Created: {square}")

    square.set_width(10)
    print(f"   After set_width(10): {square}")
    print(f"   ⚠️  PROBLEM: Height changed unexpectedly!")

    # This breaks polymorphism
    print("\n3. Polymorphic usage - expecting Rectangle behavior:")
    shapes = [BadRectangle(10, 5), BadSquare(5)]

    for shape in shapes:
        print(f"\n   Original: {shape}")
        shape.set_width(20)
        print(f"   After set_width(20): {shape}")
        if isinstance(shape, BadSquare):
            print(f"   ⚠️  Square changed height unexpectedly!")

    print("\nProblems:")
    print("  - Square violates Rectangle's contract")
    print("  - set_width() doesn't behave as expected for Square")
    print("  - Polymorphism becomes unreliable")
    print("  - Client code must know about Square's special behavior")


# ============================================================================
# GOOD EXAMPLE: Following LSP - Correct Hierarchy
# ============================================================================

class Shape(ABC):
    """
    Abstract shape class that defines the contract for all shapes.
    """

    @abstractmethod
    def get_area(self) -> float:
        """Get the area of the shape."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the shape."""
        pass


class Rectangle(Shape):
    """
    Concrete rectangle implementation.
    Rectangle can have independent width and height.
    """

    def __init__(self, width: float, height: float):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        self._width = width
        self._height = height

    def set_width(self, width: float) -> None:
        """Set width - only affects width."""
        if width <= 0:
            raise ValueError("Width must be positive")
        self._width = width

    def set_height(self, height: float) -> None:
        """Set height - only affects height."""
        if height <= 0:
            raise ValueError("Height must be positive")
        self._height = height

    def get_width(self) -> float:
        return self._width

    def get_height(self) -> float:
        return self._height

    def get_area(self) -> float:
        """Area = width * height."""
        return self._width * self._height

    def get_name(self) -> str:
        return "Rectangle"

    def __repr__(self):
        return f"Rectangle({self._width}x{self._height}, area={self.get_area()})"


class Square(Shape):
    """
    Concrete square implementation.
    Square is a SEPARATE class, not a subclass of Rectangle.
    This respects LSP because Square doesn't pretend to be a Rectangle.
    """

    def __init__(self, side: float):
        if side <= 0:
            raise ValueError("Side must be positive")
        self._side = side

    def set_side(self, side: float) -> None:
        """Set side length."""
        if side <= 0:
            raise ValueError("Side must be positive")
        self._side = side

    def get_side(self) -> float:
        return self._side

    def get_area(self) -> float:
        """Area = side * side."""
        return self._side * self._side

    def get_name(self) -> str:
        return "Square"

    def __repr__(self):
        return f"Square({self._side}x{self._side}, area={self.get_area()})"


class Circle(Shape):
    """Circle implementation."""

    def __init__(self, radius: float):
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self._radius = radius

    def set_radius(self, radius: float) -> None:
        """Set radius."""
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self._radius = radius

    def get_radius(self) -> float:
        return self._radius

    def get_area(self) -> float:
        """Area = π * r²."""
        return math.pi * (self._radius ** 2)

    def get_name(self) -> str:
        return "Circle"

    def __repr__(self):
        return f"Circle(r={self._radius}, area={self.get_area():.2f})"


def demo_good_lsp():
    """Demonstrate proper LSP implementation."""
    print("\n" + "="*70)
    print("GOOD EXAMPLE: Following LSP - Correct Class Hierarchy")
    print("="*70)

    print("\n1. Rectangle (independent width and height):")
    rect = Rectangle(10, 5)
    print(f"   Created: {rect}")
    rect.set_width(20)
    print(f"   After set_width(20): {rect}")
    rect.set_height(8)
    print(f"   After set_height(8): {rect}")

    print("\n2. Square (always square):")
    square = Square(5)
    print(f"   Created: {square}")
    square.set_side(10)
    print(f"   After set_side(10): {square}")

    print("\n3. Circle:")
    circle = Circle(5)
    print(f"   Created: {circle}")
    circle.set_radius(10)
    print(f"   After set_radius(10): {circle}")

    print("\n4. Polymorphic usage - all shapes work correctly:")
    shapes: list[Shape] = [Rectangle(10, 5), Square(5), Circle(5)]

    total_area = 0
    for shape in shapes:
        area = shape.get_area()
        total_area += area
        print(f"   {shape.get_name():10} area: {area:8.2f}")

    print(f"   {'Total':10} area: {total_area:8.2f}")

    print("\nBenefits:")
    print("  ✓ Each shape follows its own contract")
    print("  ✓ No unexpected behavior changes")
    print("  ✓ Polymorphism works correctly")
    print("  ✓ Code using Shape works with any shape")


# ============================================================================
# REAL-WORLD EXAMPLE: Payment Methods
# ============================================================================

class PaymentMethod(ABC):
    """Abstract payment method that defines expected behavior."""

    @abstractmethod
    def pay(self, amount: float) -> bool:
        """Process payment - should return True if successful."""
        pass

    @abstractmethod
    def refund(self, amount: float) -> bool:
        """Process refund - should return True if successful."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get payment method name."""
        pass


class CreditCardPayment(PaymentMethod):
    """Credit card payment - supports both payment and refund."""

    def __init__(self, card_number: str):
        self.card_number = card_number
        self.balance = 0.0

    def pay(self, amount: float) -> bool:
        """Process payment."""
        self.balance += amount
        print(f"✓ Charged ${amount} to credit card")
        return True

    def refund(self, amount: float) -> bool:
        """Process refund."""
        if amount <= self.balance:
            self.balance -= amount
            print(f"✓ Refunded ${amount} to credit card")
            return True
        return False

    def get_name(self) -> str:
        return "Credit Card"


class CashPayment(PaymentMethod):
    """
    Cash payment - supports payment but NOT refund.
    This class correctly represents that you can't refund cash in a
    system where cash is already received.
    """

    def __init__(self):
        self.total_received = 0.0

    def pay(self, amount: float) -> bool:
        """Accept cash payment."""
        self.total_received += amount
        print(f"✓ Accepted ${amount} in cash")
        return True

    def refund(self, amount: float) -> bool:
        """Cash refunds should not happen through payment system."""
        # Instead of pretending we can refund, we raise an exception
        # This is honest about the limitation
        raise NotImplementedError("Cash refunds handled separately in accounting")

    def get_name(self) -> str:
        return "Cash"


class WalletPayment(PaymentMethod):
    """Wallet payment - requires checking balance first."""

    def __init__(self, balance: float):
        self.balance = balance

    def pay(self, amount: float) -> bool:
        """Process wallet payment if sufficient balance."""
        if amount <= self.balance:
            self.balance -= amount
            print(f"✓ Deducted ${amount} from wallet (remaining: ${self.balance})")
            return True
        else:
            print(f"✗ Insufficient balance. Have ${self.balance}, need ${amount}")
            return False

    def refund(self, amount: float) -> bool:
        """Refund to wallet."""
        self.balance += amount
        print(f"✓ Refunded ${amount} to wallet (new balance: ${self.balance})")
        return True

    def get_name(self) -> str:
        return "Wallet"


class CheckoutService:
    """
    Service that uses any payment method.
    Relies on LSP - any PaymentMethod can be substituted.
    """

    def process_payment(self, amount: float, method: PaymentMethod) -> bool:
        """Process payment using any payment method."""
        print(f"\nProcessing ${amount} via {method.get_name()}:")
        return method.pay(amount)

    def process_refund(self, amount: float, method: PaymentMethod) -> bool:
        """Process refund using any payment method."""
        print(f"Processing ${amount} refund via {method.get_name()}:")
        try:
            return method.refund(amount)
        except NotImplementedError as e:
            print(f"✗ Error: {e}")
            return False


def demo_real_world():
    """Demonstrate real-world LSP usage."""
    print("\n" + "="*70)
    print("REAL-WORLD EXAMPLE: Payment Methods with LSP")
    print("="*70)

    service = CheckoutService()

    print("\n1. Credit Card Payment:")
    cc = CreditCardPayment("4532-1234-5678-9012")
    service.process_payment(99.99, cc)
    service.process_refund(25.00, cc)

    print("\n2. Wallet Payment:")
    wallet = WalletPayment(200.0)
    service.process_payment(99.99, wallet)
    service.process_payment(50.00, wallet)  # This will fail due to insufficient balance
    service.process_refund(25.00, wallet)

    print("\n3. Cash Payment:")
    cash = CashPayment()
    service.process_payment(100.0, cash)
    service.process_refund(50.0, cash)  # This will raise NotImplementedError

    print("\nNote: All payment methods follow the PaymentMethod contract.")
    print("CheckoutService works with any payment method without issues.")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LISKOV SUBSTITUTION PRINCIPLE (LSP) EXAMPLES")
    print("="*70)

    # Bad example
    demo_bad_lsp()

    # Good example
    demo_good_lsp()

    # Real-world example
    demo_real_world()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. Subclasses must be substitutable for their base classes
2. Don't violate the parent class contract in subclasses
3. If a subclass can't fulfill the parent's contract, it shouldn't inherit
4. Preconditions cannot be strengthened in subclasses
5. Postconditions cannot be weakened in subclasses
6. Invariants of parent must be preserved in subclasses
7. History rule: subclasses should not introduce methods that break parent behavior
8. Use composition over inheritance when the IS-A relationship doesn't hold
9. Abstract base classes define a contract that all implementations must honor
    """)
