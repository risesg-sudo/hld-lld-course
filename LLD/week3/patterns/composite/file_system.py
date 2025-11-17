"""Composite Pattern - File System Example"""

from abc import ABC, abstractmethod
from typing import List


class FileSystemComponent(ABC):
    @abstractmethod
    def get_size(self) -> int:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def display(self, indent: int = 0):
        pass


class File(FileSystemComponent):
    """Leaf - individual file."""

    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size

    def get_size(self) -> int:
        return self.size

    def get_name(self) -> str:
        return self.name

    def display(self, indent: int = 0):
        print("  " * indent + f"[FILE] {self.name} ({self.size} bytes)")


class Directory(FileSystemComponent):
    """Composite - contains files and directories."""

    def __init__(self, name: str):
        self.name = name
        self.children: List[FileSystemComponent] = []

    def add(self, component: FileSystemComponent):
        self.children.append(component)

    def get_size(self) -> int:
        """Recursive: sum of all children sizes."""
        return sum(child.get_size() for child in self.children)

    def get_name(self) -> str:
        return self.name

    def display(self, indent: int = 0):
        """Recursive: display self and all children."""
        print("  " * indent + f"[DIR] {self.name}/")
        for child in self.children:
            child.display(indent + 1)


if __name__ == "__main__":
    print("COMPOSITE PATTERN DEMONSTRATION")
    print("="*60)

    # Build file system
    root = Directory("root")

    docs = Directory("Documents")
    docs.add(File("resume.pdf", 512000))
    docs.add(File("cover_letter.docx", 256000))

    photos = Directory("Photos")
    photos.add(File("photo1.jpg", 2048000))
    photos.add(File("photo2.jpg", 1536000))

    root.add(docs)
    root.add(photos)
    root.add(File("readme.txt", 1024))

    # Display structure
    print("\nFile System Structure:")
    root.display()

    # Calculate size (works for file or directory!)
    print(f"\nTotal size: {root.get_size()} bytes")
    print(f"Documents size: {docs.get_size()} bytes")

    print("\n" + "="*60)
    print("Key Observations:")
    print("  - Same interface for files and directories")
    print("  - get_size() works recursively on directories")
    print("  - Client code doesn't check types")
    print("  - Easy to add new file system components")
    print("="*60)
