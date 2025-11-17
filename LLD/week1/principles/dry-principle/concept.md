# DRY Principle: Don't Repeat Yourself

## The Hook: Copy-Paste Nightmare

You write email validation logic in three places: user registration, profile update, and contact form. A bug is found. You fix it in registration. Weeks later, users report the same bug in the contact form. You forgot to fix it there. Now you must hunt through the codebase to find all copies.

This is the cost of code duplication.

## The Problem: Code Duplication

When the same logic exists in multiple places:

1. **Maintenance Burden**: Must update code in multiple places
2. **Inconsistency Risk**: Easy to update some but not all copies
3. **Bugs Multiply**: Same bug exists everywhere the code is duplicated
4. **Harder to Understand**: More code to read and maintain
5. **Wasted Effort**: Writing the same code repeatedly

Every piece of duplicated code is a liability waiting to cause problems.

## The Solution: DRY Principle

DRY states: "Every piece of knowledge must have a single, unambiguous representation in a system."

Write logic once, use it everywhere. When changes are needed, update in one place.

## How It Works

### Before DRY (Violation)

```python
class UserManager:
    def create_user(self, email):
        if not email or "@" not in email or "." not in email.split("@")[1]:
            return False
        # Create user...

    def update_email(self, email):
        if not email or "@" not in email or "." not in email.split("@")[1]:
            return False
        # Update email...

    def send_invite(self, email):
        if not email or "@" not in email or "." not in email.split("@")[1]:
            return False
        # Send invite...
```

Same validation repeated three times!

### After DRY (Following Principle)

```python
class EmailValidator:
    @staticmethod
    def is_valid(email):
        if not email:
            return False
        if "@" not in email:
            return False
        if "." not in email.split("@")[1]:
            return False
        return True

class UserManager:
    def create_user(self, email):
        if not EmailValidator.is_valid(email):
            return False
        # Create user...

    def update_email(self, email):
        if not EmailValidator.is_valid(email):
            return False
        # Update email...

    def send_invite(self, email):
        if not EmailValidator.is_valid(email):
            return False
        # Send invite...
```

Validation logic exists once. Used everywhere.

## Benefits

1. **Single Source of Truth**: One place to find and update logic
2. **Easier Maintenance**: Change once, fixed everywhere
3. **Consistency**: All usages guaranteed to be identical
4. **Less Code**: Reduce overall codebase size
5. **Fewer Bugs**: Fix once, fixed everywhere

## Trade-offs

### Advantages
- Reduces duplication
- Easier to maintain
- More consistent
- Fewer bugs

### Disadvantages
- Can create premature abstractions
- May reduce code locality (harder to see everything in one place)
- Over-DRY can make code harder to understand

## When to Use

Apply DRY when:
- Same logic appears in multiple places
- Logic is likely to change
- Duplication causes maintenance problems

Don't over-apply when:
- Code looks similar but serves different purposes
- Abstraction makes code harder to understand
- Duplication is accidental, not essential

## Real-World Applications

1. **Validation Logic**: Email, phone, password validation
2. **API Responses**: Standard response formatting
3. **Error Handling**: Common error handling patterns
4. **Database Queries**: Reusable query builders
5. **Configuration**: Centralized config management

## Key Takeaways

1. Don't Repeat Yourself - write logic once
2. Extract common patterns into reusable functions/classes
3. Single source of truth prevents inconsistencies
4. Balance between DRY and code clarity
5. Refactor duplication when you see it the third time (Rule of Three)

DRY is not about eliminating all similar code. It's about eliminating duplicated knowledge and logic.
