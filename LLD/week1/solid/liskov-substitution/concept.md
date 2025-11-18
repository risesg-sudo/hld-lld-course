# Liskov Substitution Principle (LSP)

## The Concept

Objects of a superclass should be replaceable with objects of subclasses without breaking the application.

## The Problem

:::multilang
```python
class Rectangle:
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h

class Square(Rectangle):
    def set_width(self, w):
        self.width = self.height = w  # Breaks expectation!
```

```cpp
class Rectangle {
protected:
    int width, height;
public:
    void setWidth(int w) { width = w; }
    void setHeight(int h) { height = h; }
};

class Square : public Rectangle {
public:
    void setWidth(int w) override {
        width = height = w;  // Breaks expectation!
    }
};
```

```java
public class Rectangle {
    protected int width, height;

    public void setWidth(int w) { this.width = w; }
    public void setHeight(int h) { this.height = h; }
}

public class Square extends Rectangle {
    @Override
    public void setWidth(int w) {
        this.width = this.height = w;  // Breaks expectation!
    }
}
```
:::

Square breaks Rectangle's contract!

## The Solution

Subclasses must honor parent's contract. If they can't, don't use inheritance.

:::multilang
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self): return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self): return self.side * self.side
```

```cpp
#include <memory>

class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
};

class Rectangle : public Shape {
private:
    double width, height;
public:
    Rectangle(double w, double h) : width(w), height(h) {}
    double area() const override { return width * height; }
};

class Square : public Shape {
private:
    double side;
public:
    Square(double s) : side(s) {}
    double area() const override { return side * side; }
};
```

```java
public abstract class Shape {
    public abstract double area();
}

public class Rectangle extends Shape {
    private double width, height;

    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }

    @Override
    public double area() { return width * height; }
}

public class Square extends Shape {
    private double side;

    public Square(double side) {
        this.side = side;
    }

    @Override
    public double area() { return side * side; }
}
```
:::

## Key Takeaways

- Subclasses must fulfill parent's promises
- Don't violate parent's contract
- Use composition if IS-A doesn't hold
- Ensures polymorphism works correctly
