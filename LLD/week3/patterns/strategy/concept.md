# Strategy Pattern

## The Hook

Have you ever written code that looks like this?

:::multilang:::

```python
if payment_method == "credit_card":
    # 50 lines of credit card logic
elif payment_method == "paypal":
    # 50 lines of PayPal logic
elif payment_method == "crypto":
    # 50 lines of crypto logic
elif payment_method == "apple_pay":
    # 50 lines of Apple Pay logic
```

```cpp
if (paymentMethod == "credit_card") {
    // 50 lines of credit card logic
} else if (paymentMethod == "paypal") {
    // 50 lines of PayPal logic
} else if (paymentMethod == "crypto") {
    // 50 lines of crypto logic
} else if (paymentMethod == "apple_pay") {
    // 50 lines of Apple Pay logic
}
```

```java
if (paymentMethod.equals("credit_card")) {
    // 50 lines of credit card logic
} else if (paymentMethod.equals("paypal")) {
    // 50 lines of PayPal logic
} else if (paymentMethod.equals("crypto")) {
    // 50 lines of crypto logic
} else if (paymentMethod.equals("apple_pay")) {
    // 50 lines of Apple Pay logic
}
```

:::

What happens when you need to add a new payment method? You modify this function. What happens when credit card processing rules change? You modify this function. What happens when you want to test PayPal logic in isolation? You can't easily.

This pattern appears everywhere: sorting algorithms that vary by data size, compression algorithms that vary by file type, routing algorithms that vary by user preference. The same problem surfaces repeatedly: multiple algorithms solving the same problem, tangled together in conditional chains.

## The Problem

Why does this pattern cause problems?

**Violation of Open/Closed Principle**: Every time you add a new algorithm, you modify existing code. The function grows longer. The risk of breaking existing functionality increases. You're not extending behavior; you're rewriting it.

**Testing Nightmare**: How do you test just the PayPal logic? You need to set up conditions that route through the `elif payment_method == "paypal"` branch. What if that logic depends on previous conditional checks? Testing becomes integration testing by default, not unit testing.

**Code Duplication**: Often, similar algorithms share setup code. Do you duplicate that setup in each branch? Or do you extract it, creating dependencies between branches? Either choice creates maintenance burden.

**Runtime Inflexibility**: What if the payment method needs to change during execution? What if a user wants to try PayPal, then switch to credit card without restarting? The conditional approach bakes the choice into the control flow.

**Cognitive Load**: Understanding the code requires reading through every branch. Finding the credit card logic means scanning past PayPal, crypto, and Apple Pay. The more algorithms you add, the harder navigation becomes.

The fundamental issue: you're mixing **algorithm selection** with **algorithm implementation**. These are orthogonal concerns that should vary independently.

## The Solution

Strategy pattern separates these concerns through composition.

**Define a Common Interface**: All algorithms implement the same interface. Whether processing credit cards or crypto, the operation is `pay(amount)`. The interface defines what to do; implementations define how.

**Encapsulate Each Algorithm**: Each algorithm lives in its own class. CreditCardPayment handles only credit cards. PayPalPayment handles only PayPal. Adding a new payment method means creating a new class, not modifying existing code.

**Select at Runtime**: The client holds a reference to a strategy interface. It doesn't know which concrete strategy it has—just that it implements the interface. Change the strategy object, change the behavior. No conditionals required.

Here's how it transforms the code:

:::multilang:::

```python
# Before: Conditional mess
def process_payment(amount, method, **details):
    if method == "credit_card":
        # implementation
    elif method == "paypal":
        # implementation
    # ... more branches

# After: Strategy pattern
class PaymentStrategy(ABC):
    def pay(self, amount: float) -> bool:
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        # credit card implementation

class PayPalPayment(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        # PayPal implementation

class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy

    def process_payment(self, amount: float) -> bool:
        return self._strategy.pay(amount)
```

