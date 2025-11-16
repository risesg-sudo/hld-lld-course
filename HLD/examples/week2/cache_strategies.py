"""
Caching Strategies Implementation

This module demonstrates all major caching strategies:
1. Cache-Aside (Lazy Loading)
2. Read-Through
3. Write-Through
4. Write-Back (Write-Behind)
5. Write-Around

Each strategy has different trade-offs between consistency, performance, and complexity.
"""

import time
from typing import Any, Optional, Dict, Callable
from dataclasses import dataclass
from collections import defaultdict
from queue import Queue
import threading


# ============================================================================
# Mock Database and Cache
# ============================================================================

class Database:
    """Mock database for demonstration."""

    def __init__(self, latency_ms: int = 100):
        self.data: Dict[str, Any] = {}
        self.latency_ms = latency_ms
        self.read_count = 0
        self.write_count = 0

    def get(self, key: str) -> Optional[Any]:
        """Simulate database read with latency."""
        time.sleep(self.latency_ms / 1000.0)
        self.read_count += 1
        return self.data.get(key)

    def set(self, key: str, value: Any):
        """Simulate database write with latency."""
        time.sleep(self.latency_ms / 1000.0)
        self.write_count += 1
        self.data[key] = value

    def delete(self, key: str) -> bool:
        """Delete key from database."""
        if key in self.data:
            del self.data[key]
            return True
        return False

    def get_stats(self) -> dict:
        """Get database statistics."""
        return {
            "reads": self.read_count,
            "writes": self.write_count,
            "size": len(self.data)
        }

    def reset_stats(self):
        """Reset statistics."""
        self.read_count = 0
        self.write_count = 0


class Cache:
    """Simple in-memory cache."""

    def __init__(self, latency_ms: int = 1):
        self.data: Dict[str, Any] = {}
        self.latency_ms = latency_ms
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        time.sleep(self.latency_ms / 1000.0)

        if key in self.data:
            self.hit_count += 1
            return self.data[key]
        else:
            self.miss_count += 1
            return None

    def set(self, key: str, value: Any):
        """Set value in cache."""
        time.sleep(self.latency_ms / 1000.0)
        self.data[key] = value

    def delete(self, key: str):
        """Delete key from cache."""
        if key in self.data:
            del self.data[key]

    def clear(self):
        """Clear all cache."""
        self.data.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0

        return {
            "hits": self.hit_count,
            "misses": self.miss_count,
            "hit_rate": f"{hit_rate:.2f}%",
            "size": len(self.data)
        }

    def reset_stats(self):
        """Reset statistics."""
        self.hit_count = 0
        self.miss_count = 0

    def __contains__(self, key):
        return key in self.data


# ============================================================================
# Strategy 1: Cache-Aside (Lazy Loading)
# ============================================================================

class CacheAsideStrategy:
    """
    Cache-Aside (Lazy Loading) Strategy

    Read:
    1. Check cache
    2. If miss, read from database
    3. Store in cache
    4. Return data

    Write:
    1. Write to database
    2. Invalidate cache (or update)

    Pros:
    - Only cache what's needed
    - Cache failure doesn't break system
    - Simple to implement

    Cons:
    - Cache miss penalty (3 trips)
    - Possible stale data
    - Initial requests miss
    """

    def __init__(self, cache: Cache, database: Database):
        self.cache = cache
        self.database = database

    def get(self, key: str) -> Optional[Any]:
        """Get value using cache-aside pattern."""
        # 1. Try cache first
        value = self.cache.get(key)

        if value is not None:
            return value  # Cache hit

        # 2. Cache miss - fetch from database
        value = self.database.get(key)

        if value is not None:
            # 3. Store in cache for future requests
            self.cache.set(key, value)

        return value

    def set(self, key: str, value: Any):
        """Set value using cache-aside pattern."""
        # 1. Write to database
        self.database.set(key, value)

        # 2. Invalidate cache (lazy update on next read)
        self.cache.delete(key)

        # Alternative: Update cache immediately
        # self.cache.set(key, value)

    def delete(self, key: str):
        """Delete key."""
        self.database.delete(key)
        self.cache.delete(key)


# ============================================================================
# Strategy 2: Read-Through Cache
# ============================================================================

