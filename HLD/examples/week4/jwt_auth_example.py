"""
JWT Authentication System

Comprehensive implementation of JWT-based authentication including:
- Access tokens and refresh tokens
- Token generation and validation
- User registration and login
- Protected endpoints
- Token refresh mechanism
- Blacklist for logout

Author: HLD Course
"""

import jwt
import bcrypt
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from functools import wraps
from dataclasses import dataclass, asdict


# ============================================================================
# Configuration
# ============================================================================

class Config:
    """JWT Configuration"""
    # Secret keys (In production, use environment variables!)
    JWT_SECRET_KEY = "your-super-secret-jwt-key-change-this-in-production"
    JWT_REFRESH_SECRET_KEY = "your-super-secret-refresh-key-change-this-in-production"

    # Token expiry times
    ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # Short-lived
    REFRESH_TOKEN_EXPIRES = timedelta(days=30)    # Long-lived

    # Algorithm
    ALGORITHM = "HS256"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class User:
    """User model"""
    id: str
    username: str
    email: str
    password_hash: str
    roles: list
    created_at: datetime

    def to_dict(self, include_password=False):
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if not include_password:
            del data['password_hash']
        return data


@dataclass
class TokenPair:
    """Access and Refresh token pair"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = int(Config.ACCESS_TOKEN_EXPIRES.total_seconds())


# ============================================================================
# In-Memory Storage (Use database in production!)
# ============================================================================

class Database:
    """Simulated database for demo purposes"""

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.blacklisted_tokens: set = set()

    def add_user(self, user: User):
        """Add user to database"""
        self.users[user.id] = user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def blacklist_token(self, jti: str):
        """Add token to blacklist"""
        self.blacklisted_tokens.add(jti)

    def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        return jti in self.blacklisted_tokens


# Global database instance
db = Database()


# ============================================================================
# Password Hashing
# ============================================================================

class PasswordHasher:
    """Handle password hashing and verification"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against hash

        Args:
            password: Plain text password
            password_hash: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )


# ============================================================================
# JWT Token Management
# ============================================================================

class JWTManager:
    """Manage JWT token creation and validation"""

    @staticmethod
    def create_access_token(user: User) -> str:
        """
        Create JWT access token

        Args:
            user: User object

        Returns:
            JWT access token
        """
        now = datetime.utcnow()
        expires = now + Config.ACCESS_TOKEN_EXPIRES

        payload = {
            # Registered claims (standard JWT claims)
            'sub': user.id,                    # Subject (user ID)
            'iat': int(now.timestamp()),       # Issued at
            'exp': int(expires.timestamp()),   # Expiration time
            'jti': str(uuid.uuid4()),          # JWT ID (unique identifier)

            # Custom claims (application-specific)
            'username': user.username,
            'email': user.email,
            'roles': user.roles,
            'token_type': 'access'
        }

        token = jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm=Config.ALGORITHM
        )

        return token

    @staticmethod
    def create_refresh_token(user: User) -> str:
        """
        Create JWT refresh token

        Args:
            user: User object

        Returns:
            JWT refresh token
        """
        now = datetime.utcnow()
        expires = now + Config.REFRESH_TOKEN_EXPIRES

        payload = {
            'sub': user.id,
            'iat': int(now.timestamp()),
            'exp': int(expires.timestamp()),
            'jti': str(uuid.uuid4()),
            'token_type': 'refresh'
        }

        token = jwt.encode(
            payload,
            Config.JWT_REFRESH_SECRET_KEY,
            algorithm=Config.ALGORITHM
        )

        return token

    @staticmethod
    def create_token_pair(user: User) -> TokenPair:
        """
        Create access and refresh token pair

        Args:
            user: User object

        Returns:
            TokenPair object
        """
        access_token = JWTManager.create_access_token(user)
        refresh_token = JWTManager.create_refresh_token(user)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token
        )

    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict]:
        """
        Verify and decode access token

        Args:
            token: JWT access token

        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=[Config.ALGORITHM]
            )

            # Check if token is blacklisted
            if db.is_token_blacklisted(payload.get('jti')):
                return None

            # Verify token type
            if payload.get('token_type') != 'access':
                return None

            return payload

        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {e}")
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[Dict]:
        """
        Verify and decode refresh token

        Args:
            token: JWT refresh token

        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                Config.JWT_REFRESH_SECRET_KEY,
                algorithms=[Config.ALGORITHM]
            )

            # Check if token is blacklisted
            if db.is_token_blacklisted(payload.get('jti')):
                return None

            # Verify token type
            if payload.get('token_type') != 'refresh':
                return None

            return payload

        except jwt.ExpiredSignatureError:
            print("Refresh token has expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid refresh token: {e}")
            return None

    @staticmethod
    def decode_token_without_verification(token: str) -> Optional[Dict]:
        """
        Decode token without verification (for inspection)

        Args:
            token: JWT token

        Returns:
            Decoded payload (unverified)
        """
        try:
            return jwt.decode(
                token,
                options={"verify_signature": False}
            )
        except Exception as e:
            print(f"Error decoding token: {e}")
            return None


