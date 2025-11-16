"""
Composite Pattern - Compose objects into tree structures to represent part-whole hierarchies.

This module demonstrates various composite implementations:
1. File system (directories and files)
2. UI components (panels containing panels and controls)
3. Organization hierarchy (departments with employees)
4. Graphic shapes (groups containing shapes and groups)
5. Menu systems (menus with items and submenus)
6. DOM tree structure (HTML elements)

Key Learning Points:
- Composite pattern treats individual and composite objects uniformly
- Tree structures where leaves and branches have same interface
- Enables recursive composition
- Simplifies client code by treating all objects the same
- Natural way to represent hierarchical structures
- Good for recursive algorithms on tree structures
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from enum import Enum


# ============================================================================
# 1. FILE SYSTEM - FILES AND DIRECTORIES
# ============================================================================

class FileSystemComponent(ABC):
    """Abstract base class for file system components (files and directories)."""

    @abstractmethod
    def get_size(self) -> int:
        """Get size in bytes."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get component name."""
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> None:
        """Display component in tree format."""
        pass


class File(FileSystemComponent):
    """Leaf - represents a file."""

    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size

    def get_size(self) -> int:
        return self.size

    def get_name(self) -> str:
        return self.name

    def display(self, indent: int = 0) -> None:
        print("  " * indent + f"[FILE] {self.name} ({self.size} bytes)")


class Directory(FileSystemComponent):
    """Composite - represents a directory."""

    def __init__(self, name: str):
        self.name = name
        self.children: List[FileSystemComponent] = []

    def add(self, component: FileSystemComponent) -> None:
        """Add file or subdirectory."""
        self.children.append(component)
        print(f"Added {component.get_name()} to {self.name}")

    def remove(self, component: FileSystemComponent) -> None:
        """Remove file or subdirectory."""
        if component in self.children:
            self.children.remove(component)
            print(f"Removed {component.get_name()} from {self.name}")

    def get_size(self) -> int:
        """Get total size of directory and all contents."""
        total = 0
        for child in self.children:
            total += child.get_size()
        return total

    def get_name(self) -> str:
        return self.name

    def display(self, indent: int = 0) -> None:
        """Display directory tree."""
        print("  " * indent + f"[DIR] {self.name}/")
        for child in self.children:
            child.display(indent + 1)

    def get_children(self) -> List[FileSystemComponent]:
        """Get all children."""
        return self.children


# ============================================================================
# 2. UI COMPONENTS - PANELS, BUTTONS, LABELS
# ============================================================================

class UIComponent(ABC):
    """Abstract base class for UI components."""

    @abstractmethod
    def render(self) -> None:
        """Render the component."""
        pass

    @abstractmethod
    def get_width(self) -> int:
        """Get component width."""
        pass

    @abstractmethod
    def get_height(self) -> int:
        """Get component height."""
        pass


class Button(UIComponent):
    """Leaf - represents a button."""

    def __init__(self, label: str):
        self.label = label

    def render(self) -> None:
        print(f"  [Button: {self.label}]")

    def get_width(self) -> int:
        return len(self.label) + 4

    def get_height(self) -> int:
        return 1


class Label(UIComponent):
    """Leaf - represents a label."""

    def __init__(self, text: str):
        self.text = text

    def render(self) -> None:
        print(f"  {self.text}")

    def get_width(self) -> int:
        return len(self.text)

    def get_height(self) -> int:
        return 1


class TextInput(UIComponent):
    """Leaf - represents a text input."""

    def __init__(self, placeholder: str = "Enter text"):
        self.placeholder = placeholder

    def render(self) -> None:
        print(f"  [____{self.placeholder}____]")

    def get_width(self) -> int:
        return 20

    def get_height(self) -> int:
        return 1


