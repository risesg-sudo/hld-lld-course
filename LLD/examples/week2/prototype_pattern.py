"""
Prototype Pattern - Create new objects by cloning an existing object.

This module demonstrates various prototype implementations:
1. Simple shallow copy cloning
2. Deep copy with nested objects
3. Handling circular references
4. Object pool with prototype pattern
5. Prototype registry pattern
6. Copy constructors vs cloning

Key Learning Points:
- Cloning can be faster than creating from scratch (depends on complexity)
- Must understand shallow vs deep copy implications
- Circular references need special handling
- Useful for object pools, caching, and templates
- Python's copy module provides built-in support
"""

import copy
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


# ============================================================================
# 1. SIMPLE SHALLOW COPY CLONING
# ============================================================================

class SimpleDocument:
    """
    Simple document that can be cloned with shallow copy.

    Shallow copy warning:
    - Copies object's own attributes
    - Nested objects are NOT copied (same reference)
    - Changes to nested objects affect all clones
    """

    def __init__(self, title: str, content: str, tags: List[str]):
        self.title = title
        self.content = content
        self.tags = tags  # This is a reference!
        self.created_at = datetime.now()

    def clone(self) -> "SimpleDocument":
        """Create shallow copy (WARNING: shares nested objects)."""
        return copy.copy(self)

    def __str__(self):
        return f"Document(title={self.title}, tags={self.tags})"


# ============================================================================
# 2. DEEP COPY CLONING (Safe)
# ============================================================================

class ComplexDocument:
    """
    Complex document with nested objects.

    Uses deep copy for safe cloning - all nested objects are copied.
    """

    def __init__(
        self,
        title: str,
        content: str,
        metadata: Dict[str, Any],
        sections: List[Dict[str, str]]
    ):
        self.title = title
        self.content = content
        self.metadata = metadata
        self.sections = sections
        self.created_at = datetime.now()

    def deep_clone(self) -> "ComplexDocument":
        """Create deep copy (safe - no shared references)."""
        return copy.deepcopy(self)

    def shallow_clone(self) -> "ComplexDocument":
        """Create shallow copy (WARNING: shares nested objects)."""
        return copy.copy(self)

    def update_metadata(self, key: str, value: Any):
        """Update metadata."""
        self.metadata[key] = value

    def __str__(self):
        return f"Document(title={self.title}, sections={len(self.sections)})"


# ============================================================================
# 3. COPY CONSTRUCTOR PATTERN
# ============================================================================

class UserProfile:
    """
    User profile with copy constructor pattern.

    Copy constructor provides explicit control over what gets copied.
    """

    def __init__(
        self,
        username: str,
        email: str,
        preferences: Optional[Dict[str, Any]] = None,
        profile_picture: Optional[bytes] = None
    ):
        self.username = username
        self.email = email
        self.preferences = preferences or {}
        self.profile_picture = profile_picture
        self.created_at = datetime.now()

    @classmethod
    def from_another(cls, other: "UserProfile") -> "UserProfile":
        """
        Copy constructor - explicit control over cloning.

        This demonstrates:
        - Explicit what gets copied
        - Can transform data during copy
        - More readable than implicit deep copy
        """
        return cls(
            username=other.username,
            email=other.email,
            preferences=copy.deepcopy(other.preferences),  # Deep copy preferences
            profile_picture=other.profile_picture  # Shallow copy (bytes are immutable)
        )

    def update_preference(self, key: str, value: Any):
        """Update user preference."""
        self.preferences[key] = value

    def __str__(self):
        return f"UserProfile(username={self.username}, email={self.email})"


# ============================================================================
# 4. HANDLING CIRCULAR REFERENCES
# ============================================================================

class Node:
    """
    Graph node with circular references.

    This demonstrates the challenge with deep copying circular structures.
    """

    def __init__(self, value: Any, name: str = ""):
        self.value = value
        self.name = name or str(value)
        self.neighbors: List["Node"] = []
        self.parent: Optional["Node"] = None

    def add_neighbor(self, node: "Node"):
        """Add neighbor node (can create cycles)."""
        self.neighbors.append(node)

    def set_parent(self, parent: "Node"):
        """Set parent node (can create cycles)."""
        self.parent = parent

    def clone(self) -> "Node":
        """Clone node with circular references."""
        # Deep copy handles circular references automatically
        return copy.deepcopy(self)

    def __str__(self):
        neighbor_names = [n.name for n in self.neighbors]
        parent_name = self.parent.name if self.parent else "None"
        return (
            f"Node(name={self.name}, neighbors={neighbor_names}, "
            f"parent={parent_name})"
        )


