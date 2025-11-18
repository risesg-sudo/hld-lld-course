# Dependency Inversion Principle (DIP)

## The Concept

High-level modules should not depend on low-level modules. Both should depend on abstractions.

## The Problem

:::multilang
```python
class EmailService:
    def send(self, msg): pass

class NotificationService:
    def __init__(self):
        self.email = EmailService()  # Direct dependency!
```

```cpp
#include <string>

class EmailService {
public:
    void send(const std::string& msg) { /* send email */ }
};

class NotificationService {
private:
    EmailService email;  // Direct dependency!
public:
    NotificationService() {}
    void notify(const std::string& msg) {
        email.send(msg);
    }
};
```

```java
public class EmailService {
    public void send(String msg) { /* send email */ }
}

public class NotificationService {
    private EmailService email;  // Direct dependency!

    public NotificationService() {
        this.email = new EmailService();
    }

    public void notify(String msg) {
        email.send(msg);
    }
}
```
:::

NotificationService coupled to EmailService.

## The Solution

Depend on abstractions, inject dependencies.

:::multilang
```python
from abc import ABC, abstractmethod

class MessageSender(ABC):
    @abstractmethod
    def send(self, msg): pass

class EmailSender(MessageSender):
    def send(self, msg): pass

class SMSSender(MessageSender):
    def send(self, msg): pass

class NotificationService:
    def __init__(self, sender: MessageSender):
        self.sender = sender  # Depends on abstraction!

    def notify(self, msg):
        self.sender.send(msg)
```

```cpp
#include <string>
#include <memory>

class MessageSender {
public:
    virtual ~MessageSender() = default;
    virtual void send(const std::string& msg) = 0;
};

class EmailSender : public MessageSender {
public:
    void send(const std::string& msg) override { /* send email */ }
};

class SMSSender : public MessageSender {
public:
    void send(const std::string& msg) override { /* send SMS */ }
};

class NotificationService {
private:
    std::unique_ptr<MessageSender> sender;
public:
    NotificationService(std::unique_ptr<MessageSender> s)
        : sender(std::move(s)) {}  // Depends on abstraction!

    void notify(const std::string& msg) {
        sender->send(msg);
    }
};
```

```java
public interface MessageSender {
    void send(String msg);
}

public class EmailSender implements MessageSender {
    @Override
    public void send(String msg) { /* send email */ }
}

public class SMSSender implements MessageSender {
    @Override
    public void send(String msg) { /* send SMS */ }
}

public class NotificationService {
    private MessageSender sender;

    public NotificationService(MessageSender sender) {
        this.sender = sender;  // Depends on abstraction!
    }

    public void notify(String msg) {
        sender.send(msg);
    }
}
```
:::

## Key Takeaways

- Depend on interfaces, not concrete classes
- Use dependency injection
- High-level logic independent of low-level details
- Easy to swap implementations
