"""
ABSTRACT FACTORY PATTERN
=========================

Type: Creational Design Pattern

Core Concept:
The Abstract Factory Pattern provides an interface for creating families of
related or dependent objects without specifying their concrete classes.

Instead of creating objects individually, you create a factory that knows
how to create all related objects together.

Use case: When you need to create multiple related objects that work together
as a family or suite.

Real-world analogy:
- Windows and macOS have different UI components
- A Windows factory creates Windows buttons, checkboxes, etc.
- A Mac factory creates Mac buttons, checkboxes, etc.
- Both follow the same interface but produce platform-specific components
- Your app works with any factory, not caring about the platform

Benefits:
- Ensures consistency among related objects
- Makes it easy to switch entire families of objects
- Encapsulates the creation logic for multiple objects
- Follows Open/Closed Principle
- Decouples client from concrete classes

When to use:
- When you have multiple families of objects to create
- When families should work together (consistency)
- When you want to support multiple variants (Windows/Mac, Light/Dark theme)
- When object creation is complex and interdependent
"""

from abc import ABC, abstractmethod


# ============================================================================
# EXAMPLE 1: Cross-Platform UI Components
# ============================================================================

# Abstract interfaces for UI components

class Button(ABC):
    """Abstract button interface."""

    @abstractmethod
    def click(self) -> None:
        """Handle button click."""
        pass

    @abstractmethod
    def render(self) -> str:
        """Render button."""
        pass


class Checkbox(ABC):
    """Abstract checkbox interface."""

    @abstractmethod
    def toggle(self) -> None:
        """Toggle checkbox state."""
        pass

    @abstractmethod
    def render(self) -> str:
        """Render checkbox."""
        pass


class TextBox(ABC):
    """Abstract text box interface."""

    @abstractmethod
    def set_text(self, text: str) -> None:
        """Set text."""
        pass

    @abstractmethod
    def render(self) -> str:
        """Render text box."""
        pass


# Windows implementations

class WindowsButton(Button):
    """Windows-specific button."""

    def click(self) -> None:
        print("Windows button clicked (with Windows styling)")

    def render(self) -> str:
        return "[Windows Button Style]"


class WindowsCheckbox(Checkbox):
    """Windows-specific checkbox."""

    def toggle(self) -> None:
        print("Windows checkbox toggled (with Windows styling)")

    def render(self) -> str:
        return "[x] Windows Checkbox Style"


class WindowsTextBox(TextBox):
    """Windows-specific text box."""

    def __init__(self):
        self.text = ""

    def set_text(self, text: str) -> None:
        self.text = text
        print(f"Windows text box set to: {text}")

    def render(self) -> str:
        return f"[Windows TextBox: {self.text}]"


# macOS implementations

class MacButton(Button):
    """macOS-specific button."""

    def click(self) -> None:
        print("macOS button clicked (with macOS styling)")

    def render(self) -> str:
        return "[macOS Button Style]"


class MacCheckbox(Checkbox):
    """macOS-specific checkbox."""

    def toggle(self) -> None:
        print("macOS checkbox toggled (with macOS styling)")

    def render(self) -> str:
        return "☑ macOS Checkbox Style"


class MacTextBox(TextBox):
    """macOS-specific text box."""

    def __init__(self):
        self.text = ""

    def set_text(self, text: str) -> None:
        self.text = text
        print(f"macOS text box set to: {text}")

    def render(self) -> str:
        return f"{{macOS TextBox: {self.text}}}"


# Linux implementations (bonus)

class LinuxButton(Button):
    """Linux-specific button."""

    def click(self) -> None:
        print("Linux button clicked (with Linux styling)")

    def render(self) -> str:
        return "<Linux Button Style>"


class LinuxCheckbox(Checkbox):
    """Linux-specific checkbox."""

    def toggle(self) -> None:
        print("Linux checkbox toggled (with Linux styling)")

    def render(self) -> str:
        return "◻ Linux Checkbox Style"


class LinuxTextBox(TextBox):
    """Linux-specific text box."""

    def __init__(self):
        self.text = ""

    def set_text(self, text: str) -> None:
        self.text = text
        print(f"Linux text box set to: {text}")

    def render(self) -> str:
        return f"<Linux TextBox: {self.text}>"


# Abstract Factory Interface

class UIFactory(ABC):
    """Abstract factory for creating UI components."""

    @abstractmethod
    def create_button(self) -> Button:
        """Create a button."""
        pass

    @abstractmethod
    def create_checkbox(self) -> Checkbox:
        """Create a checkbox."""
        pass

    @abstractmethod
    def create_textbox(self) -> TextBox:
        """Create a text box."""
        pass


# Concrete Factories

class WindowsUIFactory(UIFactory):
    """Factory for creating Windows UI components."""

    def create_button(self) -> Button:
        return WindowsButton()

    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

    def create_textbox(self) -> TextBox:
        return WindowsTextBox()


