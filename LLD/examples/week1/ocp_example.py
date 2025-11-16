"""
SOLID PRINCIPLE #2: OPEN/CLOSED PRINCIPLE (OCP)
================================================

Core Concept:
Software entities (classes, modules, functions) should be OPEN for extension
but CLOSED for modification. You should be able to add new functionality
without changing existing code.

Benefits:
- New features can be added without modifying existing code
- Reduces risk of breaking existing functionality
- Easier to maintain and extend codebase
- Promotes code reusability
- Follows polymorphism and abstraction concepts

Real-world analogy:
A power outlet is open for extension (you can plug different devices) but
closed for modification (you don't open it to modify how electricity flows).
"""

from abc import ABC, abstractmethod
from enum import Enum
from decimal import Decimal


# ============================================================================
# BAD EXAMPLE: Violating OCP - Modifying for Every New Discount Type
# ============================================================================

class BadDiscountCalculator:
    """
    This class violates OCP because we need to modify it every time
    we want to add a new discount type. It's CLOSED for extension but
    OPEN for modification (the opposite of what we want).
    """

    def calculate_discount(self, amount: float, discount_type: str) -> float:
        """Calculate discount based on type - needs modification for new types."""

        if discount_type == "percentage":
            # 10% discount
            return amount * 0.1

        elif discount_type == "fixed":
            # $10 fixed discount
            return 10.0

        elif discount_type == "bulk":
            # $5 discount for orders over $100
            if amount > 100:
                return 5.0
            return 0.0

        elif discount_type == "loyalty":
            # $2 per $100 spent
            return (amount // 100) * 2

        # Adding a new discount type requires MODIFYING this method!
        elif discount_type == "seasonal":
            return amount * 0.15

        else:
            raise ValueError(f"Unknown discount type: {discount_type}")

    def apply_discount(self, amount: float, discount_type: str) -> float:
        """Apply discount to amount."""
        discount = self.calculate_discount(amount, discount_type)
        return amount - discount


def demo_bad_ocp():
    """Demonstrate OCP violation."""
    print("\n" + "="*70)
    print("BAD EXAMPLE: OCP Violation - Must Modify for New Discounts")
    print("="*70)

    calculator = BadDiscountCalculator()

    print("\n1. Percentage discount:")
    final_price = calculator.apply_discount(100, "percentage")
    print(f"   Original: $100, Final: ${final_price}")

    print("\n2. Fixed discount:")
    final_price = calculator.apply_discount(100, "fixed")
    print(f"   Original: $100, Final: ${final_price}")

    print("\n3. Bulk discount:")
    final_price = calculator.apply_discount(150, "bulk")
    print(f"   Original: $150, Final: ${final_price}")

    print("\nProblems:")
    print("  - Adding new discount type requires modifying this class")
    print("  - Risk of breaking existing functionality")
    print("  - Method becomes longer and more complex")
    print("  - Hard to test individual discount types")


# ============================================================================
# GOOD EXAMPLE: Following OCP - Use Polymorphism
# ============================================================================

class DiscountStrategy(ABC):
    """
    Abstract base class for discount strategies.
    This allows new discount types to be added WITHOUT modifying existing code.
    The class is CLOSED for modification but OPEN for extension.
    """

    @abstractmethod
    def calculate(self, amount: float) -> float:
        """Calculate discount amount."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get discount name."""
        pass


class PercentageDiscount(DiscountStrategy):
    """Percentage-based discount."""

    def __init__(self, percentage: float):
        self.percentage = percentage

    def calculate(self, amount: float) -> float:
        """Calculate percentage discount."""
        return amount * (self.percentage / 100)

    def get_name(self) -> str:
        return f"Percentage ({self.percentage}%)"


class FixedDiscount(DiscountStrategy):
    """Fixed amount discount."""

    def __init__(self, amount: float):
        self.amount = amount

    def calculate(self, amount: float) -> float:
        """Calculate fixed discount."""
        return self.amount

    def get_name(self) -> str:
        return f"Fixed (${self.amount})"


class BulkDiscount(DiscountStrategy):
    """Discount for bulk orders."""

    def __init__(self, min_amount: float, discount_amount: float):
        self.min_amount = min_amount
        self.discount_amount = discount_amount

    def calculate(self, amount: float) -> float:
        """Calculate bulk discount."""
        if amount > self.min_amount:
            return self.discount_amount
        return 0.0

    def get_name(self) -> str:
        return f"Bulk (>${self.min_amount})"


class LoyaltyDiscount(DiscountStrategy):
    """Discount based on loyalty (per $100 spent)."""

    def __init__(self, discount_per_hundred: float):
        self.discount_per_hundred = discount_per_hundred

    def calculate(self, amount: float) -> float:
        """Calculate loyalty discount."""
        return (amount // 100) * self.discount_per_hundred

    def get_name(self) -> str:
        return f"Loyalty (${self.discount_per_hundred} per $100)"


class SeasonalDiscount(DiscountStrategy):
    """Seasonal discount (e.g., holiday sale)."""

    def __init__(self, percentage: float):
        self.percentage = percentage

    def calculate(self, amount: float) -> float:
        """Calculate seasonal discount."""
        return amount * (self.percentage / 100)

    def get_name(self) -> str:
        return f"Seasonal ({self.percentage}% off)"


class GoodDiscountCalculator:
    """
    This class is OPEN for extension (new discount strategies can be added)
    but CLOSED for modification (the calculate method never changes).
    """

    def apply_discount(self, amount: float, discount_strategy: DiscountStrategy) -> float:
        """Apply a discount strategy - this method NEVER changes."""
        discount = discount_strategy.calculate(amount)
        final_price = max(0, amount - discount)  # Prevent negative price
        return final_price


def demo_good_ocp():
    """Demonstrate proper OCP implementation."""
    print("\n" + "="*70)
    print("GOOD EXAMPLE: Following OCP - Open for Extension, Closed for Modification")
    print("="*70)

    calculator = GoodDiscountCalculator()

    # Test different discount strategies
    test_amount = 150.0

    discounts = [
        PercentageDiscount(10),
        FixedDiscount(10),
        BulkDiscount(100, 5),
        LoyaltyDiscount(2),
        SeasonalDiscount(15)
    ]

    print(f"\nApplying discounts to ${test_amount}:")
    print("-" * 70)

    for discount in discounts:
        final_price = calculator.apply_discount(test_amount, discount)
        discount_amount = test_amount - final_price
        print(f"{discount.get_name():30} | Discount: ${discount_amount:6.2f} | Final: ${final_price:6.2f}")

    print("\nBenefits:")
    print("  ✓ Can add new discount types without modifying calculator")
    print("  ✓ Each discount type is in its own class")
    print("  ✓ Easy to test each discount independently")
    print("  ✓ Easy to reuse discount strategies")


# ============================================================================
# DEMONSTRATION: Adding New Discount Type (No Modification Needed)
# ============================================================================

class ReferralDiscount(DiscountStrategy):
    """
    NEW discount type - added WITHOUT modifying GoodDiscountCalculator!
    This demonstrates the power of OCP.
    """

    def __init__(self, referral_count: int, discount_per_referral: float):
        self.referral_count = referral_count
        self.discount_per_referral = discount_per_referral

    def calculate(self, amount: float) -> float:
        """Calculate referral discount."""
        return self.referral_count * self.discount_per_referral

    def get_name(self) -> str:
        return f"Referral ({self.referral_count} referrals @ ${self.discount_per_referral})"


def demo_extension():
    """Show how easy it is to add new functionality with OCP."""
    print("\n" + "="*70)
    print("EXTENSION: Adding New Discount Type Without Modifying Calculator")
    print("="*70)

    calculator = GoodDiscountCalculator()
    test_amount = 100.0

    print(f"\nUsing NEW ReferralDiscount (never existed before):")
    referral_discount = ReferralDiscount(5, 3.0)  # 5 referrals @ $3 each
    final_price = calculator.apply_discount(test_amount, referral_discount)
    discount_amount = test_amount - final_price

    print(f"{referral_discount.get_name():30}")
    print(f"  Original: ${test_amount}")
    print(f"  Discount: ${discount_amount}")
    print(f"  Final: ${final_price}")

    print("\nNote: GoodDiscountCalculator was NOT modified!")
    print("This is the power of Open/Closed Principle.")


# ============================================================================
# REAL-WORLD EXAMPLE: Payment Processing System
# ============================================================================

class PaymentProcessor(ABC):
    """Abstract payment processor - open for extension."""

    @abstractmethod
    def process(self, amount: float, details: dict) -> bool:
        """Process payment."""
        pass

    @abstractmethod
    def get_method_name(self) -> str:
        """Get payment method name."""
        pass


class CreditCardProcessor(PaymentProcessor):
    """Credit card payment processing."""

    def process(self, amount: float, details: dict) -> bool:
        """Process credit card payment."""
        print(f"✓ Processing ${amount} via Credit Card")
        print(f"  Card ending in {details.get('card_last_four', '****')}")
        return True

    def get_method_name(self) -> str:
        return "Credit Card"


class PayPalProcessor(PaymentProcessor):
    """PayPal payment processing."""

    def process(self, amount: float, details: dict) -> bool:
        """Process PayPal payment."""
        print(f"✓ Processing ${amount} via PayPal")
        print(f"  Account: {details.get('email', 'unknown')}")
        return True

    def get_method_name(self) -> str:
        return "PayPal"


class ApplePayProcessor(PaymentProcessor):
    """Apple Pay payment processing."""

    def process(self, amount: float, details: dict) -> bool:
        """Process Apple Pay payment."""
        print(f"✓ Processing ${amount} via Apple Pay")
        return True

    def get_method_name(self) -> str:
        return "Apple Pay"


class GooglePayProcessor(PaymentProcessor):
    """Google Pay payment processing - NEW without modifying existing code!"""

    def process(self, amount: float, details: dict) -> bool:
        """Process Google Pay payment."""
        print(f"✓ Processing ${amount} via Google Pay")
        return True

    def get_method_name(self) -> str:
        return "Google Pay"


class PaymentGateway:
    """Payment gateway - closed for modification, open for extension."""

    def process_payment(self, amount: float, processor: PaymentProcessor, details: dict) -> bool:
        """Process payment using any payment processor."""
        print(f"\nProcessing payment via {processor.get_method_name()}:")
        return processor.process(amount, details)


def demo_real_world():
    """Demonstrate real-world OCP usage."""
    print("\n" + "="*70)
    print("REAL-WORLD EXAMPLE: Payment Processing System")
    print("="*70)

    gateway = PaymentGateway()
    amount = 99.99

    # Process with different payment methods
    processors = [
        CreditCardProcessor(),
        PayPalProcessor(),
        ApplePayProcessor(),
        GooglePayProcessor()  # NEW processor - no changes to PaymentGateway
    ]

    for processor in processors:
        details = {
            'card_last_four': '4242' if isinstance(processor, CreditCardProcessor) else None,
            'email': 'user@example.com' if isinstance(processor, PayPalProcessor) else None
        }
        gateway.process_payment(amount, processor, details)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("OPEN/CLOSED PRINCIPLE (OCP) EXAMPLES")
    print("="*70)

    # Bad example
    demo_bad_ocp()

    # Good example
    demo_good_ocp()

    # Demonstrate extension
    demo_extension()

    # Real-world example
    demo_real_world()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. Use abstraction and inheritance to allow extension without modification
2. Define abstract base classes for common behavior patterns
3. Implement new functionality by creating new classes, not modifying existing ones
4. Use polymorphism to handle different implementations
5. Apply the Strategy pattern for interchangeable behaviors
6. Each new feature should be in a new class, not a new conditional
7. This reduces bugs from modifying tested code
8. Makes code more maintainable and scalable
    """)
