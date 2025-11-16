"""
Abstraction Example: Database Connection
Demonstrates hiding complex implementation details and exposing only essential features
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Abstract base class defining the interface
class Database(ABC):
    """
    Abstract database interface - users don't need to know internal details
    """

    @abstractmethod
    def connect(self):
        """Establish database connection"""
        pass

    @abstractmethod
    def disconnect(self):
        """Close database connection"""
        pass

    @abstractmethod
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        pass

    @abstractmethod
    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert data into table"""
        pass


# Concrete implementation for MySQL
class MySQLDatabase(Database):
    def __init__(self, host, port, username, password, database):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        # Complex connection logic hidden from user
        print(f"Connecting to MySQL at {self.host}:{self.port}...")
        print(f"Authenticating user: {self.username}")
        print(f"Selecting database: {self.database}")
        self.connection = f"MySQL_Connection_{id(self)}"
        print("✓ MySQL Connected successfully")
        return True

    def disconnect(self):
        if self.connection:
            print("Closing MySQL connection...")
            self.connection = None
            print("✓ MySQL Disconnected")
            return True
        return False

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        # Complex query execution hidden
        print(f"Executing MySQL query: {query}")
        # Simulated result
        return [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]

    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        columns = ", ".join(data.keys())
        values = ", ".join([f"'{v}'" for v in data.values()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        print(f"MySQL Insert: {query}")
        return True


# Concrete implementation for MongoDB
class MongoDatabase(Database):
    def __init__(self, connection_string, database):
        self.connection_string = connection_string
        self.database = database
        self.client = None

    def connect(self):
        # Different connection mechanism, same interface
        print(f"Connecting to MongoDB...")
        print(f"Using connection string: {self.connection_string[:20]}...")
        self.client = f"MongoDB_Client_{id(self)}"
        print("✓ MongoDB Connected successfully")
        return True

    def disconnect(self):
        if self.client:
            print("Closing MongoDB connection...")
            self.client = None
            print("✓ MongoDB Disconnected")
            return True
        return False

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        print(f"Executing MongoDB query: {query}")
        # Simulated result
        return [{"_id": "1", "name": "John"}, {"_id": "2", "name": "Jane"}]

    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        collection = table
        print(f"MongoDB Insert into '{collection}': {data}")
        return True


# Concrete implementation for PostgreSQL
class PostgreSQLDatabase(Database):
    def __init__(self, host, port, username, password, database):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        print(f"Connecting to PostgreSQL at {self.host}:{self.port}...")
        print(f"Database: {self.database}, User: {self.username}")
        self.connection = f"PostgreSQL_Connection_{id(self)}"
        print("✓ PostgreSQL Connected successfully")
        return True

    def disconnect(self):
        if self.connection:
            print("Closing PostgreSQL connection...")
            self.connection = None
            print("✓ PostgreSQL Disconnected")
            return True
        return False

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        print(f"Executing PostgreSQL query: {query}")
        return [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]

    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        columns = ", ".join(data.keys())
        placeholders = ", ".join([f"${i+1}" for i in range(len(data))])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        print(f"PostgreSQL Insert: {query}")
        return True


# High-level service using abstraction
class UserService:
    """
    UserService doesn't care about database implementation details
    It works with the Database abstraction
    """

    def __init__(self, database: Database):
        self.db = database

    def initialize(self):
        """Start database connection"""
        self.db.connect()

    def cleanup(self):
        """Close database connection"""
        self.db.disconnect()

    def get_all_users(self):
        """Get all users - works with any database"""
        return self.db.execute_query("SELECT * FROM users")

    def create_user(self, name: str, email: str):
        """Create a new user - works with any database"""
        user_data = {"name": name, "email": email}
        return self.db.insert("users", user_data)


# Usage Example
if __name__ == "__main__":
    print("=" * 70)
    print("Using MySQL Database")
    print("=" * 70)

    # Use with MySQL
    mysql_db = MySQLDatabase("localhost", 3306, "admin", "password", "myapp")
    user_service = UserService(mysql_db)
    user_service.initialize()
    users = user_service.get_all_users()
    user_service.create_user("Alice", "alice@example.com")
    user_service.cleanup()

    print("\n" + "=" * 70)
    print("Using MongoDB Database")
    print("=" * 70)

    # Switch to MongoDB - same UserService code works!
    mongo_db = MongoDatabase("mongodb://localhost:27017", "myapp")
    user_service = UserService(mongo_db)  # Same service, different database
    user_service.initialize()
    users = user_service.get_all_users()
    user_service.create_user("Bob", "bob@example.com")
    user_service.cleanup()

    print("\n" + "=" * 70)
    print("Using PostgreSQL Database")
    print("=" * 70)

    # Switch to PostgreSQL - still works!
    postgres_db = PostgreSQLDatabase("localhost", 5432, "admin", "password", "myapp")
    user_service = UserService(postgres_db)
    user_service.initialize()
    users = user_service.get_all_users()
    user_service.create_user("Charlie", "charlie@example.com")
    user_service.cleanup()

    """
    Key Points about Abstraction:

    1. Hide Complexity:
       - Users of Database class don't need to know connection protocols
       - Internal implementation details are hidden

    2. Common Interface:
       - All databases provide same methods (connect, disconnect, etc.)
       - UserService works with any database without modification

    3. Focus on "What" not "How":
       - UserService knows WHAT operations to perform
       - Database implementations know HOW to perform them

    4. Easy to Extend:
       - Can add new database types (Redis, Oracle, etc.)
       - No changes needed to UserService

    5. Loose Coupling:
       - UserService depends on abstraction, not concrete implementation
       - Can swap databases easily
    """