# ============================================================================
# 5. PROTOTYPE REGISTRY PATTERN
# ============================================================================

@copy.copy
class Prototype(ABC):
    """Base class for objects supporting prototype pattern."""

    @abstractmethod
    def clone(self) -> "Prototype":
        """Clone this object."""
        pass


class ShapePrototype(Prototype):
    """Base shape prototype."""

    def __init__(self, color: str, filled: bool):
        self.color = color
        self.filled = filled
        self.created_at = datetime.now()

    def clone(self) -> "ShapePrototype":
        """Clone shape."""
        return copy.deepcopy(self)


class CirclePrototype(ShapePrototype):
    """Circle prototype."""

    def __init__(self, color: str, filled: bool, radius: float):
        super().__init__(color, filled)
        self.radius = radius

    def area(self) -> float:
        """Calculate area."""
        return 3.14159 * self.radius ** 2

    def __str__(self):
        return f"Circle(color={self.color}, radius={self.radius})"


class RectanglePrototype(ShapePrototype):
    """Rectangle prototype."""

    def __init__(self, color: str, filled: bool, width: float, height: float):
        super().__init__(color, filled)
        self.width = width
        self.height = height

    def area(self) -> float:
        """Calculate area."""
        return self.width * self.height

    def __str__(self):
        return f"Rectangle(color={self.color}, width={self.width}, height={self.height})"


class PrototypeRegistry:
    """
    Registry for prototype objects.

    Allows registration of prototypes and cloning by name.
    Useful for factory patterns where you clone registered prototypes.
    """

    def __init__(self):
        self.prototypes: Dict[str, ShapePrototype] = {}

    def register(self, name: str, prototype: ShapePrototype):
        """Register a prototype."""
        self.prototypes[name] = prototype

    def unregister(self, name: str):
        """Unregister a prototype."""
        if name in self.prototypes:
            del self.prototypes[name]

    def create(self, name: str) -> Optional[ShapePrototype]:
        """
        Create a new object by cloning registered prototype.

        Returns:
            Cloned prototype or None if not found
        """
        if name not in self.prototypes:
            return None
        return self.prototypes[name].clone()

    def list_prototypes(self) -> List[str]:
        """List all registered prototypes."""
        return list(self.prototypes.keys())


# ============================================================================
# 6. OBJECT POOL WITH PROTOTYPES
# ============================================================================

class DatabaseConnection:
    """
    Simulated database connection.

    In real scenario, these are expensive to create.
    """

    def __init__(self, host: str, port: int, database: str):
        self.host = host
        self.port = port
        self.database = database
        self.in_use = False
        self.created_at = datetime.now()
        self.connection_id = id(self)

    def clone(self) -> "DatabaseConnection":
        """Clone connection (copy configuration, create new connection)."""
        cloned = copy.copy(self)
        cloned.in_use = False
        cloned.connection_id = id(cloned)
        return cloned

    def acquire(self):
        """Acquire connection."""
        self.in_use = True

    def release(self):
        """Release connection."""
        self.in_use = False

    def __str__(self):
        status = "IN USE" if self.in_use else "AVAILABLE"
        return (
            f"Connection(id={self.connection_id}, "
            f"host={self.host}:{self.port}/{self.database}, {status})"
        )


