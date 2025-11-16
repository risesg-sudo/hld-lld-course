"""
DRY PRINCIPLE (Don't Repeat Yourself)
======================================

Core Concept:
The DRY principle states that every piece of knowledge must have a single,
unambiguous, representation within a system. It's about avoiding code duplication
and consolidating common logic into reusable functions or classes.

Benefits:
- Reduces maintenance burden
- Minimizes bugs (fix once, fixed everywhere)
- Improves code readability
- Makes updates easier and less error-prone

Real-world analogy:
Instead of writing validation logic in multiple places, write it once
and reuse it everywhere.
"""


# ============================================================================
# BAD EXAMPLE: Violating DRY Principle - Code Duplication
# ============================================================================

class BadUserValidator:
    """
    This class demonstrates DRY violation by repeating email validation logic
    in multiple methods.
    """

    def validate_user_email(self, email: str) -> bool:
        """Validate email in user creation."""
        if not email:
            print("ERROR: Email is required")
            return False

        if "@" not in email:
            print("ERROR: Invalid email format")
            return False

        if "." not in email.split("@")[1]:
            print("ERROR: Invalid email domain")
            return False

        return True

    def validate_admin_email(self, email: str) -> bool:
        """Validate email in admin creation - DUPLICATED CODE."""
        if not email:
            print("ERROR: Email is required")
            return False

        if "@" not in email:
            print("ERROR: Invalid email format")
            return False

        if "." not in email.split("@")[1]:
            print("ERROR: Invalid email domain")
            return False

        return True

    def validate_contact_email(self, email: str) -> bool:
        """Validate email in contact form - DUPLICATED CODE AGAIN."""
        if not email:
            print("ERROR: Email is required")
            return False

        if "@" not in email:
            print("ERROR: Invalid email format")
            return False

        if "." not in email.split("@")[1]:
            print("ERROR: Invalid email domain")
            return False

        return True


def demo_bad_dry():
    """Demonstrate the problem with DRY violation."""
    print("\n" + "="*70)
    print("BAD EXAMPLE: DRY Violation")
    print("="*70)

    validator = BadUserValidator()

    print("\n1. Validating user email:")
    validator.validate_user_email("john@example.com")

    print("\n2. Validating admin email:")
    validator.validate_admin_email("admin@company.com")

    print("\n3. Validating contact email:")
    validator.validate_contact_email("invalid-email")

    print("\nProblem: If we need to change validation logic, we must update")
    print("it in THREE different places! Prone to bugs and inconsistencies.")


# ============================================================================
# GOOD EXAMPLE: Following DRY Principle - Single Source of Truth
# ============================================================================

class GoodEmailValidator:
    """
    This class follows the DRY principle by centralizing email validation logic
    in a single method that is reused everywhere.
    """

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """
        Centralized email validation logic - Single Source of Truth.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"

        if "@" not in email:
            return False, "Invalid email format"

        parts = email.split("@")
        if len(parts) != 2 or "." not in parts[1]:
            return False, "Invalid email domain"

        return True, "Email is valid"

    def validate_user_email(self, email: str) -> bool:
        """Validate email in user creation."""
        is_valid, message = self.validate_email(email)
        if is_valid:
            print(f"✓ User email validation passed: {message}")
        else:
            print(f"✗ User email validation failed: {message}")
        return is_valid

    def validate_admin_email(self, email: str) -> bool:
        """Validate email in admin creation - REUSES validation logic."""
        is_valid, message = self.validate_email(email)
        if is_valid:
            print(f"✓ Admin email validation passed: {message}")
        else:
            print(f"✗ Admin email validation failed: {message}")
        return is_valid

    def validate_contact_email(self, email: str) -> bool:
        """Validate email in contact form - REUSES validation logic."""
        is_valid, message = self.validate_email(email)
        if is_valid:
            print(f"✓ Contact email validation passed: {message}")
        else:
            print(f"✗ Contact email validation failed: {message}")
        return is_valid


def demo_good_dry():
    """Demonstrate proper DRY implementation."""
    print("\n" + "="*70)
    print("GOOD EXAMPLE: Following DRY Principle")
    print("="*70)

    validator = GoodEmailValidator()

    print("\n1. Validating user email:")
    validator.validate_user_email("john@example.com")

    print("\n2. Validating admin email:")
    validator.validate_admin_email("admin@company.com")

    print("\n3. Validating contact email:")
    validator.validate_contact_email("invalid-email")

    print("\nBenefit: Change validation logic ONCE, it's updated everywhere!")
    print("Single source of truth makes code maintainable and testable.")


# ============================================================================
# REAL-WORLD EXAMPLE: API Response Handler
# ============================================================================

class APIResponseHandler:
    """
    Real-world example showing DRY principle in API response handling.
    """

    @staticmethod
    def format_response(data: dict, status: int, message: str) -> dict:
        """
        Single source of truth for response formatting.
        This method is called by all handlers instead of duplicating logic.
        """
        return {
            "status": status,
            "message": message,
            "data": data,
            "timestamp": "2024-01-15T10:30:00Z"
        }

    def get_user(self, user_id: int) -> dict:
        """Get user endpoint."""
        # Fetch user from database
        user = {"id": user_id, "name": "John Doe", "email": "john@example.com"}
        return self.format_response(user, 200, "User retrieved successfully")

    def create_user(self, name: str, email: str) -> dict:
        """Create user endpoint."""
        # Create user in database
        user = {"id": 1, "name": name, "email": email}
        return self.format_response(user, 201, "User created successfully")

    def delete_user(self, user_id: int) -> dict:
        """Delete user endpoint."""
        return self.format_response({}, 204, "User deleted successfully")


def demo_real_world():
    """Demonstrate real-world DRY principle usage."""
    print("\n" + "="*70)
    print("REAL-WORLD EXAMPLE: API Response Handler")
    print("="*70)

    handler = APIResponseHandler()

    print("\n1. Getting user:")
    import json
    print(json.dumps(handler.get_user(1), indent=2))

    print("\n2. Creating user:")
    print(json.dumps(handler.create_user("Jane Doe", "jane@example.com"), indent=2))

    print("\n3. Deleting user:")
    print(json.dumps(handler.delete_user(1), indent=2))

    print("\nBenefit: All endpoints use the same response format.")
    print("Consistent API responses across the entire application.")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DRY PRINCIPLE EXAMPLES")
    print("="*70)

    # Bad example
    demo_bad_dry()

    # Good example
    demo_good_dry()

    # Real-world example
    demo_real_world()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. Identify repeated code patterns
2. Extract common logic into reusable functions/classes
3. Create a single source of truth
4. Make changes in one place, not multiple places
5. Use inheritance, composition, and utility functions to reduce duplication
6. Regular code review to catch DRY violations early
    """)