class Panel(UIComponent):
    """Composite - represents a container for UI components."""

    def __init__(self, title: str = "Panel"):
        self.title = title
        self.children: List[UIComponent] = []

    def add(self, component: UIComponent) -> None:
        """Add component to panel."""
        self.children.append(component)

    def remove(self, component: UIComponent) -> None:
        """Remove component from panel."""
        if component in self.children:
            self.children.remove(component)

    def render(self) -> None:
        """Render panel and all children."""
        print(f"+-------- {self.title} --------+")
        for child in self.children:
            child.render()
        print("+--------------------------------+")

    def get_width(self) -> int:
        """Get width as max child width + borders."""
        if not self.children:
            return 32
        return max(child.get_width() for child in self.children) + 4

    def get_height(self) -> int:
        """Get height as sum of child heights + borders."""
        return sum(child.get_height() for child in self.children) + 2


# ============================================================================
# 3. ORGANIZATION HIERARCHY - DEPARTMENTS AND EMPLOYEES
# ============================================================================

class OrganizationComponent(ABC):
    """Abstract base class for organization components."""

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_salary(self) -> float:
        """Get total salary."""
        pass

    @abstractmethod
    def get_employee_count(self) -> int:
        """Get total employee count."""
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> None:
        """Display organization structure."""
        pass


class Employee(OrganizationComponent):
    """Leaf - represents an employee."""

    def __init__(self, name: str, title: str, salary: float):
        self.name = name
        self.title = title
        self.salary = salary

    def get_name(self) -> str:
        return self.name

    def get_salary(self) -> float:
        return self.salary

    def get_employee_count(self) -> int:
        return 1

    def display(self, indent: int = 0) -> None:
        print("  " * indent + f"[Employee] {self.name} - {self.title} (${self.salary:,.2f})")


class Department(OrganizationComponent):
    """Composite - represents a department."""

    def __init__(self, name: str):
        self.name = name
        self.members: List[OrganizationComponent] = []

    def add_member(self, member: OrganizationComponent) -> None:
        """Add employee or subdepartment."""
        self.members.append(member)

    def remove_member(self, member: OrganizationComponent) -> None:
        """Remove employee or subdepartment."""
        if member in self.members:
            self.members.remove(member)

    def get_name(self) -> str:
        return self.name

    def get_salary(self) -> float:
        """Get total salary of all members."""
        total = 0
        for member in self.members:
            total += member.get_salary()
        return total

    def get_employee_count(self) -> int:
        """Get total number of employees."""
        count = 0
        for member in self.members:
            count += member.get_employee_count()
        return count

    def display(self, indent: int = 0) -> None:
        """Display department structure."""
        print("  " * indent + f"[Department] {self.name}")
        print("  " * indent + f"  Total Salary: ${self.get_salary():,.2f}")
        print("  " * indent + f"  Employee Count: {self.get_employee_count()}")
        for member in self.members:
            member.display(indent + 1)


# ============================================================================
# 4. GRAPHIC SHAPES - INDIVIDUAL SHAPES AND GROUPS
# ============================================================================

class Shape(ABC):
    """Abstract base class for shapes."""

    @abstractmethod
    def draw(self) -> None:
        """Draw the shape."""
        pass

    @abstractmethod
    def move(self, x: int, y: int) -> None:
        """Move the shape."""
        pass

    @abstractmethod
    def get_area(self) -> float:
        """Get shape area."""
        pass


class Circle(Shape):
    """Leaf - represents a circle."""

    def __init__(self, radius: float):
        self.radius = radius

    def draw(self) -> None:
        print(f"  Drawing circle with radius {self.radius}")

    def move(self, x: int, y: int) -> None:
        print(f"  Moving circle to ({x}, {y})")

    def get_area(self) -> float:
        return 3.14159 * self.radius * self.radius


class Rectangle(Shape):
    """Leaf - represents a rectangle."""

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def draw(self) -> None:
        print(f"  Drawing rectangle {self.width}x{self.height}")

    def move(self, x: int, y: int) -> None:
        print(f"  Moving rectangle to ({x}, {y})")

    def get_area(self) -> float:
        return self.width * self.height


