# Liskov Substitution Principle (LSP)

## The Concept

Objects of a superclass should be replaceable with objects of subclasses without breaking the application.

## The Problem

```python
class Rectangle:
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h

class Square(Rectangle):
    def set_width(self, w):
        self.width = self.height = w  # Breaks expectation!
```

Square breaks Rectangle's contract!

## The Solution

Subclasses must honor parent's contract. If they can't, don't use inheritance.

```python
class Shape(ABC):
    @abstractmethod
    def area(self): pass

class Rectangle(Shape):
    def area(self): return width * height

class Square(Shape):
    def area(self): return side * side
```

## Key Takeaways

- Subclasses must fulfill parent's promises
- Don't violate parent's contract
- Use composition if IS-A doesn't hold
- Ensures polymorphism works correctly
