"""
Single Responsibility Principle Example
Each class has one, clearly defined responsibility
"""

# GOOD: Each class has single responsibility
class User:
    """Responsibility: Manage user data"""
    def __init__(self, name, email):
        self.name = name
        self.email = email


class EmailValidator:
    """Responsibility: Validate emails"""
    @staticmethod
    def is_valid(email):
        return email and "@" in email and "." in email.split("@")[1]


class UserRepository:
    """Responsibility: Database operations"""
    def __init__(self):
        self.users = {}
        
    def save(self, user):
        self.users[user.email] = user
        print(f"Saved {user.name} to database")


class EmailService:
    """Responsibility: Send emails"""
    @staticmethod
    def send_welcome(user):
        print(f"Sent welcome email to {user.email}")


class UserService:
    """Coordinates other services - orchestration responsibility"""
    def __init__(self, repo, email_service):
        self.repo = repo
        self.email_service = email_service
        
    def create_user(self, name, email):
        if not EmailValidator.is_valid(email):
            print("Invalid email")
            return False
            
        user = User(name, email)
        self.repo.save(user)
        self.email_service.send_welcome(user)
        return True


if __name__ == "__main__":
    print("=== Single Responsibility Principle ===\n")
    
    repo = UserRepository()
    email_svc = EmailService()
    user_svc = UserService(repo, email_svc)
    
    user_svc.create_user("Alice", "alice@example.com")
    print("\nEach class has one clear responsibility!")