```cpp
// Before: Conditional mess
bool processPayment(double amount, const std::string& method, /* details */) {
    if (method == "credit_card") {
        // implementation
    } else if (method == "paypal") {
        // implementation
    }
    // ... more branches
}

// After: Strategy pattern
class PaymentStrategy {
public:
    virtual ~PaymentStrategy() = default;
    virtual bool pay(double amount) = 0;
};

class CreditCardPayment : public PaymentStrategy {
public:
    bool pay(double amount) override {
        // credit card implementation
    }
};

class PayPalPayment : public PaymentStrategy {
public:
    bool pay(double amount) override {
        // PayPal implementation
    }
};

class PaymentProcessor {
private:
    std::unique_ptr<PaymentStrategy> strategy;

public:
    PaymentProcessor(std::unique_ptr<PaymentStrategy> strat)
        : strategy(std::move(strat)) {}

    bool processPayment(double amount) {
        return strategy->pay(amount);
    }
};
```

```java
// Before: Conditional mess
boolean processPayment(double amount, String method, /* details */) {
    if (method.equals("credit_card")) {
        // implementation
    } else if (method.equals("paypal")) {
        // implementation
    }
    // ... more branches
}

// After: Strategy pattern
interface PaymentStrategy {
    boolean pay(double amount);
}

class CreditCardPayment implements PaymentStrategy {
    public boolean pay(double amount) {
        // credit card implementation
    }
}

class PayPalPayment implements PaymentStrategy {
    public boolean pay(double amount) {
        // PayPal implementation
    }
}

class PaymentProcessor {
    private PaymentStrategy strategy;

    public PaymentProcessor(PaymentStrategy strategy) {
        this.strategy = strategy;
    }

    public boolean processPayment(double amount) {
        return strategy.pay(amount);
    }
}
```

:::

The client code becomes:

:::multilang:::

```python
# Select strategy
processor = PaymentProcessor(CreditCardPayment("1234-5678"))

# Use strategy
processor.process_payment(100.00)

# Change strategy at runtime
processor.set_strategy(PayPalPayment("user@email.com"))
processor.process_payment(50.00)
```

```cpp
// Select strategy
auto processor = PaymentProcessor(
    std::make_unique<CreditCardPayment>("1234-5678")
);

// Use strategy
processor.processPayment(100.00);

// Change strategy at runtime
processor.setStrategy(
    std::make_unique<PayPalPayment>("user@email.com")
);
processor.processPayment(50.00);
```

```java
// Select strategy
PaymentProcessor processor = new PaymentProcessor(
    new CreditCardPayment("1234-5678")
);

// Use strategy
processor.processPayment(100.00);

// Change strategy at runtime
processor.setStrategy(new PayPalPayment("user@email.com"));
processor.processPayment(50.00);
```

:::

**How It Works**:

1. **Strategy Interface** (`PaymentStrategy`): Declares the algorithm signature. All concrete strategies implement this interface.

2. **Concrete Strategies** (`CreditCardPayment`, `PayPalPayment`): Implement the algorithm. Each contains one algorithm, follows single responsibility principle.

3. **Context** (`PaymentProcessor`): Maintains a reference to a strategy. Delegates work to the strategy. Can switch strategies at runtime.

4. **Client**: Selects which strategy to use. Often uses a factory to create strategies based on configuration.

**Key Insight**: The context doesn't know which concrete strategy it has. It programs against the interface. This is dependency inversion in action: depend on abstractions, not concretions.

**Benefits Over Conditionals**:

- **Open/Closed**: Add new strategies without modifying existing code
- **Single Responsibility**: Each strategy handles one algorithm
- **Testability**: Test each strategy in isolation
- **Composability**: Combine with other patterns (factory, decorator)
- **Runtime Flexibility**: Change algorithms during execution
- **Clarity**: Algorithm implementation separated from selection logic

The strategy pattern transforms branching complexity into compositional simplicity. Instead of asking "which path through this conditional maze?", you ask "which object handles this?".

## Code Example

