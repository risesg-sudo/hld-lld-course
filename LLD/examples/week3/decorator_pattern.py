"""
Decorator Pattern - Attach additional responsibilities to an object dynamically.

This module demonstrates various decorator implementations:
1. Coffee shop - adding toppings to coffee
2. Text formatting - combining text decorators
3. Caching layer - adding cache around expensive operations
4. Security decorators - adding authentication/authorization
5. Logging decorators - adding instrumentation
6. Stream decoration - decorating streams with filters

Key Learning Points:
- Decorator wraps object to add behavior dynamically
- More flexible than subclassing for adding behavior
- Can be combined in any order
- Order of decorators can affect behavior
- Each decorator has single responsibility
- Implements same interface as wrapped object
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List
import time
import functools
from datetime import datetime


# ============================================================================
# 1. COFFEE SHOP DECORATOR EXAMPLE
# ============================================================================

class Beverage(ABC):
    """Abstract beverage that can be decorated."""

    @abstractmethod
    def get_description(self) -> str:
        """Get beverage description."""
        pass

    @abstractmethod
    def get_cost(self) -> float:
        """Get beverage cost."""
        pass


class SimpleCoffee(Beverage):
    """Simple coffee without any additions."""

    def get_description(self) -> str:
        return "Simple Coffee"

    def get_cost(self) -> float:
        return 2.0


class Tea(Beverage):
    """Simple tea."""

    def get_description(self) -> str:
        return "Tea"

    def get_cost(self) -> float:
        return 1.5


class BeverageDecorator(Beverage):
    """Base class for beverage decorators."""

    def __init__(self, beverage: Beverage):
        self._beverage = beverage

    @abstractmethod
    def get_description(self) -> str:
        pass

    def get_cost(self) -> float:
        return self._beverage.get_cost()


class MilkDecorator(BeverageDecorator):
    """Decorator that adds milk."""

    def get_description(self) -> str:
        return f"{self._beverage.get_description()}, Milk"

    def get_cost(self) -> float:
        return self._beverage.get_cost() + 0.5


class SugarDecorator(BeverageDecorator):
    """Decorator that adds sugar."""

    def get_description(self) -> str:
        return f"{self._beverage.get_description()}, Sugar"

    def get_cost(self) -> float:
        return self._beverage.get_cost() + 0.25


class WhippedCreamDecorator(BeverageDecorator):
    """Decorator that adds whipped cream."""

    def get_description(self) -> str:
        return f"{self._beverage.get_description()}, Whipped Cream"

    def get_cost(self) -> float:
        return self._beverage.get_cost() + 0.75


class CaramelDecorator(BeverageDecorator):
    """Decorator that adds caramel."""

    def get_description(self) -> str:
        return f"{self._beverage.get_description()}, Caramel"

    def get_cost(self) -> float:
        return self._beverage.get_cost() + 0.6


class ChocolateDecorator(BeverageDecorator):
    """Decorator that adds chocolate."""

    def get_description(self) -> str:
        return f"{self._beverage.get_description()}, Chocolate"

    def get_cost(self) -> float:
        return self._beverage.get_cost() + 0.5


# ============================================================================
# 2. TEXT FORMATTING DECORATOR EXAMPLE
# ============================================================================

class TextComponent(ABC):
    """Abstract text component that can be decorated."""

    @abstractmethod
    def render(self) -> str:
        """Render the text."""
        pass


class SimpleText(TextComponent):
    """Simple unformatted text."""

    def __init__(self, text: str):
        self.text = text

    def render(self) -> str:
        return self.text


class TextDecorator(TextComponent):
    """Base class for text decorators."""

    def __init__(self, text_component: TextComponent):
        self._component = text_component

    @abstractmethod
    def render(self) -> str:
        pass


class BoldDecorator(TextDecorator):
    """Decorator that makes text bold."""

    def render(self) -> str:
        return f"**{self._component.render()}**"


class ItalicDecorator(TextDecorator):
    """Decorator that makes text italic."""

    def render(self) -> str:
        return f"_{self._component.render()}_"


class UnderlineDecorator(TextDecorator):
    """Decorator that underlines text."""

    def render(self) -> str:
        return f"<u>{self._component.render()}</u>"


class HighlightDecorator(TextDecorator):
    """Decorator that highlights text."""

    def render(self) -> str:
        return f"[HIGHLIGHT]{self._component.render()}[/HIGHLIGHT]"


class ColorDecorator(TextDecorator):
    """Decorator that adds color to text."""

    def __init__(self, text_component: TextComponent, color: str = "red"):
        super().__init__(text_component)
        self.color = color

    def render(self) -> str:
        return f"[{self.color.upper()}]{self._component.render()}[/{self.color.upper()}]"


# ============================================================================
# 3. CACHING DECORATOR EXAMPLE
# ============================================================================

class DataRepository:
    """Repository for accessing data (expensive operation)."""

    def __init__(self):
        self.access_count = 0

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user data (simulated expensive operation)."""
        self.access_count += 1
        print(f"  Fetching user {user_id} from database... (access #{self.access_count})")
        time.sleep(0.5)  # Simulate slow database access
        return {"id": user_id, "name": f"User{user_id}", "email": f"user{user_id}@example.com"}


