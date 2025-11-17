"""
DRY Principle Example: Email Validation
Demonstrates extracting repeated logic into a single reusable component
"""

# BAD: Violating DRY - Repeated validation logic
class BadUserManager:
    def validate_user_email(self, email):
        if not email:
            return False, "Email required"
        if "@" not in email:
            return False, "Invalid email"
        if "." not in email.split("@")[1]:
            return False, "Invalid domain"
        return True, "Valid"

    def validate_admin_email(self, email):
        # Duplicate validation logic!
        if not email:
            return False, "Email required"
        if "@" not in email:
            return False, "Invalid email"
        if "." not in email.split("@")[1]:
            return False, "Invalid domain"
        return True, "Valid"

    def validate_contact_email(self, email):
        # Duplicate again!
        if not email:
            return False, "Email required"
        if "@" not in email:
            return False, "Invalid email"
        if "." not in email.split("@")[1]:
            return False, "Invalid domain"
        return True, "Valid"


# GOOD: Following DRY - Single source of truth
class EmailValidator:
    """Centralized email validation - single source of truth."""

    @staticmethod
    def validate(email):
        if not email:
            return False, "Email required"
        if "@" not in email:
            return False, "Invalid email"
        parts = email.split("@")
        if len(parts) != 2 or "." not in parts[1]:
            return False, "Invalid domain"
        return True, "Valid"


class GoodUserManager:
    """Uses centralized validation - no duplication."""

    def validate_user_email(self, email):
        return EmailValidator.validate(email)

    def validate_admin_email(self, email):
        return EmailValidator.validate(email)

    def validate_contact_email(self, email):
        return EmailValidator.validate(email)


# Demonstration
if __name__ == "__main__":
    print("=== DRY Principle Demo ===\n")

    print("BAD Example: Duplicated validation logic")
    print("-" * 50)
    bad_manager = BadUserManager()
    print(bad_manager.validate_user_email("test@example.com"))
    print(bad_manager.validate_admin_email("invalid"))
    print("Problem: Logic duplicated 3 times. Bug fix requires 3 changes!\n")

    print("GOOD Example: DRY - Single validation logic")
    print("-" * 50)
    good_manager = GoodUserManager()
    print(good_manager.validate_user_email("test@example.com"))
    print(good_manager.validate_admin_email("invalid"))
    print("Benefit: Logic in one place. Bug fix requires 1 change!")
