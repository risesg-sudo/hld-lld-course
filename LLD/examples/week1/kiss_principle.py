"""
KISS PRINCIPLE (Keep It Simple, Stupid)
========================================

Core Concept:
The KISS principle states that most systems work best if they are kept simple
rather than made complicated. Therefore, simplicity should be a key goal in
design, and unnecessary complexity should be avoided.

Benefits:
- Easier to understand and maintain
- Fewer bugs and edge cases to handle
- Faster development and debugging
- Better team collaboration
- Easier to extend and modify

Real-world analogy:
A light switch is a simple interface that works; we don't need a complex
multi-page manual to turn on a light.
"""


# ============================================================================
# BAD EXAMPLE: Over-Engineering - Making Things Unnecessarily Complex
# ============================================================================

class BadInventorySystem:
    """
    This class demonstrates anti-pattern by over-engineering a simple solution.
    It uses unnecessary design patterns, abstract layers, and complexity.
    """

    def __init__(self):
        self.items = {}
        self.transaction_history = []
        self.state_watchers = []
        self.backup_queue = []

    def register_state_watcher(self, watcher):
        """Register observers for state changes."""
        self.state_watchers.append(watcher)

    def notify_watchers(self, event):
        """Notify all watchers of state change."""
        for watcher in self.state_watchers:
            watcher.update(event)

    def add_to_backup_queue(self, operation):
        """Add operation to backup queue."""
        self.backup_queue.append(operation)

    def process_backup_queue(self):
        """Process all queued operations."""
        for operation in self.backup_queue:
            operation()
        self.backup_queue.clear()

    def add_item(self, item_id: str, quantity: int, price: float):
        """
        Add item with excessive complexity:
        - State change notification
        - Backup queuing
        - Transaction logging
        - Multiple layers of abstraction
        """
        def backup_operation():
            """Backup operation to execute later."""
            self.items[item_id] = {"quantity": quantity, "price": price}

        self.add_to_backup_queue(backup_operation)
        self.process_backup_queue()

        transaction = {
            "operation": "ADD",
            "item_id": item_id,
            "quantity": quantity,
            "price": price,
            "timestamp": "2024-01-15T10:00:00Z"
        }
        self.transaction_history.append(transaction)

        event = {"type": "ITEM_ADDED", "item_id": item_id}
        self.notify_watchers(event)

    def get_item(self, item_id: str):
        """
        Retrieve item with unnecessary validation layers.
        """
        if not isinstance(item_id, str):
            raise TypeError("Item ID must be a string")

        if not item_id or len(item_id) == 0:
            raise ValueError("Item ID cannot be empty")

        if item_id not in self.items:
            raise KeyError(f"Item {item_id} not found in inventory")

        if self.items[item_id]["quantity"] < 0:
            raise RuntimeError("Invalid inventory state detected")

        return self.items[item_id]

    def remove_item(self, item_id: str):
        """Remove item with multiple layers of processing."""
        if item_id not in self.items:
            raise KeyError(f"Item {item_id} not found")

        def backup_operation():
            del self.items[item_id]

        self.add_to_backup_queue(backup_operation)
        self.process_backup_queue()

        self.transaction_history.append({
            "operation": "REMOVE",
            "item_id": item_id
        })

        self.notify_watchers({"type": "ITEM_REMOVED", "item_id": item_id})


def demo_bad_kiss():
    """Demonstrate over-engineered solution."""
    print("\n" + "="*70)
    print("BAD EXAMPLE: Over-Engineering (Not Following KISS)")
    print("="*70)

    inventory = BadInventorySystem()

    print("\n1. Adding item (with unnecessary complexity):")
    inventory.add_item("laptop_001", 10, 999.99)
    print("   ✓ Item added (with state watchers, backup queue, transactions)")

    print("\n2. Getting item:")
    item = inventory.get_item("laptop_001")
    print(f"   ✓ Retrieved: {item}")

    print("\nProblems:")
    print("  - Too many layers for a simple operation")
    print("  - Hard to understand what the code does")
    print("  - Difficult to debug and maintain")
    print("  - Overkill features that aren't needed")


# ============================================================================
# GOOD EXAMPLE: Simple and Direct Implementation
# ============================================================================