class CachedRepository:
    """Decorator that adds caching to repository."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._cache: Dict[int, Dict] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user with caching."""
        if user_id in self._cache:
            self.cache_hits += 1
            print(f"  Cache HIT for user {user_id}")
            return self._cache[user_id]

        self.cache_misses += 1
        print(f"  Cache MISS for user {user_id}")
        user = self._repository.get_user(user_id)
        self._cache[user_id] = user
        return user

    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()


# ============================================================================
# 4. SECURITY DECORATOR EXAMPLE
# ============================================================================

class SecureOperation(ABC):
    """Abstract secure operation."""

    @abstractmethod
    def execute(self, data: str) -> str:
        pass


class DataProcessor(SecureOperation):
    """Simple data processor."""

    def execute(self, data: str) -> str:
        return f"Processing: {data}"


class SecurityDecorator(SecureOperation):
    """Base class for security decorators."""

    def __init__(self, operation: SecureOperation):
        self._operation = operation

    @abstractmethod
    def execute(self, data: str) -> str:
        pass


class AuthenticationDecorator(SecurityDecorator):
    """Decorator that adds authentication."""

    def __init__(self, operation: SecureOperation, user: str = "admin"):
        super().__init__(operation)
        self.user = user

    def execute(self, data: str) -> str:
        print(f"  Authenticating user: {self.user}")
        if not self.user:
            raise ValueError("Authentication failed")
        return self._operation.execute(data)


class AuthorizationDecorator(SecurityDecorator):
    """Decorator that adds authorization."""

    def __init__(self, operation: SecureOperation, role: str = "admin"):
        super().__init__(operation)
        self.role = role
        self.allowed_roles = ["admin", "manager"]

    def execute(self, data: str) -> str:
        print(f"  Checking authorization for role: {self.role}")
        if self.role not in self.allowed_roles:
            raise ValueError(f"Unauthorized: {self.role} not in {self.allowed_roles}")
        return self._operation.execute(data)


class EncryptionDecorator(SecurityDecorator):
    """Decorator that adds encryption."""

    def execute(self, data: str) -> str:
        encrypted = "ENCRYPTED[" + data.upper() + "]"
        print(f"  Encrypting data")
        result = self._operation.execute(encrypted)
        decrypted = result.replace("ENCRYPTED[", "").replace("]", "")
        print(f"  Decrypting result")
        return decrypted


class LoggingDecorator(SecurityDecorator):
    """Decorator that adds logging."""

    def execute(self, data: str) -> str:
        timestamp = datetime.now().isoformat()
        print(f"  [LOG {timestamp}] Executing operation")
        result = self._operation.execute(data)
        print(f"  [LOG {timestamp}] Operation completed")
        return result


# ============================================================================
# 5. STREAM DECORATOR EXAMPLE
# ============================================================================