class ConnectionPool:
    """
    Object pool using prototype pattern.

    Prototypes are cloned to create new objects rather than creating
    from scratch, which can be expensive.
    """

    def __init__(self, prototype: DatabaseConnection, pool_size: int = 5):
        self.prototype = prototype
        self.pool: List[DatabaseConnection] = []
        self.available: List[DatabaseConnection] = []

        # Initialize pool by cloning prototype
        for _ in range(pool_size):
            connection = prototype.clone()
            self.pool.append(connection)
            self.available.append(connection)

    def acquire_connection(self) -> Optional[DatabaseConnection]:
        """
        Acquire a connection from pool.

        Returns:
            Available connection or None if none available
        """
        if not self.available:
            return None

        connection = self.available.pop(0)
        connection.acquire()
        return connection

    def release_connection(self, connection: DatabaseConnection):
        """Release connection back to pool."""
        if connection in self.pool:
            connection.release()
            self.available.append(connection)

    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics."""
        in_use = sum(1 for c in self.pool if c.in_use)
        available = len(self.available)
        return {
            "total": len(self.pool),
            "in_use": in_use,
            "available": available
        }


# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

def test_shallow_vs_deep_copy():
    """Test difference between shallow and deep copy."""
    print("\n" + "="*70)
    print("TEST 1: SHALLOW VS DEEP COPY")
    print("="*70)

    # Original document
    original = SimpleDocument(
        title="Original",
        content="Content here",
        tags=["python", "design-patterns"]
    )

    # Shallow copy (shares tags list!)
    shallow = original.clone()

    print(f"Original: {original}")
    print(f"Shallow copy: {shallow}")
    print(f"Same tags list: {original.tags is shallow.tags}")

    # Modify tags in shallow copy
    shallow.tags.append("oop")
    print(f"\nAfter adding 'oop' to shallow copy:")
    print(f"Original tags: {original.tags}")
    print(f"Shallow tags: {shallow.tags}")
    print("WARNING: Original was affected by shallow copy modification!")


def test_deep_copy():
    """Test safe deep copy cloning."""
    print("\n" + "="*70)
    print("TEST 2: SAFE DEEP COPY")
    print("="*70)

    # Original document with nested structure
    original = ComplexDocument(
        title="Original",
        content="Content here",
        metadata={"author": "John", "version": "1.0"},
        sections=[
            {"title": "Introduction", "content": "Intro text"},
            {"title": "Details", "content": "Detail text"}
        ]
    )

    # Deep copy (safe - all nested objects copied)
    deep = original.deep_clone()

    print(f"Original: {original}")
    print(f"Deep copy: {deep}")
    print(f"Same metadata dict: {original.metadata is deep.metadata}")
    print(f"Same sections list: {original.sections is deep.sections}")

    # Modify deep copy
    deep.metadata["version"] = "2.0"
    deep.sections[0]["content"] = "Modified intro"

    print(f"\nAfter modifying deep copy:")
    print(f"Original metadata: {original.metadata}")
    print(f"Deep copy metadata: {deep.metadata}")
    print(f"Original section: {original.sections[0]}")
    print(f"Deep copy section: {deep.sections[0]}")
    print("SUCCESS: Original was not affected by deep copy modification!")


def test_copy_constructor():
    """Test copy constructor pattern."""
    print("\n" + "="*70)
    print("TEST 3: COPY CONSTRUCTOR PATTERN")
    print("="*70)

    # Original user
    user1 = UserProfile(
        username="john_doe",
        email="john@example.com",
        preferences={"theme": "dark", "language": "en"}
    )

    # Copy using copy constructor
    user2 = UserProfile.from_another(user1)

    print(f"Original: {user1}")
    print(f"Copy: {user2}")
    print(f"Same preferences dict: {user1.preferences is user2.preferences}")

    # Modify copy's preferences
    user2.update_preference("theme", "light")

    print(f"\nAfter modifying copy's preferences:")
    print(f"Original preferences: {user1.preferences}")
    print(f"Copy preferences: {user2.preferences}")
    print("SUCCESS: Preferences were deep copied!")


def test_circular_references():
    """Test cloning with circular references."""
    print("\n" + "="*70)
    print("TEST 4: HANDLING CIRCULAR REFERENCES")
    print("="*70)

    # Create circular reference graph
    node_a = Node("A")
    node_b = Node("B")
    node_c = Node("C")

    node_a.add_neighbor(node_b)
    node_b.add_neighbor(node_c)
    node_c.add_neighbor(node_a)  # Creates cycle!

    node_b.set_parent(node_a)

    print(f"Original graph: {node_a}")

    # Clone (Python's deepcopy handles circular references)
    cloned = node_a.clone()

    print(f"Cloned graph: {cloned}")
    print(f"Same neighbor object: {node_a.neighbors[0] is cloned.neighbors[0]}")
    print("SUCCESS: Circular references handled correctly!")


def test_prototype_registry():
    """Test prototype registry pattern."""
    print("\n" + "="*70)
    print("TEST 5: PROTOTYPE REGISTRY")
    print("="*70)

    # Create registry
    registry = PrototypeRegistry()

    # Register prototypes
    circle_proto = CirclePrototype(color="red", filled=True, radius=5.0)
    rect_proto = RectanglePrototype(color="blue", filled=False, width=10.0, height=5.0)

    registry.register("red_circle", circle_proto)
    registry.register("blue_rectangle", rect_proto)

    print(f"Registered prototypes: {registry.list_prototypes()}")

    # Create new objects by cloning prototypes
    circle1 = registry.create("red_circle")
    circle2 = registry.create("red_circle")
    rect1 = registry.create("blue_rectangle")

    print(f"\nCreated circle 1: {circle1}, area: {circle1.area():.2f}")
    print(f"Created circle 2: {circle2}, area: {circle2.area():.2f}")
    print(f"Created rectangle: {rect1}, area: {rect1.area():.2f}")
    print(f"Circles are different objects: {circle1 is not circle2}")


def test_object_pool():
    """Test object pool with prototype pattern."""
    print("\n" + "="*70)
    print("TEST 6: OBJECT POOL WITH PROTOTYPES")
    print("="*70)

    # Create prototype connection
    prototype = DatabaseConnection(host="localhost", port=5432, database="mydb")

    # Create pool from prototype
    pool = ConnectionPool(prototype, pool_size=3)

    print(f"Pool stats: {pool.get_stats()}")

    # Acquire connections
    conn1 = pool.acquire_connection()
    conn2 = pool.acquire_connection()

    print(f"\nAcquired connection 1: {conn1}")
    print(f"Acquired connection 2: {conn2}")
    print(f"Pool stats after acquiring 2: {pool.get_stats()}")

    # Release connection
    pool.release_connection(conn1)
    print(f"\nAfter releasing connection 1:")
    print(f"Pool stats: {pool.get_stats()}")

    # Acquire another
    conn3 = pool.acquire_connection()
    print(f"Acquired connection 3: {conn3}")
    print(f"Pool stats: {pool.get_stats()}")


def test_performance_comparison():
    """Compare cloning vs creating new objects."""
    print("\n" + "="*70)
    print("TEST 7: PERFORMANCE COMPARISON")
    print("="*70)

    import time

    # For this simple example, cloning might not be faster,
    # but demonstrates the pattern

    data = {
        "key1": "value1",
        "key2": "value2",
        "nested": {"deep": "data"}
    }

    # Creating new
    doc1 = ComplexDocument(
        title="Test",
        content="Content",
        metadata=data.copy(),
        sections=[]
    )

    # Cloning existing
    doc2 = doc1.deep_clone()

    print(f"Original: {doc1}")
    print(f"Cloned: {doc2}")
    print(f"Same object: {doc1 is doc2}")
    print(f"Same metadata: {doc1.metadata is doc2.metadata}")


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

def print_key_takeaways():
    """Print key learning points."""
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. SHALLOW VS DEEP COPY - CRITICAL DISTINCTION
   Shallow Copy:
   - Copies only object's own attributes
   - Nested objects are shared (same reference)
   - Changes to nested objects affect all copies
   - Use: When you want shared mutable state (rare)

   Deep Copy:
   - Recursively copies all nested objects
   - Each copy has its own nested objects
   - Changes to nested objects don't affect others
   - Use: Most of the time (safe default)

2. PYTHON'S COPY MODULE
   - copy.copy() for shallow copy
   - copy.deepcopy() for deep copy
   - Automatically handles circular references
   - Works for most objects

3. WHEN CLONING IS FASTER
   - Complex initialization logic
   - Database connection setup
   - File I/O operations
   - Network calls
   - But NOT for simple object creation (usually slower)

4. COPY CONSTRUCTOR PATTERN
   - More explicit than implicit deep copy
   - Better control over what gets copied
   - Can transform data during copy
   - Self-documenting code

5. CIRCULAR REFERENCES
   - Python's copy module handles them automatically
   - Deep copy maintains structure correctly
   - Uses memo dict to track already-copied objects
   - Important in graph/tree structures

6. PROTOTYPE REGISTRY PATTERN
   - Register prototype templates
   - Clone to create new objects
   - Useful for factory patterns
   - Decouples object creation from specific classes

7. OBJECT POOL WITH PROTOTYPES
   - Clone prototype to initialize pool
   - Faster than creating from scratch
   - Connection pooling, thread pools, etc.
   - Resource management pattern

8. ALTERNATIVES TO CONSIDER
   - Factory methods - for creating variations
   - Abstract factories - for families of objects
   - But Prototype is best when:
     * Cloning is significantly faster
     * Object creation is expensive
     * You have many variations
     * You need to create objects at runtime

9. COMMON GOTCHAS
   - Forgetting deep copy with mutable attributes
   - Shared state from shallow copies
   - Circular references (but Python handles them)
   - Performance assumptions (measure before optimizing)

10. REAL-WORLD EXAMPLES
    - Database connection pooling
    - HTTP request/response cloning
    - Document templates
    - GUI element cloning
    - Configuration object copying
    - Cache invalidation patterns
    """)


if __name__ == "__main__":
    test_shallow_vs_deep_copy()
    test_deep_copy()
    test_copy_constructor()
    test_circular_references()
    test_prototype_registry()
    test_object_pool()
    test_performance_comparison()
    print_key_takeaways()
