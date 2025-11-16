"""
Proxy Pattern - Provide a surrogate or placeholder for another object to control access to it.

This module demonstrates various proxy implementations:
1. Virtual proxy - lazy initialization of expensive objects
2. Protection proxy - controls access to objects
3. Remote proxy - represents object on remote system
4. Smart reference - reference counting, garbage collection
5. Caching proxy - caches expensive operation results
6. Logging proxy - logs access to objects

Key Learning Points:
- Proxy provides same interface as real object
- Proxy controls access to real object
- Proxy can defer expensive operations
- Proxy can add behavior (logging, caching)
- Proxy and real object must have same interface
- Useful for lazy loading, access control, logging
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
import time
from datetime import datetime


# ============================================================================
# 1. VIRTUAL PROXY - LAZY INITIALIZATION
# ============================================================================

class Image(ABC):
    """Abstract interface for images."""

    @abstractmethod
    def display(self) -> None:
        """Display the image."""
        pass


class RealImage(Image):
    """Real image object - expensive to create."""

    def __init__(self, filename: str):
        self.filename = filename
        self._load_image()

    def _load_image(self) -> None:
        """Simulate expensive image loading."""
        print(f"Loading image: {self.filename} (this is expensive!)")
        time.sleep(0.5)  # Simulate slow disk I/O
        print(f"Image {self.filename} loaded into memory")

    def display(self) -> None:
        print(f"Displaying image: {self.filename}")


class ImageProxy(Image):
    """Virtual proxy for images - defers loading until display."""

    def __init__(self, filename: str):
        self.filename = filename
        self._image: Optional[RealImage] = None

    def display(self) -> None:
        """Load image on first access."""
        if self._image is None:
            print("First access - loading image now...")
            self._image = RealImage(self.filename)
        self._image.display()


# ============================================================================
# 2. PROTECTION PROXY - ACCESS CONTROL
# ============================================================================

class BankAccount:
    """Abstract bank account interface."""

    def withdraw(self, amount: float) -> bool:
        pass

    def deposit(self, amount: float) -> bool:
        pass

    def get_balance(self) -> float:
        pass


class RealBankAccount(BankAccount):
    """Real bank account."""

    def __init__(self, account_number: str, balance: float = 0):
        self.account_number = account_number
        self.balance = balance

    def withdraw(self, amount: float) -> bool:
        if amount <= self.balance:
            self.balance -= amount
            print(f"Withdrew ${amount:.2f}. New balance: ${self.balance:.2f}")
            return True
        print("Insufficient funds")
        return False

    def deposit(self, amount: float) -> bool:
        self.balance += amount
        print(f"Deposited ${amount:.2f}. New balance: ${self.balance:.2f}")
        return True

    def get_balance(self) -> float:
        return self.balance


class BankAccountProxy(BankAccount):
    """Protection proxy for bank account - controls access."""

    def __init__(self, account: RealBankAccount, user_role: str = "user"):
        self._account = account
        self.user_role = user_role

    def withdraw(self, amount: float) -> bool:
        """Only admins can withdraw, users can withdraw up to $1000."""
        if self.user_role == "admin":
            print(f"Admin withdrawing ${amount:.2f}")
            return self._account.withdraw(amount)
        elif self.user_role == "user":
            if amount <= 1000:
                print(f"User withdrawing ${amount:.2f}")
                return self._account.withdraw(amount)
            else:
                print(f"User cannot withdraw more than $1000 (requested ${amount:.2f})")
                return False
        else:
            print("Guest cannot withdraw")
            return False

    def deposit(self, amount: float) -> bool:
        """Anyone can deposit."""
        print(f"{self.user_role.capitalize()} depositing ${amount:.2f}")
        return self._account.deposit(amount)

    def get_balance(self) -> float:
        """Everyone can check balance."""
        return self._account.get_balance()


# ============================================================================
# 3. REMOTE PROXY - RPC SIMULATION
# ============================================================================

class DataService:
    """Abstract data service interface."""

    def get_user(self, user_id: int) -> Dict[str, Any]:
        pass

    def create_user(self, name: str, email: str) -> bool:
        pass


class RemoteDataService(DataService):
    """Simulates remote data service (on different server)."""

    def get_user(self, user_id: int) -> Dict[str, Any]:
        print(f"[REMOTE SERVER] Fetching user {user_id} from database")
        time.sleep(0.3)  # Simulate network latency
        return {"id": user_id, "name": "John Doe", "email": "john@example.com"}

    def create_user(self, name: str, email: str) -> bool:
        print(f"[REMOTE SERVER] Creating user: {name} ({email})")
        time.sleep(0.2)  # Simulate network latency
        return True


class DataServiceProxy(DataService):
    """Remote proxy for data service - handles RPC communication."""

    def __init__(self, remote_service: RemoteDataService):
        self._service = remote_service
        self.call_count = 0

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user via remote service."""
        self.call_count += 1
        print(f"[PROXY] RPC Call #{self.call_count}: get_user({user_id})")
        print("[PROXY] Sending request to remote server...")
        result = self._service.get_user(user_id)
        print("[PROXY] Received response from server")
        return result

    def create_user(self, name: str, email: str) -> bool:
        """Create user via remote service."""
        self.call_count += 1
        print(f"[PROXY] RPC Call #{self.call_count}: create_user({name}, {email})")
        print("[PROXY] Sending request to remote server...")
        result = self._service.create_user(name, email)
        print("[PROXY] Operation completed on server")
        return result