class ShapeGroup(Shape):
    """Composite - represents a group of shapes."""

    def __init__(self, name: str = "Group"):
        self.name = name
        self.shapes: List[Shape] = []

    def add_shape(self, shape: Shape) -> None:
        """Add shape to group."""
        self.shapes.append(shape)

    def remove_shape(self, shape: Shape) -> None:
        """Remove shape from group."""
        if shape in self.shapes:
            self.shapes.remove(shape)

    def draw(self) -> None:
        """Draw all shapes in group."""
        print(f"Drawing {self.name}:")
        for shape in self.shapes:
            shape.draw()

    def move(self, x: int, y: int) -> None:
        """Move all shapes in group."""
        print(f"Moving {self.name} to ({x}, {y}):")
        for shape in self.shapes:
            shape.move(x, y)

    def get_area(self) -> float:
        """Get total area of all shapes."""
        total = 0
        for shape in self.shapes:
            total += shape.get_area()
        return total


# ============================================================================
# 5. MENU SYSTEM - MENU ITEMS AND SUBMENUS
# ============================================================================

class MenuItem(ABC):
    """Abstract base class for menu items."""

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> None:
        pass

    @abstractmethod
    def execute(self) -> None:
        pass


class Command(MenuItem):
    """Leaf - represents a command (executable menu item)."""

    def __init__(self, name: str, action: callable):
        self.name = name
        self.action = action

    def get_name(self) -> str:
        return self.name

    def display(self, indent: int = 0) -> None:
        print("  " * indent + f"[Cmd] {self.name}")

    def execute(self) -> None:
        print(f"Executing: {self.name}")
        if self.action:
            self.action()


class Menu(MenuItem):
    """Composite - represents a menu with items and submenus."""

    def __init__(self, name: str):
        self.name = name
        self.items: List[MenuItem] = []

    def add_item(self, item: MenuItem) -> None:
        """Add item or submenu."""
        self.items.append(item)

    def remove_item(self, item: MenuItem) -> None:
        """Remove item or submenu."""
        if item in self.items:
            self.items.remove(item)

    def get_name(self) -> str:
        return self.name

    def display(self, indent: int = 0) -> None:
        """Display menu structure."""
        print("  " * indent + f"[Menu] {self.name}")
        for item in self.items:
            item.display(indent + 1)

    def execute(self) -> None:
        """Execute menu (display it)."""
        self.display()


# ============================================================================
# 6. ITERATOR FOR TREE TRAVERSAL
# ============================================================================

def traverse_file_system(component: FileSystemComponent, action: callable = None) -> None:
    """Traverse file system tree."""
    if action:
        action(component)

    if isinstance(component, Directory):
        for child in component.get_children():
            traverse_file_system(child, action)


def calculate_total_size(root: FileSystemComponent) -> int:
    """Calculate total size in file system tree."""
    if isinstance(root, File):
        return root.get_size()

    if isinstance(root, Directory):
        total = 0
        for child in root.get_children():
            total += calculate_total_size(child)
        return total

    return 0


def find_largest_file(root: FileSystemComponent) -> Optional[File]:
    """Find largest file in tree."""
    largest = None

    if isinstance(root, File):
        return root

    if isinstance(root, Directory):
        for child in root.get_children():
            found = find_largest_file(child)
            if found and (largest is None or found.get_size() > largest.get_size()):
                largest = found

    return largest


# ============================================================================
# 7. DEMONSTRATION
# ============================================================================

