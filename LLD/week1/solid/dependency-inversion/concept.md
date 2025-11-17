# Dependency Inversion Principle (DIP)

## The Concept

High-level modules should not depend on low-level modules. Both should depend on abstractions.

## The Problem

```python
class EmailService:
    def send(self, msg): pass

class NotificationService:
    def __init__(self):
        self.email = EmailService()  # Direct dependency!
```

NotificationService coupled to EmailService.

## The Solution

Depend on abstractions, inject dependencies.

```python
class MessageSender(ABC):
    @abstractmethod
    def send(self, msg): pass

class EmailSender(MessageSender):
    def send(self, msg): pass

class NotificationService:
    def __init__(self, sender: MessageSender):
        self.sender = sender  # Depends on abstraction!
```

## Key Takeaways

- Depend on interfaces, not concrete classes
- Use dependency injection
- High-level logic independent of low-level details
- Easy to swap implementations
