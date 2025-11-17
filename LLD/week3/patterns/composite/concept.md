# Composite Pattern

## The Hook

A file system has files and directories. Directories contain files... and other directories. You want to calculate total size. Do you write separate code for files and directories? Do you use isinstance() checks everywhere? Do you manually track what's a file versus a directory?

Tree structures are everywhere: file systems, UI components, organization charts, menu systems. The pattern is always the same: some nodes are leaves (files), some are composites (directories). How do you treat them uniformly without type checking?

## The Problem

**Treating Individuals vs Collections**: A file has size. A directory has size (sum of contents). Client code needs to calculate size. Does it check "if directory, loop and sum; if file, return size"? That couples client to structure.

**Tree Traversal**: To process a directory tree, you need recursive traversal. Without a pattern, every operation (size, display, search) reimplements traversal logic.

**Adding New Node Types**: Want to add symbolic links? Shortcuts? Do you update every place that checks node types?

The fundamental problem: trees have recursive structure (nodes contain nodes), but without a pattern, you lose the elegance of recursion.

## The Solution

Composite pattern treats individual objects and compositions uniformly through a common interface.

**Component Interface** (works for both files and directories):
```python
class FileSystemComponent(ABC):
    def get_size(self) -> int:
        pass

    def display(self, indent: int = 0):
        pass
```

**Leaf** (individual - file):
```python
class File(FileSystemComponent):
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def get_size(self):
        return self.size
```

**Composite** (collection - directory):
```python
class Directory(FileSystemComponent):
    def __init__(self, name):
        self.name = name
        self.children = []

    def add(self, component):
        self.children.append(component)

    def get_size(self):
        return sum(child.get_size() for child in self.children)
```

**Client** (treats both the same):
```python
# Works with file or directory!
def print_size(component: FileSystemComponent):
    print(f"{component.get_name()}: {component.get_size()} bytes")
```

## Code Example

See `/home/user/hld-lld-course/LLD/week3/patterns/composite/file_system.py`

## When to Use

Tree structures, part-whole hierarchies, uniform treatment of individuals and collections, recursive composition.

## Trade-offs

**Gains**: Uniform interface, recursive composition, simple client code, easy to extend
**Loses**: Type safety issues, overly general in some cases

## Key Takeaways

1. Composite represents tree structures with uniform interface
2. Leaf and composite both implement same interface
3. Composite delegates to children recursively
4. Client treats individuals and collections identically
5. Natural for hierarchical data