# ============================================================================
# Authentication Service
# ============================================================================

class AuthService:
    """Handle authentication operations"""

    @staticmethod
    def register(username: str, email: str, password: str,
                 roles: list = None) -> Tuple[bool, str, Optional[User]]:
        """
        Register new user

        Args:
            username: Username
            email: Email address
            password: Plain text password
            roles: User roles

        Returns:
            (success, message, user)
        """
        # Validate inputs
        if len(username) < 3:
            return False, "Username must be at least 3 characters", None

        if len(password) < 8:
            return False, "Password must be at least 8 characters", None

        # Check if user already exists
        if db.get_user_by_username(username):
            return False, "Username already exists", None

        if db.get_user_by_email(email):
            return False, "Email already exists", None

        # Create user
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=PasswordHasher.hash_password(password),
            roles=roles or ['user'],
            created_at=datetime.utcnow()
        )

        db.add_user(user)

        return True, "User registered successfully", user

    @staticmethod
    def login(username: str, password: str) -> Tuple[bool, str, Optional[TokenPair]]:
        """
        Login user

        Args:
            username: Username
            password: Plain text password

        Returns:
            (success, message, token_pair)
        """
        # Find user
        user = db.get_user_by_username(username)
        if not user:
            return False, "Invalid username or password", None

        # Verify password
        if not PasswordHasher.verify_password(password, user.password_hash):
            return False, "Invalid username or password", None

        # Create tokens
        token_pair = JWTManager.create_token_pair(user)

        return True, "Login successful", token_pair

    @staticmethod
    def refresh_token(refresh_token: str) -> Tuple[bool, str, Optional[TokenPair]]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            (success, message, token_pair)
        """
        # Verify refresh token
        payload = JWTManager.verify_refresh_token(refresh_token)
        if not payload:
            return False, "Invalid or expired refresh token", None

        # Get user
        user = db.get_user_by_id(payload['sub'])
        if not user:
            return False, "User not found", None

        # Create new token pair
        token_pair = JWTManager.create_token_pair(user)

        return True, "Token refreshed successfully", token_pair

    @staticmethod
    def logout(access_token: str) -> Tuple[bool, str]:
        """
        Logout user by blacklisting token

        Args:
            access_token: Access token to blacklist

        Returns:
            (success, message)
        """
        payload = JWTManager.verify_access_token(access_token)
        if not payload:
            return False, "Invalid token"

        # Blacklist token
        db.blacklist_token(payload['jti'])

        return True, "Logged out successfully"


# ============================================================================
# Authentication Decorators
# ============================================================================

def require_auth(func):
    """
    Decorator to require authentication

    Usage:
        @require_auth
        def protected_endpoint(current_user):
            return f"Hello {current_user['username']}"
    """
    @wraps(func)
    def wrapper(token: str, *args, **kwargs):
        payload = JWTManager.verify_access_token(token)
        if not payload:
            raise PermissionError("Authentication required")

        # Pass user info to function
        return func(payload, *args, **kwargs)

    return wrapper


def require_roles(*required_roles):
    """
    Decorator to require specific roles

    Usage:
        @require_roles('admin', 'moderator')
        def admin_endpoint(current_user):
            return "Admin access granted"
    """
    def decorator(func):
        @wraps(func)
        def wrapper(token: str, *args, **kwargs):
            payload = JWTManager.verify_access_token(token)
            if not payload:
                raise PermissionError("Authentication required")

            user_roles = payload.get('roles', [])
            if not any(role in user_roles for role in required_roles):
                raise PermissionError(f"Requires one of roles: {required_roles}")

            return func(payload, *args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# Example API Endpoints
# ============================================================================

class API:
    """Simulated API endpoints"""

    @staticmethod
    def register_endpoint(username: str, email: str, password: str) -> Dict:
        """
        POST /api/auth/register
        """
        success, message, user = AuthService.register(username, email, password)

        if success:
            return {
                'success': True,
                'message': message,
                'user': user.to_dict()
            }
        else:
            return {
                'success': False,
                'message': message
            }

    @staticmethod
    def login_endpoint(username: str, password: str) -> Dict:
        """
        POST /api/auth/login
        """
        success, message, token_pair = AuthService.login(username, password)

        if success:
            return {
                'success': True,
                'message': message,
                'access_token': token_pair.access_token,
                'refresh_token': token_pair.refresh_token,
                'token_type': token_pair.token_type,
                'expires_in': token_pair.expires_in
            }
        else:
            return {
                'success': False,
                'message': message
            }

    @staticmethod
    def refresh_endpoint(refresh_token: str) -> Dict:
        """
        POST /api/auth/refresh
        """
        success, message, token_pair = AuthService.refresh_token(refresh_token)

        if success:
            return {
                'success': True,
                'message': message,
                'access_token': token_pair.access_token,
                'refresh_token': token_pair.refresh_token,
                'token_type': token_pair.token_type,
                'expires_in': token_pair.expires_in
            }
        else:
            return {
                'success': False,
                'message': message
            }

    @staticmethod
    @require_auth
    def profile_endpoint(current_user: Dict) -> Dict:
        """
        GET /api/profile
        (Protected endpoint)
        """
        user = db.get_user_by_id(current_user['sub'])

        return {
            'success': True,
            'user': user.to_dict()
        }

    @staticmethod
    @require_roles('admin')
    def admin_endpoint(current_user: Dict) -> Dict:
        """
        GET /api/admin
        (Protected endpoint - admin only)
        """
        return {
            'success': True,
            'message': f"Welcome admin {current_user['username']}",
            'users_count': len(db.users)
        }

    @staticmethod
    @require_auth
    def logout_endpoint(current_user: Dict, access_token: str) -> Dict:
        """
        POST /api/auth/logout
        """
        success, message = AuthService.logout(access_token)

        return {
            'success': success,
            'message': message
        }


# ============================================================================
# Demo
# ============================================================================

def demo_jwt_authentication():
    """Demonstrate JWT authentication system"""
    print("\n" + "=" * 70)
    print("JWT Authentication System Demo")
    print("=" * 70)

    # 1. Register users
    print("\n--- 1. User Registration ---")

    result = API.register_endpoint("john_doe", "john@example.com", "password123")
    print(f"Register john_doe: {result['message']}")

    result = API.register_endpoint("jane_admin", "jane@example.com", "admin123")
    print(f"Register jane_admin: {result['message']}")

    # Make jane an admin
    jane = db.get_user_by_username("jane_admin")
    jane.roles.append('admin')

    # 2. Login
    print("\n--- 2. User Login ---")

    login_result = API.login_endpoint("john_doe", "password123")
    if login_result['success']:
        print(f"✓ Login successful!")
        print(f"  Access Token: {login_result['access_token'][:50]}...")
        print(f"  Refresh Token: {login_result['refresh_token'][:50]}...")
        print(f"  Expires in: {login_result['expires_in']} seconds")

        john_access_token = login_result['access_token']
        john_refresh_token = login_result['refresh_token']
    else:
        print(f"✗ Login failed: {login_result['message']}")
        return

    # Login admin
    admin_result = API.login_endpoint("jane_admin", "admin123")
    jane_access_token = admin_result['access_token']

    # 3. Access protected endpoint
    print("\n--- 3. Access Protected Endpoint ---")

    try:
        profile = API.profile_endpoint(john_access_token)
        print(f"✓ Profile retrieved:")
        print(f"  Username: {profile['user']['username']}")
        print(f"  Email: {profile['user']['email']}")
        print(f"  Roles: {profile['user']['roles']}")
    except PermissionError as e:
        print(f"✗ Access denied: {e}")

    # 4. Decode token (inspect)
    print("\n--- 4. Inspect Access Token ---")

    payload = JWTManager.decode_token_without_verification(john_access_token)
    print(f"Token payload:")
    print(f"  User ID: {payload['sub']}")
    print(f"  Username: {payload['username']}")
    print(f"  Roles: {payload['roles']}")
    print(f"  Issued at: {datetime.fromtimestamp(payload['iat'])}")
    print(f"  Expires at: {datetime.fromtimestamp(payload['exp'])}")
    print(f"  Token ID (JTI): {payload['jti']}")

    # 5. Try admin endpoint with regular user (should fail)
    print("\n--- 5. Authorization Test (Regular User -> Admin Endpoint) ---")

    try:
        admin_data = API.admin_endpoint(john_access_token)
        print(f"✓ Admin access granted (shouldn't happen!)")
    except PermissionError as e:
        print(f"✗ Access denied (expected): {e}")

    # 6. Try admin endpoint with admin user (should succeed)
    print("\n--- 6. Authorization Test (Admin User -> Admin Endpoint) ---")

    try:
        admin_data = API.admin_endpoint(jane_access_token)
        print(f"✓ Admin access granted!")
        print(f"  Message: {admin_data['message']}")
        print(f"  Total users: {admin_data['users_count']}")
    except PermissionError as e:
        print(f"✗ Access denied: {e}")

    # 7. Refresh token
    print("\n--- 7. Token Refresh ---")

    refresh_result = API.refresh_endpoint(john_refresh_token)
    if refresh_result['success']:
        print(f"✓ Token refreshed!")
        print(f"  New Access Token: {refresh_result['access_token'][:50]}...")
        new_access_token = refresh_result['access_token']
    else:
        print(f"✗ Token refresh failed: {refresh_result['message']}")

    # 8. Logout
    print("\n--- 8. Logout (Blacklist Token) ---")

    logout_result = API.logout_endpoint(john_access_token, john_access_token)
    print(f"Logout: {logout_result['message']}")

    # 9. Try to use logged out token
    print("\n--- 9. Use Blacklisted Token ---")

    try:
        profile = API.profile_endpoint(john_access_token)
        print(f"✓ Profile retrieved (shouldn't happen!)")
    except PermissionError as e:
        print(f"✗ Access denied (expected): {e}")

    # 10. Use new token (should work)
    print("\n--- 10. Use New Token (After Logout) ---")

    try:
        profile = API.profile_endpoint(new_access_token)
        print(f"✓ Profile retrieved with new token!")
    except PermissionError as e:
        print(f"✗ Access denied: {e}")


def demo_token_expiry():
    """Demonstrate token expiry"""
    print("\n" + "=" * 70)
    print("Token Expiry Demo")
    print("=" * 70)

    # Create short-lived token for demo
    original_expiry = Config.ACCESS_TOKEN_EXPIRES
    Config.ACCESS_TOKEN_EXPIRES = timedelta(seconds=2)

    # Register and login
    AuthService.register("test_user", "test@example.com", "password123")
    success, message, token_pair = AuthService.login("test_user", "password123")

    print(f"\n✓ Created token with 2 second expiry")
    print(f"  Token: {token_pair.access_token[:50]}...")

    # Use token immediately
    print(f"\n⏱  Using token immediately...")
    payload = JWTManager.verify_access_token(token_pair.access_token)
    if payload:
        print(f"✓ Token valid")
    else:
        print(f"✗ Token invalid")

    # Wait for expiry
    print(f"\n⏱  Waiting 3 seconds for token to expire...")
    time.sleep(3)

    # Try to use expired token
    print(f"\n⏱  Using token after expiry...")
    payload = JWTManager.verify_access_token(token_pair.access_token)
    if payload:
        print(f"✓ Token valid (shouldn't happen!)")
    else:
        print(f"✗ Token expired (expected)")

    # Restore original expiry
    Config.ACCESS_TOKEN_EXPIRES = original_expiry


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("JWT AUTHENTICATION - COMPREHENSIVE DEMONSTRATION")
    print("=" * 70)

    demo_jwt_authentication()
    demo_token_expiry()

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)

    print("\n📝 Key Takeaways:")
    print("1. Access tokens are short-lived (15 minutes)")
    print("2. Refresh tokens are long-lived (30 days)")
    print("3. Tokens are stateless and self-contained")
    print("4. Use blacklist for logout functionality")
    print("5. Always validate tokens on protected endpoints")
    print("6. Store tokens securely (httpOnly cookies)")
    print("7. Use HTTPS in production")
    print("8. Implement role-based access control (RBAC)")
    print("9. Rotate refresh tokens on use")
    print("10. Never store sensitive data in JWT payload")
    print("=" * 70)
