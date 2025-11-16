"""
LRU (Least Recently Used) Cache Implementation

An LRU cache evicts the least recently accessed item when capacity is reached.

Data Structure: HashMap + Doubly Linked List
- HashMap: O(1) lookup
- Doubly Linked List: O(1) insert/delete, maintains access order

Time Complexity:
- get(): O(1)
- put(): O(1)

Space Complexity: O(capacity)
"""

from typing import Optional, Any
from dataclasses import dataclass


class Node:
    """Doubly linked list node."""

    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value
        self.prev: Optional[Node] = None
        self.next: Optional[Node] = None

    def __repr__(self):
        return f"Node({self.key}: {self.value})"


class LRUCache:
    """
    LRU Cache Implementation

    Most recently used items are at the tail (right side).
    Least recently used items are at the head (left side).

    Structure:
        Head → [LRU] ← → [item] ← → [MRU] ← Tail

    Example:
        Cache(capacity=3):
        put(1,1): [1]
        put(2,2): [1, 2]
        put(3,3): [1, 2, 3]
        get(1):   [2, 3, 1]  (1 moved to end)
        put(4,4): [3, 1, 4]  (2 evicted)
    """

    def __init__(self, capacity: int):
        """
        Initialize LRU cache with fixed capacity.

        Args:
            capacity: Maximum number of items in cache
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")

        self.capacity = capacity
        self.cache = {}  # key -> Node

        # Dummy head and tail nodes
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _add_to_tail(self, node: Node):
        """Add node before tail (most recently used position)."""
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def _remove_node(self, node: Node):
        """Remove node from list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_tail(self, node: Node):
        """Move existing node to tail (mark as recently used)."""
        self._remove_node(node)
        self._add_to_tail(node)

    def _remove_head(self) -> Node:
        """Remove and return least recently used node (after head)."""
        lru_node = self.head.next
        self._remove_node(lru_node)
        return lru_node

    def get(self, key: Any) -> Optional[Any]:
        """
        Get value for key and mark as recently used.

        Args:
            key: Key to look up

        Returns:
            Value if key exists, None otherwise

        Time Complexity: O(1)
        """
        if key not in self.cache:
            self.misses += 1
            return None

        node = self.cache[key]
        self._move_to_tail(node)  # Mark as recently used
        self.hits += 1
        return node.value

    def put(self, key: Any, value: Any):
        """
        Add or update key-value pair in cache.

        If key exists: update value and move to end
        If key doesn't exist and cache is full: evict LRU item
        If key doesn't exist and cache not full: add new item

        Args:
            key: Key to store
            value: Value to store

        Time Complexity: O(1)
        """
        # Update existing key
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_tail(node)
            return

        # Add new key
        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add_to_tail(new_node)

        # Check capacity
        if len(self.cache) > self.capacity:
            # Remove LRU item
            lru = self._remove_head()
            del self.cache[lru.key]
            self.evictions += 1

    def delete(self, key: Any) -> bool:
        """
        Delete key from cache.

        Args:
            key: Key to delete

        Returns:
            True if key existed, False otherwise
        """
        if key not in self.cache:
            return False

        node = self.cache[key]
        self._remove_node(node)
        del self.cache[key]
        return True

    def clear(self):
        """Clear all items from cache."""
        self.cache.clear()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "capacity": self.capacity,
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": f"{hit_rate:.2f}%"
        }

    def get_items_lru_order(self) -> list:
        """Get all items in LRU order (least to most recent)."""
        items = []
        current = self.head.next
        while current != self.tail:
            items.append((current.key, current.value))
            current = current.next
        return items

    def __str__(self):
        """String representation showing items in MRU order."""
        items = self.get_items_lru_order()
        return f"LRUCache({items})"

    def __contains__(self, key):
        """Check if key exists in cache."""
        return key in self.cache

    def __len__(self):
        """Get cache size."""
        return len(self.cache)


