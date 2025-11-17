# Polymorphism

## The Hook: One Interface, Multiple Behaviors

You're building a payment system. You have credit cards, PayPal, cryptocurrency, and bank transfers. Each processes payments differently, but your checkout code shouldn't care about these details:

```python
# Messy approach
if payment_type == "credit_card":
    process_credit_card(amount, card_details)
elif payment_type == "paypal":
    process_paypal(amount, email)
elif payment_type == "crypto":
    process_crypto(amount, wallet)
# ... endless if-else chains
```

Every new payment method requires modifying this code. What if you could write:

```python
payment_method.process(amount)  # Works for any payment type!
```

This is polymorphism: one interface, many implementations.

## The Problem: Handling Multiple Types

Real applications work with multiple types of objects that share similar behavior but differ in implementation. Without polymorphism:

1. **Tight Coupling**: Code depends on specific types
2. **Rigid Design**: Adding new types requires extensive changes
3. **Code Duplication**: Similar logic repeated for each type
4. **Difficult Testing**: Must test every conditional branch
5. **Poor Extensibility**: Cannot add types without modifying existing code

Traditional approach creates fragile, hard-to-maintain code that violates the Open/Closed Principle.

## The Solution: Polymorphism

Polymorphism (Greek: "many forms") allows objects of different types to be treated through a common interface, with each type providing its own implementation.

### Core Concept

The same method call produces different behavior depending on the object's type:

```python
# Same method name, different behaviors
circle.draw()     # Draws a circle
rectangle.draw()  # Draws a rectangle
triangle.draw()   # Draws a triangle
```

### Types of Polymorphism

**1. Compile-Time Polymorphism** (Method Overloading)
- Same method name, different parameters
- Python doesn't support traditional overloading

**2. Runtime Polymorphism** (Method Overriding)
- Subclass provides specific implementation of parent method
- Most common in Python

**3. Duck Typing** (Python-specific)
- "If it walks like a duck and quacks like a duck, it's a duck"
- Object's suitability determined by presence of methods, not type

## How It Works

### 1. Define Common Interface

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass
```

### 2. Implement Different Behaviors

```python
class CreditCard(PaymentMethod):
    def process_payment(self, amount):
        return f"Charged ${amount} to credit card"

class PayPal(PaymentMethod):
    def process_payment(self, amount):
        return f"Processed ${amount} via PayPal"
```

### 3. Use Polymorphically

```python
def checkout(payment: PaymentMethod, amount: float):
    result = payment.process_payment(amount)  # Works with any PaymentMethod!
    return result

# Same function works with different types
checkout(CreditCard(), 100)
checkout(PayPal(), 100)
```

## Benefits

1. **Flexibility**: Easy to add new types without modifying existing code
2. **Maintainability**: Changes to one type don't affect others
3. **Testability**: Each type can be tested independently
4. **Extensibility**: New implementations added by creating new classes
5. **Loose Coupling**: Code depends on interfaces, not concrete types
6. **Code Reuse**: Common logic in shared interface/base class

## Real-World Example: Shape Hierarchy

```python
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def perimeter(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

# Polymorphic function
def print_shape_info(shape: Shape):
    print(f"Area: {shape.area()}")
    print(f"Perimeter: {shape.perimeter()}")

# Works with any shape
print_shape_info(Circle(5))
print_shape_info(Rectangle(4, 6))
```

## Duck Typing in Python

Python's dynamic nature allows polymorphism without explicit interfaces:

```python
class Dog:
    def speak(self):
        return "Woof!"

class Cat:
    def speak(self):
        return "Meow!"

class Duck:
    def speak(self):
        return "Quack!"

def make_it_speak(animal):
    # No type checking needed
    return animal.speak()

# Works with any object that has a speak() method
make_it_speak(Dog())   # "Woof!"
make_it_speak(Cat())   # "Meow!"
make_it_speak(Duck())  # "Quack!"
```

## Operator Overloading

Python allows polymorphism through special methods:

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(1, 2)
v2 = Vector(3, 4)
v3 = v1 + v2  # Calls __add__
print(v3)     # Calls __str__
```

## Trade-offs

### Advantages
- Highly flexible and extensible
- Reduces coupling
- Follows Open/Closed Principle
- Easy to add new types

### Disadvantages
- Can be harder to understand flow
- Slight performance overhead (method lookup)
- May obscure what code actually does
- Requires good interface design

## When to Use

Use polymorphism when:
- Multiple types share common behavior
- Behavior varies by type
- New types will be added in future
- You want to follow Open/Closed Principle

Avoid when:
- Types have nothing in common
- Performance is absolutely critical
- Code is simple and won't change
- Only one implementation exists

## Best Practices

1. **Design Clear Interfaces**: Abstract base classes define contracts
2. **Liskov Substitution**: Subtypes must be substitutable for base types
3. **Composition Over Inheritance**: Sometimes better to compose behaviors
4. **Don't Overuse**: Not every similarity needs polymorphism
5. **Document Contracts**: Clear expectations for implementations

## Common Patterns

### Strategy Pattern

```python
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data):
        pass

class QuickSort(SortStrategy):
    def sort(self, data):
        # Quick sort implementation
        pass

class MergeSort(SortStrategy):
    def sort(self, data):
        # Merge sort implementation
        pass

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def sort(self, data):
        return self.strategy.sort(data)
```

## Key Takeaways

1. Polymorphism enables one interface with multiple implementations
2. Subclasses override methods to provide specific behavior
3. Python supports duck typing for flexible polymorphism
4. Abstract base classes define contracts
5. Enables Open/Closed Principle
6. Reduces coupling and improves maintainability
7. Works with inheritance and composition
8. Essential for building flexible, extensible systems

Polymorphism is about writing code that works with abstractions, allowing different concrete implementations to be used interchangeably without changing the code that uses them.