class MacUIFactory(UIFactory):
    """Factory for creating macOS UI components."""

    def create_button(self) -> Button:
        return MacButton()

    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()

    def create_textbox(self) -> TextBox:
        return MacTextBox()


class LinuxUIFactory(UIFactory):
    """Factory for creating Linux UI components."""

    def create_button(self) -> Button:
        return LinuxButton()

    def create_checkbox(self) -> Checkbox:
        return LinuxCheckbox()

    def create_textbox(self) -> TextBox:
        return LinuxTextBox()


# Client code

class ApplicationWindow:
    """
    Application window that uses UI components.
    Works with any factory - doesn't care about platform.
    """

    def __init__(self, factory: UIFactory):
        self.factory = factory
        self.button = factory.create_button()
        self.checkbox = factory.create_checkbox()
        self.textbox = factory.create_textbox()

    def render(self) -> None:
        """Render all UI components."""
        print("\nRendering UI components:")
        print(f"  {self.button.render()}")
        print(f"  {self.checkbox.render()}")
        print(f"  {self.textbox.render()}")

    def run(self) -> None:
        """Demonstrate UI interactions."""
        print("\nInteracting with UI components:")
        self.button.click()
        self.checkbox.toggle()
        self.textbox.set_text("Hello, World!")


def demo_cross_platform_ui():
    """Demonstrate abstract factory for cross-platform UI."""
    print("\n" + "="*70)
    print("ABSTRACT FACTORY PATTERN: Cross-Platform UI Components")
    print("="*70)

    # Windows application
    print("\n1. Windows Application:")
    windows_factory = WindowsUIFactory()
    windows_app = ApplicationWindow(windows_factory)
    windows_app.render()
    windows_app.run()

    # macOS application
    print("\n2. macOS Application:")
    mac_factory = MacUIFactory()
    mac_app = ApplicationWindow(mac_factory)
    mac_app.render()
    mac_app.run()

    # Linux application
    print("\n3. Linux Application:")
    linux_factory = LinuxUIFactory()
    linux_app = ApplicationWindow(linux_factory)
    linux_app.render()
    linux_app.run()

    print("\nBenefits:")
    print("  ✓ ApplicationWindow works with any platform")
    print("  ✓ All components from a factory match the platform")
    print("  ✓ Easy to add new platforms (create new factory)")
    print("  ✓ Client code doesn't know about platform details")


# ============================================================================
# EXAMPLE 2: Theme Factory (Light/Dark Theme)
# ============================================================================

class Theme(ABC):
    """Abstract theme."""

    @abstractmethod
    def get_background_color(self) -> str:
        """Get background color."""
        pass

    @abstractmethod
    def get_text_color(self) -> str:
        """Get text color."""
        pass


class LightTheme(Theme):
    """Light theme."""

    def get_background_color(self) -> str:
        return "White"

    def get_text_color(self) -> str:
        return "Black"


class DarkTheme(Theme):
    """Dark theme."""

    def get_background_color(self) -> str:
        return "Black"

    def get_text_color(self) -> str:
        return "White"


class Font(ABC):
    """Abstract font."""

    @abstractmethod
    def get_font_name(self) -> str:
        """Get font name."""
        pass

    @abstractmethod
    def get_font_size(self) -> int:
        """Get font size."""
        pass


class SerifFont(Font):
    """Serif font for light theme."""

    def get_font_name(self) -> str:
        return "Georgia"

    def get_font_size(self) -> int:
        return 12


class MonospaceFont(Font):
    """Monospace font for dark theme."""

    def get_font_name(self) -> str:
        return "Courier New"

    def get_font_size(self) -> int:
        return 10


class ThemeFactory(ABC):
    """Abstract factory for creating theme elements."""

    @abstractmethod
    def create_theme(self) -> Theme:
        """Create theme."""
        pass

    @abstractmethod
    def create_font(self) -> Font:
        """Create font."""
        pass


class LightThemeFactory(ThemeFactory):
    """Factory for light theme components."""

    def create_theme(self) -> Theme:
        return LightTheme()

    def create_font(self) -> Font:
        return SerifFont()


class DarkThemeFactory(ThemeFactory):
    """Factory for dark theme components."""

    def create_theme(self) -> Theme:
        return DarkTheme()

    def create_font(self) -> Font:
        return MonospaceFont()


class Editor:
    """Text editor that uses theme factory."""

    def __init__(self, factory: ThemeFactory):
        self.theme = factory.create_theme()
        self.font = factory.create_font()

    def render(self) -> None:
        """Render editor with theme."""
        bg = self.theme.get_background_color()
        text = self.theme.get_text_color()
        font = self.font.get_font_name()
        size = self.font.get_font_size()

        print(f"Background: {bg}, Text: {text}")
        print(f"Font: {font}, Size: {size}pt")