class GoodInventorySystem:
    """
    This class demonstrates the KISS principle with a simple, direct implementation.
    It does what's needed without unnecessary complexity.
    """

    def __init__(self):
        self.items = {}

    def add_item(self, item_id: str, quantity: int, price: float) -> None:
        """Add item to inventory - simple and straightforward."""
        self.items[item_id] = {"quantity": quantity, "price": price}
        print(f"Added {item_id}: {quantity} units @ ${price}")

    def get_item(self, item_id: str) -> dict:
        """Get item from inventory - direct access."""
        if item_id not in self.items:
            raise KeyError(f"Item {item_id} not found")
        return self.items[item_id]

    def remove_item(self, item_id: str) -> None:
        """Remove item from inventory - simple deletion."""
        if item_id in self.items:
            del self.items[item_id]
            print(f"Removed {item_id}")
        else:
            raise KeyError(f"Item {item_id} not found")

    def update_quantity(self, item_id: str, quantity: int) -> None:
        """Update item quantity."""
        if item_id not in self.items:
            raise KeyError(f"Item {item_id} not found")
        self.items[item_id]["quantity"] = quantity

    def get_all_items(self) -> dict:
        """Get all items - simple dictionary return."""
        return self.items.copy()


def demo_good_kiss():
    """Demonstrate simple, maintainable solution."""
    print("\n" + "="*70)
    print("GOOD EXAMPLE: Following KISS Principle")
    print("="*70)

    inventory = GoodInventorySystem()

    print("\n1. Adding items:")
    inventory.add_item("laptop_001", 10, 999.99)
    inventory.add_item("mouse_001", 50, 29.99)
    inventory.add_item("keyboard_001", 30, 79.99)

    print("\n2. Getting an item:")
    item = inventory.get_item("laptop_001")
    print(f"   ✓ Retrieved laptop_001: {item}")

    print("\n3. Updating quantity:")
    inventory.update_quantity("laptop_001", 8)
    print(f"   ✓ Updated laptop_001 quantity to 8")

    print("\n4. Viewing all items:")
    all_items = inventory.get_all_items()
    for item_id, details in all_items.items():
        print(f"   - {item_id}: {details['quantity']} units @ ${details['price']}")

    print("\n5. Removing item:")
    inventory.remove_item("mouse_001")

    print("\nBenefits:")
    print("  - Easy to understand at a glance")
    print("  - Quick to implement and test")
    print("  - Simple to debug and maintain")
    print("  - Scales without added complexity")


# ============================================================================
# COMPARISON: String Processing
# ============================================================================

def bad_string_reverse(text: str) -> str:
    """
    Over-complicated string reversal with unnecessary abstractions.
    """
    # Create a complex pipeline
    class CharacterProcessor:
        def __init__(self, text):
            self.text = text
            self.characters = list(text)

        def reverse(self):
            return ''.join(reversed(self.characters))

    processor = CharacterProcessor(text)
    return processor.reverse()


def good_string_reverse(text: str) -> str:
    """
    Simple and direct string reversal.
    """
    return text[::-1]


def demo_string_comparison():
    """Compare complex vs simple string reversal."""
    print("\n" + "="*70)
    print("COMPARISON: String Reversal")
    print("="*70)

    test_string = "Hello World"

    print(f"\nOriginal: {test_string}")
    print(f"Bad method result: {bad_string_reverse(test_string)}")
    print(f"Good method result: {good_string_reverse(test_string)}")

    print("\nThe good method is:")
    print("  - Shorter")
    print("  - More readable")
    print("  - More Pythonic")
    print("  - Same result with less code")


# ============================================================================
# REAL-WORLD EXAMPLE: Calculator
# ============================================================================

class SimpleCalculator:
    """
    Real-world example: Simple calculator following KISS principle.
    """

    @staticmethod
    def add(a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Subtract two numbers."""
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    @staticmethod
    def calculate(expression: str) -> float:
        """
        Simple expression evaluator.
        Handles: "5 + 3", "10 - 2", "4 * 3", "20 / 4"
        """
        try:
            result = eval(expression)  # Simple but effective for basic math
            return result
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")


def demo_calculator():
    """Demonstrate simple calculator."""
    print("\n" + "="*70)
    print("REAL-WORLD EXAMPLE: Simple Calculator")
    print("="*70)

    calc = SimpleCalculator()

    print(f"\n5 + 3 = {calc.add(5, 3)}")
    print(f"10 - 2 = {calc.subtract(10, 2)}")
    print(f"4 * 3 = {calc.multiply(4, 3)}")
    print(f"20 / 4 = {calc.divide(20, 4)}")

    print(f"\nExpression '(5 + 3) * 2 = {calc.calculate('(5 + 3) * 2')}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("KISS PRINCIPLE EXAMPLES")
    print("="*70)

    # Bad example
    demo_bad_kiss()

    # Good example
    demo_good_kiss()

    # Comparison
    demo_string_comparison()

    # Real-world example
    demo_calculator()

    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. Start with the simplest solution that works
2. Avoid premature optimization
3. Don't add features you don't need yet
4. Avoid over-engineering for edge cases
5. Write code that is easy to understand
6. Use built-in functions and libraries when appropriate
7. Simplicity often leads to better performance
8. Complex code is harder to test and maintain
    """)