class LRUCacheDict(dict):
    """
    Simple LRU Cache using Python's OrderedDict behavior (Python 3.7+).

    Less efficient than custom implementation but simpler.
    Dictionaries maintain insertion order in Python 3.7+.

    Note: For production, use custom implementation or functools.lru_cache
    """

    def __init__(self, capacity: int):
        super().__init__()
        self.capacity = capacity

    def get(self, key: Any) -> Optional[Any]:
        """Get value and move to end (most recent)."""
        if key not in self:
            return None

        # Move to end by deleting and re-inserting
        value = self.pop(key)
        self[key] = value
        return value

    def put(self, key: Any, value: Any):
        """Add/update value, evict LRU if needed."""
        if key in self:
            self.pop(key)
        elif len(self) >= self.capacity:
            # Remove first item (LRU)
            oldest = next(iter(self))
            self.pop(oldest)

        self[key] = value


# ============================================================================
# Time-Aware LRU Cache (TTL Support)
# ============================================================================

import time


class TTLLRUCache(LRUCache):
    """
    LRU Cache with Time-To-Live (TTL) support.

    Items expire after TTL seconds regardless of access.
    Combines LRU eviction with time-based expiration.
    """

    def __init__(self, capacity: int, default_ttl: int = 3600):
        """
        Initialize TTL-aware LRU cache.

        Args:
            capacity: Maximum cache size
            default_ttl: Default time-to-live in seconds
        """
        super().__init__(capacity)
        self.default_ttl = default_ttl
        self.expiry_times = {}  # key -> expiration timestamp

    def put(self, key: Any, value: Any, ttl: Optional[int] = None):
        """
        Add item with TTL.

        Args:
            key: Cache key
            value: Cache value
            ttl: Time-to-live in seconds (None = default_ttl)
        """
        super().put(key, value)
        expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
        self.expiry_times[key] = expiry

    def get(self, key: Any) -> Optional[Any]:
        """Get value if exists and not expired."""
        if key not in self.cache:
            return None

        # Check expiration
        if time.time() > self.expiry_times.get(key, float('inf')):
            # Expired
            self.delete(key)
            self.misses += 1
            return None

        return super().get(key)

    def delete(self, key: Any) -> bool:
        """Delete key and its expiry."""
        if key in self.expiry_times:
            del self.expiry_times[key]
        return super().delete(key)

    def clear(self):
        """Clear cache and expiry times."""
        super().clear()
        self.expiry_times.clear()

    def cleanup_expired(self):
        """Remove all expired items."""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self.expiry_times.items()
            if current_time > expiry
        ]

        for key in expired_keys:
            self.delete(key)

        return len(expired_keys)


# ============================================================================
# Demonstration and Testing
# ============================================================================

