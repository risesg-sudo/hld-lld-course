"""
Singleton Pattern - Ensure a class has only one instance.

This module demonstrates various singleton implementations:
1. Eager initialization (simple but not lazy)
2. Lazy initialization with thread safety
3. Decorator-based singleton
4. Real-world logger example
5. Thread-safe singleton with synchronization

Key Learning Points:
- Singleton ensures single instance throughout application
- Thread safety is critical in concurrent environments
- Singletons can make testing harder (dependency injection preferred)
- Module-level instances in Python can serve same purpose as singleton
"""

import threading
import time
from abc import ABC, abstractmethod


# ============================================================================
# 1. EAGER INITIALIZATION SINGLETON (Simple but not lazy)
# ============================================================================

class EagerSingleton:
    """
    Simplest singleton implementation - instance created when class loads.

    Pros:
    - Thread-safe by default (Python GIL)
    - Simple implementation

    Cons:
    - Not lazy - always creates instance even if not used
    - Can't handle initialization with parameters
    """
    _instance = None

    def __init__(self):
        if EagerSingleton._instance is not None:
            raise RuntimeError("Singleton instance already exists!")
        self.value = 0
        self.data = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EagerSingleton()
        return cls._instance


# ============================================================================
# 2. LAZY INITIALIZATION SINGLETON (Thread-safe)
# ============================================================================

