# Dry Run: Payment Strategy Pattern

This document traces the execution of the payment strategy pattern step-by-step, showing how objects interact in memory.

## Initial Setup

We start by creating a payment processor with a credit card strategy.

```python
processor = PaymentProcessor(
    CreditCardPayment("4111111111111111", "123", "12/25")
)
```

### Step 1: Create Credit Card Strategy

**Object Creation**:
```
CreditCardPayment instance created
  card_number: "4111111111111111"
  cvv: "123"
  expiry: "12/25"

Memory address: 0x1001
```

### Step 2: Create Payment Processor

**Object Creation**:
```
PaymentProcessor instance created
  _strategy: <reference to CreditCardPayment at 0x1001>

Memory address: 0x2001
```

**Memory State**:
```
0x2001: PaymentProcessor
  |
  +---> _strategy: 0x1001 (CreditCardPayment)

0x1001: CreditCardPayment
  card_number: "4111111111111111"
  cvv: "123"
  expiry: "12/25"
```

## Operation 1: Process Credit Card Payment

```python
processor.process_payment(100.00)
```

### Step 1: Enter PaymentProcessor.process_payment()

**Current Context**:
```
self = PaymentProcessor at 0x2001
amount = 100.00
self._strategy = CreditCardPayment at 0x1001
```

**Print statements execute**:
```
Output: "Payment Amount: $100.00"
Output: "Method: CreditCardPayment"
```

### Step 2: Delegate to Strategy

**Method Call**:
```
self._strategy.pay(100.00)
→ CreditCardPayment.pay(100.00)
```

**Enters CreditCardPayment.pay()**:
```
self = CreditCardPayment at 0x1001
amount = 100.00
```

### Step 3: Validate Credit Card

**Method Call**:
```
self.validate()
```

**Validation Logic**:
```
Check: len("4111111111111111") < 13?
  → 16 < 13 = False ✓

Check: len("123") != 3?
  → 3 != 3 = False ✓

Return: True
```

### Step 4: Process Payment

**Since validation passed**:
```
Output: "Processing $100.00 via Credit Card"
Output: "  Card: ****-****-****-1111"
Output: "  Payment successful"

Return: True
```

### Step 5: Return to Context

**Back in PaymentProcessor.process_payment()**:
```
Result: True
Return: True to caller
```

**Final State After First Payment**:
```
0x2001: PaymentProcessor
  _strategy: 0x1001 (still CreditCardPayment)
```

## Operation 2: Switch to PayPal Strategy

```python
processor.set_strategy(
    PayPalPayment("user@example.com", "securepass123")
)
```

### Step 1: Create PayPal Strategy

**Object Creation**:
```
PayPalPayment instance created
  email: "user@example.com"
  password: "securepass123"

Memory address: 0x1002
```

### Step 2: Update Processor Strategy

**Method Call**:
```
PaymentProcessor.set_strategy(PayPalPayment at 0x1002)
```

**Update Reference**:
```
Before:
  self._strategy = 0x1001 (CreditCardPayment)

After:
  self._strategy = 0x1002 (PayPalPayment)
```

**Memory State**:
```
0x2001: PaymentProcessor
  |
  +---> _strategy: 0x1002 (PayPalPayment)  [CHANGED]

0x1001: CreditCardPayment
  (no longer referenced, eligible for garbage collection)

0x1002: PayPalPayment
  email: "user@example.com"
  password: "securepass123"
```

## Operation 3: Process PayPal Payment

```python
processor.process_payment(50.00)
```

### Step 1: Enter PaymentProcessor.process_payment()

**Current Context**:
```
self = PaymentProcessor at 0x2001
amount = 50.00
self._strategy = PayPalPayment at 0x1002  [CHANGED STRATEGY]
```

**Print statements execute**:
```
Output: "Payment Amount: $50.00"
Output: "Method: PayPalPayment"  [DIFFERENT FROM BEFORE]
```

### Step 2: Delegate to Strategy

**Method Call**:
```
self._strategy.pay(50.00)
→ PayPalPayment.pay(50.00)  [DIFFERENT STRATEGY CALLED]
```

**Enters PayPalPayment.pay()**:
```
self = PayPalPayment at 0x1002
amount = 50.00
```

### Step 3: Validate PayPal

**Method Call**:
```
self.validate()
```

**Validation Logic**:
```
Check: "@" not in "user@example.com"?
  → False (@ is present) ✓

Check: len("securepass123") < 6?
  → 13 < 6 = False ✓

Return: True
```

### Step 4: Process Payment

**Since validation passed**:
```
Output: "Processing $50.00 via PayPal"
Output: "  Email: user@example.com"
Output: "  Authenticating..."
Output: "  Payment successful"

Return: True
```

## Key Observations

### 1. Same Interface, Different Behavior

**PaymentProcessor code never changed**:
```python
# This line is the same regardless of strategy
return self._strategy.pay(amount)
```

**But behavior changed**:
- With CreditCardPayment: processed credit card
- With PayPalPayment: processed PayPal

### 2. Runtime Flexibility

**Strategy switched during execution**:
```
Initial state: processor → CreditCardPayment
After set_strategy(): processor → PayPalPayment
After another set_strategy(): processor → CryptocurrencyPayment
```

No code recompilation needed. No conditionals in processor.

### 3. Polymorphism in Action

**Processor doesn't know concrete type**:
```python
# Processor sees this type:
_strategy: PaymentStrategy

# Actual runtime types:
_strategy = CreditCardPayment    # is-a PaymentStrategy ✓
_strategy = PayPalPayment        # is-a PaymentStrategy ✓
_strategy = CryptocurrencyPayment  # is-a PaymentStrategy ✓
```

The `pay()` method resolves to correct implementation at runtime through virtual dispatch.

### 4. Memory Lifecycle

**Strategies come and go**:
```
Time 0: Only CreditCardPayment exists
Time 1: PayPalPayment created, CreditCardPayment unreferenced
Time 2: CryptocurrencyPayment created, PayPalPayment unreferenced
```

Old strategies garbage collected when no longer referenced.

## Comparison: With vs. Without Strategy

### Without Strategy (Conditional Approach):

```python
def process_payment(amount, method, details):
    if method == "credit_card":
        # validate card
        # process card
    elif method == "paypal":
        # validate paypal
        # process paypal
    elif method == "crypto":
        # validate crypto
        # process crypto
```

**To add new payment method**: Modify this function (violates Open/Closed)
**To test PayPal**: Must execute conditional logic to reach PayPal branch
**To change method at runtime**: Must call with different parameters

### With Strategy:

```python
processor.set_strategy(new_strategy)
processor.process_payment(amount)
```

**To add new payment method**: Create new class implementing PaymentStrategy (Open/Closed satisfied)
**To test PayPal**: Test PayPalPayment class directly
**To change method at runtime**: Just call `set_strategy()`

## Summary

The strategy pattern achieves flexibility through composition and polymorphism:

1. **Composition**: Processor contains a strategy reference, not inheritance
2. **Polymorphism**: All strategies conform to PaymentStrategy interface
3. **Runtime Selection**: Change strategy object, change behavior
4. **No Conditionals**: Processor never checks strategy type
5. **Testability**: Each strategy tests independently

The cost: more classes and indirection. The benefit: extensible, maintainable, testable code.
