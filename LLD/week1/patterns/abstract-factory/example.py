"""
Abstract Factory Pattern: UI Components
Creates families of related UI components
"""
from abc import ABC, abstractmethod

# Abstract products
class Button(ABC):
    @abstractmethod
    def click(self): pass

class Checkbox(ABC):
    @abstractmethod
    def toggle(self): pass

# Windows family
class WindowsButton(Button):
    def click(self): return "Windows button clicked"

class WindowsCheckbox(Checkbox):
    def toggle(self): return "Windows checkbox toggled"

# Mac family
class MacButton(Button):
    def click(self): return "Mac button clicked"

class MacCheckbox(Checkbox):
    def toggle(self): return "Mac checkbox toggled"

# Abstract factory
class UIFactory(ABC):
    @abstractmethod
    def create_button(self): pass
    @abstractmethod
    def create_checkbox(self): pass

# Concrete factories
class WindowsFactory(UIFactory):
    def create_button(self): return WindowsButton()
    def create_checkbox(self): return WindowsCheckbox()

class MacFactory(UIFactory):
    def create_button(self): return MacButton()
    def create_checkbox(self): return MacCheckbox()

# Client code
class Application:
    def __init__(self, factory: UIFactory):
        self.button = factory.create_button()
        self.checkbox = factory.create_checkbox()
        
    def render(self):
        print(self.button.click())
        print(self.checkbox.toggle())

if __name__ == "__main__":
    print("=== Abstract Factory Demo ===\n")
    
    print("Windows UI:")
    app1 = Application(WindowsFactory())
    app1.render()
    
    print("\nMac UI:")
    app2 = Application(MacFactory())
    app2.render()
    
    print("\nAll components match their platform!")