class ReadThroughCache:
    """
    Read-Through Cache Strategy

    Cache automatically loads data from database on miss.
    Application only interacts with cache.

    Read:
    1. Check cache
    2. If miss, cache loads from database automatically
    3. Return data

    Write:
    1. Write to database
    2. Invalidate or update cache

    Pros:
    - Simplified application code
    - Consistent read path
    - Cache manages itself

    Cons:
    - Cache miss still has penalty
    - Tighter coupling with cache
    """

    def __init__(self, cache: Cache, database: Database):
        self.cache = cache
        self.database = database

    def get(self, key: str) -> Optional[Any]:
        """Get value - cache handles database lookup."""
        # Check cache
        value = self.cache.get(key)

        if value is not None:
            return value

        # Cache miss - load from database
        value = self.database.get(key)

        if value is not None:
            # Cache automatically stores it
            self.cache.set(key, value)

        return value

    def set(self, key: str, value: Any):
        """Set value."""
        # Write to database
        self.database.set(key, value)

        # Invalidate cache
        self.cache.delete(key)

    def delete(self, key: str):
        """Delete key."""
        self.database.delete(key)
        self.cache.delete(key)


# ============================================================================
# Strategy 3: Write-Through Cache
# ============================================================================

class WriteThroughCache:
    """
    Write-Through Cache Strategy

    Writes go through cache to database synchronously.
    Cache and database always in sync.

    Read:
    1. Check cache
    2. If miss, load from database and cache

    Write:
    1. Write to cache
    2. Synchronously write to database
    3. Return after both complete

    Pros:
    - Strong consistency
    - No stale data
    - Simplified reads

    Cons:
    - Higher write latency (2 writes)
    - Cache may store rarely-read data
    - Write performance penalty
    """

    def __init__(self, cache: Cache, database: Database):
        self.cache = cache
        self.database = database

    def get(self, key: str) -> Optional[Any]:
        """Get value."""
        # Check cache
        value = self.cache.get(key)

        if value is not None:
            return value

        # Cache miss - load from database
        value = self.database.get(key)

        if value is not None:
            self.cache.set(key, value)

        return value

    def set(self, key: str, value: Any):
        """Set value - write through to database."""
        # 1. Write to cache
        self.cache.set(key, value)

        # 2. Synchronously write to database
        self.database.set(key, value)

        # Both complete before returning

    def delete(self, key: str):
        """Delete key."""
        self.cache.delete(key)
        self.database.delete(key)


# ============================================================================
# Strategy 4: Write-Back (Write-Behind) Cache
# ============================================================================

class WriteBackCache:
    """
    Write-Back (Write-Behind) Cache Strategy

    Writes go to cache only, database updated asynchronously.
    Best performance but risk of data loss.

    Read:
    1. Check cache
    2. If miss, load from database and cache

    Write:
    1. Write to cache (immediate return)
    2. Queue for async database write
    3. Background worker flushes to database

    Pros:
    - Lowest write latency
    - Can batch writes
    - Reduces database load
    - Best performance

    Cons:
    - Risk of data loss if cache crashes
    - Eventual consistency
    - Complex implementation
    - Need persistence or WAL
    """

    def __init__(self, cache: Cache, database: Database, batch_size: int = 10, flush_interval: float = 1.0):
        self.cache = cache
        self.database = database
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self.write_queue: Queue = Queue()
        self.pending_writes: Dict[str, Any] = {}
        self.running = True

        # Start background flush thread
        self.flush_thread = threading.Thread(target=self._flush_worker, daemon=True)
        self.flush_thread.start()

    def _flush_worker(self):
        """Background worker to flush writes to database."""
        while self.running:
            time.sleep(self.flush_interval)

            if self.pending_writes:
                # Batch write to database
                writes = dict(self.pending_writes)
                self.pending_writes.clear()

                for key, value in writes.items():
                    self.database.set(key, value)

    def get(self, key: str) -> Optional[Any]:
        """Get value."""
        # Check cache first (may have unflushed writes)
        value = self.cache.get(key)

        if value is not None:
            return value

        # Check pending writes
        if key in self.pending_writes:
            return self.pending_writes[key]

        # Cache miss - load from database
        value = self.database.get(key)

        if value is not None:
            self.cache.set(key, value)

        return value

    def set(self, key: str, value: Any):
        """Set value - write to cache, async to database."""
        # 1. Write to cache immediately
        self.cache.set(key, value)

        # 2. Queue for async database write
        self.pending_writes[key] = value

        # Immediate return (async write)

    def delete(self, key: str):
        """Delete key."""
        self.cache.delete(key)
        if key in self.pending_writes:
            del self.pending_writes[key]
        self.database.delete(key)

    def flush(self):
        """Force flush all pending writes."""
        if self.pending_writes:
            writes = dict(self.pending_writes)
            self.pending_writes.clear()

            for key, value in writes.items():
                self.database.set(key, value)

    def shutdown(self):
        """Shutdown and flush remaining writes."""
        self.flush()
        self.running = False
        if self.flush_thread.is_alive():
            self.flush_thread.join(timeout=5)