# ============================================================================
# 4. SMART REFERENCE - REFERENCE COUNTING
# ============================================================================

class Resource:
    """A resource that needs to be managed."""

    def __init__(self, name: str):
        self.name = name
        self.data = "Important data for " + name

    def use(self) -> None:
        print(f"Using resource: {self.name}")

    def __del__(self):
        print(f"Resource {self.name} destroyed")


class SmartPointer:
    """Smart reference with reference counting."""

    # Class variable to track all instances
    _instances: Dict[int, int] = {}  # id -> reference count

    def __init__(self, resource: Optional[Resource] = None):
        self._resource = resource
        if resource:
            res_id = id(resource)
            if res_id not in SmartPointer._instances:
                SmartPointer._instances[res_id] = 0
            SmartPointer._instances[res_id] += 1
            print(f"Smart reference created. Ref count: {SmartPointer._instances[res_id]}")

    def get(self) -> Optional[Resource]:
        """Get the referenced resource."""
        return self._resource

    def use(self) -> None:
        """Use the referenced resource."""
        if self._resource:
            self._resource.use()

    def __del__(self):
        if self._resource:
            res_id = id(self._resource)
            if res_id in SmartPointer._instances:
                SmartPointer._instances[res_id] -= 1
                print(f"Smart reference destroyed. Ref count: {SmartPointer._instances[res_id]}")
                if SmartPointer._instances[res_id] == 0:
                    del SmartPointer._instances[res_id]


# ============================================================================
# 5. CACHING PROXY
# ============================================================================

class Calculator:
    """Abstract calculator interface."""

    def add(self, a: int, b: int) -> int:
        pass

    def multiply(self, a: int, b: int) -> int:
        pass

    def fibonacci(self, n: int) -> int:
        pass


class RealCalculator(Calculator):
    """Real calculator with expensive operations."""

    def __init__(self):
        self.operation_count = 0

    def add(self, a: int, b: int) -> int:
        self.operation_count += 1
        print(f"[REAL] Computing {a} + {b}")
        return a + b

    def multiply(self, a: int, b: int) -> int:
        self.operation_count += 1
        print(f"[REAL] Computing {a} * {b}")
        return a * b

    def fibonacci(self, n: int) -> int:
        self.operation_count += 1
        print(f"[REAL] Computing fibonacci({n})")
        if n <= 1:
            return n
        return self.fibonacci(n-1) + self.fibonacci(n-2)


class CachingCalculator(Calculator):
    """Caching proxy for calculator."""

    def __init__(self, calculator: RealCalculator):
        self._calculator = calculator
        self._cache: Dict[str, int] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def _cache_key(self, operation: str, *args) -> str:
        """Generate cache key from operation and arguments."""
        return f"{operation}({','.join(map(str, args))})"

    def add(self, a: int, b: int) -> int:
        key = self._cache_key("add", a, b)
        if key in self._cache:
            self.cache_hits += 1
            print(f"[CACHE] HIT: {key}")
            return self._cache[key]

        self.cache_misses += 1
        result = self._calculator.add(a, b)
        self._cache[key] = result
        print(f"[CACHE] MISS: {key} = {result}")
        return result

    def multiply(self, a: int, b: int) -> int:
        key = self._cache_key("multiply", a, b)
        if key in self._cache:
            self.cache_hits += 1
            print(f"[CACHE] HIT: {key}")
            return self._cache[key]

        self.cache_misses += 1
        result = self._calculator.multiply(a, b)
        self._cache[key] = result
        print(f"[CACHE] MISS: {key} = {result}")
        return result

    def fibonacci(self, n: int) -> int:
        key = self._cache_key("fib", n)
        if key in self._cache:
            self.cache_hits += 1
            print(f"[CACHE] HIT: {key}")
            return self._cache[key]

        self.cache_misses += 1
        result = self._calculator.fibonacci(n)
        self._cache[key] = result
        print(f"[CACHE] MISS: {key} = {result}")
        return result


