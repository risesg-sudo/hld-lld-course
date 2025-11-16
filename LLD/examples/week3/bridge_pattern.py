"""
Bridge Pattern - Decouple abstraction from implementation.

This module demonstrates various bridge pattern implementations:
1. Remote control (abstraction) controlling devices (implementation)
2. Database drivers (abstraction) for different databases
3. Graphics shapes (abstraction) with rendering engines
4. Payment systems (abstraction) with different processors
5. Message systems (abstraction) with different protocols
6. Storage systems (abstraction) with different backends

Key Learning Points:
- Bridge separates abstraction from implementation
- Allows independent variation of abstraction and implementation
- Solves problem of subclass explosion from multiple axes
- Implementation can be changed at runtime
- More flexible than deep inheritance hierarchies
- Implementation details hidden behind abstraction
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum


# ============================================================================
# 1. REMOTE CONTROL - ABSTRACTION & DEVICE - IMPLEMENTATION
# ============================================================================

class Device(ABC):
    """
    Implementation interface for devices.
    This is the "implementation" part of the bridge.
    """

    @abstractmethod
    def turn_on(self) -> None:
        pass

    @abstractmethod
    def turn_off(self) -> None:
        pass

    @abstractmethod
    def set_channel(self, channel: int) -> None:
        pass

    @abstractmethod
    def set_volume(self, volume: int) -> None:
        pass


class Television(Device):
    """Concrete TV implementation."""

    def __init__(self):
        self.on = False
        self.channel = 1
        self.volume = 30

    def turn_on(self) -> None:
        self.on = True
        print("TV is ON")

    def turn_off(self) -> None:
        self.on = False
        print("TV is OFF")

    def set_channel(self, channel: int) -> None:
        if self.on:
            self.channel = channel
            print(f"TV: Set to channel {channel}")

    def set_volume(self, volume: int) -> None:
        if self.on:
            self.volume = volume
            print(f"TV: Volume set to {volume}")


class Radio(Device):
    """Concrete Radio implementation."""

    def __init__(self):
        self.on = False
        self.frequency = 88.5
        self.volume = 20

    def turn_on(self) -> None:
        self.on = True
        print("Radio is ON")

    def turn_off(self) -> None:
        self.on = False
        print("Radio is OFF")

    def set_channel(self, channel: int) -> None:
        if self.on:
            # Convert channel number to frequency
            self.frequency = 88.5 + (channel * 0.5)
            print(f"Radio: Set to frequency {self.frequency} FM")

    def set_volume(self, volume: int) -> None:
        if self.on:
            self.volume = volume
            print(f"Radio: Volume set to {volume}")


class SmartSpeaker(Device):
    """Concrete Smart Speaker implementation."""

    def __init__(self):
        self.on = False
        self.playlist = 1
        self.volume = 50

    def turn_on(self) -> None:
        self.on = True
        print("Smart Speaker is ON")

    def turn_off(self) -> None:
        self.on = False
        print("Smart Speaker is OFF")

    def set_channel(self, channel: int) -> None:
        if self.on:
            self.playlist = channel
            print(f"Smart Speaker: Playing playlist {channel}")

    def set_volume(self, volume: int) -> None:
        if self.on:
            self.volume = volume
            print(f"Smart Speaker: Volume set to {volume}%")


class RemoteControl(ABC):
    """
    Abstraction for remote controls.
    This is the "abstraction" part of the bridge.
    Uses Device through bridge interface.
    """

    def __init__(self, device: Device):
        self._device = device

    def power(self) -> None:
        print("Remote: Power button")
        # This would need state tracking, simplified for example

    @abstractmethod
    def channel_up(self) -> None:
        pass

    @abstractmethod
    def channel_down(self) -> None:
        pass

    @abstractmethod
    def volume_up(self) -> None:
        pass

    @abstractmethod
    def volume_down(self) -> None:
        pass


class BasicRemote(RemoteControl):
    """Basic remote control implementation."""

    def __init__(self, device: Device):
        super().__init__(device)
        self.current_channel = 1
        self.current_volume = 30

    def power(self) -> None:
        self._device.turn_on()

    def channel_up(self) -> None:
        self.current_channel += 1
        self._device.set_channel(self.current_channel)
        print(f"Basic Remote: Channel up to {self.current_channel}")

    def channel_down(self) -> None:
        self.current_channel -= 1
        self._device.set_channel(self.current_channel)
        print(f"Basic Remote: Channel down to {self.current_channel}")

    def volume_up(self) -> None:
        self.current_volume += 5
        self._device.set_volume(self.current_volume)
        print(f"Basic Remote: Volume up to {self.current_volume}")

    def volume_down(self) -> None:
        self.current_volume -= 5
        self._device.set_volume(self.current_volume)
        print(f"Basic Remote: Volume down to {self.current_volume}")


class AdvancedRemote(RemoteControl):
    """Advanced remote with more features."""

    def __init__(self, device: Device):
        super().__init__(device)
        self.current_channel = 1
        self.current_volume = 30
        self.favorites = {}

    def power(self) -> None:
        self._device.turn_on()

    def channel_up(self) -> None:
        self.current_channel = min(100, self.current_channel + 1)
        self._device.set_channel(self.current_channel)

    def channel_down(self) -> None:
        self.current_channel = max(1, self.current_channel - 1)
        self._device.set_channel(self.current_channel)

    def volume_up(self) -> None:
        self.current_volume = min(100, self.current_volume + 2)
        self._device.set_volume(self.current_volume)

    def volume_down(self) -> None:
        self.current_volume = max(0, self.current_volume - 2)
        self._device.set_volume(self.current_volume)

    def save_favorite(self, name: str, channel: int) -> None:
        self.favorites[name] = channel
        print(f"Advanced Remote: Saved favorite '{name}' at channel {channel}")

    def go_to_favorite(self, name: str) -> None:
        if name in self.favorites:
            channel = self.favorites[name]
            self._device.set_channel(channel)
            print(f"Advanced Remote: Going to favorite '{name}' (channel {channel})")


# ============================================================================
# 2. DATABASE BRIDGE PATTERN
# ============================================================================

class DatabaseQueryEngine(ABC):
    """Implementation interface for database engines."""

    @abstractmethod
    def execute_query(self, query: str) -> List[Dict]:
        pass

    @abstractmethod
    def execute_insert(self, table: str, data: Dict) -> bool:
        pass

    @abstractmethod
    def close_connection(self) -> None:
        pass


class MySQLEngine(DatabaseQueryEngine):
    """Concrete MySQL engine implementation."""

    def __init__(self):
        self.name = "MySQL"

    def execute_query(self, query: str) -> List[Dict]:
        print(f"MySQL: Executing query: {query[:40]}...")
        return [{"id": 1, "name": "John"}]

    def execute_insert(self, table: str, data: Dict) -> bool:
        print(f"MySQL: Inserting into {table}: {data}")
        return True

    def close_connection(self) -> None:
        print("MySQL: Connection closed")


class PostgreSQLEngine(DatabaseQueryEngine):
    """Concrete PostgreSQL engine implementation."""

    def __init__(self):
        self.name = "PostgreSQL"

    def execute_query(self, query: str) -> List[Dict]:
        print(f"PostgreSQL: Executing with ACID compliance: {query[:40]}...")
        return [{"id": 1, "name": "John", "role": "admin"}]

    def execute_insert(self, table: str, data: Dict) -> bool:
        print(f"PostgreSQL: Transactional insert into {table}")
        return True

    def close_connection(self) -> None:
        print("PostgreSQL: Transaction committed and closed")


class MongoDBEngine(DatabaseQueryEngine):
    """Concrete MongoDB engine implementation."""

    def __init__(self):
        self.name = "MongoDB"

    def execute_query(self, query: str) -> List[Dict]:
        print(f"MongoDB: Document query with aggregation: {query[:40]}...")
        return [{"_id": "1", "name": "John", "metadata": {}}]

    def execute_insert(self, table: str, data: Dict) -> bool:
        print(f"MongoDB: Inserting document into '{table}'")
        return True

    def close_connection(self) -> None:
        print("MongoDB: Connection closed")


class Database(ABC):
    """Abstraction for database interface."""

    def __init__(self, engine: DatabaseQueryEngine):
        self._engine = engine

    @abstractmethod
    def query(self, sql: str) -> List[Dict]:
        pass

    @abstractmethod
    def insert(self, table: str, data: Dict) -> bool:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class UserDatabase(Database):
    """Concrete database for user operations."""

    def query(self, sql: str) -> List[Dict]:
        return self._engine.execute_query(f"USER_QUERY: {sql}")

    def insert(self, table: str, data: Dict) -> bool:
        return self._engine.execute_insert(f"users_{table}", data)

    def close(self) -> None:
        self._engine.close_connection()

    def get_user(self, user_id: int) -> Dict:
        return self.query(f"SELECT * FROM users WHERE id = {user_id}")[0]

    def create_user(self, name: str, email: str) -> bool:
        return self.insert("", {"name": name, "email": email})


class ProductDatabase(Database):
    """Concrete database for product operations."""

    def query(self, sql: str) -> List[Dict]:
        return self._engine.execute_query(f"PRODUCT_QUERY: {sql}")

    def insert(self, table: str, data: Dict) -> bool:
        return self._engine.execute_insert(f"products_{table}", data)

    def close(self) -> None:
        self._engine.close_connection()

    def get_product(self, product_id: int) -> Dict:
        return self.query(f"SELECT * FROM products WHERE id = {product_id}")[0]

    def create_product(self, name: str, price: float) -> bool:
        return self.insert("", {"name": name, "price": price})


# ============================================================================
# 3. GRAPHICS SHAPES WITH RENDERING ENGINES
# ============================================================================

class Renderer(ABC):
    """Implementation interface for rendering."""

    @abstractmethod
    def render_circle(self, x: float, y: float, radius: float) -> None:
        pass

    @abstractmethod
    def render_square(self, x: float, y: float, side: float) -> None:
        pass

    @abstractmethod
    def render_triangle(self, x: float, y: float, size: float) -> None:
        pass


class OpenGLRenderer(Renderer):
    """OpenGL rendering implementation."""

    def render_circle(self, x: float, y: float, radius: float) -> None:
        print(f"OpenGL: Drawing circle at ({x}, {y}) with radius {radius}")

    def render_square(self, x: float, y: float, side: float) -> None:
        print(f"OpenGL: Drawing square at ({x}, {y}) with side {side}")

    def render_triangle(self, x: float, y: float, size: float) -> None:
        print(f"OpenGL: Drawing triangle at ({x}, {y}) with size {size}")


class CanvasRenderer(Renderer):
    """Canvas rendering implementation."""

    def render_circle(self, x: float, y: float, radius: float) -> None:
        print(f"Canvas: arc({x}, {y}, {radius})")

    def render_square(self, x: float, y: float, side: float) -> None:
        print(f"Canvas: rect({x}, {y}, {side}, {side})")

    def render_triangle(self, x: float, y: float, size: float) -> None:
        print(f"Canvas: path(triangle at {x}, {y})")


class VectorRenderer(Renderer):
    """Vector rendering implementation."""

    def render_circle(self, x: float, y: float, radius: float) -> None:
        print(f"SVG: <circle cx='{x}' cy='{y}' r='{radius}' />")

    def render_square(self, x: float, y: float, side: float) -> None:
        print(f"SVG: <rect x='{x}' y='{y}' width='{side}' height='{side}' />")

    def render_triangle(self, x: float, y: float, size: float) -> None:
        print(f"SVG: <polygon points='triangle at ({x},{y})' />")


class Shape(ABC):
    """Abstraction for shapes."""

    def __init__(self, renderer: Renderer):
        self._renderer = renderer

    @abstractmethod
    def draw(self) -> None:
        pass


class Circle(Shape):
    """Concrete Circle shape."""

    def __init__(self, renderer: Renderer, x: float, y: float, radius: float):
        super().__init__(renderer)
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self) -> None:
        self._renderer.render_circle(self.x, self.y, self.radius)


class Square(Shape):
    """Concrete Square shape."""

    def __init__(self, renderer: Renderer, x: float, y: float, side: float):
        super().__init__(renderer)
        self.x = x
        self.y = y
        self.side = side

    def draw(self) -> None:
        self._renderer.render_square(self.x, self.y, self.side)


class Triangle(Shape):
    """Concrete Triangle shape."""

    def __init__(self, renderer: Renderer, x: float, y: float, size: float):
        super().__init__(renderer)
        self.x = x
        self.y = y
        self.size = size

    def draw(self) -> None:
        self._renderer.render_triangle(self.x, self.y, self.size)


# ============================================================================
# 4. DEMONSTRATION
# ============================================================================

def demo_remote_control():
    """Demonstrate remote control bridge pattern."""
    print("\n" + "="*60)
    print("BRIDGE PATTERN - REMOTE CONTROL EXAMPLE")
    print("="*60)

    # Create devices
    tv = Television()
    radio = Radio()
    speaker = SmartSpeaker()

    # Basic remotes
    print("\nBasic Remote with TV:")
    tv_remote = BasicRemote(tv)
    tv_remote.power()
    tv_remote.channel_up()
    tv_remote.channel_up()
    tv_remote.volume_up()
    tv_remote.volume_up()

    print("\nBasic Remote with Radio:")
    radio_remote = BasicRemote(radio)
    radio_remote.power()
    radio_remote.channel_up()
    radio_remote.volume_down()

    # Advanced remote
    print("\nAdvanced Remote with TV:")
    advanced_remote = AdvancedRemote(tv)
    advanced_remote.power()
    advanced_remote.channel_up()
    advanced_remote.save_favorite("News", 5)
    advanced_remote.save_favorite("Sports", 10)
    advanced_remote.go_to_favorite("News")

    print("\nAdvanced Remote with Speaker:")
    speaker_remote = AdvancedRemote(speaker)
    speaker_remote.power()
    speaker_remote.save_favorite("Rock", 1)
    speaker_remote.save_favorite("Jazz", 2)
    speaker_remote.go_to_favorite("Jazz")


def demo_database_bridge():
    """Demonstrate database bridge pattern."""
    print("\n" + "="*60)
    print("BRIDGE PATTERN - DATABASE BRIDGE EXAMPLE")
    print("="*60)

    # MySQL
    print("\nMySQL Database:")
    mysql_engine = MySQLEngine()
    user_db_mysql = UserDatabase(mysql_engine)
    user_db_mysql.create_user("Alice", "alice@example.com")
    user_db_mysql.get_user(1)
    user_db_mysql.close()

    # PostgreSQL
    print("\nPostgreSQL Database:")
    postgres_engine = PostgreSQLEngine()
    product_db_postgres = ProductDatabase(postgres_engine)
    product_db_postgres.create_product("Laptop", 999.99)
    product_db_postgres.get_product(1)
    product_db_postgres.close()

    # MongoDB
    print("\nMongoDB Database:")
    mongo_engine = MongoDBEngine()
    user_db_mongo = UserDatabase(mongo_engine)
    user_db_mongo.create_user("Bob", "bob@example.com")
    user_db_mongo.get_user(1)
    user_db_mongo.close()

    # Easy to switch engines
    print("\nSwitching MySQL to PostgreSQL:")
    user_db_mysql._engine = postgres_engine
    user_db_mysql.create_user("Charlie", "charlie@example.com")
    user_db_mysql.close()


def demo_graphics_rendering():
    """Demonstrate graphics rendering bridge pattern."""
    print("\n" + "="*60)
    print("BRIDGE PATTERN - GRAPHICS RENDERING EXAMPLE")
    print("="*60)

    shapes: List[Shape] = [
        Circle(OpenGLRenderer(), 50, 50, 25),
        Square(OpenGLRenderer(), 100, 100, 30),
        Triangle(OpenGLRenderer(), 150, 150, 40),
    ]

    print("\nOpenGL Rendering:")
    for shape in shapes:
        shape.draw()

    print("\nCanvas Rendering:")
    shapes[0]._renderer = CanvasRenderer()
    shapes[1]._renderer = CanvasRenderer()
    shapes[2]._renderer = CanvasRenderer()
    for shape in shapes:
        shape.draw()

    print("\nVector Rendering:")
    shapes[0]._renderer = VectorRenderer()
    shapes[1]._renderer = VectorRenderer()
    shapes[2]._renderer = VectorRenderer()
    for shape in shapes:
        shape.draw()


def demo_bridge_pattern_benefits():
    """Demonstrate bridge pattern benefits."""
    print("\n" + "="*60)
    print("BRIDGE PATTERN - BENEFITS")
    print("="*60)

    print("""
