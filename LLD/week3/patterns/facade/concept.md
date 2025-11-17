# Facade Pattern

## The Hook

To watch a movie in your home theater, you need to: turn on projector, set to wide screen mode, turn on sound system, set volume, turn on DVD player, play movie, dim lights, lower screen. That's 8 steps.

You just want to watch a movie. You don't care about the sequence of operations on different subsystems. Can you have one button that does it all?

This is what facade provides: a simplified interface to a complex subsystem.

## The Problem

**Complex Subsystems**: Multiple classes with many methods. Client needs to interact with many components.

**Tight Coupling**: Client knows about all subsystem classes. Changes to subsystem affect all clients.

**Common Use Cases**: 90% of the time, clients use the same sequence of operations. Why repeat the sequence everywhere?

**Difficult to Use**: Learning curve for using subsystem correctly.

The fundamental problem: subsystems are powerful but complex. Most clients need simple operations.

## The Solution

Facade provides simple methods that coordinate subsystem components.

**Without Facade**:
```python
def watch_movie():
    lights.dim(10)
    screen.down()
    projector.on()
    projector.wide_screen_mode()
    sound.on()
    sound.set_volume(75)
    dvd.on()
    dvd.play("Movie")
```

**With Facade**:
```python
class HomeTheaterFacade:
    def __init__(self, lights, screen, projector, sound, dvd):
        self.lights = lights
        self.screen = screen
        self.projector = projector
        self.sound = sound
        self.dvd = dvd

    def watch_movie(self, movie):
        self.lights.dim(10)
        self.screen.down()
        self.projector.on()
        self.projector.wide_screen_mode()
        self.sound.on()
        self.sound.set_volume(75)
        self.dvd.on()
        self.dvd.play(movie)
```

**Client**:
```python
theater.watch_movie("The Matrix")  # One call!
```

## Code Example

See `/home/user/hld-lld-course/LLD/week3/patterns/facade/home_theater.py`

## When to Use

Complex subsystems, simplify common use cases, decouple clients from subsystems, provide entry point to layered architecture.

## Trade-offs

**Gains**: Simplification, decoupling, convenience, single entry point
**Loses**: Can hide important functionality, facade can become god object

## Key Takeaways

1. Facade simplifies complex subsystem behind simple interface
2. Doesn't prevent direct access to subsystem
3. Coordinates multiple subsystem components
4. Different from adapter: simplifies vs makes compatible
5. Keep facade focused on common use cases
6. Don't hide all subsystem functionality
