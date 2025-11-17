from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): pass

class Rectangle(Shape):
    def __init__(self, w, h):
        self.width, self.height = w, h
    def area(self): return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self): return self.side ** 2

def print_area(shape: Shape):
    print(f"Area: {shape.area()}")

if __name__ == "__main__":
    shapes = [Rectangle(4, 5), Square(4)]
    for shape in shapes:
        print_area(shape)  # Works for both!
