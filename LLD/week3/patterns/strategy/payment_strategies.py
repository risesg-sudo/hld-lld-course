"""
Payment Strategy Pattern Example

Demonstrates how strategy pattern eliminates conditional complexity
when handling multiple payment methods.
"""

from abc import ABC, abstractmethod


# ============================================================================
# STRATEGY INTERFACE
# ============================================================================

class PaymentStrategy(ABC):
    """
    Strategy interface for payment processing.
    All payment methods implement this interface.
    """

    @abstractmethod
    def validate(self) -> bool:
        """Validate payment method details."""
        pass

    @abstractmethod
    def pay(self, amount: float) -> bool:
        """Process payment with this strategy."""
        pass


# ============================================================================
# CONCRETE STRATEGIES
# ============================================================================

class CreditCardPayment(PaymentStrategy):
    """Strategy for credit card payment."""

    def __init__(self, card_number: str, cvv: str, expiry: str):
        self.card_number = card_number
        self.cvv = cvv
        self.expiry = expiry

    def validate(self) -> bool:
        """Validate credit card details."""
        if len(self.card_number) < 13 or len(self.cvv) != 3:
            return False
        return True

    def pay(self, amount: float) -> bool:
        """Process credit card payment."""
        if not self.validate():
            print(f"Invalid credit card details")
            return False

        print(f"Processing ${amount:.2f} via Credit Card")
        print(f"  Card: ****-****-****-{self.card_number[-4:]}")
        print(f"  Payment successful")
        return True


class PayPalPayment(PaymentStrategy):
    """Strategy for PayPal payment."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def validate(self) -> bool:
        """Validate PayPal credentials."""
        if "@" not in self.email or len(self.password) < 6:
            return False
        return True

    def pay(self, amount: float) -> bool:
        """Process PayPal payment."""
        if not self.validate():
            print(f"Invalid PayPal credentials")
            return False

        print(f"Processing ${amount:.2f} via PayPal")
        print(f"  Email: {self.email}")
        print(f"  Authenticating...")
        print(f"  Payment successful")
        return True


class CryptocurrencyPayment(PaymentStrategy):
    """Strategy for cryptocurrency payment."""

    def __init__(self, wallet_address: str, coin_type: str = "BTC"):
        self.wallet_address = wallet_address
        self.coin_type = coin_type

    def validate(self) -> bool:
        """Validate wallet address."""
        if len(self.wallet_address) < 20:
            return False
        return True

    def pay(self, amount: float) -> bool:
        """Process cryptocurrency payment."""
        if not self.validate():
            print(f"Invalid wallet address")
            return False

        print(f"Processing {amount:.8f} {self.coin_type}")
        print(f"  Wallet: {self.wallet_address[:10]}...{self.wallet_address[-10:]}")
        print(f"  Confirming on blockchain...")
        print(f"  Payment successful")
        return True


# ============================================================================
# CONTEXT
# ============================================================================

class PaymentProcessor:
    """
    Context that uses payment strategies.

    Client code works with this context, not directly with strategies.
    Can switch strategies at runtime.
    """

    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: PaymentStrategy) -> None:
        """Change payment strategy at runtime."""
        self._strategy = strategy

    def process_payment(self, amount: float) -> bool:
        """Process payment using configured strategy."""
        print(f"\n{'='*50}")
        print(f"Payment Amount: ${amount:.2f}")
        print(f"Method: {self._strategy.__class__.__name__}")
        print(f"{'='*50}")

        return self._strategy.pay(amount)


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("STRATEGY PATTERN DEMONSTRATION")
    print("="*60)

    # Create processor with credit card strategy
    processor = PaymentProcessor(
        CreditCardPayment("4111111111111111", "123", "12/25")
    )

    # Process payment
    processor.process_payment(100.00)

    # Switch to PayPal strategy at runtime
    processor.set_strategy(
        PayPalPayment("user@example.com", "securepass123")
    )
    processor.process_payment(50.00)

    # Switch to cryptocurrency strategy
    processor.set_strategy(
        CryptocurrencyPayment("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "BTC")
    )
    processor.process_payment(0.005)

    print("\n" + "="*60)
    print("Key Observation:")
    print("  - Same processor interface for all payment methods")
    print("  - No if/else conditionals in client code")
    print("  - Easy to add new payment methods")
    print("  - Each strategy tested independently")
    print("="*60)
