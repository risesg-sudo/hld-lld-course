# Decorator Pattern

## The Hook

You're building a coffee shop system. A simple coffee costs $2. Add milk? $0.50 more. Add sugar? $0.25. Add whipped cream? $0.75. How many classes do you need?

Without thinking, you might create: `Coffee`, `CoffeeWithMilk`, `CoffeeWithSugar`, `CoffeeWithMilkAndSugar`, `CoffeeWithMilkAndWhippedCream`, `CoffeeWithSugarAndWhippedCream`, `CoffeeWithMilkSugarAndWhippedCream`. That's already 7 classes for 3 add-ons.

Add caramel as a fourth option? Now you need 15 classes. Five options? 31 classes. The combinatorial explosion is unsustainable.

There must be a better way to add behavior dynamically without creating a class for every possible combination.

## The Problem

**Subclass Explosion**: Each combination of features requires a new subclass. N features means 2^N possible combinations. This doesn't scale.

**Static Composition**: Inheritance bakes features in at compile time. You can't add or remove features at runtime based on user choice.

**Code Duplication**: Similar classes share code. `CoffeeWithMilkAndSugar` and `CoffeeWithMilkAndCaramel` both handle milk. Where does that code go? Do you duplicate it?

**Single Inheritance Limitation**: A class can only extend one parent. How do you combine behaviors from multiple sources?

The fundamental issue: inheritance is too rigid for dynamic, combinable behaviors. You need a flexible way to mix and match features.

## The Solution

Decorator pattern wraps objects in layers, each layer adding behavior.

Instead of `CoffeeWithMilkAndSugar` class, create:

:::multilang:::

```python
coffee = SimpleCoffee()           # $2.00
coffee = MilkDecorator(coffee)    # $2.00 + $0.50
coffee = SugarDecorator(coffee)   # $2.50 + $0.25 = $2.75
```

```cpp
auto coffee = std::make_unique<SimpleCoffee>();                    // $2.00
coffee = std::make_unique<MilkDecorator>(std::move(coffee));       // $2.00 + $0.50
coffee = std::make_unique<SugarDecorator>(std::move(coffee));      // $2.50 + $0.25 = $2.75
```

```java
Beverage coffee = new SimpleCoffee();              // $2.00
coffee = new MilkDecorator(coffee);                // $2.00 + $0.50
coffee = new SugarDecorator(coffee);               // $2.50 + $0.25 = $2.75
```

:::

**How It Works**:

1. **Component Interface**: All objects (base and decorators) implement same interface
2. **Base Component**: Simple object with core functionality
3. **Decorator**: Implements same interface, wraps another component
4. **Stacking**: Decorators can wrap other decorators

:::multilang:::

```python
class Beverage(ABC):
    def get_cost(self) -> float:
        pass

class SimpleCoffee(Beverage):
    def get_cost(self) -> float:
        return 2.00

class MilkDecorator(Beverage):
    def __init__(self, beverage: Beverage):
        self._beverage = beverage

    def get_cost(self) -> float:
        return self._beverage.get_cost() + 0.50
```

```cpp
class Beverage {
public:
    virtual ~Beverage() = default;
    virtual double getCost() const = 0;
};

class SimpleCoffee : public Beverage {
public:
    double getCost() const override {
        return 2.00;
    }
};

class MilkDecorator : public Beverage {
private:
    std::unique_ptr<Beverage> beverage;

public:
    MilkDecorator(std::unique_ptr<Beverage> bev)
        : beverage(std::move(bev)) {}

    double getCost() const override {
        return beverage->getCost() + 0.50;
    }
};
```

```java
interface Beverage {
    double getCost();
}

class SimpleCoffee implements Beverage {
    public double getCost() {
        return 2.00;
    }
}

class MilkDecorator implements Beverage {
    private Beverage beverage;

    public MilkDecorator(Beverage beverage) {
        this.beverage = beverage;
    }

    public double getCost() {
        return beverage.getCost() + 0.50;
    }
}
```

:::

Build combinations at runtime:

:::multilang:::

```python
# Just coffee
order1 = SimpleCoffee()  # $2.00

# Coffee with milk
order2 = MilkDecorator(SimpleCoffee())  # $2.50

# Coffee with milk and sugar
order3 = SugarDecorator(MilkDecorator(SimpleCoffee()))  # $2.75
```

```cpp
// Just coffee
auto order1 = std::make_unique<SimpleCoffee>();  // $2.00

// Coffee with milk
auto order2 = std::make_unique<MilkDecorator>(
    std::make_unique<SimpleCoffee>()
);  // $2.50

// Coffee with milk and sugar
auto order3 = std::make_unique<SugarDecorator>(
    std::make_unique<MilkDecorator>(
        std::make_unique<SimpleCoffee>()
    )
);  // $2.75
```

```java
// Just coffee
Beverage order1 = new SimpleCoffee();  // $2.00

// Coffee with milk
Beverage order2 = new MilkDecorator(new SimpleCoffee());  // $2.50

// Coffee with milk and sugar
Beverage order3 = new SugarDecorator(
    new MilkDecorator(new SimpleCoffee())
);  // $2.75
```

:::

With 3 add-ons: 4 classes (base + 3 decorators) instead of 8 subclasses. With 5 add-ons: 6 classes instead of 32.

## Code Example

See `/home/user/hld-lld-course/LLD/week3/patterns/decorator/coffee_shop.py`

## When to Use

**Avoiding Subclass Explosion**: Multiple optional features that can be combined

**Runtime Composition**: Features selected during execution, not at compile time

**Cross-Cutting Concerns**: Logging, caching, validation, authorization apply to many classes

**Reversible Enhancement**: Need to add/remove behaviors dynamically

## Trade-offs

**What You Gain**: Flexible composition, open/closed principle, single responsibility, no subclass explosion

**What You Lose**: More objects, complex initialization, order sensitivity, harder debugging

## Key Takeaways

1. Decorator wraps objects to add behavior
2. More flexible than inheritance for combining features
3. Each decorator has single responsibility
4. Can stack decorators in any order
5. Trade-off: Structural complexity for behavioral flexibility
6. Watch for order-dependent decorators
7. Don't overuse for simple problems
8. Common in streams, middleware, UI frameworks