# ============================================================================
# Strategy 5: Write-Around Cache
# ============================================================================

class WriteAroundCache:
    """
    Write-Around Cache Strategy

    Writes bypass cache and go directly to database.
    Cache populated only on read miss.

    Read:
    1. Check cache
    2. If miss, load from database and cache

    Write:
    1. Write directly to database (bypass cache)
    2. Don't update cache

    Pros:
    - No cache pollution from one-time writes
    - Good for write-heavy, read-light workloads
    - Simpler than write-through

    Cons:
    - Recently written data not cached
    - Read miss after write
    - Higher read latency after writes
    """

    def __init__(self, cache: Cache, database: Database):
        self.cache = cache
        self.database = database

    def get(self, key: str) -> Optional[Any]:
        """Get value."""
        # Check cache
        value = self.cache.get(key)

        if value is not None:
            return value

        # Cache miss - load from database
        value = self.database.get(key)

        if value is not None:
            # Cache for future reads
            self.cache.set(key, value)

        return value

    def set(self, key: str, value: Any):
        """Set value - bypass cache."""
        # Write directly to database (bypass cache)
        self.database.set(key, value)

        # Don't update cache
        # Cache will be populated on next read

    def delete(self, key: str):
        """Delete key."""
        self.database.delete(key)
        self.cache.delete(key)


# ============================================================================
# Demonstration and Testing
# ============================================================================

def benchmark_strategy(name: str, strategy, operations: list):
    """Benchmark a caching strategy."""
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")

    # Get cache and database
    cache = strategy.cache
    database = strategy.database

    # Reset stats
    cache.reset_stats()
    database.reset_stats()

    # Run operations
    start_time = time.time()

    for op_type, key, value in operations:
        if op_type == "read":
            strategy.get(key)
        elif op_type == "write":
            strategy.set(key, value)

    # Flush pending writes for write-back
    if isinstance(strategy, WriteBackCache):
        strategy.flush()

    elapsed = time.time() - start_time

    # Print results
    print(f"\nOperations: {len(operations)}")
    print(f"Time: {elapsed:.4f}s")
    print(f"Throughput: {len(operations)/elapsed:.0f} ops/sec")

    print(f"\nCache Stats:")
    cache_stats = cache.get_stats()
    for key, value in cache_stats.items():
        print(f"  {key}: {value}")

    print(f"\nDatabase Stats:")
    db_stats = database.get_stats()
    for key, value in db_stats.items():
        print(f"  {key}: {value}")

    return elapsed, cache_stats, db_stats