KEY BENEFITS:

1. AVOIDS SUBCLASS EXPLOSION
   Without Bridge:
   - RemoteControl -> BasicRemote, AdvancedRemote
   - Device -> TV, Radio, Speaker
   - Creates N x M combinations (2 x 3 = 6 classes)

   With Bridge:
   - 2 Remote types + 3 Device types = 5 classes (not 6)
   - Can add new remotes/devices independently

2. INDEPENDENT VARIATION
   - Can vary abstraction (remote controls) independently
   - Can vary implementation (devices) independently
   - Add new device without changing remotes
   - Add new remote without changing devices

3. SEPARATION OF CONCERNS
   - Abstraction handles high-level interface
   - Implementation handles low-level details
   - Clear separation of responsibilities

4. RUNTIME FLEXIBILITY
   - Can change implementation at runtime
   - Switch database from MySQL to PostgreSQL
   - Change rendering engine on the fly

5. OPEN/CLOSED PRINCIPLE
   - Open for extension (new remotes, new devices)
   - Closed for modification (existing code unchanged)

EXAMPLE: Remote Control + Devices
- Without Bridge: 2 remotes × 3 devices = 6 classes
- With Bridge: 2 remotes + 3 devices = 5 classes
- If add third remote: 3 remotes + 3 devices = 6 classes
    """)


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

"""
KEY TAKEAWAYS - BRIDGE PATTERN:

1. WHEN TO USE:
   - Multiple axes of variation (abstraction + implementation)
   - Avoid subclass explosion
   - Implementation details should be hidden
   - Need runtime implementation switching
   - Want flexible combinations of abstractions

2. BRIDGE vs ADAPTER:
   - Bridge: Planned at design time for variations
   - Adapter: Retrofitted for incompatible interfaces
   - Use Bridge when designing multi-variant systems

3. BRIDGE vs DECORATOR:
   - Bridge: Separates abstraction from implementation
   - Decorator: Adds behavior to objects
   - Bridge for two-axis variation, Decorator for behavior

4. STRUCTURE:
   - Abstraction (high-level interface)
   - RefinedAbstraction (specialized interface)
   - Implementor (low-level interface)
   - ConcreteImplementor (actual implementation)

5. IDENTIFY VARIATION POINTS:
   - List axis 1 variations (e.g., remote types)
   - List axis 2 variations (e.g., device types)
   - If multiple axes, consider bridge

6. REAL WORLD EXAMPLES:
   - Remote controls with different devices
   - UI toolkits with different OS implementations
   - Database abstraction layers
   - Graphics rendering with different engines
   - Message systems with different protocols
   - Payment systems with different processors

7. DESIGN TIPS:
   - Keep abstraction simple and focused
   - Don't expose implementation details
   - Use composition for variation
   - Document how bridge can be extended

8. COMMON MISTAKES:
   - Over-engineering when inheritance sufficient
   - Making abstraction too close to implementation
   - Not identifying true variation axes
   - Using bridge when decorator more appropriate
"""


if __name__ == "__main__":
    demo_remote_control()
    demo_database_bridge()
    demo_graphics_rendering()
    demo_bridge_pattern_benefits()

    print("\n" + "="*60)
    print("All Bridge Pattern examples completed!")
    print("="*60)