See the complete implementation in `/home/user/hld-lld-course/LLD/week3/patterns/strategy/payment_strategies.py`.

The example demonstrates:
- Payment processing with multiple methods (credit card, PayPal, cryptocurrency, Apple Pay)
- Strategy selection through dependency injection
- Runtime strategy switching
- How client code uses strategies without knowing concrete implementations

Run the example to see how different payment strategies work interchangeably through the same interface.

## When to Use

**Multiple Algorithm Variations**: You have different ways to accomplish the same task—different sorting algorithms, compression formats, or validation rules.

**Runtime Selection**: The algorithm choice depends on runtime conditions—user preference, data characteristics, or system state. You can't determine the algorithm at compile time.

**Avoiding Conditional Complexity**: Your code has growing if/else or switch statements based on type or mode. Each branch contains significant logic that's hard to test independently.

**Future Extensibility**: You anticipate adding more algorithms. New payment methods, new export formats, new routing strategies. You want to add these without touching existing code.

**Testing Requirements**: You need to test each algorithm in isolation. You need to mock or stub different algorithm implementations for testing client code.

## Trade-offs

**What You Gain**:

- **Flexibility**: Change algorithms at runtime without client code changes
- **Testability**: Each strategy tested independently; easy to mock
- **Maintainability**: Adding strategies doesn't modify existing code
- **Clarity**: Algorithm logic separated from selection logic; easier to understand each piece
- **Reusability**: Same strategy used in multiple contexts

**What You Lose**:

- **Class Count**: More classes than conditional approach; overhead in simple cases
- **Indirection**: One more layer between client and implementation; slightly harder to trace
- **Selection Logic**: You still need to decide which strategy to use; moves from control flow to object creation
- **Overkill Risk**: For 2-3 simple algorithms that never change, conditionals might be clearer

**When Not to Use**:

- Algorithms won't change or grow
- Only 1-2 simple variations exist
- Selection logic is more complex than the algorithms themselves
- Performance-critical code where virtual dispatch overhead matters

The pattern trades structural complexity (more classes) for behavioral flexibility (easier to extend and modify). Choose strategy when you value flexibility over simplicity.

## Related Patterns

**Strategy vs. State**: State pattern uses a similar structure, but state objects determine their own successor states. Strategy objects are selected by the client or context, and don't know about each other.

**Strategy vs. Template Method**: Template method uses inheritance to vary parts of an algorithm. Strategy uses composition to vary entire algorithms. Prefer strategy for more flexibility; template method for enforcing algorithm structure.

**Strategy + Factory**: Common combination. Factory creates appropriate strategy based on configuration or runtime conditions. Separates strategy selection from strategy usage.

**Strategy + Decorator**: Can decorate strategies to add behavior (logging, caching, monitoring) without modifying strategy implementations.

## Implementation Considerations

**Strategy Selection**: Who chooses the strategy? Options:
- Client creates and passes strategy (dependency injection)
- Factory creates strategy based on configuration
- Context selects strategy based on internal state

**Strategy State**: Should strategies be stateless or stateful?
- Stateless strategies can be shared/reused safely
- Stateful strategies need careful lifecycle management

**Parameter Passing**: How much data do strategies need?
- Pass everything needed to `execute()` method
- Or let strategy query context for data
- Balance coupling against parameter list complexity

**Strategy Composition**: Can strategies delegate to other strategies? Can they be combined? Consider whether you need composite strategies for complex algorithms.

## Key Takeaways

1. Strategy pattern encapsulates interchangeable algorithms behind a common interface
2. Eliminates conditional complexity by replacing branches with objects
3. Enables runtime algorithm selection and testing in isolation
4. Follows Open/Closed: extend with new strategies without modifying existing code
5. Trade-off: More classes for more flexibility
6. Best for multiple algorithms that vary at runtime
7. Combine with Factory for clean strategy selection
8. Don't overuse: simple conditionals are fine for 2-3 stable variants
