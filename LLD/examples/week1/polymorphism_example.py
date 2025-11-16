"""
Polymorphism Example: Payment Processing
Demonstrates how different objects can be treated through a common interface
"""

from abc import ABC, abstractmethod

# Base class defining the interface
class PaymentMethod(ABC):
    @abstractmethod
    def process_payment(self, amount):
        """Process payment - must be implemented by subclasses"""
        pass

    @abstractmethod
    def refund(self, transaction_id, amount):
        """Process refund - must be implemented by subclasses"""
        pass


# Different payment implementations
class CreditCardPayment(PaymentMethod):
    def __init__(self, card_number, cvv, expiry):
        self.card_number = card_number[-4:]  # Store only last 4 digits
        self.cvv = cvv
        self.expiry = expiry

    def process_payment(self, amount):
        # Simulate credit card processing
        return f"Processed ${amount} via Credit Card ending in {self.card_number}"

    def refund(self, transaction_id, amount):
        return f"Refunded ${amount} to Credit Card ending in {self.card_number} (Transaction: {transaction_id})"


class PayPalPayment(PaymentMethod):
    def __init__(self, email):
        self.email = email

    def process_payment(self, amount):
        return f"Processed ${amount} via PayPal account: {self.email}"

    def refund(self, transaction_id, amount):
        return f"Refunded ${amount} to PayPal: {self.email} (Transaction: {transaction_id})"


class CryptoPayment(PaymentMethod):
    def __init__(self, wallet_address, crypto_type="Bitcoin"):
        self.wallet_address = wallet_address
        self.crypto_type = crypto_type

    def process_payment(self, amount):
        return f"Processed ${amount} via {self.crypto_type} to wallet: {self.wallet_address[:10]}..."

    def refund(self, transaction_id, amount):
        return f"Refunded ${amount} in {self.crypto_type} to wallet: {self.wallet_address[:10]}... (Transaction: {transaction_id})"


class BankTransferPayment(PaymentMethod):
    def __init__(self, account_number, routing_number):
        self.account_number = account_number
        self.routing_number = routing_number

    def process_payment(self, amount):
        return f"Processed ${amount} via Bank Transfer (Account: ***{self.account_number[-4:]})"

    def refund(self, transaction_id, amount):
        return f"Refunded ${amount} via Bank Transfer (Transaction: {transaction_id})"


# Payment processor that works with any payment method
class PaymentProcessor:
    def __init__(self):
        self.transactions = []

    def execute_payment(self, payment_method: PaymentMethod, amount: float):
        """
        Polymorphism in action: works with any PaymentMethod subclass
        """
        result = payment_method.process_payment(amount)
        transaction_id = f"TXN{len(self.transactions) + 1:04d}"
        self.transactions.append({
            'id': transaction_id,
            'amount': amount,
            'method': payment_method.__class__.__name__,
            'result': result
        })
        return transaction_id, result

    def execute_refund(self, payment_method: PaymentMethod, transaction_id: str, amount: float):
        """
        Polymorphism: refund works regardless of payment method type
        """
        return payment_method.refund(transaction_id, amount)

    def get_transaction_summary(self):
        total = sum(t['amount'] for t in self.transactions)
        return f"Total transactions: {len(self.transactions)}, Total amount: ${total}"


# Usage Example
if __name__ == "__main__":
    # Create payment processor
    processor = PaymentProcessor()

    # Create different payment methods
    credit_card = CreditCardPayment("1234-5678-9012-3456", "123", "12/25")
    paypal = PayPalPayment("user@example.com")
    crypto = CryptoPayment("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Bitcoin")
    bank = BankTransferPayment("9876543210", "123456789")

    # Process payments using different methods (POLYMORPHISM!)
    # Same method call works for all payment types
    payment_methods = [
        (credit_card, 150.00),
        (paypal, 75.50),
        (crypto, 200.00),
        (bank, 500.00)
    ]

    print("Processing Payments:")
    print("=" * 70)
    for method, amount in payment_methods:
        txn_id, result = processor.execute_payment(method, amount)
        print(f"{txn_id}: {result}")

    print("\n" + processor.get_transaction_summary())

    print("\n" + "=" * 70)
    print("Processing Refunds:")
    print("=" * 70)

    # Process refunds (polymorphism again!)
    print(processor.execute_refund(credit_card, "TXN0001", 150.00))
    print(processor.execute_refund(paypal, "TXN0002", 75.50))

    """
    Output demonstrates polymorphism:
    - Same method calls (process_payment, refund) work for all payment types
    - PaymentProcessor doesn't need to know specific payment method details
    - Easy to add new payment methods without changing PaymentProcessor

    Key Benefits:
    1. Code flexibility - add new payment methods easily
    2. Maintainability - changes to one payment type don't affect others
    3. Testability - can test each payment method independently
    4. Extensibility - open for extension, closed for modification
    """
