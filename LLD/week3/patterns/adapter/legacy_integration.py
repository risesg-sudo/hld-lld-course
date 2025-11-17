"""
Adapter Pattern Example

Demonstrates how adapter pattern integrates legacy systems
with modern interfaces without rewriting client code.
"""

from abc import ABC, abstractmethod


# ============================================================================
# TARGET INTERFACE (What Client Expects)
# ============================================================================

class PaymentProcessor(ABC):
    """Modern payment processor interface."""

    @abstractmethod
    def process_payment(self, amount: float, card_number: str) -> bool:
        """Process payment with card."""
        pass

    @abstractmethod
    def get_transaction_id(self) -> str:
        """Get last transaction ID."""
        pass


# ============================================================================
# MODERN IMPLEMENTATION
# ============================================================================

class ModernPaymentProcessor(PaymentProcessor):
    """Modern payment processor with clean interface."""

    def __init__(self):
        self.last_transaction = ""

    def process_payment(self, amount: float, card_number: str) -> bool:
        """Process payment."""
        self.last_transaction = f"TXN-{hash(card_number) % 10000}"
        print(f"Modern Processor: Processing ${amount:.2f}")
        print(f"  Card: ****{card_number[-4:]}")
        print(f"  Transaction: {self.last_transaction}")
        return True

    def get_transaction_id(self) -> str:
        """Get transaction ID."""
        return self.last_transaction


# ============================================================================
# ADAPTEE (Legacy System with Different Interface)
# ============================================================================

class LegacyPaymentSystem:
    """
    Legacy payment system with incompatible interface.

    This represents old code we can't modify.
    Different method names, different parameters.
    """

    def __init__(self):
        self.last_payment_id = ""

    def make_payment(self, sum_amount, payment_details, merchant_code):
        """
        Legacy method with different signature.

        Note: Different parameter names and order than modern interface.
        """
        self.last_payment_id = f"LEG-{merchant_code}-{int(sum_amount)}"
        print(f"Legacy System: Payment of ${sum_amount}")
        print(f"  Details: {payment_details}")
        print(f"  Merchant: {merchant_code}")
        print(f"  Payment ID: {self.last_payment_id}")
        return {"status": "success", "id": self.last_payment_id}

    def get_last_payment_reference(self):
        """Legacy method to get payment ID (different name)."""
        return self.last_payment_id


# ============================================================================
# ADAPTER (Makes Legacy Compatible with Modern Interface)
# ============================================================================

class LegacyPaymentAdapter(PaymentProcessor):
    """
    Adapter that makes legacy payment system compatible with modern interface.

    Implements PaymentProcessor interface, delegates to LegacyPaymentSystem.
    """

    def __init__(self, legacy_system: LegacyPaymentSystem, merchant_code: str = "MERCH123"):
        self.legacy_system = legacy_system
        self.merchant_code = merchant_code

    def process_payment(self, amount: float, card_number: str) -> bool:
        """
        Translate modern interface to legacy interface.

        Modern interface: process_payment(amount, card_number)
        Legacy interface: make_payment(sum_amount, payment_details, merchant_code)
        """
        # Prepare parameters in legacy format
        payment_details = f"Card ending in {card_number[-4:]}"

        # Call legacy method with translated parameters
        result = self.legacy_system.make_payment(
            sum_amount=amount,
            payment_details=payment_details,
            merchant_code=self.merchant_code
        )

        # Translate legacy result to modern expectation
        return result["status"] == "success"

    def get_transaction_id(self) -> str:
        """
        Translate modern interface to legacy interface.

        Modern interface: get_transaction_id()
        Legacy interface: get_last_payment_reference()
        """
        return self.legacy_system.get_last_payment_reference()


# ============================================================================
# CLIENT CODE
# ============================================================================

def checkout(processor: PaymentProcessor, amount: float, card: str) -> None:
    """
    Client code that works with any PaymentProcessor.

    Doesn't know whether it's using modern or legacy implementation.
    Programs against the interface, not the implementation.
    """
    print(f"\n{'='*60}")
    print(f"Processing checkout for ${amount:.2f}")
    print(f"{'='*60}")

    success = processor.process_payment(amount, card)

    if success:
        transaction_id = processor.get_transaction_id()
        print(f"\nCheckout successful!")
        print(f"Transaction ID: {transaction_id}")
    else:
        print(f"\nCheckout failed!")


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("ADAPTER PATTERN DEMONSTRATION")
    print("="*60)

    # Test with modern implementation
    print("\n1. Using Modern Payment Processor:")
    modern = ModernPaymentProcessor()
    checkout(modern, 100.00, "4111111111111111")

    # Test with legacy system via adapter
    print("\n2. Using Legacy System (via Adapter):")
    legacy = LegacyPaymentSystem()
    adapter = LegacyPaymentAdapter(legacy, "STORE_456")
    checkout(adapter, 75.50, "5555555555554444")

    print("\n" + "="*60)
    print("Key Observation:")
    print("  - checkout() works with both implementations")
    print("  - Client code unchanged for legacy system")
    print("  - Adapter translates between incompatible interfaces")
    print("  - Easy to add new payment systems via adapters")
    print("="*60)
