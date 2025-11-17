# Dry Run: Single Responsibility Principle

## Operation: Create User

```python
user_svc.create_user("Alice", "alice@example.com")
```

### Execution Flow

**Step 1**: EmailValidator validates email
- Responsibility: Validation only
- Result: Valid

**Step 2**: User object created
- Responsibility: Data storage only
- Result: User("Alice", "alice@example.com")

**Step 3**: UserRepository saves to database
- Responsibility: Persistence only
- Result: Saved to database

**Step 4**: EmailService sends welcome email
- Responsibility: Email sending only
- Result: Email sent

### Classes Involved

| Class | Responsibility | Lines |
|-------|---------------|-------|
| User | Store data | 3 |
| EmailValidator | Validate emails | 4 |
| UserRepository | Database ops | 8 |
| EmailService | Send emails | 4 |
| UserService | Orchestrate | 10 |

### Benefits Demonstrated

1. **Clarity**: Each class has clear purpose
2. **Testability**: Test each class independently
3. **Maintainability**: Change database without affecting email
4. **Reusability**: Use EmailValidator anywhere

SRP creates modular, focused classes that are easy to understand and maintain.
