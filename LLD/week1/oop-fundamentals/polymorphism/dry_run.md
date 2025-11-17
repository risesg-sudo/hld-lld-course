# Dry Run: Polymorphic Payment Processing

This trace demonstrates how polymorphism allows different payment methods to be used interchangeably through a common interface.

## Initial Setup

```python
processor = PaymentProcessor()
credit_card = CreditCardPayment("1234-5678-9012-3456", "123", "12/25")
paypal = PayPalPayment("user@example.com")
crypto = CryptoPayment("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Bitcoin")
```

### Memory State

**Processor:**
```
transactions: []
```

**credit_card (CreditCardPayment instance):**
```
card_number: "3456"  (last 4 digits)
cvv: "123"
expiry: "12/25"
```

**paypal (PayPalPayment instance):**
```
email: "user@example.com"
```

**crypto (CryptoPayment instance):**
```
wallet_address: "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
crypto_type: "Bitcoin"
```

---

## Operation 1: Polymorphic Payment with Credit Card

```python
processor.execute_payment(credit_card, 150.00)
```

### Execution Steps

**Step 1**: `execute_payment(credit_card, 150.00)` is called
- `payment_method` parameter receives `credit_card` object
- `payment_method` has type `PaymentMethod` (interface)
- Actual object is `CreditCardPayment` (concrete implementation)

**Step 2**: Call `payment_method.process_payment(150.00)`
- Python performs dynamic dispatch
- Looks up actual type: CreditCardPayment
- Calls `CreditCardPayment.process_payment(150.00)`

**Step 3**: `CreditCardPayment.process_payment()` executes
- Prints: "Processing $150.0 via Credit Card (ending in 3456)"
- Simulates credit card processing steps
- Returns: "Transaction successful: $150.0 charged to card 3456"

**Step 4**: Record transaction
- Create transaction_id: "TXN0001"
- Add to transactions list

### Memory State After Operation

**Processor:**
```
transactions: [
    {
        'id': 'TXN0001',
        'amount': 150.00,
        'method': 'CreditCardPayment',
        'result': 'Transaction successful: $150.0 charged to card 3456'
    }
]
```

### Polymorphism in Action

The `execute_payment` method:
- Accepts parameter of type `PaymentMethod` (abstract)
- Receives `CreditCardPayment` (concrete)
- Doesn't know or care about specific implementation
- Calls `process_payment()` which resolves to credit card logic

---

## Operation 2: Polymorphic Payment with PayPal

```python
processor.execute_payment(paypal, 75.50)
```

### Execution Steps

**Step 1**: `execute_payment(paypal, 75.50)` is called
- Same method signature as before
- Different concrete type (PayPalPayment instead of CreditCardPayment)

**Step 2**: Call `payment_method.process_payment(75.50)`
- Dynamic dispatch occurs
- Actual type: PayPalPayment
- Calls `PayPalPayment.process_payment(75.50)`

**Step 3**: `PayPalPayment.process_payment()` executes
- Completely different logic than credit card
- Prints: "Processing $75.5 via PayPal (user@example.com)"
- Simulates PayPal-specific flow
- Returns: "PayPal payment successful: $75.5 from user@example.com"

**Step 4**: Record transaction with ID "TXN0002"

### Memory State After Operation

**Processor:**
```
transactions: [
    {
        'id': 'TXN0001',
        'amount': 150.00,
        'method': 'CreditCardPayment',
        'result': '...'
    },
    {
        'id': 'TXN0002',
        'amount': 75.50,
        'method': 'PayPalPayment',
        'result': 'PayPal payment successful: $75.5 from user@example.com'
    }
]
```

### Key Observation

**Same method call, different behavior:**
- `execute_payment` code is identical
- Different `process_payment` implementation is called
- Behavior determined by actual object type at runtime

---

## Operation 3: Polymorphic Payment with Cryptocurrency

```python
processor.execute_payment(crypto, 200.00)
```

### Execution Steps

**Step 1-2**: Dynamic dispatch to `CryptoPayment.process_payment(200.00)`

**Step 3**: `CryptoPayment.process_payment()` executes
- Again, different implementation
- Prints: "Processing $200.0 via Bitcoin"
- Simulates blockchain confirmation
- Returns: "Bitcoin payment: $200.0 to 1A1zP1eP5Q..."

