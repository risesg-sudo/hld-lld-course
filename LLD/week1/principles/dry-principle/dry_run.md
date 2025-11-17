# Dry Run: DRY Principle

## Problem: Duplicated Logic

### Initial State (Bad Design)

Three methods with identical validation:
```
validate_user_email()
validate_admin_email()
validate_contact_email()
```

Each contains:
```python
if not email: return False
if "@" not in email: return False
if "." not in email.split("@")[1]: return False
return True
```

### Operation: Validate Email "test@example"

Executes in all three methods:
1. Check empty: False
2. Check @: True (contains @)
3. Check domain: False (no . after @)
4. Return: False, "Invalid domain"

**Problem**: Same 4 steps executed in 3 different places.

## Solution: DRY Implementation

### Refactored State

One validator:
```
EmailValidator.validate()
```

Three methods call it:
```
validate_user_email() → EmailValidator.validate()
validate_admin_email() → EmailValidator.validate()
validate_contact_email() → EmailValidator.validate()
```

### Operation: Validate "user@example.com"

**Step 1**: Call `validate_user_email("user@example.com")`

**Step 2**: Delegates to `EmailValidator.validate("user@example.com")`

**Step 3**: Validation executes once:
- Check empty: No
- Check @: Yes
- Check domain: "example.com" has "."
- Return: True, "Valid"

**Result**: Logic executed once, result shared by all callers.

## Key Difference

**Before (DRY Violation)**:
- 3 copies of validation logic
- Bug fix requires 3 changes
- Risk of inconsistency

**After (Following DRY)**:
- 1 validation implementation
- Bug fix requires 1 change
- Always consistent

## Benefits Demonstrated

1. **Maintenance**: Update validation once, applies everywhere
2. **Consistency**: All methods use identical logic
3. **Testability**: Test validator once, covers all uses
4. **Clarity**: Clear where validation logic lives

DRY eliminates duplication, creating maintainable, consistent code.
