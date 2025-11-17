"""
Polymorphism Example: Payment Processing System
Demonstrates how different payment methods can be used through a common interface
"""

from abc import ABC, abstractmethod

# Abstract base class defines the interface
class PaymentMethod(ABC):
    """
    Abstract payment method interface.
    All payment methods must implement these methods.
    """

    @abstractmethod
    def process_payment(self, amount):
        """Process a payment of the given amount."""
        pass

    @abstractmethod
    def refund(self, transaction_id, amount):
        """Process a refund."""
        pass


# Concrete implementations
class CreditCardPayment(PaymentMethod):
    """Credit card payment implementation."""

    def __init__(self, card_number, cvv, expiry):
        self.card_number = card_number[-4:]  # Store only last 4 digits
        self.cvv = cvv
        self.expiry = expiry

    def process_payment(self, amount):
        # Simulate credit card processing
        print(f"Processing ${amount} via Credit Card (ending in {self.card_number})")
        print(f"  - Validating card details...")
        print(f"  - Contacting payment gateway...")
        print(f"  - Payment authorized")
        return f"Transaction successful: ${amount} charged to card {self.card_number}"

    def refund(self, transaction_id, amount):
        print(f"Refunding ${amount} to credit card {self.card_number}")
        return f"Refund processed: ${amount} to transaction {transaction_id}"


class PayPalPayment(PaymentMethod):
    """PayPal payment implementation."""

    def __init__(self, email):
        self.email = email

    def process_payment(self, amount):
        print(f"Processing ${amount} via PayPal ({self.email})")
        print(f"  - Redirecting to PayPal...")
        print(f"  - User authenticated")
        print(f"  - Payment completed")
        return f"PayPal payment successful: ${amount} from {self.email}"

    def refund(self, transaction_id, amount):
        print(f"Initiating PayPal refund of ${amount} to {self.email}")
        return f"PayPal refund: ${amount} to {self.email}"


class CryptoPayment(PaymentMethod):
    """Cryptocurrency payment implementation."""

    def __init__(self, wallet_address, crypto_type="Bitcoin"):
        self.wallet_address = wallet_address
        self.crypto_type = crypto_type

    def process_payment(self, amount):
        print(f"Processing ${amount} via {self.crypto_type}")
        print(f"  - Converting to {self.crypto_type}...")
        print(f"  - Waiting for blockchain confirmation...")
        print(f"  - Transaction confirmed")
        return f"{self.crypto_type} payment: ${amount} to {self.wallet_address[:10]}..."

    def refund(self, transaction_id, amount):
        print(f"Processing {self.crypto_type} refund of ${amount}")
        return f"Crypto refund: ${amount} in {self.crypto_type}"


# Polymorphic payment processor
class PaymentProcessor:
    """
    Payment processor that works with ANY payment method.
    This class demonstrates polymorphism - it doesn't care about
    the specific payment type, only that it implements PaymentMethod.
    """

    def __init__(self):
        self.transactions = []

    def execute_payment(self, payment_method: PaymentMethod, amount: float):
        """
        Execute payment using any payment method.
        This method works polymorphically with all PaymentMethod types.
        """
        print(f"\n{'='*60}")
        print(f"Executing payment of ${amount}")
        print(f"{'='*60}")

        # Call the appropriate implementation based on actual type
        result = payment_method.process_payment(amount)

        # Record transaction
        transaction_id = f"TXN{len(self.transactions) + 1:04d}"
        self.transactions.append({
            'id': transaction_id,
            'amount': amount,
            'method': payment_method.__class__.__name__,
            'result': result
        })

        print(f"Transaction ID: {transaction_id}")
        return transaction_id

    def execute_refund(self, payment_method: PaymentMethod, transaction_id: str, amount: float):
        """Polymorphic refund - works with any payment method."""
        print(f"\n{'='*60}")
        print(f"Executing refund for transaction {transaction_id}")
        print(f"{'='*60}")

        # Polymorphism: same method call, different behavior
        result = payment_method.refund(transaction_id, amount)
        print(f"Refund completed")
        return result

    def get_summary(self):
        """Get transaction summary."""
        total = sum(t['amount'] for t in self.transactions)
        return {
            'total_transactions': len(self.transactions),
            'total_amount': total,
            'transactions': self.transactions
        }


# Demonstration
if __name__ == "__main__":
    print("=== Polymorphism in Payment Processing ===\n")

    # Create payment processor
    processor = PaymentProcessor()

    # Create different payment methods
    credit_card = CreditCardPayment("1234-5678-9012-3456", "123", "12/25")
    paypal = PayPalPayment("user@example.com")
    crypto = CryptoPayment("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Bitcoin")

    # Polymorphism in action: same method, different implementations
    print("\n*** Processing Different Payment Types ***")

    # Same method call works for all payment types
    processor.execute_payment(credit_card, 150.00)
    processor.execute_payment(paypal, 75.50)
    processor.execute_payment(crypto, 200.00)

    # Polymorphic refund processing
    print("\n\n*** Processing Refunds ***")
    processor.execute_refund(credit_card, "TXN0001", 50.00)
    processor.execute_refund(paypal, "TXN0002", 25.00)

    # Summary
    print("\n\n*** Transaction Summary ***")
    summary = processor.get_summary()
    print(f"Total Transactions: {summary['total_transactions']}")
    print(f"Total Amount: ${summary['total_amount']}")

    print("\n\n*** Key Polymorphism Benefits Demonstrated ***")
    print("1. Same interface (process_payment, refund) for all types")
    print("2. PaymentProcessor doesn't know specific implementation details")
    print("3. Easy to add new payment methods (just implement PaymentMethod)")
    print("4. Each payment type has its own unique behavior")
    print("5. Code using PaymentProcessor doesn't change when adding new types")
