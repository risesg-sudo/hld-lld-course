# Single Responsibility Principle (SRP)

## The Hook: The Swiss Army Class

You create a `User` class that handles:
- User data storage
- Email validation
- Database persistence
- Email sending
- Logging

One class, five responsibilities. When email format changes, you modify User. When logging framework changes, you modify User. When database changes, you modify User. Too many reasons to change!

## The Problem

Classes with multiple responsibilities:
1. **Hard to Understand**: Too many concerns in one place
2. **Difficult to Test**: Must test multiple unrelated features
3. **Fragile**: Changes to one feature can break others
4. **Poor Reusability**: Cannot reuse one responsibility without the others

## The Solution: SRP

A class should have only ONE reason to change. Each class should have a single, well-defined responsibility.

### Before SRP

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        
    def validate_email(self):
        # Email validation logic
        pass
        
    def save_to_database(self):
        # Database logic
        pass
        
    def send_welcome_email(self):
        # Email sending logic
        pass
        
    def log_activity(self):
        # Logging logic
        pass
```

One class, four responsibilities!

### After SRP

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class EmailValidator:
    def validate(self, email):
        # Validation logic
        pass

class UserRepository:
    def save(self, user):
        # Database logic
        pass

class EmailService:
    def send_welcome(self, user):
        # Email logic
        pass

class Logger:
    def log(self, message):
        # Logging logic
        pass
```

Each class has one responsibility!

## Benefits

1. **Easy to Understand**: Clear what each class does
2. **Easy to Test**: Test one responsibility at a time
3. **Easy to Modify**: Changes isolated to one class
4. **Reusable**: Use each class independently

## When to Use

Apply SRP when:
- Class has multiple unrelated methods
- Class changes for different reasons
- Class is hard to name clearly
- Class is difficult to test

## Key Takeaways

1. One class, one responsibility
2. One reason to change
3. Separate concerns into different classes
4. Enables easier testing and maintenance
5. Use composition to combine responsibilities

SRP makes code modular, testable, and maintainable.