def demonstrate_read_heavy_workload():
    """Demonstrate strategies with read-heavy workload."""
    print("\n" + "="*60)
    print("READ-HEAVY WORKLOAD COMPARISON")
    print("="*60)
    print("\nWorkload: 80% reads, 20% writes")

    # Create operations (80% reads, 20% writes)
    operations = []
    keys = [f"key_{i}" for i in range(10)]

    # Warm up with writes
    for key in keys:
        operations.append(("write", key, f"value_{key}"))

    # Read-heavy pattern
    import random
    for _ in range(100):
        if random.random() < 0.8:  # 80% reads
            key = random.choice(keys)
            operations.append(("read", key, None))
        else:  # 20% writes
            key = random.choice(keys)
            operations.append(("write", key, f"updated_{key}"))

    # Test each strategy
    strategies = {
        "Cache-Aside": CacheAsideStrategy(Cache(), Database()),
        "Read-Through": ReadThroughCache(Cache(), Database()),
        "Write-Through": WriteThroughCache(Cache(), Database()),
        "Write-Back": WriteBackCache(Cache(), Database()),
        "Write-Around": WriteAroundCache(Cache(), Database()),
    }

    results = {}
    for name, strategy in strategies.items():
        elapsed, cache_stats, db_stats = benchmark_strategy(name, strategy, operations[:])
        results[name] = {
            "time": elapsed,
            "cache_hit_rate": cache_stats["hit_rate"],
            "db_reads": db_stats["reads"],
            "db_writes": db_stats["writes"]
        }

    # Summary
    print("\n" + "="*60)
    print("SUMMARY - Read-Heavy Workload")
    print("="*60)
    print(f"\n{'Strategy':<20} {'Time (s)':<12} {'Hit Rate':<12} {'DB Reads':<12} {'DB Writes'}")
    print("-" * 80)
    for name, stats in results.items():
        print(f"{name:<20} {stats['time']:<12.4f} {stats['cache_hit_rate']:<12} "
              f"{stats['db_reads']:<12} {stats['db_writes']}")


def demonstrate_write_heavy_workload():
    """Demonstrate strategies with write-heavy workload."""
    print("\n" + "="*60)
    print("WRITE-HEAVY WORKLOAD COMPARISON")
    print("="*60)
    print("\nWorkload: 30% reads, 70% writes")

    # Create operations (30% reads, 70% writes)
    operations = []
    keys = [f"key_{i}" for i in range(10)]

    import random
    for i in range(100):
        if random.random() < 0.3:  # 30% reads
            key = random.choice(keys)
            operations.append(("read", key, None))
        else:  # 70% writes
            key = random.choice(keys)
            operations.append(("write", key, f"value_{i}"))

    # Test each strategy
    strategies = {
        "Cache-Aside": CacheAsideStrategy(Cache(), Database()),
        "Write-Through": WriteThroughCache(Cache(), Database()),
        "Write-Back": WriteBackCache(Cache(), Database()),
        "Write-Around": WriteAroundCache(Cache(), Database()),
    }

    results = {}
    for name, strategy in strategies.items():
        elapsed, cache_stats, db_stats = benchmark_strategy(name, strategy, operations[:])
        results[name] = {
            "time": elapsed,
            "db_writes": db_stats["writes"]
        }

    # Summary
    print("\n" + "="*60)
    print("SUMMARY - Write-Heavy Workload")
    print("="*60)
    print(f"\n{'Strategy':<20} {'Time (s)':<15} {'DB Writes'}")
    print("-" * 60)
    for name, stats in results.items():
        print(f"{name:<20} {stats['time']:<15.4f} {stats['db_writes']}")

    print("\nObservation:")
    print("- Write-Back is fastest (async writes)")
    print("- Write-Through is slowest (sync writes)")
    print("- Write-Around bypasses cache (good for one-time writes)")


def demonstrate_consistency():
    """Demonstrate consistency differences."""
    print("\n" + "="*60)
    print("CONSISTENCY DEMONSTRATION")
    print("="*60)

    # Write-Through (Strong Consistency)
    print("\n1. Write-Through Cache (Strong Consistency):")
    wt_cache = WriteThroughCache(Cache(), Database())

    wt_cache.set("user:1", {"name": "Alice", "age": 30})
    cached = wt_cache.cache.get("user:1")
    db_value = wt_cache.database.get("user:1")

    print(f"   Cache: {cached}")
    print(f"   Database: {db_value}")
    print(f"   Consistent: {cached == db_value}")

    # Write-Back (Eventual Consistency)
    print("\n2. Write-Back Cache (Eventual Consistency):")
    wb_cache = WriteBackCache(Cache(), Database())

    wb_cache.set("user:2", {"name": "Bob", "age": 25})
    cached = wb_cache.cache.get("user:2")
    db_value = wb_cache.database.get("user:2")  # May be None initially

    print(f"   Cache: {cached}")
    print(f"   Database (before flush): {db_value}")
    print(f"   Consistent: {cached == db_value}")

    # Flush and check again
    wb_cache.flush()
    db_value = wb_cache.database.get("user:2")
    print(f"   Database (after flush): {db_value}")
    print(f"   Consistent: {cached == db_value}")