class DataStream(ABC):
    """Abstract data stream."""

    @abstractmethod
    def read(self) -> str:
        pass


class FileStream(DataStream):
    """Simple file stream."""

    def __init__(self, filename: str):
        self.filename = filename

    def read(self) -> str:
        return f"Content of {self.filename}"


class StreamDecorator(DataStream):
    """Base class for stream decorators."""

    def __init__(self, stream: DataStream):
        self._stream = stream

    @abstractmethod
    def read(self) -> str:
        pass


class CompressedStream(StreamDecorator):
    """Decorator that adds compression."""

    def read(self) -> str:
        data = self._stream.read()
        compressed = f"COMPRESSED({len(data)} bytes -> {len(data)//2} bytes)"
        return compressed


class BufferedStream(StreamDecorator):
    """Decorator that adds buffering."""

    def read(self) -> str:
        data = self._stream.read()
        return f"BUFFERED[{data}]"


class EncryptedStream(StreamDecorator):
    """Decorator that encrypts stream."""

    def read(self) -> str:
        data = self._stream.read()
        encrypted = "".join(chr(ord(c) + 1) for c in data)
        return f"ENCRYPTED<{encrypted[:20]}...>"


class MonitoredStream(StreamDecorator):
    """Decorator that monitors stream access."""

    def __init__(self, stream: DataStream):
        super().__init__(stream)
        self.access_count = 0

    def read(self) -> str:
        self.access_count += 1
        print(f"  Stream access #{self.access_count}")
        return self._stream.read()


# ============================================================================
# 6. FUNCTION DECORATOR EXAMPLE (PYTHON-SPECIFIC)
# ============================================================================

def timing_decorator(func: Callable) -> Callable:
    """Decorator that measures execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  {func.__name__} took {elapsed:.4f} seconds")
        return result
    return wrapper


def caching_decorator(func: Callable) -> Callable:
    """Decorator that caches function results."""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args in cache:
            print(f"  Cache hit for {func.__name__}{args}")
            return cache[args]
        print(f"  Cache miss for {func.__name__}{args}")
        result = func(*args)
        cache[args] = result
        return result

    return wrapper


def logging_decorator(func: Callable) -> Callable:
    """Decorator that logs function calls."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"  {func.__name__} returned {result}")
        return result
    return wrapper


@caching_decorator
@timing_decorator
def expensive_calculation(n: int) -> int:
    """Expensive calculation (decorated with caching and timing)."""
    time.sleep(0.2)
    return n * n


# ============================================================================
# 7. DEMONSTRATION
# ============================================================================

def demo_coffee_decorator():
    """Demonstrate coffee shop decorator."""
    print("\n" + "="*60)
    print("DECORATOR PATTERN - COFFEE SHOP EXAMPLE")
    print("="*60)

    # Simple coffee
    print("\nSimple Coffee:")
    coffee = SimpleCoffee()
    print(f"  Description: {coffee.get_description()}")
    print(f"  Cost: ${coffee.get_cost():.2f}")

    # Coffee with milk
    print("\nCoffee with Milk:")
    coffee_with_milk = MilkDecorator(coffee)
    print(f"  Description: {coffee_with_milk.get_description()}")
    print(f"  Cost: ${coffee_with_milk.get_cost():.2f}")

    # Coffee with milk, sugar, and whipped cream
    print("\nCoffee with Milk, Sugar, and Whipped Cream:")
    fancy_coffee = WhippedCreamDecorator(
        SugarDecorator(
            MilkDecorator(SimpleCoffee())
        )
    )
    print(f"  Description: {fancy_coffee.get_description()}")
    print(f"  Cost: ${fancy_coffee.get_cost():.2f}")

    # Different combinations
    print("\nDifferent Combinations:")
    combinations = [
        (ChocolateDecorator(SimpleCoffee()), "Chocolate Coffee"),
        (CaramelDecorator(MilkDecorator(SimpleCoffee())), "Caramel Latte"),
        (WhippedCreamDecorator(ChocolateDecorator(MilkDecorator(SimpleCoffee()))), "Mocha with Cream"),
    ]

    for beverage, name in combinations:
        print(f"\n  {name}:")
        print(f"    Cost: ${beverage.get_cost():.2f}")
        print(f"    Description: {beverage.get_description()}")


