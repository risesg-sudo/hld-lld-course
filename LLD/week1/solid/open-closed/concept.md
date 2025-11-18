# Open/Closed Principle (OCP)

## The Hook

You have a discount calculator with if-else for each discount type. Every new discount requires modifying the calculator class. This violates OCP.

## The Problem

Modifying existing code for new features:
- Risk breaking existing functionality
- Must test everything again
- Violates "closed for modification"

## The Solution

Classes should be:
- **Open for extension**: Can add new functionality
- **Closed for modification**: Don't change existing code

Use abstraction and polymorphism to achieve this.

### Implementation

:::multilang
```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, amount):
        pass

class PercentageDiscount(DiscountStrategy):
    def calculate(self, amount):
        return amount * 0.1

class FixedDiscount(DiscountStrategy):
    def calculate(self, amount):
        return 10.0

class DiscountCalculator:
    def apply(self, amount, strategy):
        return amount - strategy.calculate(amount)
```

```cpp
#include <memory>

class DiscountStrategy {
public:
    virtual ~DiscountStrategy() = default;
    virtual double calculate(double amount) const = 0;
};

class PercentageDiscount : public DiscountStrategy {
public:
    double calculate(double amount) const override {
        return amount * 0.1;
    }
};

class FixedDiscount : public DiscountStrategy {
public:
    double calculate(double amount) const override {
        return 10.0;
    }
};

class DiscountCalculator {
public:
    double apply(double amount, const DiscountStrategy& strategy) const {
        return amount - strategy.calculate(amount);
    }
};
```

```java
public abstract class DiscountStrategy {
    public abstract double calculate(double amount);
}

public class PercentageDiscount extends DiscountStrategy {
    @Override
    public double calculate(double amount) {
        return amount * 0.1;
    }
}

public class FixedDiscount extends DiscountStrategy {
    @Override
    public double calculate(double amount) {
        return 10.0;
    }
}

public class DiscountCalculator {
    public double apply(double amount, DiscountStrategy strategy) {
        return amount - strategy.calculate(amount);
    }
}
```
:::

Add new discount by creating new class, not modifying calculator!

## Benefits

1. Extend functionality without changing existing code
2. Reduce risk of breaking working features
3. Follows polymorphism principles
4. Easy to add new types

## Key Takeaways

- Use abstraction for extensibility
- Add features by creating new classes
- Don't modify existing, tested code
- Polymorphism enables OCP