# ============================================================================
# 6. LOGGING PROXY
# ============================================================================

class DataStore:
    """Abstract data store interface."""

    def read(self, key: str) -> Optional[str]:
        pass

    def write(self, key: str, value: str) -> bool:
        pass

    def delete(self, key: str) -> bool:
        pass


class RealDataStore(DataStore):
    """Real data store implementation."""

    def __init__(self):
        self._data: Dict[str, str] = {}

    def read(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def write(self, key: str, value: str) -> bool:
        self._data[key] = value
        return True

    def delete(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            return True
        return False


class LoggingDataStore(DataStore):
    """Logging proxy for data store."""

    def __init__(self, store: RealDataStore):
        self._store = store
        self._access_log: List[str] = []

    def read(self, key: str) -> Optional[str]:
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] READ {key}"
        self._access_log.append(log_entry)
        print(log_entry)
        return self._store.read(key)

    def write(self, key: str, value: str) -> bool:
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] WRITE {key} = {value}"
        self._access_log.append(log_entry)
        print(log_entry)
        return self._store.write(key, value)

    def delete(self, key: str) -> bool:
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] DELETE {key}"
        self._access_log.append(log_entry)
        print(log_entry)
        return self._store.delete(key)

    def get_log(self) -> List[str]:
        """Get access log."""
        return self._access_log.copy()


# ============================================================================
# 7. DEMONSTRATION
# ============================================================================

def demo_virtual_proxy():
    """Demonstrate virtual proxy."""
    print("\n" + "="*60)
    print("PROXY PATTERN - VIRTUAL PROXY (LAZY LOADING)")
    print("="*60)

    print("\nCreating proxy (no loading yet):")
    proxy = ImageProxy("photo.jpg")

    print("\nFirst display (triggers loading):")
    proxy.display()

    print("\nSecond display (uses already loaded image):")
    proxy.display()


def demo_protection_proxy():
    """Demonstrate protection proxy."""
    print("\n" + "="*60)
    print("PROXY PATTERN - PROTECTION PROXY (ACCESS CONTROL)")
    print("="*60)

    account = RealBankAccount("12345", 5000)

    print("\nUser accessing account:")
    user_proxy = BankAccountProxy(account, "user")
    user_proxy.deposit(1000)
    user_proxy.withdraw(500)
    user_proxy.withdraw(1500)  # Should fail - exceeds limit

    print("\nAdmin accessing account:")
    admin_proxy = BankAccountProxy(account, "admin")
    admin_proxy.withdraw(2000)  # Should succeed

    print("\nGuest accessing account:")
    guest_proxy = BankAccountProxy(account, "guest")
    guest_proxy.deposit(100)  # Should succeed
    guest_proxy.withdraw(100)  # Should fail


def demo_remote_proxy():
    """Demonstrate remote proxy."""
    print("\n" + "="*60)
    print("PROXY PATTERN - REMOTE PROXY (RPC)")
    print("="*60)

    remote_service = RemoteDataService()
    proxy = DataServiceProxy(remote_service)

    print("\nFetching user via proxy:")
    user = proxy.get_user(123)
    print(f"Result: {user}\n")

    print("Creating user via proxy:")
    proxy.create_user("Jane", "jane@example.com")


def demo_smart_reference():
    """Demonstrate smart reference."""
    print("\n" + "="*60)
    print("PROXY PATTERN - SMART REFERENCE (REFERENCE COUNTING)")
    print("="*60)

    print("\nCreating resource:")
    resource = Resource("Database Connection")

    print("\nCreating smart pointers:")
    ptr1 = SmartPointer(resource)
    ptr2 = SmartPointer(resource)
    ptr3 = SmartPointer(resource)

    print("\nUsing via smart pointers:")
    ptr1.use()

    print("\nDeleting smart pointers:")
    del ptr1
    del ptr2
    del ptr3