def demo_theme_factory():
    """Demonstrate theme factory."""
    print("\n" + "="*70)
    print("ABSTRACT FACTORY PATTERN: Theme Factory (Light/Dark)")
    print("="*70)

    print("\n1. Light Theme Editor:")
    light_editor = Editor(LightThemeFactory())
    light_editor.render()

    print("\n2. Dark Theme Editor:")
    dark_editor = Editor(DarkThemeFactory())
    dark_editor.render()

    print("\nBenefit: Easy to switch entire theme with one factory change.")


# ============================================================================
# REAL-WORLD EXAMPLE: Database Connection Factories
# ============================================================================

class Connection(ABC):
    """Abstract database connection."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to database."""
        pass

    @abstractmethod
    def query(self, sql: str) -> list:
        """Execute query."""
        pass


class MySQLConnection(Connection):
    """MySQL connection."""

    def connect(self) -> None:
        print("✓ Connected to MySQL database")

    def query(self, sql: str) -> list:
        print(f"  Executing MySQL query: {sql}")
        return []


class PostgreSQLConnection(Connection):
    """PostgreSQL connection."""

    def connect(self) -> None:
        print("✓ Connected to PostgreSQL database")

    def query(self, sql: str) -> list:
        print(f"  Executing PostgreSQL query: {sql}")
        return []


class ConnectionPool(ABC):
    """Abstract connection pool."""

    @abstractmethod
    def create_pool(self) -> None:
        """Create connection pool."""
        pass


class MySQLPool(ConnectionPool):
    """MySQL connection pool."""

    def create_pool(self) -> None:
        print("✓ Created MySQL connection pool")


class PostgreSQLPool(ConnectionPool):
    """PostgreSQL connection pool."""

    def create_pool(self) -> None:
        print("✓ Created PostgreSQL connection pool")


class DatabaseFactory(ABC):
    """Abstract factory for database components."""

    @abstractmethod
    def create_connection(self) -> Connection:
        """Create database connection."""
        pass

    @abstractmethod
    def create_pool(self) -> ConnectionPool:
        """Create connection pool."""
        pass


class MySQLDatabaseFactory(DatabaseFactory):
    """Factory for MySQL database components."""

    def create_connection(self) -> Connection:
        return MySQLConnection()

    def create_pool(self) -> ConnectionPool:
        return MySQLPool()


class PostgreSQLDatabaseFactory(DatabaseFactory):
    """Factory for PostgreSQL database components."""

    def create_connection(self) -> Connection:
        return PostgreSQLConnection()

    def create_pool(self) -> ConnectionPool:
        return PostgreSQLPool()


class DatabaseManager:
    """Database manager using factory."""

    def __init__(self, factory: DatabaseFactory):
        self.connection = factory.create_connection()
        self.pool = factory.create_pool()

    def initialize(self) -> None:
        """Initialize database components."""
        self.pool.create_pool()
        self.connection.connect()

    def execute_query(self, sql: str) -> None:
        """Execute a query."""
        self.connection.query(sql)


def demo_database_factory():
    """Demonstrate database factory."""
    print("\n" + "="*70)
    print("REAL-WORLD EXAMPLE: Database Factory")
    print("="*70)

    print("\n1. MySQL Database Setup:")
    mysql_manager = DatabaseManager(MySQLDatabaseFactory())
    mysql_manager.initialize()
    mysql_manager.execute_query("SELECT * FROM users")

    print("\n2. PostgreSQL Database Setup:")
    postgres_manager = DatabaseManager(PostgreSQLDatabaseFactory())
    postgres_manager.initialize()
    postgres_manager.execute_query("SELECT * FROM users")

    print("\nBenefit: Entire database infrastructure can be swapped.")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ABSTRACT FACTORY PATTERN EXAMPLES")
    print("="*70)

    # Example 1: Cross-platform UI
    demo_cross_platform_ui()

    # Example 2: Theme factory
    demo_theme_factory()

    # Real-world example: Database factory
    demo_database_factory()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. Abstract Factory creates families of related objects
2. Provides an interface for object creation without specifying classes
3. Ensures consistency among related objects
4. Makes it easy to swap entire families of objects
5. Client works with abstract factory, not concrete ones
6. Good for multi-variant systems (OS, theme, database)
7. Encapsulates complex object creation logic
8. Follows SOLID principles:
   - Open/Closed: Can add new families without modifying existing
   - Dependency Inversion: Depend on abstractions
   - Single Responsibility: Each factory handles one family
9. More complex than Simple Factory but more powerful
10. Use when:
    - Related products need to be created together
    - Need to support multiple families
    - Want to enforce consistency
    - Product creation logic is complex
    """)
