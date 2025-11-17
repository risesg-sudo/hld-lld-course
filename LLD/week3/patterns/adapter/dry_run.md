# Dry Run: Adapter Pattern

This document traces how the adapter translates between incompatible interfaces.

## Setup

Create legacy system and adapter:

```python
legacy = LegacyPaymentSystem()
adapter = LegacyPaymentAdapter(legacy, "STORE_456")
```

**Memory State**:
```
0x4001: LegacyPaymentSystem
  last_payment_id: ""

0x4002: LegacyPaymentAdapter
  legacy_system: <reference to 0x4001>
  merchant_code: "STORE_456"
```

## Operation: Process Payment via Adapter

Client calls:
```python
checkout(adapter, 75.50, "5555555555554444")
```

### Step 1: Client Calls checkout()

**Function Entry**:
```
processor = LegacyPaymentAdapter at 0x4002
amount = 75.50
card = "5555555555554444"
```

**Client sees**: `processor` as type `PaymentProcessor` (interface)
**Actual type**: `LegacyPaymentAdapter` (implementation)

### Step 2: checkout() Calls process_payment()

**Method Call**:
```
processor.process_payment(75.50, "5555555555554444")
→ LegacyPaymentAdapter.process_payment(75.50, "5555555555554444")
```

**Enter Adapter's process_payment()**:
```
self = LegacyPaymentAdapter at 0x4002
amount = 75.50
card_number = "5555555555554444"
```

### Step 3: Adapter Translates Parameters

**Modern interface** expects:
```
process_payment(amount: float, card_number: str) → bool
```

**Legacy interface** expects:
```
make_payment(sum_amount, payment_details, merchant_code) → dict
```

**Adapter Translation**:
```
sum_amount = 75.50  (direct mapping)
payment_details = f"Card ending in {card_number[-4:]}"
               = "Card ending in 4444"
merchant_code = self.merchant_code
              = "STORE_456"
```

### Step 4: Adapter Calls Legacy System

**Method Call**:
```
self.legacy_system.make_payment(
    sum_amount=75.50,
    payment_details="Card ending in 4444",
    merchant_code="STORE_456"
)
```

**Enters LegacyPaymentSystem.make_payment()**:
```
self = LegacyPaymentSystem at 0x4001
sum_amount = 75.50
payment_details = "Card ending in 4444"
merchant_code = "STORE_456"
```

**Legacy Processing**:
```
Create payment ID:
  last_payment_id = f"LEG-{merchant_code}-{int(sum_amount)}"
                 = f"LEG-STORE_456-75"
                 = "LEG-STORE_456-75"

Output: "Legacy System: Payment of $75.5"
Output: "  Details: Card ending in 4444"
Output: "  Merchant: STORE_456"
Output: "  Payment ID: LEG-STORE_456-75"

Update state:
  self.last_payment_id = "LEG-STORE_456-75"

Return: {"status": "success", "id": "LEG-STORE_456-75"}
```

### Step 5: Adapter Translates Result

**Legacy returns**: `{"status": "success", "id": "LEG-STORE_456-75"}`
**Modern expects**: `bool`

**Adapter Translation**:
```
result = {"status": "success", "id": "LEG-STORE_456-75"}
success = result["status"] == "success"
        = "success" == "success"
        = True

Return: True
```

### Step 6: Back to Client

**checkout() receives**: `success = True`

**Client calls**:
```
transaction_id = processor.get_transaction_id()
→ LegacyPaymentAdapter.get_transaction_id()
```

### Step 7: Adapter Translates get_transaction_id()

**Modern interface**: `get_transaction_id() → str`
**Legacy interface**: `get_last_payment_reference() → str`

**Adapter Call**:
```
self.legacy_system.get_last_payment_reference()
→ Returns: "LEG-STORE_456-75"
```

**Adapter Returns**: `"LEG-STORE_456-75"`

### Step 8: Client Displays Result

```
Output: "Checkout successful!"
Output: "Transaction ID: LEG-STORE_456-75"
```

## Interface Translation Table

| Client Interface | Adapter Translation | Legacy Interface |
|-----------------|-------------------|------------------|
| `process_payment(amount, card)` | Extract last 4 digits | `make_payment(sum_amount, payment_details, merchant_code)` |
| Returns `bool` | Check `status == "success"` | Returns `{"status": "...", "id": "..."}` |
| `get_transaction_id()` | Direct delegation | `get_last_payment_reference()` |
| Returns `str` | No translation needed | Returns `str` |

## Key Observations

### 1. Interface Compatibility

**Client expects**:
```python
class PaymentProcessor(ABC):
    def process_payment(self, amount: float, card_number: str) -> bool
    def get_transaction_id(self) -> str
```

**Adapter provides**:
```python
class LegacyPaymentAdapter(PaymentProcessor):  # Implements interface
    def process_payment(self, amount: float, card_number: str) -> bool  # ✓
    def get_transaction_id(self) -> str  # ✓
```

Client sees adapter as `PaymentProcessor`. Type checks pass.

### 2. Parameter Translation

Modern call:
```python
process_payment(75.50, "5555555555554444")
```

Becomes legacy call:
```python
make_payment(
    sum_amount=75.50,
    payment_details="Card ending in 4444",  # Translated
    merchant_code="STORE_456"  # Added by adapter
)
```

Adapter adds missing information (merchant_code) and reformats data.

### 3. Result Translation

Legacy result:
```python
{"status": "success", "id": "LEG-STORE_456-75"}
```

Becomes modern result:
```python
True  # Extracted from {"status": "success"}
```

Adapter extracts relevant information and converts to expected type.

### 4. Client Ignorance

Client code:
```python
def checkout(processor: PaymentProcessor, amount, card):
    success = processor.process_payment(amount, card)
    if success:
        txn_id = processor.get_transaction_id()
```

**Client never knows**:
- Whether using modern or legacy implementation
- That adapter is translating interfaces
- That legacy system has different method names
- That legacy system returns different data types

This is **polymorphism** in action.

## Comparison: Direct Integration vs. Adapter

### Without Adapter (Client uses legacy directly):

```python
def checkout_with_legacy(amount, card, merchant):
    legacy = LegacyPaymentSystem()
    details = f"Card ending in {card[-4:]}"
    result = legacy.make_payment(amount, details, merchant)

    if result["status"] == "success":
        txn_id = legacy.get_last_payment_reference()
        print(f"Success: {txn_id}")
```

**Problems**:
- Client coupled to legacy interface
- Every call site must translate
- Can't use same code for modern and legacy
- Hard to switch implementations

### With Adapter:

```python
def checkout(processor: PaymentProcessor, amount, card):
    success = processor.process_payment(amount, card)
    if success:
        txn_id = processor.get_transaction_id()
        print(f"Success: {txn_id}")
```

**Benefits**:
- Client coupled to interface, not implementation
- Translation centralized in adapter
- Same code works for all implementations
- Easy to switch by passing different adapter

## Summary

Adapter pattern achieves interface compatibility through:

1. **Wrapper Object**: Adapter wraps incompatible object
2. **Interface Implementation**: Adapter implements expected interface
3. **Translation Layer**: Adapter translates calls and data
4. **Composition**: Adapter contains adaptee, delegates to it
5. **Client Transparency**: Client unaware of adapter's existence

The cost: extra object and method calls. The benefit: interface compatibility without modifying existing code.
