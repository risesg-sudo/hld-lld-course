"""Facade Pattern - Home Theater Example"""


class Light:
    def dim(self, level):
        print(f"Lights dimmed to {level}%")


class Screen:
    def down(self):
        print("Screen going down")


class Projector:
    def on(self):
        print("Projector on")

    def wide_screen_mode(self):
        print("Projector in wide screen mode")


class SoundSystem:
    def on(self):
        print("Sound system on")

    def set_volume(self, volume):
        print(f"Volume set to {volume}")


class DVDPlayer:
    def on(self):
        print("DVD player on")

    def play(self, movie):
        print(f"Playing '{movie}'")


class HomeTheaterFacade:
    """Facade that simplifies home theater operations."""

    def __init__(self, light, screen, projector, sound, dvd):
        self.light = light
        self.screen = screen
        self.projector = projector
        self.sound = sound
        self.dvd = dvd

    def watch_movie(self, movie):
        """Simplified interface to watch movie."""
        print(f"\nStarting movie: {movie}")
        print("-" * 40)
        self.light.dim(10)
        self.screen.down()
        self.projector.on()
        self.projector.wide_screen_mode()
        self.sound.on()
        self.sound.set_volume(75)
        self.dvd.on()
        self.dvd.play(movie)
        print("-" * 40)
        print("Movie started - enjoy!")


if __name__ == "__main__":
    print("FACADE PATTERN DEMONSTRATION")
    print("="*60)

    # Create subsystem components
    light = Light()
    screen = Screen()
    projector = Projector()
    sound = SoundSystem()
    dvd = DVDPlayer()

    # Create facade
    theater = HomeTheaterFacade(light, screen, projector, sound, dvd)

    # Simple interface - one call does everything
    theater.watch_movie("The Matrix")

    print("\n" + "="*60)
    print("Key Observations:")
    print("  - One method call replaces 8 individual calls")
    print("  - Client decoupled from subsystem components")
    print("  - Can still access subsystem directly if needed")
    print("  - Facade coordinates complex operation sequence")
    print("="*60)
