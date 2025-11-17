# Adapter Pattern

## The Hook

You've just integrated a fantastic third-party payment library into your e-commerce platform. It works perfectly. Six months later, you need to switch to a different provider—better rates, more features. But their API is completely different.

Your code expects `process_payment(amount, card_number)`. The new library provides `makePayment(sum, cardInfo, merchantId, timestamp)`. Do you rewrite every call to `process_payment()` throughout your codebase? Do you wrap every call in translation logic, scattering adapter code everywhere?

This isn't just about payment libraries. Legacy systems with old interfaces. Third-party APIs with quirky designs. Multiple database drivers with incompatible methods. The same problem surfaces whenever interfaces don't match expectations.

How do you make incompatible interfaces work together without rewriting everything?

## The Problem

Why is interface incompatibility such a persistent problem?

**You Can't Change External Code**: The third-party library is compiled. The legacy system is running in production and can't be modified. The vendor's API is their design, not yours. You don't control these interfaces, yet you need to use them.

**Client Code Expects Specific Interface**: Your application is built around a particular interface. Hundreds of method calls depend on this interface. Changing every call is error-prone and time-consuming.

**Multiple Incompatible Implementations**: You're using MySQL today, but want to support PostgreSQL and MongoDB tomorrow. Each has different method names and parameters. Do you write conditional code for each database? That couples your code to every possible implementation.

**Evolution and Migration**: Systems evolve. APIs change. New versions aren't backwards compatible. You need to support both old and new interfaces during migration. How do you make both work without maintaining two code paths?

The core problem: **interface mismatch**. The interface you have isn't the interface you need.

## The Solution

Adapter pattern provides a wrapper that translates one interface to another.

**Create an Adapter Class**: The adapter implements the interface your client expects (target interface). Inside, it holds a reference to the object with the incompatible interface (adaptee). The adapter translates calls from target to adaptee.

```python
# Client expects this interface
class PaymentGateway(ABC):
    def process_payment(self, amount: float, card: str) -> bool:
        pass

# Third-party library has this interface
class LegacyPaymentAPI:
    def makePayment(self, sum, cardInfo, merchantId, timestamp):
        # legacy implementation

# Adapter makes them compatible
class PaymentAdapter(PaymentGateway):
    def __init__(self, legacy_api: LegacyPaymentAPI):
        self.legacy_api = legacy_api

    def process_payment(self, amount: float, card: str) -> bool:
        # Translate from target interface to adaptee interface
        merchant_id = "MERCHANT_123"
        timestamp = datetime.now()
        return self.legacy_api.makePayment(amount, card, merchant_id, timestamp)
```

**Client Code Unchanged**: The client calls `process_payment()` as before. It doesn't know about the adapter or the legacy API. It programs against the interface, not the implementation.

```python
# Works with any PaymentGateway implementation
def checkout(gateway: PaymentGateway, amount: float, card: str):
    return gateway.process_payment(amount, card)

# Use modern implementation
checkout(ModernPaymentGateway(), 100, "1234")

# Use legacy implementation via adapter
legacy = LegacyPaymentAPI()
adapter = PaymentAdapter(legacy)
checkout(adapter, 100, "1234")  # Same call, different implementation
```

**Two Types of Adapters**:

1. **Object Adapter** (uses composition):
```python
class Adapter:
    def __init__(self, adaptee):
        self.adaptee = adaptee  # Composition

    def target_method(self):
        return self.adaptee.incompatible_method()
```

2. **Class Adapter** (uses multiple inheritance):
```python
class Adapter(Target, Adaptee):  # Multiple inheritance
    def target_method(self):
        return self.incompatible_method()
```

Object adapter is more flexible and generally preferred. Class adapter only works in languages supporting multiple inheritance.

**How It Works**:

1. Client holds reference to target interface
2. Adapter implements target interface
3. Adapter contains reference to adaptee
4. When client calls target method, adapter translates to adaptee method
5. Adapter returns result in expected format

The adapter acts as a translator, converting calls and data between incompatible interfaces. It's the interface equivalent of a power plug adapter for international travel.

## Code Example

See the complete implementation in `/home/user/hld-lld-course/LLD/week3/patterns/adapter/legacy_integration.py`.

The example demonstrates:
- Adapting a legacy payment system to modern interface
- Multiple implementations of same target interface
- How client code works with all implementations uniformly
- Adapter translating method names and parameters

Run the example to see how the adapter makes legacy code work with modern interfaces.

## When to Use

**Legacy System Integration**: You have old code with outdated interfaces that can't be changed. You need to use it alongside new code with modern interfaces.

**Third-Party Library Integration**: External library doesn't match your interface. Creating an adapter isolates your code from the library's interface, making it easier to switch libraries later.

**Multiple Implementations**: Supporting multiple backends (databases, payment processors, cloud providers) with different APIs. Adapters provide a uniform interface.

**Interface Standardization**: Different teams created components with incompatible interfaces. Adapters provide a standard interface without rewriting components.

**Gradual Migration**: Moving from old to new system. Adapters let both systems coexist during transition.

## Trade-offs

**What You Gain**:

- **Compatibility**: Make incompatible interfaces work together
- **Isolation**: Client code independent of adaptee implementation
- **Flexibility**: Easy to switch implementations by swapping adapters
- **Reusability**: Reuse existing classes without modification
- **Open/Closed**: Add new implementations without changing client code

**What You Lose**:

- **Indirection**: Extra layer between client and real implementation
- **Complexity**: More classes to understand and maintain
- **Overhead**: Additional method calls through adapter
- **Over-Abstraction**: Can hide important details of underlying implementation

**When Not to Use**:

- You control both interfaces and can make them compatible
- Only one implementation exists and will ever exist
- Adapter logic is more complex than rewriting client code
- Performance overhead of indirection is unacceptable

## Related Patterns

**Adapter vs Bridge**: Adapter retrofits incompatible interfaces after the fact. Bridge separates abstraction from implementation upfront. Adapter solves compatibility; Bridge prevents coupling.

**Adapter vs Decorator**: Adapter changes the interface. Decorator enhances behavior while keeping the same interface. Adapter for compatibility; Decorator for enhancement.

**Adapter vs Facade**: Adapter makes one interface compatible with another. Facade simplifies a complex subsystem. Adapter translates; Facade simplifies.

**Adapter + Factory**: Common combination. Factory creates appropriate adapter based on configuration, hiding adapter selection from client.

## Implementation Considerations

**Adapter Direction**: One-way or two-way? Most adapters translate in one direction (target → adaptee). Two-way adapters translate both directions, but add complexity.

**Adapter Statefulness**: Should adapters be stateless or maintain state? Stateless adapters are simpler and safer. Stateful adapters can optimize (caching) but complicate lifecycle.

**Minimal Translation**: Adapter should translate interfaces, not add business logic. Keep adapters thin. Complex adapters are hard to maintain and test.

**Multiple Adaptees**: Can one adapter work with multiple adaptees? If adaptee interface is standard, yes. Otherwise, one adapter per adaptee type.

## Key Takeaways

1. Adapter translates incompatible interfaces to make them compatible
2. Object adapter (composition) more flexible than class adapter (inheritance)
3. Client programs against target interface, doesn't know about adaptee
4. Essential for integrating legacy code, third-party libraries, multiple implementations
5. Trade-off: Adds indirection layer for compatibility
6. Don't use when you can change interfaces to be compatible directly
7. Combine with Factory for clean adapter selection
8. Keep adapters focused on interface translation, not business logic