def demo_text_formatting_decorator():
    """Demonstrate text formatting decorator."""
    print("\n" + "="*60)
    print("DECORATOR PATTERN - TEXT FORMATTING EXAMPLE")
    print("="*60)

    text = SimpleText("Hello World")

    print(f"\nPlain text: {text.render()}")

    bold_text = BoldDecorator(text)
    print(f"Bold text: {bold_text.render()}")

    italic_bold_text = ItalicDecorator(BoldDecorator(text))
    print(f"Italic + Bold: {italic_bold_text.render()}")

    fancy_text = UnderlineDecorator(
        ItalicDecorator(
            BoldDecorator(
                ColorDecorator(text, "red")
            )
        )
    )
    print(f"Fancy (Bold+Italic+Underline+Color): {fancy_text.render()}")

    # Test highlight
    highlighted = HighlightDecorator(SimpleText("Important"))
    print(f"Highlighted: {highlighted.render()}")


def demo_caching_decorator():
    """Demonstrate caching decorator."""
    print("\n" + "="*60)
    print("DECORATOR PATTERN - CACHING DECORATOR EXAMPLE")
    print("="*60)

    repository = DataRepository()

    print("\nWithout caching:")
    for i in range(1, 4):
        repository.get_user(i)

    print(f"Total database accesses: {repository.access_count}")

    print("\nWith caching:")
    cached = CachedRepository(DataRepository())
    for i in range(1, 4):
        cached.get_user(i)
    print("Accessing same users again:")
    for i in range(1, 4):
        cached.get_user(i)

    print(f"\nCache hits: {cached.cache_hits}, Cache misses: {cached.cache_misses}")


def demo_security_decorators():
    """Demonstrate security decorators."""
    print("\n" + "="*60)
    print("DECORATOR PATTERN - SECURITY DECORATORS")
    print("="*60)

    processor = DataProcessor()

    print("\nBasic processing:")
    result = processor.execute("sensitive_data")
    print(f"  Result: {result}")

    print("\nWith authentication:")
    auth_processor = AuthenticationDecorator(processor, "user")
    result = auth_processor.execute("sensitive_data")
    print(f"  Result: {result}")

    print("\nWith authentication + authorization:")
    secure_processor = AuthorizationDecorator(
        AuthenticationDecorator(processor, "admin"),
        "admin"
    )
    result = secure_processor.execute("sensitive_data")
    print(f"  Result: {result}")

    print("\nWith authentication + authorization + encryption + logging:")
    fully_secure = LoggingDecorator(
        EncryptionDecorator(
            AuthorizationDecorator(
                AuthenticationDecorator(processor, "admin"),
                "admin"
            )
        )
    )
    result = fully_secure.execute("sensitive_data")
    print(f"  Result: {result}")


def demo_stream_decorators():
    """Demonstrate stream decorators."""
    print("\n" + "="*60)
    print("DECORATOR PATTERN - STREAM DECORATORS")
    print("="*60)

    stream = FileStream("data.txt")

    print("\nBasic stream:")
    print(f"  {stream.read()}")

    print("\nBuffered stream:")
    buffered = BufferedStream(stream)
    print(f"  {buffered.read()}")

    print("\nCompressed stream:")
    compressed = CompressedStream(stream)
    print(f"  {compressed.read()}")

    print("\nMultiple decorators:")
    complex_stream = CompressedStream(
        BufferedStream(
            EncryptedStream(
                MonitoredStream(stream)
            )
        )
    )
    print(f"  {complex_stream.read()}")
    print(f"  Monitor access count: {((MonitoredStream(stream)).access_count)}")


