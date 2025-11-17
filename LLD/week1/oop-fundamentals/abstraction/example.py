"""
Abstraction Example: Database Connection Layer
Demonstrates hiding complex implementation details behind a simple interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Abstract base class defining the interface
class Database(ABC):
    """
    Abstract database interface - defines WHAT operations are available.
    Users work with this abstraction, not caring HOW operations are implemented.
    """

    @abstractmethod
    def connect(self):
        """Establish database connection."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close database connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        pass

    @abstractmethod
    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert data into a table."""
        pass


# Concrete implementation for MySQL
class MySQLDatabase(Database):
    """
    MySQL implementation - hides all MySQL-specific complexity.
    Users don't need to know about MySQL drivers, connection strings, etc.
    """

    def __init__(self, host, port, username, password, database):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """
        Abstraction: Simple connect() method
        Hidden: Connection pooling, authentication, network protocols
        """
        print(f"[MySQL] Connecting to {self.host}:{self.port}")
        print(f"[MySQL] Authenticating user: {self.username}")
        print(f"[MySQL] Selecting database: {self.database}")

        # Hidden complexity: connection pooling, retries, timeouts
        self.connection = f"MySQL_Connection_{id(self)}"

        print(f"[MySQL] Connected successfully")
        return True

    def disconnect(self):
        """Abstraction: Simple disconnect() - hides cleanup complexity."""
        if self.connection:
            print("[MySQL] Closing connection and releasing resources")
            self.connection = None
            return True
        return False

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Abstraction: Execute query
        Hidden: Query parsing, optimization, result set handling
        """
        print(f"[MySQL] Executing: {query}")
        # Hidden: query optimization, prepared statements, result buffering
        return [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]

    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        """Hidden: SQL generation, escaping, transaction handling."""
        columns = ", ".join(data.keys())
        values = ", ".join([f"'{v}'" for v in data.values()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        print(f"[MySQL] {query}")
        return True


# Concrete implementation for MongoDB
class MongoDatabase(Database):
    """
    MongoDB implementation - completely different internals, same interface.
    """

    def __init__(self, connection_string, database):
        self.connection_string = connection_string
        self.database = database
        self.client = None

    def connect(self):
        """Same interface, different implementation."""
        print(f"[MongoDB] Parsing connection string...")
        print(f"[MongoDB] Establishing connection to cluster")

        # Hidden: replica set discovery, connection pooling, auth
        self.client = f"MongoDB_Client_{id(self)}"

        print(f"[MongoDB] Connected to database: {self.database}")
        return True

    def disconnect(self):
        """Same method name, MongoDB-specific cleanup."""
        if self.client:
            print("[MongoDB] Closing connection pool")
            self.client = None
            return True
        return False

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """MongoDB uses different query language internally."""
        print(f"[MongoDB] Executing: {query}")
        # Hidden: BSON parsing, query translation, cursor handling
        return [{"_id": "507f1f77bcf86cd799439011", "name": "Bob"}]

    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        """MongoDB calls it 'collection', but abstraction calls it 'table'."""
        print(f"[MongoDB] Inserting into collection '{table}': {data}")
        # Hidden: BSON encoding, write concerns, journaling
        return True


# High-level service using abstraction
class UserService:
    """
    UserService works with Database abstraction.
    It doesn't know or care which database is being used.
    This demonstrates the power of abstraction.
    """

    def __init__(self, database: Database):
        """Depends on abstraction, not concrete implementation."""
        self.db = database

    def initialize(self):
        """Simple method - complexity hidden in database implementation."""
        print("\n=== Initializing UserService ===")
        self.db.connect()

    def cleanup(self):
        """Clean interface - internal complexity abstracted away."""
        print("\n=== Cleaning up UserService ===")
        self.db.disconnect()

    def get_all_users(self):
        """
        UserService doesn't know HOW data is fetched.
        It just calls the abstract interface.
        """
        print("\n--- Fetching all users ---")
        return self.db.execute_query("SELECT * FROM users")

    def create_user(self, name: str, email: str):
        """Same simple interface works with any database."""
        print(f"\n--- Creating user: {name} ---")
        user_data = {"name": name, "email": email}
        return self.db.insert("users", user_data)


# Demonstration
if __name__ == "__main__":
    print("=== Database Abstraction Demo ===\n")

    print("=" * 70)
    print("DEMO 1: Using MySQL Database")
    print("=" * 70)

    # Create service with MySQL
    mysql_db = MySQLDatabase("localhost", 3306, "admin", "password", "myapp")
    user_service = UserService(mysql_db)

    user_service.initialize()
    users = user_service.get_all_users()
    user_service.create_user("Alice", "alice@example.com")
    user_service.cleanup()

    print("\n" + "=" * 70)
    print("DEMO 2: Using MongoDB Database")
    print("=" * 70)

    # Switch to MongoDB - UserService code doesn't change!
    mongo_db = MongoDatabase("mongodb://localhost:27017", "myapp")
    user_service = UserService(mongo_db)

    user_service.initialize()
    users = user_service.get_all_users()
    user_service.create_user("Bob", "bob@example.com")
    user_service.cleanup()

    print("\n" + "=" * 70)
    print("KEY ABSTRACTION BENEFITS DEMONSTRATED:")
    print("=" * 70)
    print("1. UserService works with ANY database implementation")
    print("2. Complex database details hidden from UserService")
    print("3. Same interface (connect, query, insert) for all databases")
    print("4. Easy to switch database without changing UserService code")
    print("5. UserService focuses on WHAT to do, not HOW to do it")
