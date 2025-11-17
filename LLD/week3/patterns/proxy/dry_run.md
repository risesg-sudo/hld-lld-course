# Dry Run: Proxy Pattern

## Setup
```python
proxy = ImageProxy("photo.jpg")
```

Memory:
```
0x7001: ImageProxy
  filename: "photo.jpg"
  _image: None  # Not loaded!
```

Image NOT loaded yet. This is key—deferred initialization.

## Operation 1: proxy.display() (first call)

**Step 1: Check if loaded**
```
if self._image is None:  # None → True
```

**Step 2: Load now**
```
Output: "First access - loading image now..."
self._image = RealImage("photo.jpg")
```

**RealImage creation**:
```
RealImage.__init__():
  self.filename = "photo.jpg"
  self._load()
    Output: "Loading photo.jpg from disk... (expensive operation)"
    sleep(0.5)  # Simulate slow disk I/O

Created at 0x7002
```

**Memory updated**:
```
0x7001: ImageProxy
  filename: "photo.jpg"
  _image: → 0x7002 (RealImage)

0x7002: RealImage
  filename: "photo.jpg"
```

**Step 3: Delegate to real image**
```
self._image.display()
→ RealImage.display()
  Output: "Displaying photo.jpg"
```

## Operation 2: proxy.display() (second call)

**Step 1: Check if loaded**
```
if self._image is None:  # → 0x7002 (not None) → False
```

**Step 2: Skip loading** (already loaded!)

**Step 3: Delegate directly**
```
self._image.display()
→ RealImage.display()
  Output: "Displaying photo.jpg"
```

No loading delay on second call. Proxy reuses loaded image.

## Key: Lazy Initialization

**Without Proxy**:
- Image loaded in constructor
- Pay cost immediately
- Even if never used

**With Proxy**:
- Image NOT loaded in constructor
- Pay cost on first use
- If never used, never loaded

This is virtual proxy pattern—defer expensive initialization.