class LazySingleton:
    """
    Thread-safe lazy singleton using locking.

    Pros:
    - Lazy initialization (created only when needed)
    - Thread-safe

    Cons:
    - Synchronization overhead (locking for every access)
    - Still lock contention after first initialization
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.value = 0
        self.config = {}
        self.initialized_time = time.time()

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = LazySingleton()
        return cls._instance


# ============================================================================
# 3. DOUBLE-CHECKED LOCKING SINGLETON (Optimal)
# ============================================================================

class DoubleCheckedSingleton:
    """
    Double-checked locking singleton - best balance of performance and safety.

    Pros:
    - Lazy initialization
    - Minimal synchronization overhead (only once)
    - Good performance

    Cons:
    - More complex code
    - Subtle threading issues possible (though not in Python due to GIL)

    Note: In Python, GIL ensures atomicity, but this pattern is good practice
    for understanding thread-safe patterns.
    """
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.value = 0
        self.state = {}
        self.initialized = True

    @classmethod
    def get_instance(cls):
        # First check (without lock) - optimization
        if cls._instance is None:
            with cls._lock:
                # Second check (with lock) - thread safety
                if cls._instance is None:
                    cls._instance = DoubleCheckedSingleton()
        return cls._instance


# ============================================================================
# 4. DECORATOR-BASED SINGLETON (Pythonic)
# ============================================================================

def singleton(cls):
    """
    Decorator to convert any class into a singleton.

    Usage:
        @singleton
        class MyClass:
            pass

    This is the most Pythonic way to create singletons.
    """
    instances = {}
    lock = threading.Lock()

    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class DatabaseConnection:
    """Example singleton database connection."""

    def __init__(self):
        self.connection = None
        self.connected = False
        print(f"Creating database connection: {id(self)}")

    def connect(self, host, port):
        """Simulate database connection."""
        self.host = host
        self.port = port
        self.connected = True
        print(f"Connected to {host}:{port}")

    def execute(self, query):
        """Execute a database query."""
        if not self.connected:
            raise RuntimeError("Database not connected")
        return f"Executing: {query}"


# ============================================================================
# 5. REAL-WORLD EXAMPLE: THREAD-SAFE LOGGER
# ============================================================================

class Logger(metaclass=type):
    """
    Thread-safe logger singleton using metaclass approach.

    This demonstrates a more advanced singleton pattern using metaclass.
    It provides:
    - Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Thread-safe logging
    - Both console and file output
    - Singleton pattern via metaclass
    """
    _instance = None
    _lock = threading.Lock()

    class __LoggerMeta(type):
        """Metaclass to ensure singleton pattern."""
        _instance = None
        _lock = threading.Lock()

        def __call__(cls, *args, **kwargs):
            if cls._instance is None:
                with cls._lock:
                    if cls._instance is None:
                        cls._instance = super().__call__(*args, **kwargs)
            return cls._instance

    class _LoggerImpl(metaclass=__LoggerMeta):
        """Actual logger implementation."""

        # Log levels
        DEBUG = 0
        INFO = 1
        WARNING = 2
        ERROR = 3
        CRITICAL = 4

        _LEVEL_NAMES = {
            0: "DEBUG",
            1: "INFO",
            2: "WARNING",
            3: "ERROR",
            4: "CRITICAL"
        }

        def __init__(self):
            self.log_level = self.INFO
            self.logs = []
            self.lock = threading.Lock()
            self.file_path = None

        def set_log_level(self, level):
            """Set minimum log level to display."""
            self.log_level = level

        def log(self, level, message):
            """
            Log a message at given level.

            Thread-safe implementation.
            """
            with self.lock:
                if level >= self.log_level:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    level_name = self._LEVEL_NAMES.get(level, "UNKNOWN")
                    formatted = f"[{timestamp}] {level_name}: {message}"

                    self.logs.append(formatted)
                    print(formatted)

                    if self.file_path:
                        with open(self.file_path, 'a') as f:
                            f.write(formatted + "\n")

        def debug(self, message):
            """Log debug message."""
            self.log(self.DEBUG, message)

        def info(self, message):
            """Log info message."""
            self.log(self.INFO, message)

        def warning(self, message):
            """Log warning message."""
            self.log(self.WARNING, message)

        def error(self, message):
            """Log error message."""
            self.log(self.ERROR, message)

        def critical(self, message):
            """Log critical message."""
            self.log(self.CRITICAL, message)

        def get_logs(self):
            """Get all logged messages."""
            with self.lock:
                return self.logs.copy()

    @classmethod
    def get_instance(cls):
        """Get singleton logger instance."""
        return cls._LoggerImpl()


# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

def test_eager_singleton():
    """Test eager initialization singleton."""
    print("\n" + "="*70)
    print("TEST 1: EAGER INITIALIZATION SINGLETON")
    print("="*70)

    instance1 = EagerSingleton.get_instance()
    instance2 = EagerSingleton.get_instance()

    print(f"Instance 1 ID: {id(instance1)}")
    print(f"Instance 2 ID: {id(instance2)}")
    print(f"Same instance: {instance1 is instance2}")

    instance1.value = 42
    print(f"After setting value=42 on instance1, instance2.value={instance2.value}")


def test_lazy_singleton():
    """Test lazy initialization singleton."""
    print("\n" + "="*70)
    print("TEST 2: LAZY INITIALIZATION SINGLETON")
    print("="*70)

    instance1 = LazySingleton.get_instance()
    instance2 = LazySingleton.get_instance()

    print(f"Instance 1 ID: {id(instance1)}")
    print(f"Instance 2 ID: {id(instance2)}")
    print(f"Same instance: {instance1 is instance2}")

    instance1.value = 100
    print(f"After setting value=100 on instance1, instance2.value={instance2.value}")


def test_double_checked_singleton():
    """Test double-checked locking singleton."""
    print("\n" + "="*70)
    print("TEST 3: DOUBLE-CHECKED LOCKING SINGLETON")
    print("="*70)

    instance1 = DoubleCheckedSingleton.get_instance()
    instance2 = DoubleCheckedSingleton.get_instance()

    print(f"Instance 1 ID: {id(instance1)}")
    print(f"Instance 2 ID: {id(instance2)}")
    print(f"Same instance: {instance1 is instance2}")


def test_decorator_singleton():
    """Test decorator-based singleton."""
    print("\n" + "="*70)
    print("TEST 4: DECORATOR-BASED SINGLETON")
    print("="*70)

    db1 = DatabaseConnection()
    db1.connect("localhost", 5432)

    db2 = DatabaseConnection()
    print(f"\nDatabase 1 ID: {id(db1)}")
    print(f"Database 2 ID: {id(db2)}")
    print(f"Same instance: {db1 is db2}")
    print(f"Connected: {db2.connected}")


def test_logger_singleton():
    """Test logger singleton."""
    print("\n" + "="*70)
    print("TEST 5: THREAD-SAFE LOGGER SINGLETON")
    print("="*70)

    logger = Logger.get_instance()
    logger.set_log_level(logger.DEBUG)

    logger.debug("Application started")
    logger.info("Processing request")
    logger.warning("High memory usage")
    logger.error("Failed to connect to database")
    logger.critical("System failure!")

    # Verify same instance from multiple threads
    instance_ids = []

    def get_logger():
        lg = Logger.get_instance()
        instance_ids.append(id(lg))

    threads = [threading.Thread(target=get_logger) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"\nLogger ID from main: {id(logger)}")
    print(f"Logger IDs from threads: {instance_ids}")
    print(f"All same instance: {all(lid == id(logger) for lid in instance_ids)}")

    # Show logs
    print(f"\nTotal logs captured: {len(logger.get_logs())}")


def test_thread_safety():
    """Test thread safety of singletons."""
    print("\n" + "="*70)
    print("TEST 6: THREAD SAFETY TEST")
    print("="*70)

    instances = []

    def worker():
        instance = DoubleCheckedSingleton.get_instance()
        instances.append(id(instance))
        instance.value += 1

    threads = [threading.Thread(target=worker) for _ in range(10)]
    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start

    unique_ids = set(instances)
    print(f"Thread count: 10")
    print(f"Unique instance IDs: {len(unique_ids)}")
    print(f"All same instance: {len(unique_ids) == 1}")
    print(f"Final value: {DoubleCheckedSingleton.get_instance().value}")
    print(f"Time taken: {elapsed:.4f}s")


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

def print_key_takeaways():
    """Print key learning points."""
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. THREAD SAFETY IS CRITICAL
   - Always use locking or atomic operations
   - Double-checked locking balances safety and performance

2. SINGLETON VS DEPENDENCY INJECTION
   - Singletons make testing harder (hard to mock/stub)
   - Dependency injection is preferred in modern applications
   - Consider if you really need a singleton

3. LAZY VS EAGER INITIALIZATION
   - Lazy initialization saves memory if not used
   - Eager initialization is simpler but wastes resources
   - Double-checked locking provides best of both worlds

4. PYTHONIC ALTERNATIVES
   - Module-level instances serve same purpose as singleton
   - Decorators provide clean syntax for singleton pattern
   - Use sparingly - often dependency injection is better

5. REAL-WORLD GOTCHAS
   - Serialization and deserialization can create new instances
   - Reflection can bypass singleton (in reflective languages)
   - Testing becomes complicated with singletons
   - Memory leaks if singleton holds references to other objects

6. WHEN TO USE SINGLETON
   - Logger, logging system (single source of truth)
   - Database connection pool (resource management)
   - Configuration manager (shared configuration)
   - Thread pools, executor services
   - Cache managers
   - BUT: Consider dependency injection first!
    """)


if __name__ == "__main__":
    test_eager_singleton()
    test_lazy_singleton()
    test_double_checked_singleton()
    test_decorator_singleton()
    test_logger_singleton()
    test_thread_safety()
    print_key_takeaways()
