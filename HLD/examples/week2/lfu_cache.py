"""
LFU (Least Frequently Used) Cache Implementation

An LFU cache evicts the item with the lowest access frequency when capacity is reached.
If multiple items have the same frequency, evict the least recently used among them.

Data Structure: HashMap + Frequency Map + Doubly Linked Lists
- HashMap: key -> (value, frequency) for O(1) lookup
- Frequency Map: frequency -> list of keys with that frequency
- Within each frequency: LRU order

Time Complexity:
- get(): O(1)
- put(): O(1)

Space Complexity: O(capacity)
"""

from typing import Any, Optional, Dict, Set
from collections import defaultdict, OrderedDict
from dataclasses import dataclass
import time


class Node:
    """Node in doubly linked list for LFU cache."""

    def __init__(self, key: Any, value: Any, freq: int = 1):
        self.key = key
        self.value = value
        self.freq = freq
        self.prev: Optional[Node] = None
        self.next: Optional[Node] = None

    def __repr__(self):
        return f"Node({self.key}: {self.value}, freq={self.freq})"


class DoublyLinkedList:
    """Doubly linked list for maintaining items with same frequency."""

    def __init__(self):
        self.head = Node(0, 0, 0)
        self.tail = Node(0, 0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def add_to_head(self, node: Node):
        """Add node right after head (most recently used position)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
        self.size += 1

    def remove_node(self, node: Node):
        """Remove node from list."""
        if node.prev and node.next:
            node.prev.next = node.next
            node.next.prev = node.prev
            self.size -= 1

    def remove_tail(self) -> Optional[Node]:
        """Remove and return least recently used node (before tail)."""
        if self.size == 0:
            return None

        lru_node = self.tail.prev
        self.remove_node(lru_node)
        return lru_node

    def is_empty(self) -> bool:
        """Check if list is empty."""
        return self.size == 0


class LFUCache:
    """
    LFU Cache Implementation

    Eviction Strategy:
    1. Find items with minimum frequency
    2. Among those, evict least recently used

    Example:
        Cache(capacity=2):
        put(1,1): {1:freq=1}
        put(2,2): {1:freq=1, 2:freq=1}
        get(1):   {1:freq=2, 2:freq=1}
        put(3,3): {1:freq=2, 3:freq=1}  (2 evicted, lowest freq)
        get(3):   {1:freq=2, 3:freq=2}
        put(4,4): {3:freq=2, 4:freq=1}  (1 evicted, oldest at freq=2)
    """

    def __init__(self, capacity: int):
        """
        Initialize LFU cache.

        Args:
            capacity: Maximum number of items in cache
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")

        self.capacity = capacity
        self.min_freq = 0
        self.node_map: Dict[Any, Node] = {}  # key -> Node
        self.freq_map: Dict[int, DoublyLinkedList] = defaultdict(DoublyLinkedList)

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _update_freq(self, node: Node):
        """Update node frequency and move to appropriate frequency list."""
        # Remove from current frequency list
        old_freq = node.freq
        self.freq_map[old_freq].remove_node(node)

        # Update min_freq if necessary
        if old_freq == self.min_freq and self.freq_map[old_freq].is_empty():
            self.min_freq += 1

        # Increment frequency and add to new frequency list
        node.freq += 1
        self.freq_map[node.freq].add_to_head(node)

    def get(self, key: Any) -> Optional[Any]:
        """
        Get value for key and increment its frequency.

        Args:
            key: Key to look up

        Returns:
            Value if key exists, None otherwise

        Time Complexity: O(1)
        """
        if key not in self.node_map:
            self.misses += 1
            return None

        node = self.node_map[key]
        self._update_freq(node)
        self.hits += 1
        return node.value

    def put(self, key: Any, value: Any):
        """
        Add or update key-value pair in cache.

        Args:
            key: Key to store
            value: Value to store

        Time Complexity: O(1)
        """
        if self.capacity == 0:
            return

        # Update existing key
        if key in self.node_map:
            node = self.node_map[key]
            node.value = value
            self._update_freq(node)
            return

        # Cache is full - evict LFU item
        if len(self.node_map) >= self.capacity:
            # Get LRU node from minimum frequency list
            min_freq_list = self.freq_map[self.min_freq]
            lfu_node = min_freq_list.remove_tail()

            if lfu_node:
                del self.node_map[lfu_node.key]
                self.evictions += 1

        # Add new node
        new_node = Node(key, value, freq=1)
        self.node_map[key] = new_node
        self.freq_map[1].add_to_head(new_node)
        self.min_freq = 1

    def delete(self, key: Any) -> bool:
        """
        Delete key from cache.

        Args:
            key: Key to delete

        Returns:
            True if key existed, False otherwise
        """
        if key not in self.node_map:
            return False

        node = self.node_map[key]
        self.freq_map[node.freq].remove_node(node)
        del self.node_map[key]

        # Update min_freq if necessary
        if self.freq_map[self.min_freq].is_empty():
            # Find next minimum frequency
            if self.node_map:
                self.min_freq = min(node.freq for node in self.node_map.values())
            else:
                self.min_freq = 0

        return True

    def clear(self):
        """Clear all items from cache."""
        self.node_map.clear()
        self.freq_map.clear()
        self.min_freq = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def size(self) -> int:
        """Get current cache size."""
        return len(self.node_map)

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        # Frequency distribution
        freq_dist = defaultdict(int)
        for node in self.node_map.values():
            freq_dist[node.freq] += 1

        return {
            "capacity": self.capacity,
            "size": len(self.node_map),
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": f"{hit_rate:.2f}%",
            "min_frequency": self.min_freq,
            "frequency_distribution": dict(freq_dist)
        }

    def get_items_by_frequency(self) -> Dict[int, list]:
        """Get items grouped by frequency."""
        result = defaultdict(list)
        for key, node in self.node_map.items():
            result[node.freq].append((key, node.value))
        return dict(result)

    def __str__(self):
        """String representation."""
        items = [(k, v.value, v.freq) for k, v in self.node_map.items()]
        return f"LFUCache({items})"

    def __contains__(self, key):
        """Check if key exists in cache."""
        return key in self.node_map

    def __len__(self):
        """Get cache size."""
        return len(self.node_map)


class SimpleLFUCache:
    """
    Simplified LFU Cache using OrderedDict

    Less optimal than custom implementation but easier to understand.
    Uses OrderedDict to maintain LRU order within each frequency.

    Time Complexity:
    - get(): O(1) average
    - put(): O(n) worst case (when updating frequency)
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> (value, frequency)
        self.freq_lists: Dict[int, OrderedDict] = defaultdict(OrderedDict)
        self.min_freq = 0

    def _update_freq(self, key: Any):
        """Update frequency for key."""
        value, freq = self.cache[key]

        # Remove from old frequency list
        self.freq_lists[freq].pop(key)
        if not self.freq_lists[freq] and freq == self.min_freq:
            self.min_freq += 1

        # Add to new frequency list
        new_freq = freq + 1
        self.freq_lists[new_freq][key] = None
        self.cache[key] = (value, new_freq)

    def get(self, key: Any) -> Optional[Any]:
        """Get value and increment frequency."""
        if key not in self.cache:
            return None

        self._update_freq(key)
        return self.cache[key][0]

    def put(self, key: Any, value: Any):
        """Add or update key-value pair."""
        if self.capacity == 0:
            return

        # Update existing key
        if key in self.cache:
            self.cache[key] = (value, self.cache[key][1])
            self._update_freq(key)
            return

        # Evict if full
        if len(self.cache) >= self.capacity:
            # Get LFU key (first key in min frequency list)
            evict_key, _ = self.freq_lists[self.min_freq].popitem(last=False)
            del self.cache[evict_key]

        # Add new key
        self.cache[key] = (value, 1)
        self.freq_lists[1][key] = None
        self.min_freq = 1


# ============================================================================
# Demonstration and Testing
# ============================================================================

def demonstrate_basic_operations():
    """Demonstrate basic LFU cache operations."""
    print("="*60)
    print("BASIC LFU CACHE OPERATIONS")
    print("="*60)

    cache = LFUCache(capacity=3)

    print("\n1. Adding items to cache (capacity=3):")
    operations = [
        ("put", 1, "one"),
        ("put", 2, "two"),
        ("put", 3, "three"),
    ]

    for op, key, value in operations:
        cache.put(key, value)
        items = [(k, n.value, n.freq) for k, n in cache.node_map.items()]
        print(f"   put({key}, '{value}') → {items}")

    print("\n2. Access item (increases frequency):")
    for _ in range(3):
        cache.get(1)
    items = [(k, n.value, n.freq) for k, n in cache.node_map.items()]
    print(f"   get(1) x3 → {items}")
    print(f"   (Key 1 now has frequency=4)")

    print("\n3. Add item when full (evicts LFU):")
    cache.put(4, "four")
    items = [(k, n.value, n.freq) for k, n in cache.node_map.items()]
    print(f"   put(4, 'four') → {items}")
    print(f"   (Key 2 or 3 evicted - lowest frequency=1)")

    print(f"\n4. Frequency Distribution:")
    print(f"   {cache.get_items_by_frequency()}")

    print(f"\n5. Cache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


def demonstrate_lfu_vs_lru():
    """Compare LFU behavior with LRU."""
    print("\n" + "="*60)
    print("LFU vs LRU BEHAVIOR COMPARISON")
    print("="*60)

    from lru_cache import LRUCache

    print("\nScenario: Access pattern with popular item")
    print("Access sequence: 1, 2, 3, 1, 1, 1, 4")

    # LFU Cache
    print("\n" + "-"*40)
    print("LFU Cache (capacity=3):")
    print("-"*40)
    lfu = LFUCache(capacity=3)

    sequence = [1, 2, 3, 1, 1, 1, 4]
    for key in sequence:
        if key not in lfu:
            lfu.put(key, f"value{key}")
            print(f"put({key})", end=" ")
        else:
            lfu.get(key)
            print(f"get({key})", end=" ")

    print()
    items = [(k, n.value, n.freq) for k, n in lfu.node_map.items()]
    print(f"Final cache: {items}")
    print("Result: Key 1 retained (high frequency)")
    print("        Key 2 evicted (low frequency)")

    # LRU Cache
    print("\n" + "-"*40)
    print("LRU Cache (capacity=3):")
    print("-"*40)
    lru = LRUCache(capacity=3)

    for key in sequence:
        if key not in lru:
            lru.put(key, f"value{key}")
            print(f"put({key})", end=" ")
        else:
            lru.get(key)
            print(f"get({key})", end=" ")

    print()
    items = lru.get_items_lru_order()
    print(f"Final cache: {items}")
    print("Result: Key 3 evicted (least recently used)")
    print("        All recent accesses retained")


def demonstrate_frequency_based_retention():
    """Show how LFU retains frequently accessed items."""
    print("\n" + "="*60)
    print("FREQUENCY-BASED RETENTION")
    print("="*60)

    cache = LFUCache(capacity=4)

    print("\n1. Simulate content popularity (video views):")

    # Popular content
    popular = [101, 102, 103]
    # One-time content
    occasional = [201, 202, 203, 204, 205]

    # Access pattern
    print("\n   Popular videos (viewed multiple times):")
    for video_id in popular:
        cache.put(video_id, f"video_{video_id}")
        # Popular videos accessed 5 times
        for _ in range(5):
            cache.get(video_id)
        print(f"   Video {video_id}: 5 views")

    # Occasional videos
    print("\n   Occasional videos (viewed once):")
    for video_id in occasional:
        if video_id not in cache:
            cache.put(video_id, f"video_{video_id}")
            print(f"   Video {video_id}: 1 view → ", end="")

            if len(cache) > cache.capacity:
                print("evicted a video")
            else:
                print("added to cache")

    print(f"\n2. Final cache state:")
    items = cache.get_items_by_frequency()
    for freq, videos in sorted(items.items(), reverse=True):
        print(f"   Frequency {freq}: {videos}")

    print("\n3. Result: Popular videos retained in cache!")
    print(f"   Cache contents: {list(cache.node_map.keys())}")


def simulate_real_world_scenario():
    """Simulate real-world CDN caching scenario."""
    print("\n" + "="*60)
    print("REAL-WORLD SCENARIO: CDN CACHING")
    print("="*60)

    import random

    cache = LFUCache(capacity=100)

    # Simulate content with different popularity
    # 20% of content generates 80% of requests (Pareto principle)
    popular_content = list(range(1, 21))  # 20 popular items
    regular_content = list(range(21, 101))  # 80 regular items

    print("\nSimulating 1000 requests with Pareto distribution:")
    print("(20% popular content, 80% regular content)")

    requests = []
    for _ in range(1000):
        if random.random() < 0.8:  # 80% requests for popular content
            content_id = random.choice(popular_content)
        else:
            content_id = random.choice(regular_content)
        requests.append(content_id)

    # Process requests
    for content_id in requests:
        if content_id not in cache:
            cache.put(content_id, f"content_{content_id}")
        else:
            cache.get(content_id)

    # Analyze results
    stats = cache.get_stats()
    freq_dist = cache.get_items_by_frequency()

    print(f"\nResults:")
    print(f"  Total requests: 1000")
    print(f"  Cache hits: {stats['hits']}")
    print(f"  Cache misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate']}")
    print(f"  Evictions: {stats['evictions']}")

    print(f"\nFrequency Distribution:")
    for freq in sorted(freq_dist.keys(), reverse=True)[:5]:
        count = len(freq_dist[freq])
        print(f"  Frequency {freq}: {count} items")

    # Check if popular content is cached
    popular_in_cache = sum(1 for cid in popular_content if cid in cache)
    print(f"\nPopular content in cache: {popular_in_cache}/20 ({popular_in_cache*5}%)")
    print(f"Regular content in cache: {len(cache) - popular_in_cache}/{len(cache)}")


def benchmark_lfu_cache():
    """Benchmark LFU cache performance."""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)

    import random

    cache = LFUCache(capacity=1000)
    num_operations = 10000

    # Warm up
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


def compare_lfu_implementations():
    """Compare custom vs simple LFU implementations."""
    print("\n" + "="*60)
    print("LFU IMPLEMENTATION COMPARISON")
    print("="*60)

    import random

    # Custom implementation
    print("\n" + "-"*40)
    print("Custom LFU (O(1) operations)")
    print("-"*40)
    cache1 = LFUCache(capacity=100)

    start = time.time()
    for i in range(1000):
        cache1.put(i, f"value{i}")
        if i % 2 == 0:
            cache1.get(random.randint(0, i))
    time1 = time.time() - start

    print(f"Time: {time1:.4f}s")
    print(f"Stats: {cache1.get_stats()}")

    # Simple implementation
    print("\n" + "-"*40)
    print("Simple LFU (OrderedDict-based)")
    print("-"*40)
    cache2 = SimpleLFUCache(capacity=100)

    start = time.time()
    for i in range(1000):
        cache2.put(i, f"value{i}")
        if i % 2 == 0:
            cache2.get(random.randint(0, i))
    time2 = time.time() - start

    print(f"Time: {time2:.4f}s")
    print(f"Size: {len(cache2.cache)}")

    if time1 > 0:
        print(f"\nCustom implementation is {time2/time1:.2f}x faster")


if __name__ == "__main__":
    print("\nLFU Cache Implementation and Demonstration")
    print("="*60)

    demonstrate_basic_operations()
    demonstrate_lfu_vs_lru()
    demonstrate_frequency_based_retention()
    simulate_real_world_scenario()
    benchmark_lfu_cache()
    compare_lfu_implementations()

    print("\n" + "="*60)
    print("Demonstration Complete!")
    print("="*60 + "\n")
