# Interface Segregation Principle (ISP)

## The Concept

Clients should not be forced to depend on interfaces they don't use.

## The Problem

:::multilang
```python
from abc import ABC, abstractmethod

class Worker(ABC):
    @abstractmethod
    def work(self): pass
    @abstractmethod
    def eat(self): pass

class Robot(Worker):
    def work(self): pass
    def eat(self): raise NotImplementedError  # Robots don't eat!
```

```cpp
#include <stdexcept>

class Worker {
public:
    virtual ~Worker() = default;
    virtual void work() = 0;
    virtual void eat() = 0;
};

class Robot : public Worker {
public:
    void work() override { /* work implementation */ }
    void eat() override {
        throw std::runtime_error("Robots don't eat!");  // Forced to implement!
    }
};
```

```java
public interface Worker {
    void work();
    void eat();
}

public class Robot implements Worker {
    @Override
    public void work() { /* work implementation */ }

    @Override
    public void eat() {
        throw new UnsupportedOperationException("Robots don't eat!");  // Forced to implement!
    }
}
```
:::

Robot forced to implement unused method!

## The Solution

Split large interfaces into smaller, specific ones.

:::multilang
```python
from abc import ABC, abstractmethod

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

```cpp
class Workable {
public:
    virtual ~Workable() = default;
    virtual void work() = 0;
};

class Eatable {
public:
    virtual ~Eatable() = default;
    virtual void eat() = 0;
};

class Human : public Workable, public Eatable {
public:
    void work() override { /* work implementation */ }
    void eat() override { /* eat implementation */ }
};

class Robot : public Workable {
public:
    void work() override { /* work implementation */ }
    // No need to implement eat()!
};
```

```java
public interface Workable {
    void work();
}

public interface Eatable {
    void eat();
}

public class Human implements Workable, Eatable {
    @Override
    public void work() { /* work implementation */ }

    @Override
    public void eat() { /* eat implementation */ }
}

public class Robot implements Workable {
    @Override
    public void work() { /* work implementation */ }
    // No need to implement eat()!
}
```
:::

## Key Takeaways

- Many specific interfaces better than one general
- Classes implement only what they need
- Reduces coupling
- More flexible design
