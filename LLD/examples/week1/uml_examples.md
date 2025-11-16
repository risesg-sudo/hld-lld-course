# UML Diagram Examples for LLD Week 1

This document contains UML diagram examples in ASCII art format for the design principles and patterns covered in Week 1.

---

## Table of Contents
1. [Class Diagram Basics](#class-diagram-basics)
2. [Inheritance (IS-A Relationship)](#inheritance-is-a-relationship)
3. [Composition (HAS-A Relationship)](#composition-has-a-relationship)
4. [Dependency Relationship](#dependency-relationship)
5. [Aggregation Relationship](#aggregation-relationship)
6. [Single Responsibility Principle](#single-responsibility-principle)
7. [Open/Closed Principle](#open-closed-principle)
8. [Liskov Substitution Principle](#liskov-substitution-principle)
9. [Interface Segregation Principle](#interface-segregation-principle)
10. [Dependency Inversion Principle](#dependency-inversion-principle)
11. [Factory Pattern](#factory-pattern)
12. [Abstract Factory Pattern](#abstract-factory-pattern)

---

## Class Diagram Basics

### Simple Class

```
┌─────────────────────────┐
│      ClassName          │
├─────────────────────────┤
│ - attribute: Type       │
│ - anotherAttr: String   │
├─────────────────────────┤
│ + method(): ReturnType  │
│ + anotherMethod()       │
└─────────────────────────┘
```

### Class with Visibility Modifiers

```
┌─────────────────────────────┐
│      Car                    │
├─────────────────────────────┤
│ - speed: int                │ (private, -)
│ # gear: String              │ (protected, #)
│ + color: String             │ (public, +)
├─────────────────────────────┤
│ + start(): void             │
│ + stop(): void              │
│ - checkEngine(): boolean    │
└─────────────────────────────┘
```

---

## Inheritance (IS-A Relationship)

```
                ┌──────────────────┐
                │    Vehicle       │
                │ (Abstract Class) │
                ├──────────────────┤
                │ - speed: int     │
                ├──────────────────┤
                │ + start()        │
                │ + stop()         │
                │ + drive()        │
                └──────────────────┘
                        ▲
           ┌────────────┼────────────┐
           │            │            │
           │            │            │
      ┌────┴─────┐ ┌───┴────┐ ┌───┴─────┐
      │    Car   │ │Motorcycle│ │  Truck │
      ├──────────┤ ├────────┤ ├────────┤
      │ + doors  │ │ -wheels│ │ +cargo │
      └──────────┘ └────────┘ └────────┘

Legend:
─────── (hollow triangle) = Inheritance
        The child class IS-A type of parent class
```

---

## Composition (HAS-A Relationship)

```
┌─────────────────────────┐
│      Car                │
├─────────────────────────┤
│ - engine: Engine ◆      │
│ - wheels: Wheel[] ◆     │
│ - seats: Seat[] ◆       │
├─────────────────────────┤
│ + start()               │
└─────────────────────────┘
        ◆ (filled diamond)

        │
        │ (whole-part relationship)
        │ Car OWNS-A Engine
        │
        ▼

┌─────────────────────────┐
│      Engine             │
├─────────────────────────┤
│ - horsepower: int       │
│ - type: String          │
├─────────────────────────┤
│ + ignite()              │
│ + stop()                │
└─────────────────────────┘

Legend:
◆ (filled diamond) = Composition (whole-part, strong ownership)
  If Car is destroyed, Engine is destroyed
```

---

## Aggregation Relationship

```
┌─────────────────────────┐
│      Company            │
├─────────────────────────┤
│ - name: String          │
│ - employees: Employee[] │
├─────────────────────────┤
│ + hire()                │
│ + fire()                │
└─────────────────────────┘
        ◇ (hollow diamond)

        │
        │ (has-a relationship)
        │ Company HAS Employee(s)
        │ But Employee can exist independently
        │
        ▼

┌─────────────────────────┐
│      Employee           │
├─────────────────────────┤
│ - name: String          │
│ - salary: float         │
├─────────────────────────┤
│ + work()                │
│ + getTax()              │
└─────────────────────────┘

Legend:
◇ (hollow diamond) = Aggregation (has-a, weak ownership)
  Employee can exist even if Company is destroyed
```

---

## Dependency Relationship

```
┌──────────────────────────────┐
│     NotificationService      │
├──────────────────────────────┤
│ - senders: list              │
├──────────────────────────────┤
│ + sendNotification()         │
└──────────────────────────────┘
        ┊
        ┊ ──────► (dashed line = dependency)
        ┊         Depends on, but doesn't own
        ┊
        ▼

┌──────────────────────────────┐
│    NotificationSender        │
│ (Abstract/Interface)         │
├──────────────────────────────┤
│ + send(message): boolean     │
└──────────────────────────────┘

Legend:
┊────► = Dependency (dashed line with arrow)
        Uses but doesn't own or inherit
```

---

## Single Responsibility Principle

### ❌ BAD: Multiple Responsibilities

```
┌─────────────────────────────────────────┐
│          BadUser                        │
├─────────────────────────────────────────┤
│ - name: String                          │
│ - email: String                         │
├─────────────────────────────────────────┤
│ + validateEmail()                       │ ← Validation
│ + validateName()                        │ ← Validation
│ + saveToDB()                            │ ← Database
│ + sendWelcomeEmail()                    │ ← Email
│ + logUserCreation()                     │ ← Logging
│ + createUser()                          │ ← Orchestration
└─────────────────────────────────────────┘

Problem: Too many reasons to change!
- Change validation logic → modify User
- Change database structure → modify User
- Change email provider → modify User
- Change logging format → modify User
```

### ✅ GOOD: Single Responsibilities

```
┌──────────────┐
│    User      │
├──────────────┤
│ - name       │
│ - email      │
├──────────────┤
│ + toString() │
└──────────────┘
    ▲
    │ (uses)
    │
    ├──────────────────────────────────────┐
    │                                      │
    ▼                                      ▼

┌─────────────────────┐     ┌──────────────────────┐
│ UserValidator       │     │ UserRepository       │
├─────────────────────┤     ├──────────────────────┤
│ + validateEmail()   │     │ + save()             │
│ + validateName()    │     │ + get()              │
│ + validateUser()    │     │ + delete()           │
└─────────────────────┘     └──────────────────────┘
         ▲                            ▲
         │                            │
         ├───┬────────────────────┬───┤
         │   │                    │   │
         │   ▼                    ▼   │
         │
        ┌─────────────────────┐
        │ EmailService        │
        ├─────────────────────┤
        │ + sendWelcome()     │
        │ + sendNotification()│
        └─────────────────────┘
         │
         │
        ┌─────────────────────┐
        │ Logger              │
        ├─────────────────────┤
        │ + log()             │
        └─────────────────────┘
        │
        │
        ┌─────────────────────┐
        │ UserService         │
        │ (Orchestrator)      │
        ├─────────────────────┤
        │ + createUser()      │
        └─────────────────────┘

Each class: ONE reason to change
```

---

## Open/Closed Principle

### ❌ BAD: Closed for Extension

```
┌──────────────────────────────────────┐
│   BadDiscountCalculator              │
├──────────────────────────────────────┤
│ + calculate(type: String): float     │
│   if type == "percentage"            │
│   if type == "fixed"                 │
│   if type == "bulk"                  │
│   if type == "loyalty"               │
│                                      │
│   NEED TO MODIFY THIS METHOD FOR     │
│   EVERY NEW DISCOUNT TYPE!           │
└──────────────────────────────────────┘

Problem: CLOSED for extension (can't add without modifying)
         OPEN for modification (must change code)
         (Opposite of what we want!)
```

### ✅ GOOD: Open for Extension, Closed for Modification

```
┌──────────────────────────┐
│ DiscountStrategy         │
│ (Abstract)               │
├──────────────────────────┤
│ + calculate(): float     │
└──────────────────────────┘
         △ △ △
         │ │ │
    ┌────┘ │ └──────┐
    │      │        │
    ▼      ▼        ▼

┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
│PercentageDisc   │  │ FixedDiscount│  │ BulkDiscount │
├──────────────────┤  ├──────────────┤  ├──────────────┤
│ percentage       │  │ amount       │  │ minAmount    │
├──────────────────┤  ├──────────────┤  ├──────────────┤
│ + calculate()    │  │ + calculate()│  │ + calculate()│
└──────────────────┘  └──────────────┘  └──────────────┘

    ┌──────────────────────────┐
    │ ReferralDiscount         │ ← NEW! No changes to existing code!
    ├──────────────────────────┤
    │ referralCount            │
    ├──────────────────────────┤
    │ + calculate()            │
    └──────────────────────────┘

Benefits:
- OPEN for extension (add new DiscountStrategy)
- CLOSED for modification (DiscountCalculator never changes)
```

---

## Liskov Substitution Principle

### ❌ BAD: Violating LSP

```
        ┌──────────────────┐
        │    Rectangle     │
        ├──────────────────┤
        │ - width          │
        │ - height         │
        ├──────────────────┤
        │ + setWidth()     │
        │ + setHeight()    │
        │ + getArea()      │
        └──────────────────┘
                ▲
                │
                │ IS-A (wrong inheritance!)
                │
                ▼

        ┌──────────────────┐
        │     Square       │
        ├──────────────────┤
        │ - side           │
        ├──────────────────┤
        │ + setWidth()     │ ← Changes height too! (breaks contract)
        │ + setHeight()    │ ← Changes width too! (breaks contract)
        │ + getArea()      │
        └──────────────────┘

Problem: Square doesn't follow Rectangle's contract!
- Rectangle: setWidth() changes only width
- Square: setWidth() changes both width and height
- Can't substitute Square for Rectangle safely
```

### ✅ GOOD: Respecting LSP

```
        ┌──────────────┐
        │    Shape     │
        │ (Abstract)   │
        ├──────────────┤
        │ + getArea()  │
        │ + getName()  │
        └──────────────┘
                △ △
                │ │
       ┌────────┘ └────────┐
       │                   │
       ▼                   ▼

┌──────────────────┐  ┌──────────────────┐
│   Rectangle      │  │     Square       │
├──────────────────┤  ├──────────────────┤
│ - width          │  │ - side           │
│ - height         │  ├──────────────────┤
├──────────────────┤  │ + setSide()      │
│ + setWidth()     │  │ + getArea()      │
│ + setHeight()    │  │ + getName()      │
│ + getArea()      │  └──────────────────┘
│ + getName()      │
└──────────────────┘

Also...

┌──────────────────┐
│     Circle       │
├──────────────────┤
│ - radius         │
├──────────────────┤
│ + setRadius()    │
│ + getArea()      │
│ + getName()      │
└──────────────────┘

Benefits:
✓ Each shape respects its own contract
✓ Rectangle, Square, Circle all implement Shape correctly
✓ Can substitute any Shape for another
✓ No unexpected behavior
```

---

## Interface Segregation Principle

### ❌ BAD: Fat Interface

```
┌─────────────────────────────────┐
│ BadMultiFunctionDevice          │
│ (Fat Interface - too much!)     │
├─────────────────────────────────┤
│ + print()                       │
│ + scan()                        │
│ + fax()                         │
│ + copy()                        │
└─────────────────────────────────┘
      ▲            ▲
      │            │
      │            └─── SimplePrinter
      │                 (can only print!)
      │                 Forced to implement scan(), fax(), copy()
      │
      └─── Copier
           (can only copy!)
           Forced to implement print(), scan(), fax()

Problem: Classes forced to implement methods they don't have!
         Raises NotImplementedError
         Violates Liskov Substitution Principle
```

### ✅ GOOD: Segregated Interfaces

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Printer    │   │   Scanner    │   │    Copier    │
├──────────────┤   ├──────────────┤   ├──────────────┤
│ + print()    │   │ + scan()     │   │ + copy()     │
└──────────────┘   └──────────────┘   └──────────────┘
       △ △ △             △ △             △ △
       │ │ │             │ │             │ │
       │ │ │             │ │             │ │
       │ │ └─────────┐   │ │             │ │
       │ │           │   │ │             │ │
       │ │           ▼   ▼ ▼             ▼ ▼
       │ │
    ┌──┴─┴──────────────────────────────┐
    │   MultiPurposeDevice              │
    │  (implements all interfaces)      │
    ├───────────────────────────────────┤
    │ + print()                         │
    │ + scan()                          │
    │ + copy()                          │
    │ + fax()                           │
    └───────────────────────────────────┘
       │ │ │ │
       │ │ │ └───────────────────────────── FaxMachine interface
       │ │ └─────────────────────────────── Copier interface
       │ └───────────────────────────────── Scanner interface
       └─────────────────────────────────── Printer interface

Also...

┌──────────────┐   ┌──────────────┐
│SimplePrinter │   │ BasicCopier  │
│(Printer only)│   │ (Copier only)│
├──────────────┤   ├──────────────┤
│ + print()    │   │ + copy()     │
└──────────────┘   └──────────────┘

Benefits:
✓ Each class implements only what it needs
✓ No NotImplementedError
✓ Clear what each device can do
✓ Easy to add new devices
✓ No unused methods
```

---

## Dependency Inversion Principle

### ❌ BAD: High-Level Depends on Low-Level

```
┌──────────────────────────────┐
│ NotificationService          │ (High-level)
│ (Concrete Dependencies)      │
├──────────────────────────────┤
│ - emailSender: EmailSender   │ ← Direct dependency
│ - smsSender: SMSSender       │ ← Direct dependency
├──────────────────────────────┤
│ + sendNotification()         │
└──────────────────────────────┘
  │         │
  │ uses    │ uses (concrete)
  │         │
  ▼         ▼

┌──────────────────┐  ┌──────────────────┐
│  EmailSender     │  │   SMSSender      │
│ (Low-level)      │  │ (Low-level)      │
├──────────────────┤  ├──────────────────┤
│ + sendEmail()    │  │ + sendSms()      │
└──────────────────┘  └──────────────────┘

Problem: High-level (NotificationService) depends on low-level (EmailSender)
         Tight coupling
         Can't easily add new senders
         Hard to test
```

### ✅ GOOD: Both Depend on Abstraction

```
┌──────────────────────────────┐
│ NotificationService          │ (High-level)
│ (Depends on abstraction)     │
├──────────────────────────────┤
│ - senders: dict              │
├──────────────────────────────┤
│ + registerSender()           │
│ + sendNotification()         │
└──────────────────────────────┘
      │
      │ depends on
      │ (abstract)
      ▼

┌──────────────────────────────┐
│    NotificationSender        │
│      (Abstraction)           │
├──────────────────────────────┤
│ + send(message): boolean     │
└──────────────────────────────┘
           △ △ △ △
           │ │ │ │
    ┌──────┘ │ │ └───┐
    │        │ │     │
    ▼        ▼ ▼     ▼

┌──────────────┐ ┌─────────┐ ┌──────┐ ┌────────┐
│   Email      │ │  SMS    │ │Slack │ │ Teams  │
│  Sender      │ │ Sender  │ │Sender│ │ Sender │
│(Low-level)   │ │(Low-lvl)│ │(Low) │ │ (New!) │
└──────────────┘ └─────────┘ └──────┘ └────────┘

Benefits:
✓ High-level depends on abstraction
✓ Low-level implements abstraction
✓ Loose coupling
✓ Easy to add new senders
✓ Easy to test with mocks
✓ Follows Dependency Injection pattern
```

---

## Factory Pattern

```
┌──────────────────────────────┐
│    VehicleFactory            │
│    (Concrete Factory)        │
├──────────────────────────────┤
│ + createVehicle(type)        │
│   if type == "car" → new Car │
│   if type == "bike" → new Bike
│   if type == "truck" → new Truck
└──────────────────────────────┘
        │
        │ creates
        │
        ├─────────────────┬──────────────┬─────────────┐
        │                 │              │             │
        ▼                 ▼              ▼             ▼

┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Car        │ │  Motorcycle  │ │    Truck     │ │     Bus      │
│(Concrete)    │ │(Concrete)    │ │(Concrete)    │ │(Concrete)    │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ + start()    │ │ + start()    │ │ + start()    │ │ + start()    │
│ + drive()    │ │ + drive()    │ │ + drive()    │ │ + drive()    │
│ + stop()     │ │ + stop()     │ │ + stop()     │ │ + stop()     │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         △              △              △              △
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                       │
                       │ implements
                       │
                       ▼
              ┌──────────────────┐
              │    Vehicle       │
              │   (Abstract)     │
              ├──────────────────┤
              │ + start()        │
              │ + drive()        │
              │ + stop()         │
              └──────────────────┘

Usage:
  vehicle = VehicleFactory.create_vehicle("car")
  vehicle.start()
  vehicle.drive()

Benefits:
✓ Client doesn't know about concrete classes
✓ Object creation centralized
✓ Easy to add new types
✓ Follows OCP and DIP
```

---

## Abstract Factory Pattern

```
┌────────────────────────────────────────────────┐
│           UIFactory                            │
│      (Abstract Factory)                        │
├────────────────────────────────────────────────┤
│ + createButton()                               │
│ + createCheckbox()                             │
│ + createTextBox()                              │
└────────────────────────────────────────────────┘
         △ △ △
         │ │ │
    ┌────┘ │ └──────┐
    │      │        │
    ▼      ▼        ▼

┌─────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ WindowsUIFactory    │  │ MacUIFactory     │  │ LinuxUIFactory   │
├─────────────────────┤  ├──────────────────┤  ├──────────────────┤
│ + createButton()    │  │ + createButton() │  │ + createButton() │
│ + createCheckbox()  │  │ + createCheckbox │  │ + createCheckbox │
│ + createTextBox()   │  │ + createTextBox()│  │ + createTextBox()│
└─────────────────────┘  └──────────────────┘  └──────────────────┘
         │                       │                       │
         │ creates family        │ creates family        │ creates family
         │ of Windows UI         │ of Mac UI             │ of Linux UI
         │
         ├──────────────┬──────────────┬─────────────────┐
         │              │              │                 │
         ▼              ▼              ▼                 ▼

┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│WindowsButton │ │WindowsChkbox │ │WindowsTextBox│ ...
└──────────────┘ └──────────────┘ └──────────────┘

    △ △ △ △                △ △ △ △                △ △ △ △
    │ │ │ │                │ │ │ │                │ │ │ │
    └─┴─┴─┘                └─┴─┴─┘                └─┴─┴─┘
       │                      │                      │
       ▼                      ▼                      ▼

   ┌──────────┐          ┌──────────┐          ┌──────────┐
   │  Button  │          │ Checkbox │          │ TextBox  │
   │(Abstract)│          │(Abstract)│          │(Abstract)│
   └──────────┘          └──────────┘          └──────────┘

Client Code:
  if (platform == "windows"):
      factory = WindowsUIFactory()
  elif (platform == "mac"):
      factory = MacUIFactory()

  window = ApplicationWindow(factory)
  window.render()

Benefits:
✓ Creates families of related objects together
✓ Ensures consistency across family
✓ Easy to switch entire UI framework
✓ Client doesn't know platform
✓ Follows OCP and DIP
```

---

## Relationship Summary Table

| Relationship | Symbol | Meaning | Code Example |
|---|---|---|---|
| **Inheritance** | ─┬─ (hollow triangle) | IS-A relationship | `class Dog(Animal):` |
| **Composition** | ◆─── (filled diamond) | Whole-part, strong ownership | `self.engine = Engine()` |
| **Aggregation** | ◇─── (hollow diamond) | Has-a, weak ownership | `self.employees = []` |
| **Dependency** | ┊──→ (dashed arrow) | Uses/depends on | `def process(db: Database)` |
| **Realization** | ┈┈→ (dotted arrow) | Implements interface | `class Car(Vehicle):` |

---

## Design Pattern Quick Reference

### Creational Patterns (Object Creation)
- **Factory Pattern**: Single method creates different object types
- **Abstract Factory**: Creates families of related objects
- **Builder Pattern**: Complex object construction (step-by-step)
- **Singleton Pattern**: Only one instance exists
- **Prototype Pattern**: Clone existing objects

### Structural Patterns (Object Composition)
- **Adapter Pattern**: Make incompatible interfaces work together
- **Decorator Pattern**: Add behavior to objects dynamically
- **Facade Pattern**: Provide simplified interface to subsystem
- **Proxy Pattern**: Control access to another object
- **Bridge Pattern**: Decouple abstraction from implementation
- **Composite Pattern**: Tree structure of objects

### Behavioral Patterns (Object Interaction)
- **Observer Pattern**: Notify multiple objects of state change
- **Strategy Pattern**: Encapsulate interchangeable algorithms
- **Command Pattern**: Encapsulate requests as objects
- **State Pattern**: Object behavior changes with internal state
- **Template Method**: Define algorithm skeleton in base class
- **Iterator Pattern**: Access elements sequentially

---

## Notes on Reading UML Diagrams

### Arrows and Lines

```
Inheritance:
    ▲
    │ (solid line, hollow triangle)
    ├─ IS-A relationship
    │ Child extends Parent

Composition:
    ◆ (filled diamond)
    │ Whole-Part relationship
    │ Whole owns Part
    │ If Whole deleted, Part deleted

Aggregation:
    ◇ (hollow diamond)
    │ Has-A relationship
    │ Whole has Part
    │ Part can exist independently

Dependency:
    ┊──→ (dashed line, arrow)
    │ Uses/depends on
    │ Temporary relationship

Realization:
    ┈┈→ (dotted line, triangle)
    │ Class implements Interface
```

### Multiplicity Notations

```
1    - Exactly one
0..1 - Zero or one
*    - Zero or more (any number)
1..*  - One or more
2..5 - Between 2 and 5
n    - Specific number
```

Example:
```
Company ────┐ 1      * ┌──── Employee
            │ (has many)  │
            └────────────┘
```

---

## Summary

This guide provides visual representations of:
1. **SOLID Principles**: Design guidelines for maintainable code
2. **Design Patterns**: Reusable solutions to common problems
3. **UML Notation**: Standard way to document design

Master these concepts and you'll be able to design robust, maintainable, and scalable software systems!