def demo_file_system():
    """Demonstrate file system composite pattern."""
    print("\n" + "="*60)
    print("COMPOSITE PATTERN - FILE SYSTEM EXAMPLE")
    print("="*60)

    # Create file system
    root = Directory("root")

    documents = Directory("Documents")
    documents.add(File("resume.pdf", 512000))
    documents.add(File("cover_letter.docx", 256000))

    photos = Directory("Photos")
    photos.add(File("photo1.jpg", 2048000))
    photos.add(File("photo2.jpg", 1536000))

    vacation = Directory("Vacation")
    vacation.add(File("beach.jpg", 3072000))
    vacation.add(File("mountain.jpg", 2560000))
    photos.add(vacation)

    root.add(documents)
    root.add(photos)
    root.add(File("readme.txt", 1024))

    # Display tree
    print("\nFile System Structure:")
    root.display()

    # Calculate total size
    print(f"\nTotal size: {root.get_size()} bytes ({root.get_size() / (1024*1024):.2f} MB)")

    # Find largest file
    largest = find_largest_file(root)
    if largest:
        print(f"Largest file: {largest.get_name()} ({largest.get_size()} bytes)")


def demo_ui_components():
    """Demonstrate UI component composite pattern."""
    print("\n" + "="*60)
    print("COMPOSITE PATTERN - UI COMPONENTS EXAMPLE")
    print("="*60)

    # Create login form
    form = Panel("Login Form")
    form.add(Label("Username:"))
    form.add(TextInput("Enter username"))
    form.add(Label("Password:"))
    form.add(TextInput("Enter password"))
    form.add(Button("Login"))
    form.add(Button("Cancel"))

    print("\nUI Component Tree:")
    form.render()

    print(f"\nForm dimensions: {form.get_width()}x{form.get_height()}")


def demo_organization_hierarchy():
    """Demonstrate organization hierarchy composite pattern."""
    print("\n" + "="*60)
    print("COMPOSITE PATTERN - ORGANIZATION HIERARCHY EXAMPLE")
    print("="*60)

    # Create organization
    company = Department("Tech Corp")

    engineering = Department("Engineering")
    engineering.add_member(Employee("Alice", "Senior Engineer", 120000))
    engineering.add_member(Employee("Bob", "Engineer", 80000))
    engineering.add_member(Employee("Charlie", "Junior Engineer", 50000))

    sales = Department("Sales")
    sales.add_member(Employee("Diana", "Sales Manager", 100000))
    sales.add_member(Employee("Eve", "Sales Rep", 60000))

    company.add_member(engineering)
    company.add_member(sales)
    company.add_member(Employee("Frank", "CEO", 200000))

    print("\nOrganization Structure:")
    company.display()


def demo_graphic_shapes():
    """Demonstrate graphic shapes composite pattern."""
    print("\n" + "="*60)
    print("COMPOSITE PATTERN - GRAPHIC SHAPES EXAMPLE")
    print("="*60)

    # Create shape composition
    main_group = ShapeGroup("Main Scene")

    # Create a car (group of shapes)
    car = ShapeGroup("Car")
    car.add_shape(Rectangle(4, 2))
    car.add_shape(Circle(0.5))
    car.add_shape(Circle(0.5))

    # Create trees
    trees = ShapeGroup("Trees")
    trees.add_shape(Circle(2))
    trees.add_shape(Circle(2.5))

    main_group.add_shape(car)
    main_group.add_shape(trees)

    print("\nDrawing composite scene:")
    main_group.draw()

    print(f"\nTotal area: {main_group.get_area():.2f}")


