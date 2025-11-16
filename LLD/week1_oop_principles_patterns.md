# Week 1: OOP Fundamentals, Principles & Design Patterns

## Table of Contents
1. [Object-Oriented Programming Fundamentals](#1-oop-fundamentals)
2. [DRY and KISS Principles](#2-dry-and-kiss-principles)
3. [SOLID Design Principles](#3-solid-principles)
4. [UML Class Diagrams](#4-uml-class-diagrams)
5. [Factory Pattern](#5-factory-pattern)
6. [Abstract Factory Pattern](#6-abstract-factory-pattern)

---

## 1. OOP Fundamentals

### Four Pillars of OOP

#### 1.1 Encapsulation
Bundling data and methods that operate on that data within a single unit (class), hiding internal details.

**Example: Bank Account**
```python
# See: LLD/examples/week1/encapsulation_example.py
```

#### 1.2 Inheritance
Mechanism where a new class derives properties and behavior from an existing class.

**Example: Vehicle Hierarchy**
```python
# See: LLD/examples/week1/inheritance_example.py
```

#### 1.3 Polymorphism
Ability of objects to take multiple forms. Same interface, different implementations.

**Example: Payment Processing**
```python
# See: LLD/examples/week1/polymorphism_example.py
```

#### 1.4 Abstraction
Hiding complex implementation details and showing only essential features.

**Example: Abstract Payment Processor**
```python
# See: LLD/examples/week1/abstraction_example.py
```

---

## 2. DRY and KISS Principles

### 2.1 DRY (Don't Repeat Yourself)
Every piece of knowledge must have a single, unambiguous representation in the system.

**Bad vs Good Example:**
```python
# See: LLD/examples/week1/dry_principle.py
```

### 2.2 KISS (Keep It Simple, Stupid)
Systems work best when they're kept simple rather than complex.

**Example:**
```python
# See: LLD/examples/week1/kiss_principle.py
```

---

## 3. SOLID Principles

### 3.1 Single Responsibility Principle (SRP)
A class should have only one reason to change.

**Example: User Management**
```python
# See: LLD/examples/week1/srp_example.py
```

### 3.2 Open/Closed Principle (OCP)
Software entities should be open for extension but closed for modification.

**Example: Discount Calculator**
```python
# See: LLD/examples/week1/ocp_example.py
```

### 3.3 Liskov Substitution Principle (LSP)
Objects of a superclass should be replaceable with objects of subclasses without breaking the application.

**Example: Rectangle and Square**
```python
# See: LLD/examples/week1/lsp_example.py
```

### 3.4 Interface Segregation Principle (ISP)
Clients should not be forced to depend on interfaces they don't use.

**Example: Multi-function Device**
```python
# See: LLD/examples/week1/isp_example.py
```

### 3.5 Dependency Inversion Principle (DIP)
High-level modules should not depend on low-level modules. Both should depend on abstractions.

**Example: Notification System**
```python
# See: LLD/examples/week1/dip_example.py
```

---

## 4. UML Class Diagrams

### Relationships in UML

1. **Association** - "has-a" relationship
2. **Aggregation** - "has-a" (weak ownership)
3. **Composition** - "has-a" (strong ownership)
4. **Inheritance** - "is-a" relationship
5. **Dependency** - "uses-a" relationship
6. **Realization** - implements interface

**Example Diagrams:**
```
See: LLD/examples/week1/uml_examples.md
```

---

## 5. Factory Pattern

### Intent
Define an interface for creating objects, but let subclasses decide which class to instantiate.

### When to Use
- When you don't know ahead of time what class object you need
- When classes delegate responsibility to subclasses
- When you want to localize object creation logic

### Example: Vehicle Factory
```python
# See: LLD/examples/week1/factory_pattern.py
```

**Real-world use case:** Creating different types of database connections (MySQL, PostgreSQL, MongoDB)

---

## 6. Abstract Factory Pattern

### Intent
Provide an interface for creating families of related or dependent objects without specifying their concrete classes.

### When to Use
- When system needs to be independent of how objects are created
- When you need to create families of related objects
- When you want to enforce constraints on which objects can be used together

### Example: UI Component Factory
```python
# See: LLD/examples/week1/abstract_factory_pattern.py
```

**Real-world use case:** Creating UI components for different operating systems (Windows, Mac, Linux)

---

## Key Takeaways

1. **OOP Fundamentals** are the foundation - master encapsulation, inheritance, polymorphism, and abstraction
2. **DRY and KISS** keep code maintainable and understandable
3. **SOLID Principles** ensure code is flexible, maintainable, and testable
4. **Factory Pattern** decouples object creation from usage
5. **Abstract Factory** creates families of related objects

## Interview Tips

1. Always explain the **why** behind using a pattern
2. Discuss trade-offs (complexity vs flexibility)
3. Relate patterns to real-world scenarios
4. Be ready to code patterns from scratch
5. Know when NOT to use a pattern (over-engineering)

## Practice Problems

1. Design a logging system using Factory pattern
2. Create a cross-platform GUI framework using Abstract Factory
3. Refactor a code snippet to follow SOLID principles
4. Design a payment processing system demonstrating all OOP concepts

---

Next: [Week 2: Creational & Behavioral Patterns](./week2_creational_behavioral.md)
