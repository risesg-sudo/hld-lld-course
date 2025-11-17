"""
KISS Principle Example: Inventory Management
Demonstrates simple solution vs over-engineered solution
"""

# BAD: Over-engineered with unnecessary complexity
class ComplexInventory:
    def __init__(self):
        self.items = {}
        self.observers = []
        self.backup_queue = []
        
    def register_observer(self, observer):
        self.observers.append(observer)
        
    def notify_observers(self, event):
        for observer in self.observers:
            observer.update(event)
            
    def add_to_queue(self, operation):
        self.backup_queue.append(operation)
        
    def process_queue(self):
        for op in self.backup_queue:
            op()
        self.backup_queue.clear()
        
    def add_item(self, item_id, quantity):
        def backup_operation():
            self.items[item_id] = quantity
        self.add_to_queue(backup_operation)
        self.process_queue()
        self.notify_observers("ITEM_ADDED")
        print(f"Complex: Added {item_id} (with observers, queue, etc.)")


# GOOD: Simple, clear implementation
class SimpleInventory:
    def __init__(self):
        self.items = {}
        
    def add_item(self, item_id, quantity):
        self.items[item_id] = quantity
        print(f"Simple: Added {item_id}")
        
    def get_item(self, item_id):
        return self.items.get(item_id, 0)
        
    def remove_item(self, item_id):
        if item_id in self.items:
            del self.items[item_id]


if __name__ == "__main__":
    print("=== KISS Principle Demo ===\n")
    
    print("Complex (Over-Engineered):")
    complex_inv = ComplexInventory()
    complex_inv.add_item("laptop", 10)
    print(f"Lines of code: ~40\n")
    
    print("Simple (KISS):")
    simple_inv = SimpleInventory()
    simple_inv.add_item("laptop", 10)
    print(f"Lines of code: ~10")
    print("\nBoth do the same thing. Simple is better!")
