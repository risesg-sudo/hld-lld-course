# Encapsulation

## The Hook: A Real-World Problem

Imagine you're building a banking application. You create a `BankAccount` class with a `balance` attribute. Any part of your application can directly access and modify this balance:

```python
account.balance = -1000000  # Uh oh, negative balance!
account.balance = "invalid"  # Data corruption!
```

Without protection, critical data is vulnerable to corruption, unauthorized access, and violation of business rules. How do we solve this?

## The Problem: Uncontrolled Access to Data

In software systems, data integrity is paramount. When class attributes are exposed directly, several problems arise:

1. **No Validation**: Anyone can set invalid data (negative balances, incorrect formats)
2. **No Business Logic Enforcement**: Rules like "withdrawals cannot exceed balance" are bypassed
3. **Tight Coupling**: External code becomes dependent on internal implementation details
4. **Difficult to Debug**: When data corruption occurs, finding the source is nearly impossible
5. **No Audit Trail**: Cannot track when or how data was modified

Consider a simple `User` class without encapsulation:

```python
class User:
    def __init__(self, email):
        self.email = email
        self.is_verified = False

# External code can break everything
user = User("john@example.com")
user.email = "not-an-email"  # Invalid email
user.is_verified = "yes"      # Wrong type
```

The class has no control over its own data. This violates a fundamental principle: objects should be responsible for their own state.

## The Solution: Encapsulation

Encapsulation is the bundling of data (attributes) and methods (functions) that operate on that data within a single unit (class), while hiding the internal details from the outside world.

### Core Principles

1. **Hide Internal State**: Make attributes private
2. **Controlled Access**: Provide public methods for interaction
3. **Validation**: Enforce rules when data changes
4. **Abstraction**: Hide complexity, expose simple interface

### Implementation in Python

Python uses naming conventions for access control:

- **Public**: `name` - Accessible from anywhere
- **Protected**: `_name` - Convention: internal use only (not enforced)
- **Private**: `__name` - Name mangling prevents external access

### Proper Encapsulation Pattern

```python
class BankAccount:
    def __init__(self, account_number, initial_balance):
        self.__account_number = account_number  # Private
        self.__balance = initial_balance        # Private
        self.__transaction_history = []         # Private

    def deposit(self, amount):
        """Public method with validation"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self.__balance += amount
        self.__transaction_history.append(f"Deposit: ${amount}")
        return True

    def withdraw(self, amount):
        """Public method with business logic"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if amount > self.__balance:
            raise ValueError("Insufficient funds")

        self.__balance -= amount
        self.__transaction_history.append(f"Withdrawal: ${amount}")
        return True

    def get_balance(self):
        """Read-only access to balance"""
        return self.__balance
```

## Why It Works

### 1. Data Integrity

The class controls all access to its data. Invalid operations are prevented:

```python
account = BankAccount("ACC001", 1000)
account.withdraw(500)   # OK
account.withdraw(1000)  # Raises ValueError: Insufficient funds
```

### 2. Flexibility to Change Implementation

Since external code doesn't access internal attributes directly, you can change implementation without breaking clients:

```python
# Before: simple float
self.__balance = initial_balance

# After: use Decimal for precision (internal change, no external impact)
from decimal import Decimal
self.__balance = Decimal(str(initial_balance))
```

### 3. Audit and Logging

You can add logging, tracking, or notifications in one place:

```python
def withdraw(self, amount):
    if amount > 1000:
        self.__send_fraud_alert()  # Security check

    self.__log_transaction("withdraw", amount)  # Audit trail
    self.__balance -= amount
```

## Benefits of Encapsulation

1. **Data Protection**: Invalid states are prevented
2. **Maintainability**: Internal changes don't break external code
3. **Debugging**: Easy to track where data changes
4. **Reusability**: Well-encapsulated classes are easier to reuse
5. **Security**: Sensitive data is protected from unauthorized access

## Trade-offs

### Advantages
- Robust, reliable code
- Easy to maintain and extend
- Clear interface for users
- Enforces business rules

### Disadvantages
- More code to write (getters, setters, validation)
- Slight performance overhead from method calls
- Can be over-engineered for simple cases

## When to Use

Use encapsulation when:

- Data has validation requirements
- Business rules must be enforced
- Data is sensitive or critical
- Implementation may change in the future
- Multiple parts of code access the same data

Avoid over-encapsulation for:

- Simple data containers (DTOs, configuration objects)
- Internal helper classes
- Performance-critical sections where direct access is needed

## Common Patterns

### Read-Only Properties

```python
class Product:
    def __init__(self, id, name):
        self.__id = id
        self.__name = name

    def get_id(self):
        """ID is read-only, cannot be changed after creation"""
        return self.__id
```

### Computed Properties

```python
class Rectangle:
    def __init__(self, width, height):
        self.__width = width
        self.__height = height

    def get_area(self):
        """Computed property, not stored"""
        return self.__width * self.__height
```

### Lazy Initialization

```python
class DataLoader:
    def __init__(self, filename):
        self.__filename = filename
        self.__data = None

    def get_data(self):
        """Load data only when first accessed"""
        if self.__data is None:
            self.__data = self.__load_from_file()
        return self.__data
```

## Real-World Applications

1. **Database Connections**: Hide connection details, expose simple query methods
2. **Configuration Management**: Validate settings, prevent invalid configurations
3. **User Authentication**: Protect password hashes, enforce security policies
4. **Financial Systems**: Ensure data integrity, enforce business rules
5. **Game Development**: Protect game state, prevent cheating

## Key Takeaways

1. Bundle data and methods that operate on that data
2. Hide internal implementation details
3. Provide controlled access through public methods
4. Validate all inputs to maintain data integrity
5. Encapsulation enables changes without breaking external code
6. Balance between protection and simplicity
7. Use private attributes (`__name`) for critical data
8. Provide getters for read access, methods for write access
9. Encapsulation is the foundation for building robust, maintainable systems

Encapsulation is not about hiding everything. It's about defining a clear contract between a class and its users, protecting invariants, and enabling evolution without breaking existing code.