def demo_caching_proxy():
    """Demonstrate caching proxy."""
    print("\n" + "="*60)
    print("PROXY PATTERN - CACHING PROXY")
    print("="*60)

    calculator = RealCalculator()
    cached = CachingCalculator(calculator)

    print("\nCaching arithmetic operations:")
    print(f"2 + 3 = {cached.add(2, 3)}")
    print(f"2 + 3 = {cached.add(2, 3)} (should be cached)")
    print(f"4 * 5 = {cached.multiply(4, 5)}")
    print(f"4 * 5 = {cached.multiply(4, 5)} (should be cached)")

    print(f"\nCache hits: {cached.cache_hits}, Cache misses: {cached.cache_misses}")


def demo_logging_proxy():
    """Demonstrate logging proxy."""
    print("\n" + "="*60)
    print("PROXY PATTERN - LOGGING PROXY")
    print("="*60)

    store = RealDataStore()
    logged_store = LoggingDataStore(store)

    print("\nOperations on data store:")
    logged_store.write("username", "john_doe")
    logged_store.write("email", "john@example.com")
    logged_store.read("username")
    logged_store.delete("email")

    print("\nAccess log:")
    for log_entry in logged_store.get_log():
        print(f"  {log_entry}")


def demo_proxy_pattern_benefits():
    """Demonstrate proxy pattern benefits."""
    print("\n" + "="*60)
    print("PROXY PATTERN - BENEFITS")
    print("="*60)

    print("""
KEY BENEFITS:

1. LAZY INITIALIZATION
   - Defer expensive operations until needed
   - Improve startup time
   - Load on demand

2. ACCESS CONTROL
   - Restrict who can access objects
   - Implement role-based access
   - Add authentication/authorization

3. LOGGING & MONITORING
   - Track access to objects
   - Monitor usage patterns
   - Create audit trails

4. CACHING
   - Cache expensive operation results
   - Reduce computation overhead
   - Improve performance

5. REMOTE PROXY
   - Access remote objects as local
   - Hide network communication
   - RPC calls transparently

6. REFERENCE COUNTING
   - Automatic resource management
   - Prevent memory leaks
   - Smart pointers behavior

7. TRANSPARENCY
   - Client code sees same interface
   - Works like real object
   - Can switch between proxy and real object

TYPES OF PROXIES:
- Virtual: Defer initialization
- Protection: Control access
- Remote: RPC calls
- Smart Reference: Resource management
- Caching: Memoization
- Logging: Audit trails
- Validation: Check before operations
    """)


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

"""
KEY TAKEAWAYS - PROXY PATTERN:

1. WHEN TO USE:
   - Need to control access to object
   - Want lazy initialization
   - Need to add logging/monitoring
   - Remote object access needed
   - Need caching of expensive operations

2. PROXY vs DECORATOR:
   - Proxy: Controls access to original object
   - Decorator: Adds behavior to object
   - Proxy focuses on control, Decorator on enhancement

3. PROXY vs FACADE:
   - Proxy: Represents single object
   - Facade: Simplifies complex subsystem
   - Proxy maintains interface, Facade simplifies it

4. SAME INTERFACE
   - Proxy must implement same interface as real object
   - Client shouldn't need to know about proxy
   - Transparent replacement

5. WHEN NOT TO USE:
   - Simpler alternatives available
   - Overhead not justified
   - Interface changes frequently
   - Too many proxy types

6. REAL WORLD EXAMPLES:
   - Lazy-loading in ORM frameworks
   - Authentication/authorization systems
   - Caching layers
   - Logging middleware
   - RPC stubs for remote calls
   - Virtual proxies for expensive resources
   - Smart pointers (C++)
   - Copy-on-write (COW) optimization

7. PERFORMANCE CONSIDERATIONS:
   - Proxy adds small overhead
   - Benefit should outweigh overhead
   - Caching proxy can improve performance
   - Lazy loading proxy improves startup

8. THREAD SAFETY:
   - Proxy should be thread-safe
   - Control access to shared resources
   - Protect shared state
"""


if __name__ == "__main__":
    demo_virtual_proxy()
    demo_protection_proxy()
    demo_remote_proxy()
    demo_smart_reference()
    demo_caching_proxy()
    demo_logging_proxy()
    demo_proxy_pattern_benefits()

    print("\n" + "="*60)
    print("All Proxy Pattern examples completed!")
    print("="*60)