### Memory State After Operation

**Processor:**
```
transactions: [
    {...},  // TXN0001 - Credit Card
    {...},  // TXN0002 - PayPal
    {
        'id': 'TXN0003',
        'amount': 200.00,
        'method': 'CryptoPayment',
        'result': 'Bitcoin payment: $200.0 to 1A1zP1eP5Q...'
    }
]
```

---

## Polymorphism Visualization

```
processor.execute_payment(payment_method, amount)
           ↓
payment_method.process_payment(amount)
           ↓
    Runtime Type Lookup
           ↓
    ┌──────┴──────┬──────────┐
    ↓             ↓          ↓
CreditCard    PayPal      Crypto
.process()  .process()  .process()
```

Each type provides different implementation of the same interface method.

---

## Operation 4: Polymorphic Refund

```python
processor.execute_refund(credit_card, "TXN0001", 50.00)
```

### Execution Steps

**Step 1**: `execute_refund(credit_card, "TXN0001", 50.00)` called

**Step 2**: Dynamic dispatch to `CreditCardPayment.refund("TXN0001", 50.00)`

**Step 3**: `CreditCardPayment.refund()` executes
- Prints: "Refunding $50.0 to credit card 3456"
- Returns: "Refund processed: $50.0 to transaction TXN0001"

### Method Resolution Process

```
execute_refund receives PaymentMethod interface
    ↓
Actual object: CreditCardPayment
    ↓
Method lookup: refund() in CreditCardPayment
    ↓
Execute CreditCardPayment.refund()
```

---

## Adding New Payment Type at Runtime

```python
class ApplePayPayment(PaymentMethod):
    def process_payment(self, amount):
        return f"Apple Pay: ${amount}"

    def refund(self, transaction_id, amount):
        return f"Apple Pay refund: ${amount}"

apple_pay = ApplePayPayment()
processor.execute_payment(apple_pay, 99.99)
```

### What Happens

**Step 1**: New class implements `PaymentMethod` interface

**Step 2**: `execute_payment` called with new type
- Method signature doesn't change
- No modification to `PaymentProcessor`
- Polymorphism handles new type automatically

**Step 3**: `ApplePayPayment.process_payment()` is called
- Works seamlessly with existing code

### This Demonstrates

**Open/Closed Principle**: System is:
- Open for extension (new payment types)
- Closed for modification (no changes to PaymentProcessor)

---

## Final State Summary

**Processor transactions:**
```
Total: 3 transactions
Total amount: $425.50

[0] TXN0001 - CreditCardPayment - $150.00
[1] TXN0002 - PayPalPayment - $75.50
[2] TXN0003 - CryptoPayment - $200.00
```

---

## Key Polymorphism Principles Demonstrated

### 1. Single Interface, Multiple Implementations

```
PaymentMethod (interface)
    ↓
┌───────┼────────┬──────────┐
↓       ↓        ↓          ↓
Credit  PayPal   Crypto   (Future types)
```

### 2. Runtime Type Resolution

- Compiler knows: parameter is PaymentMethod
- Runtime knows: actual type is CreditCardPayment/PayPal/Crypto
- Correct implementation called at runtime

### 3. Decoupling

```
PaymentProcessor
    ↓ (depends on)
PaymentMethod (abstraction)
    ↑ (implemented by)
Concrete types (CreditCard, PayPal, etc.)
```

PaymentProcessor never depends on concrete types.

### 4. Extensibility

Adding new payment types:
- Create new class implementing PaymentMethod
- No changes to PaymentProcessor needed
- Existing code continues to work

### 5. Substitutability (Liskov Substitution)

Any PaymentMethod subtype can be used wherever PaymentMethod is expected:

```python
methods = [credit_card, paypal, crypto, apple_pay]
for method in methods:
    processor.execute_payment(method, 100)  # All work!
```

---

## Benefits Observed

1. **Flexibility**: Easy to add new payment types
2. **Maintainability**: Changes isolated to specific implementations
3. **Testability**: Can test each payment type independently
4. **Reusability**: PaymentProcessor works with any payment type
5. **Scalability**: System grows without modifying core logic

This demonstrates polymorphism enabling flexible, extensible, and maintainable code through abstraction and dynamic dispatch.
