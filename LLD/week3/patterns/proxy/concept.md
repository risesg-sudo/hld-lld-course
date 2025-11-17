# Proxy Pattern

## The Hook

Loading a high-resolution image takes 2 seconds and 100MB of memory. Your photo gallery displays thumbnails of 100 images. Do you load all 100 images immediately? That's 200 seconds and 10GB. Users only click on 5 images on average.

What if you could delay loading until needed? What if you could control access to expensive objects? What if you could add logging without touching the original class?

This is where proxy comes in: a surrogate object that controls access to the real object.

## The Problem

**Expensive Initialization**: Creating objects is costly (memory, time, resources). You don't want to pay the cost until necessary.

**Access Control**: Some operations need authorization. You want to check permissions before allowing access.

**Remote Access**: Object lives on different machine. You need local representative.

**Additional Behavior**: Want logging, caching, monitoring without modifying original class.

The fundamental problem: you need control over object access that the object itself doesn't provide.

## The Solution

Proxy implements the same interface as real object but adds control layer.

**Virtual Proxy** (lazy loading):
```python
class ImageProxy(Image):
    def __init__(self, filename):
        self.filename = filename
        self._image = None  # Not loaded yet

    def display(self):
        if self._image is None:
            self._image = RealImage(self.filename)  # Load on first access
        self._image.display()
```

**Protection Proxy** (access control):
```python
class ProtectedDocument(Document):
    def __init__(self, document, user_role):
        self._document = document
        self.user_role = user_role

    def view(self):
        if self.user_role in ["admin", "editor"]:
            self._document.view()
        else:
            raise PermissionError()
```

Client uses proxy just like real object—same interface, transparent substitution.

## Code Example

See `/home/user/hld-lld-course/LLD/week3/patterns/proxy/image_loader.py`

## When to Use

Lazy initialization, access control, remote objects, caching expensive operations, logging/monitoring.

## Trade-offs

**Gains**: Lazy loading, access control, transparency, additional behavior
**Loses**: Indirection layer, complexity, must match interface exactly

## Key Takeaways

1. Proxy controls access to real object
2. Same interface as real object
3. Types: virtual (lazy), protection (access), remote (RPC), caching, logging
4. Transparent to client
5. Different from decorator: proxy controls access, decorator adds behavior