def demo_function_decorators():
    """Demonstrate function decorators."""
    print("\n" + "="*60)
    print("DECORATOR PATTERN - FUNCTION DECORATORS")
    print("="*60)

    print("\nCaching and timing decorators:")
    result1 = expensive_calculation(5)
    print(f"  Result: {result1}")

    print("\nSecond call (should be cached):")
    result2 = expensive_calculation(5)
    print(f"  Result: {result2}")

    print("\nDifferent argument:")
    result3 = expensive_calculation(10)
    print(f"  Result: {result3}")


def demo_decorator_benefits():
    """Demonstrate decorator pattern benefits."""
    print("\n" + "="*60)
    print("DECORATOR PATTERN - BENEFITS")
    print("="*60)

    print("""
KEY BENEFITS:

1. AVOID SUBCLASS EXPLOSION
   - Instead of CoffeeMilk, CoffeeMilkSugar, etc.
   - Use composition: MilkDecorator(SugarDecorator(Coffee))

2. FLEXIBLE COMPOSITION
   - Combine behaviors in any order
   - Mix and match decorators
   - Add behavior dynamically at runtime

3. SINGLE RESPONSIBILITY
   - Each decorator handles one aspect
   - Easy to test and maintain
   - Changes to one decorator don't affect others

4. OPEN/CLOSED PRINCIPLE
   - Open for extension (new decorators)
   - Closed for modification (original class unchanged)

5. TRANSPARENT
   - Client sees same interface
   - Works with original object and decorators the same way

6. RUNTIME CUSTOMIZATION
   - Choose decorators at runtime
   - Build behavior combinations dynamically
   - No recompilation needed

7. DECORATOR STACKING
   - Stack multiple decorators
   - Each layer adds functionality
   - Order can matter (placement affects behavior)

CAUTION:
- Order of decorators can affect results
- Each decorator adds performance overhead
- Can become hard to trace with many decorators
- Not suitable for simple problems
    """)


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

"""
KEY TAKEAWAYS - DECORATOR PATTERN:

1. WHEN TO USE:
   - Need to add behavior without subclassing
   - Avoid subclass explosion with many combinations
   - Add/remove features dynamically at runtime
   - Cross-cutting concerns (logging, caching, security)

2. DECORATOR vs INHERITANCE:
   - Decorator: Composition-based, flexible, runtime configuration
   - Inheritance: Fixed at compile time, simple for few variations
   - Choose Decorator when combinations of features needed

3. DECORATOR vs ADAPTER:
   - Decorator: Adds behavior (enhancement)
   - Adapter: Converts interface (compatibility)
   - Decorator doesn't change interface, just adds to it

4. COMMON PATTERNS:
   - Caching layer (memoization)
   - Security (authentication, authorization, encryption)
   - Logging/monitoring (instrumentation)
   - Format conversion (compression, encoding)
   - Stream processing (buffering, filtering)

5. REAL WORLD EXAMPLES:
   - Java IO streams (BufferedInputStream, DataInputStream, etc.)
   - Python decorators (@staticmethod, @property, @functools.lru_cache)
   - REST API response wrappers (compression, encryption)
   - CSS-in-JS styling (building styles through composition)
   - Middleware in web frameworks

6. DESIGN GUIDELINES:
   - Keep decorators simple and focused
   - Preserve original object interface
   - Consider order of decorators
   - Document which decorators can be combined
   - Avoid infinite decorator chains

7. ORDER MATTERS:
   - Some combinations order-sensitive
   - Example: Compression then Encryption vs Encryption then Compression
   - Design to minimize order-dependency

8. ALTERNATIVES:
   - Strategy pattern (different algorithms)
   - Composition (simple case)
   - Inheritance (few combinations)
   - AOP frameworks (cross-cutting concerns)
"""


if __name__ == "__main__":
    demo_coffee_decorator()
    demo_text_formatting_decorator()
    demo_caching_decorator()
    demo_security_decorators()
    demo_stream_decorators()
    demo_function_decorators()
    demo_decorator_benefits()

    print("\n" + "="*60)
    print("All Decorator Pattern examples completed!")
    print("="*60)
