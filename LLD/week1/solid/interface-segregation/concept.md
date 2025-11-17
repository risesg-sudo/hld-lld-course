# Interface Segregation Principle (ISP)

## The Concept

Clients should not be forced to depend on interfaces they don't use.

## The Problem

```python
class Worker(ABC):
    @abstractmethod
    def work(self): pass
    @abstractmethod
    def eat(self): pass

class Robot(Worker):
    def work(self): pass
    def eat(self): raise NotImplementedError  # Robots don't eat!
```

Robot forced to implement unused method!

## The Solution

Split large interfaces into smaller, specific ones.

```python
class Workable(ABC):
    @abstractmethod
    def work(self): pass

class Eatable(ABC):
    @abstractmethod
    def eat(self): pass

class Human(Workable, Eatable):
    def work(self): pass
    def eat(self): pass

class Robot(Workable):
    def work(self): pass
```

## Key Takeaways

- Many specific interfaces better than one general
- Classes implement only what they need
- Reduces coupling
- More flexible design
