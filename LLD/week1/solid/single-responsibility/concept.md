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

:::multilang
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

```cpp
#include <string>

class User {
private:
    std::string name;
    std::string email;

public:
    User(const std::string& name, const std::string& email)
        : name(name), email(email) {}

    void validateEmail() {
        // Email validation logic
    }

    void saveToDatabase() {
        // Database logic
    }

    void sendWelcomeEmail() {
        // Email sending logic
    }

    void logActivity() {
        // Logging logic
    }
};
```

```java
public class User {
    private String name;
    private String email;

    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }

    public void validateEmail() {
        // Email validation logic
    }

    public void saveToDatabase() {
        // Database logic
    }

    public void sendWelcomeEmail() {
        // Email sending logic
    }

    public void logActivity() {
        // Logging logic
    }
}
```
:::

One class, four responsibilities!

### After SRP

:::multilang
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

```cpp
#include <string>
#include <memory>

class User {
private:
    std::string name;
    std::string email;

public:
    User(const std::string& name, const std::string& email)
        : name(name), email(email) {}

    std::string getName() const { return name; }
    std::string getEmail() const { return email; }
};

class EmailValidator {
public:
    bool validate(const std::string& email) {
        // Validation logic
        return true;
    }
};

class UserRepository {
public:
    void save(const User& user) {
        // Database logic
    }
};

class EmailService {
public:
    void sendWelcome(const User& user) {
        // Email logic
    }
};

class Logger {
public:
    void log(const std::string& message) {
        // Logging logic
    }
};
```

```java
public class User {
    private String name;
    private String email;

    public User(String name, String email) {
        this.name = name;
        this.email = email;
    }

    public String getName() { return name; }
    public String getEmail() { return email; }
}

public class EmailValidator {
    public boolean validate(String email) {
        // Validation logic
        return true;
    }
}

public class UserRepository {
    public void save(User user) {
        // Database logic
    }
}

public class EmailService {
    public void sendWelcome(User user) {
        // Email logic
    }
}

public class Logger {
    public void log(String message) {
        // Logging logic
    }
}
```
:::

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
