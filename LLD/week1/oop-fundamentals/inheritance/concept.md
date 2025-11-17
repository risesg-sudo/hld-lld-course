# Inheritance

## The Hook: Code Duplication Nightmare

You're building a transportation app with cars, motorcycles, and trucks. You write:

```python
class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
    def start(self): pass
    def stop(self): pass

class Motorcycle:
    def __init__(self, brand, model):  # Duplicate!
        self.brand = brand
        self.model = model
    def start(self): pass  # Duplicate!
    def stop(self): pass   # Duplicate!

class Truck:
    def __init__(self, brand, model):  # Duplicate again!
        self.brand = brand
        self.model = model
    def start(self): pass  # Duplicate again!
    def stop(self): pass   # Duplicate again!
```

When you need to add a feature like "fuel efficiency," you must modify three classes. When you fix a bug in `start()`, you fix it three times. This violates the DRY principle and becomes unmaintainable.

## The Problem: Code Reuse and Hierarchical Relationships

Real-world entities often have hierarchical relationships. A car IS-A vehicle. A motorcycle IS-A vehicle. They share common characteristics but also have unique features.

Without inheritance, we face several issues:

1. **Code Duplication**: Common functionality is copied across classes
2. **Maintenance Nightmare**: Changes must be made in multiple places
3. **Inconsistency Risk**: Easy to update one class but forget others
4. **No Common Type**: Cannot treat different vehicles polymorphically
5. **Poor Modeling**: Code structure doesn't match real-world relationships

Consider employee management:

```python
class Manager:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
    def work(self): pass
    def request_leave(self): pass

class Developer:
    def __init__(self, name, salary):  # Same as Manager
        self.name = name
        self.salary = salary
    def work(self): pass               # Same as Manager
    def request_leave(self): pass      # Same as Manager
```

Every employee type duplicates basic employee functionality. This is wasteful and error-prone.

## The Solution: Inheritance

Inheritance is a mechanism where a new class (child/derived class) is created from an existing class (parent/base class), inheriting its attributes and methods while adding or modifying functionality.

### Core Concepts

1. **Base Class (Parent/Superclass)**: The class being inherited from
2. **Derived Class (Child/Subclass)**: The class that inherits
3. **IS-A Relationship**: Child IS-A type of Parent (Dog IS-A Animal)
4. **Code Reuse**: Inherit common functionality, add specific behavior
5. **Method Overriding**: Child can replace parent's method with its own version

### Basic Syntax

```python
class Vehicle:  # Base class
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def start(self):
        print(f"{self.brand} {self.model} started")

class Car(Vehicle):  # Derived class inherits from Vehicle
    def __init__(self, brand, model, num_doors):
        super().__init__(brand, model)  # Call parent constructor
        self.num_doors = num_doors

    # Inherit start() method from Vehicle
    # Add car-specific method
    def open_trunk(self):
        print("Trunk opened")
```

## How It Works

### 1. Inheriting Attributes and Methods

```python
car = Car("Toyota", "Camry", 4)
car.start()  # Inherited method from Vehicle
# Output: "Toyota Camry started"
```

The `Car` class has access to all public and protected members of `Vehicle`.

### 2. Extending Functionality

Child classes can add new methods and attributes:

```python
class ElectricCar(Car):
    def __init__(self, brand, model, num_doors, battery_capacity):
        super().__init__(brand, model, num_doors)
        self.battery_capacity = battery_capacity

    def charge(self):  # New method specific to ElectricCar
        print(f"Charging {self.battery_capacity}kWh battery")
```

### 3. Method Overriding

Child classes can replace parent methods:

```python
class ElectricCar(Vehicle):
    def start(self):  # Overrides Vehicle.start()
        print(f"Electric {self.brand} {self.model} powered on silently")
```

### 4. Using super()

`super()` allows calling the parent class's methods:

```python
class Car(Vehicle):
    def start(self):
        super().start()  # Call parent's start()
        print("Engine running")
```

## Types of Inheritance

### Single Inheritance

One child inherits from one parent:

```
Vehicle
   |
  Car
```

### Multi-Level Inheritance

Chain of inheritance:

```
Vehicle
   |
  Car
   |
ElectricCar
```

### Multiple Inheritance (Python supports this)

One child inherits from multiple parents:

```python
class ElectricCar(Car, Battery):
    pass
```

## Benefits

1. **Code Reuse**: Write common code once, use everywhere
2. **Maintainability**: Update in one place, reflects in all children
3. **Logical Hierarchy**: Models real-world relationships
4. **Polymorphism**: Treat different types uniformly
5. **Extensibility**: Add new types without modifying existing code

## Trade-offs

### Advantages
- Reduces code duplication
- Easy to add new types
- Clear hierarchical structure
- Supports polymorphism

### Disadvantages
- Creates tight coupling between parent and child
- Changes to parent affect all children
- Deep hierarchies can be hard to understand
- Can lead to fragile base class problem

## When to Use

Use inheritance when:
- Clear IS-A relationship exists (Dog IS-A Animal)
- Significant code can be reused
- You need polymorphic behavior
- Hierarchy is stable and logical

Avoid inheritance when:
- Relationship is HAS-A not IS-A (Car HAS-A Engine, use composition)
- Hierarchy is deep or unclear
- You just want code reuse (consider composition instead)
- Child doesn't fit parent's contract (violates Liskov Substitution)

## Best Practices

### 1. Keep Hierarchies Shallow

Prefer 2-3 levels maximum. Deep hierarchies are hard to understand.

### 2. Favor Composition Over Inheritance

If the relationship isn't clearly IS-A, use composition:

```python
class Car:
    def __init__(self):
        self.engine = Engine()  # HAS-A relationship
```

### 3. Don't Break Parent's Contract

Child classes must fulfill parent's promises (Liskov Substitution Principle).

### 4. Use Abstract Base Classes

Define clear contracts for hierarchies:

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def make_sound(self):
        pass
```

## Real-World Applications

1. **GUI Frameworks**: Button, TextBox, CheckBox all inherit from Widget
2. **Game Development**: Player, Enemy, NPC inherit from Character
3. **Web Frameworks**: Different view types inherit from BaseView
4. **Database Models**: Specific models inherit from Model base class
5. **Exception Handling**: Custom exceptions inherit from Exception

## Common Patterns

### Template Method Pattern

```python
class DataProcessor:
    def process(self):
        self.load_data()
        self.parse_data()
        self.save_data()

    def load_data(self):
        raise NotImplementedError

class CSVProcessor(DataProcessor):
    def load_data(self):
        # CSV-specific loading
        pass
```

### Protected Members

```python
class Base:
    def __init__(self):
        self._protected_var = 10  # Convention: for internal/child use

class Derived(Base):
    def use_protected(self):
        return self._protected_var * 2
```

## Key Takeaways

1. Inheritance models IS-A relationships
2. Child classes inherit attributes and methods from parents
3. Use `super()` to call parent class methods
4. Method overriding allows specialization
5. Supports code reuse and polymorphism
6. Keep hierarchies shallow and logical
7. Prefer composition when relationship isn't IS-A
8. Inheritance creates coupling between classes
9. Abstract base classes define contracts
10. Balance reuse benefits against coupling costs

Inheritance is powerful but should be used judiciously. Ask "IS-A or HAS-A?" before choosing inheritance over composition.
