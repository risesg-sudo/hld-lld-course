# Dry Run: Facade Pattern

## Operation: theater.watch_movie("The Matrix")

**Call**: `HomeTheaterFacade.watch_movie("The Matrix")`

### Execution Sequence

Facade coordinates subsystem calls:

```
1. self.light.dim(10)
   → Light.dim(10)
   Output: "Lights dimmed to 10%"

2. self.screen.down()
   → Screen.down()
   Output: "Screen going down"

3. self.projector.on()
   → Projector.on()
   Output: "Projector on"

4. self.projector.wide_screen_mode()
   → Projector.wide_screen_mode()
   Output: "Projector in wide screen mode"

5. self.sound.on()
   → SoundSystem.on()
   Output: "Sound system on"

6. self.sound.set_volume(75)
   → SoundSystem.set_volume(75)
   Output: "Volume set to 75"

7. self.dvd.on()
   → DVDPlayer.on()
   Output: "DVD player on"

8. self.dvd.play("The Matrix")
   → DVDPlayer.play("The Matrix")
   Output: "Playing 'The Matrix'"
```

## Key: Coordination

**Without Facade**: Client makes 8 calls in correct order
**With Facade**: Client makes 1 call, facade handles order

Facade knows the correct sequence and encapsulates it. Client doesn't need to remember the steps.

## Not Just Delegation

Facade doesn't just delegate—it coordinates. It knows:
- Which components to call
- In what order
- With what parameters

This is the value: encapsulating complex orchestration behind simple interface.