def demo_menu_system():
    """Demonstrate menu system composite pattern."""
    print("\n" + "="*60)
    print("COMPOSITE PATTERN - MENU SYSTEM EXAMPLE")
    print("="*60)

    # Create menu structure
    main_menu = Menu("Main Menu")

    file_menu = Menu("File")
    file_menu.add_item(Command("New", lambda: print("  Creating new file")))
    file_menu.add_item(Command("Open", lambda: print("  Opening file")))
    file_menu.add_item(Command("Save", lambda: print("  Saving file")))

    edit_menu = Menu("Edit")
    edit_menu.add_item(Command("Undo", lambda: print("  Undoing")))
    edit_menu.add_item(Command("Redo", lambda: print("  Redoing")))
    edit_menu.add_item(Command("Cut", lambda: print("  Cutting")))
    edit_menu.add_item(Command("Copy", lambda: print("  Copying")))
    edit_menu.add_item(Command("Paste", lambda: print("  Pasting")))

    help_menu = Menu("Help")
    help_menu.add_item(Command("About", lambda: print("  Showing about dialog")))
    help_menu.add_item(Command("Documentation", lambda: print("  Opening docs")))

    main_menu.add_item(file_menu)
    main_menu.add_item(edit_menu)
    main_menu.add_item(help_menu)

    print("\nMenu Structure:")
    main_menu.display()


def demo_composite_pattern_benefits():
    """Demonstrate composite pattern benefits."""
    print("\n" + "="*60)
    print("COMPOSITE PATTERN - BENEFITS")
    print("="*60)

    print("""
KEY BENEFITS:

1. UNIFORM INTERFACE
   - Treat individual and composite objects the same way
   - Single interface for all tree nodes
   - Simplifies client code

2. TREE STRUCTURES
   - Natural way to represent hierarchical data
   - Recursive composition
   - Flexible depth

3. SIMPLIFIED CLIENT CODE
   - No need to distinguish between leaves and composites
   - Same operations on all components
   - Polymorphic behavior

4. EASY TO ADD NODES
   - Add new leaf or composite types
   - Existing code continues to work
   - Open/Closed Principle

5. RECURSIVE ALGORITHMS
   - Natural implementation of recursive algorithms
   - Tree traversal
   - Aggregate operations (sum, max, etc.)

6. PART-WHOLE HIERARCHIES
   - Express complex structures as combinations of parts
   - Each part has same interface as whole
   - Composability at different levels

EXAMPLES:
- File systems (directories with files)
- UI frameworks (panels with controls)
- Organization charts (departments with employees)
- Graphics systems (groups with shapes)
- DOM trees (elements with children)
- Menu systems (menus with items)
    """)


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

"""
KEY TAKEAWAYS - COMPOSITE PATTERN:

1. WHEN TO USE:
   - Part-whole hierarchies
   - Tree structures (files, UI, organization, etc.)
   - Want uniform interface for single and composite objects
   - Need recursive composition

2. STRUCTURE:
   - Component (abstract base)
   - Leaf (concrete, no children)
   - Composite (can have children)
   - Client works through Component interface

3. RECURSIVE COMPOSITION:
   - Composites contain Components
   - Components can be Leaves or Composites
   - Unlimited nesting depth

4. TYPE SAFETY:
   - Can't enforce type constraints (what children allowed)
   - Either check types at runtime or trust client
   - Trade-off between flexibility and safety

5. ALTERNATIVES:
   - Transparent composite (all classes implement same interface)
   - Safe composite (check type before treating as composite)
   - Iterator for tree traversal

6. REAL WORLD EXAMPLES:
   - File systems (directories, files)
   - UI frameworks (panels, buttons, labels)
   - DOM API (elements with children)
   - Graphics systems (groups, shapes)
   - Organization charts (departments, employees)
   - Menu systems (menus, items)
   - Company structures (divisions, departments)

7. TRAVERSAL PATTERNS:
   - Depth-first (recursive)
   - Breadth-first (queue-based)
   - In-order, pre-order, post-order
   - Can use separate iterator

8. COMPOSITE vs DECORATOR:
   - Composite: Hierarchical tree structure
   - Decorator: Linear wrapper chain
   - Composite for collections, Decorator for enhancement
"""


if __name__ == "__main__":
    demo_file_system()
    demo_ui_components()
    demo_organization_hierarchy()
    demo_graphic_shapes()
    demo_menu_system()
    demo_composite_pattern_benefits()

    print("\n" + "="*60)
    print("All Composite Pattern examples completed!")
    print("="*60)