def demonstrate_failure_scenarios():
    """Demonstrate failure scenarios."""
    print("\n" + "="*60)
    print("FAILURE SCENARIOS")
    print("="*60)

    # Cache-Aside: Cache failure doesn't break system
    print("\n1. Cache-Aside: Cache Failure (System Still Works):")
    ca_strategy = CacheAsideStrategy(Cache(), Database())

    # Populate database
    ca_strategy.database.set("user:1", "Alice")

    # Simulate cache failure by clearing it
    ca_strategy.cache.clear()
    print("   Cache cleared (simulating failure)")

    # System still works (reads from database)
    value = ca_strategy.get("user:1")
    print(f"   Read user:1: {value} (from database)")
    print("   ✓ System continues to work")

    # Write-Back: Cache failure means data loss
    print("\n2. Write-Back: Cache Failure (Data Loss Risk):")
    wb_cache = WriteBackCache(Cache(), Database())

    # Write to cache (not yet flushed)
    wb_cache.set("important:1", "critical_data")
    print("   Written to cache: important:1 = critical_data")

    # Simulate cache crash before flush
    wb_cache.cache.clear()
    wb_cache.pending_writes.clear()
    print("   Cache crashed (data lost!)")

    # Data lost
    value = wb_cache.database.get("important:1")
    print(f"   Database value: {value}")
    print("   ✗ Data lost (not yet flushed)")


def print_strategy_comparison_table():
    """Print comprehensive strategy comparison table."""
    print("\n" + "="*60)
    print("CACHING STRATEGIES COMPARISON")
    print("="*60)

    comparison = {
        "Cache-Aside": {
            "Read Latency": "Medium",
            "Write Latency": "Low",
            "Consistency": "Eventual",
            "Complexity": "Low",
            "Data Loss Risk": "Low",
            "Best For": "Read-heavy, general purpose"
        },
        "Read-Through": {
            "Read Latency": "Medium",
            "Write Latency": "Low",
            "Consistency": "Eventual",
            "Complexity": "Medium",
            "Data Loss Risk": "Low",
            "Best For": "Simplified read path"
        },
        "Write-Through": {
            "Read Latency": "Low",
            "Write Latency": "High",
            "Consistency": "Strong",
            "Complexity": "Medium",
            "Data Loss Risk": "Very Low",
            "Best For": "Consistency-critical apps"
        },
        "Write-Back": {
            "Read Latency": "Low",
            "Write Latency": "Very Low",
            "Consistency": "Eventual",
            "Complexity": "High",
            "Data Loss Risk": "Medium",
            "Best For": "Write-heavy, performance-critical"
        },
        "Write-Around": {
            "Read Latency": "High",
            "Write Latency": "Low",
            "Consistency": "Strong",
            "Complexity": "Low",
            "Data Loss Risk": "Low",
            "Best For": "Write-once, read-rarely"
        }
    }

    print(f"\n{'Strategy':<15} {'Read Lat':<12} {'Write Lat':<12} {'Consistency':<13} "
          f"{'Complexity':<12} {'Risk':<12}")
    print("-" * 100)

    for strategy, metrics in comparison.items():
        print(f"{strategy:<15} {metrics['Read Latency']:<12} {metrics['Write Latency']:<12} "
              f"{metrics['Consistency']:<13} {metrics['Complexity']:<12} "
              f"{metrics['Data Loss Risk']:<12}")

    print("\nBest Use Cases:")
    print("-" * 100)
    for strategy, metrics in comparison.items():
        print(f"{strategy:<15} {metrics['Best For']}")


if __name__ == "__main__":
    print("\nCaching Strategies Implementation and Demonstration")
    print("="*60)

    print_strategy_comparison_table()
    demonstrate_read_heavy_workload()
    demonstrate_write_heavy_workload()
    demonstrate_consistency()
    demonstrate_failure_scenarios()

    print("\n" + "="*60)
    print("Demonstration Complete!")
    print("="*60 + "\n")
