# Bridge Pattern

## The Hook

You're building a graphics application that draws shapes. You have circles, squares, and triangles. You need to render them using OpenGL, Canvas, or SVG. Without thinking, you create: `OpenGLCircle`, `CanvasCircle`, `SVGCircle`, `OpenGLSquare`, `CanvasSquare`, `SVGSquare`... that's already 9 classes for 3 shapes and 3 renderers.

Add a fourth shape? 12 classes. Add a fourth renderer? 16 classes. Each new dimension multiplies the class count. This is the "Cartesian product problem"—two independent hierarchies creating exponential combinations.

How do you handle multiple dimensions of variation without class explosion?

## The Problem

**Multiple Axes of Variation**: Shapes vary (circle, square). Renderers vary (OpenGL, Canvas). These vary independently. Inheritance forces you to combine them: every shape-renderer pair needs a class.

**Rigid Coupling**: With inheritance, you must choose: inherit from Shape or inherit from Renderer? You can't have both hierarchies independent. Changes to one affect the other.

**Code Duplication**: `OpenGLCircle` and `CanvasCircle` share circle-drawing logic but duplicate it because they're in different inheritance branches.

The fundamental problem: when two things vary independently, inheritance couples them together.

## The Solution

Bridge separates abstraction (shapes) from implementation (renderers) using composition.

**Two Hierarchies**:
```
Abstraction (Shape) hierarchy:     Implementation (Renderer) hierarchy:
    Shape                              Renderer
    ├── Circle                         ├── OpenGLRenderer
    ├── Square                         ├── CanvasRenderer
    └── Triangle                       └── SVGRenderer
```

**Bridge Connection**:
```python
class Shape(ABC):
    def __init__(self, renderer: Renderer):
        self._renderer = renderer  # Bridge to implementation

    def draw(self):
        pass  # Uses self._renderer

class Circle(Shape):
    def draw(self):
        self._renderer.render_circle(self.x, self.y, self.radius)
```

**Flexible Combinations**:
```python
# Any shape with any renderer
opengl_circle = Circle(OpenGLRenderer(), 10, 10, 5)
canvas_circle = Circle(CanvasRenderer(), 10, 10, 5)
svg_square = Square(SVGRenderer(), 20, 20, 10)
```

**Class Count**:
- Without Bridge: 3 shapes × 3 renderers = 9 classes
- With Bridge: 3 shapes + 3 renderers = 6 classes

## Code Example

See `/home/user/hld-lld-course/LLD/week3/patterns/bridge/remote_control.py`

## When to Use

Multiple independent dimensions of variation, avoid Cartesian product problem, runtime implementation switching, platform-specific implementations.

## Trade-offs

**Gains**: Decoupling, independent variation, reduced classes, runtime flexibility
**Loses**: Extra complexity, indirection layer, requires upfront design

## Key Takeaways

1. Bridge separates abstraction from implementation via composition
2. Two hierarchies vary independently
3. Avoids class explosion from multiple variation axes
4. Choose bridge when you have N×M problem
5. Design pattern, not retrofitted like adapter