def demonstrate_basic_operations():
    """Demonstrate basic LRU cache operations."""
    print("="*60)
    print("BASIC LRU CACHE OPERATIONS")
    print("="*60)

    cache = LRUCache(capacity=3)

    print("\n1. Adding items to cache (capacity=3):")
    operations = [
        ("put", 1, "one"),
        ("put", 2, "two"),
        ("put", 3, "three"),
    ]

    for op, key, value in operations:
        cache.put(key, value)
        print(f"   put({key}, '{value}') → {cache.get_items_lru_order()}")

    print("\n2. Get item (moves to end):")
    value = cache.get(1)
    print(f"   get(1) → '{value}'")
    print(f"   Order after get: {cache.get_items_lru_order()}")

    print("\n3. Add item when full (evicts LRU):")
    cache.put(4, "four")
    print(f"   put(4, 'four') → {cache.get_items_lru_order()}")
    print(f"   (Key 2 evicted - was LRU)")

    print("\n4. Update existing item:")
    cache.put(3, "THREE")
    print(f"   put(3, 'THREE') → {cache.get_items_lru_order()}")

    print(f"\n5. Cache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


def demonstrate_access_patterns():
    """Demonstrate different access patterns."""
    print("\n" + "="*60)
    print("ACCESS PATTERN DEMONSTRATION")
    print("="*60)

    cache = LRUCache(capacity=4)

    # Sequential access
    print("\n1. Sequential Access (1,2,3,4,5):")
    for i in range(1, 6):
        cache.put(i, f"value{i}")
        print(f"   put({i}) → {cache.get_items_lru_order()}")

    # Repeated access
    print("\n2. Repeated Access (get 3 multiple times):")
    cache.clear()
    for i in range(1, 5):
        cache.put(i, f"value{i}")

    print(f"   Initial: {cache.get_items_lru_order()}")
    for _ in range(3):
        cache.get(3)
    print(f"   After get(3) x3: {cache.get_items_lru_order()}")

    # Working set pattern
    print("\n3. Working Set Pattern (frequently access subset):")
    cache.clear()
    accesses = [1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 5]

    for key in accesses:
        if key not in cache:
            cache.put(key, f"value{key}")
        else:
            cache.get(key)

    print(f"   Access pattern: {accesses}")
    print(f"   Final cache: {cache.get_items_lru_order()}")
    print(f"   Keys 1,2,3 retained (working set)")
    print(f"   Hit rate: {cache.get_stats()['hit_rate']}")


def demonstrate_ttl_cache():
    """Demonstrate TTL-aware LRU cache."""
    print("\n" + "="*60)
    print("TTL LRU CACHE DEMONSTRATION")
    print("="*60)

    cache = TTLLRUCache(capacity=5, default_ttl=2)  # 2 second TTL

    print("\n1. Add items with default TTL (2 seconds):")
    cache.put("session1", "user_data_1")
    cache.put("session2", "user_data_2")
    print(f"   Added 2 sessions")
    print(f"   Cache: {list(cache.cache.keys())}")

    print("\n2. Add item with custom TTL (5 seconds):")
    cache.put("long_session", "important_data", ttl=5)
    print(f"   Cache: {list(cache.cache.keys())}")

    print("\n3. Wait 2.5 seconds...")
    time.sleep(2.5)

    print("\n4. Access items (some should be expired):")
    results = {
        "session1": cache.get("session1"),
        "session2": cache.get("session2"),
        "long_session": cache.get("long_session")
    }

    for key, value in results.items():
        status = "✓ Found" if value else "✗ Expired"
        print(f"   get('{key}'): {status}")

    print(f"\n5. Cleanup expired items:")
    removed = cache.cleanup_expired()
    print(f"   Removed {removed} expired items")
    print(f"   Remaining: {list(cache.cache.keys())}")


def benchmark_cache():
    """Benchmark cache performance."""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)

    import random

    cache = LRUCache(capacity=1000)
    num_operations = 10000

    # Warm up cache
    for i in range(1000):
        cache.put(i, f"value{i}")

    # Benchmark gets
    start = time.time()
    for _ in range(num_operations):
        key = random.randint(0, 1999)
        cache.get(key)
    get_time = time.time() - start

    # Benchmark puts
    start = time.time()
    for i in range(num_operations):
        key = random.randint(0, 1999)
        cache.put(key, f"value{key}")
    put_time = time.time() - start

    print(f"\nOperations: {num_operations:,}")
    print(f"Get Operations: {get_time:.4f}s ({num_operations/get_time:,.0f} ops/sec)")
    print(f"Put Operations: {put_time:.4f}s ({num_operations/put_time:,.0f} ops/sec)")
    print(f"\nCache Stats:")
    for key, value in cache.get_stats().items():
        print(f"  {key}: {value}")


def compare_implementations():
    """Compare custom implementation vs dict-based."""
    print("\n" + "="*60)
    print("IMPLEMENTATION COMPARISON")
    print("="*60)

    import random

    print("\n" + "-"*40)
    print("Custom LRUCache Implementation")
    print("-"*40)
    cache1 = LRUCache(capacity=100)

    start = time.time()
    for i in range(1000):
        cache1.put(i, f"value{i}")
        if i % 2 == 0:
            cache1.get(random.randint(0, i))
    time1 = time.time() - start

    print(f"Time: {time1:.4f}s")
    print(f"Stats: {cache1.get_stats()}")

    print("\n" + "-"*40)
    print("Dict-based LRUCache")
    print("-"*40)
    cache2 = LRUCacheDict(capacity=100)

    start = time.time()
    for i in range(1000):
        cache2.put(i, f"value{i}")
        if i % 2 == 0:
            cache2.get(random.randint(0, i))
    time2 = time.time() - start

    print(f"Time: {time2:.4f}s")
    print(f"Size: {len(cache2)}")

    print(f"\nCustom implementation is {time2/time1:.2f}x faster")


if __name__ == "__main__":
    print("\nLRU Cache Implementation and Demonstration")
    print("="*60)

    demonstrate_basic_operations()
    demonstrate_access_patterns()
    demonstrate_ttl_cache()
    benchmark_cache()
    compare_implementations()

    print("\n" + "="*60)
    print("Demonstration Complete!")
    print("="*60 + "\n")
