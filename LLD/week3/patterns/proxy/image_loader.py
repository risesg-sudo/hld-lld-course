"""Proxy Pattern - Image Loading Example"""

from abc import ABC, abstractmethod
import time


class Image(ABC):
    @abstractmethod
    def display(self):
        pass


class RealImage(Image):
    """Expensive object - loads from disk."""

    def __init__(self, filename):
        self.filename = filename
        self._load()

    def _load(self):
        print(f"Loading {self.filename} from disk... (expensive operation)")
        time.sleep(0.5)  # Simulate slow loading

    def display(self):
        print(f"Displaying {self.filename}")


class ImageProxy(Image):
    """Virtual proxy - defers loading until needed."""

    def __init__(self, filename):
        self.filename = filename
        self._image = None  # Not loaded yet

    def display(self):
        if self._image is None:
            print(f"First access - loading image now...")
            self._image = RealImage(self.filename)
        self._image.display()


if __name__ == "__main__":
    print("PROXY PATTERN DEMONSTRATION")
    print("="*60)

    print("\nWithout Proxy (loads immediately):")
    img1 = RealImage("photo1.jpg")
    img1.display()

    print("\n" + "-"*60)

    print("\nWith Proxy (loads on first access):")
    img2 = ImageProxy("photo2.jpg")
    print("Proxy created (image not loaded yet)")
    print("Calling display()...")
    img2.display()
    print("\nCalling display() again...")
    img2.display()  # Uses already loaded image

    print("\n" + "="*60)
    print("Key Observations:")
    print("  - Proxy delays loading until display() called")
    print("  - Subsequent calls use loaded image")
    print("  - Client code identical for proxy and real image")
    print("  - Improves startup performance")
    print("="*60)
