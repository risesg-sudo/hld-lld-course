"""
Basic Singleton Implementation

This module demonstrates a simple singleton pattern using Python.
Shows both eager and lazy initialization approaches.
"""


class DatabaseConnection:
    """
    Simple singleton for database connection management.

    Uses lazy initialization - instance created only when first requested.
    Not thread-safe - suitable for single-threaded applications only.
    """

    _instance = None

    def __init__(self):
        """Private constructor - should not be called directly."""
        if DatabaseConnection._instance is not None:
            raise RuntimeError(
                "Singleton instance already exists! Use get_instance() instead."
            )

        # Initialize connection details
        self.host = "localhost"
        self.port = 5432
        self.database = "myapp_db"
        self.connected = False
        self.connection_count = 0

    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance.

        Returns:
            DatabaseConnection: The singleton instance
        """
        if cls._instance is None:
            cls._instance = DatabaseConnection()
            print(f"Created new DatabaseConnection instance: {id(cls._instance)}")
        return cls._instance

    def connect(self):
        """Simulate connecting to database."""
        if not self.connected:
            self.connected = True
            self.connection_count += 1
            print(f"Connected to {self.host}:{self.port}/{self.database}")
        else:
            print("Already connected")

    def disconnect(self):
        """Simulate disconnecting from database."""
        if self.connected:
            self.connected = False
            print(f"Disconnected from database")

    def execute_query(self, query: str):
        """Execute a database query."""
        if not self.connected:
            raise RuntimeError("Not connected to database")
        print(f"Executing query: {query}")
        return f"Result of: {query}"


class ConfigurationManager:
    """
    Singleton configuration manager with eager initialization.

    Instance created immediately when class loads.
    Thread-safe by default (Python module loading is thread-safe).
    """

    # Eager initialization - instance created immediately
    _instance = None

    def __init__(self):
        """Private constructor."""
        if ConfigurationManager._instance is not None:
            raise RuntimeError("Use get_instance() to access ConfigurationManager")

        # Load configuration
        self.config = {
            "app_name": "MyApplication",
            "version": "1.0.0",
            "debug": True,
            "max_connections": 100,
            "timeout": 30
        }
        print("Configuration loaded")

    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = ConfigurationManager()
        return cls._instance

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """Set configuration value."""
        self.config[key] = value
        print(f"Config updated: {key} = {value}")


def demonstrate_basic_singleton():
    """Demonstrate basic singleton behavior."""
    print("="*70)
    print("BASIC SINGLETON DEMONSTRATION")
    print("="*70)

    print("\n1. Getting first database connection instance:")
    db1 = DatabaseConnection.get_instance()
    print(f"   Instance ID: {id(db1)}")

    print("\n2. Getting second database connection instance:")
    db2 = DatabaseConnection.get_instance()
    print(f"   Instance ID: {id(db2)}")

    print(f"\n3. Checking if instances are identical:")
    print(f"   db1 is db2: {db1 is db2}")
    print(f"   Same memory address: {id(db1) == id(db2)}")

    print("\n4. Connecting via first instance:")
    db1.connect()

    print("\n5. Checking connection status via second instance:")
    print(f"   db2.connected: {db2.connected}")
    print("   (State is shared because it's the same instance!)")

    print("\n6. Attempting to create instance directly:")
    try:
        db3 = DatabaseConnection()
    except RuntimeError as e:
        print(f"   Error (expected): {e}")


def demonstrate_configuration_singleton():
    """Demonstrate configuration manager singleton."""
    print("\n" + "="*70)
    print("CONFIGURATION SINGLETON DEMONSTRATION")
    print("="*70)

    print("\n1. Getting first config instance:")
    config1 = ConfigurationManager.get_instance()
    print(f"   App Name: {config1.get('app_name')}")
    print(f"   Instance ID: {id(config1)}")

    print("\n2. Modifying config via first instance:")
    config1.set("debug", False)

    print("\n3. Getting second config instance:")
    config2 = ConfigurationManager.get_instance()
    print(f"   Instance ID: {id(config2)}")
    print(f"   Debug mode: {config2.get('debug')}")
    print("   (Change visible through second reference!)")

    print("\n4. Verifying instances are identical:")
    print(f"   config1 is config2: {config1 is config2}")


if __name__ == "__main__":
    demonstrate_basic_singleton()
    demonstrate_configuration_singleton()

    print("\n" + "="*70)
    print("KEY POINTS")
    print("="*70)
    print("""
1. Only one instance exists for the entire application
2. All references point to the same object in memory
3. State changes are visible through all references
4. Direct instantiation is prevented (raises error)
5. Access controlled through get_instance() class method
    """)
