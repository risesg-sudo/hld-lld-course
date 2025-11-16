"""
Database Indexing Performance Comparison

This module demonstrates and compares different index types:
1. B-Tree Index (most common, general purpose)
2. Hash Index (fast equality lookups)
3. Bitmap Index (low cardinality, analytics)

Performance Analysis:
- Insertion time
- Query time (equality, range, sorting)
- Space overhead
- Update performance

Real-World Usage:
- PostgreSQL: B-Tree (default), Hash, GIN, GiST, BRIN
- MySQL: B-Tree (default), Hash (MEMORY engine)
- Oracle: B-Tree, Bitmap, Hash
"""

import time
import random
import bisect
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class IndexStats:
    """Statistics for index performance"""

    build_time: float
    space_bytes: int
    equality_query_time: float
    range_query_time: float
    insert_time: float


class BTreeIndex:
    """
    B-Tree Index Implementation (Simplified)

    Real B-Trees have multiple keys per node and are disk-optimized.
    This is a simplified in-memory version using Python's bisect module.

    Characteristics:
    - O(log n) search, insert, delete
    - Maintains sorted order
    - Excellent for range queries
    - Good for most use cases
    """

    def __init__(self):
        self.keys = []  # Sorted list of keys
        self.values = []  # Corresponding row pointers/values

    def insert(self, key: Any, value: Any):
        """Insert key-value pair maintaining sorted order"""
        # Binary search to find insertion position
        idx = bisect.bisect_left(self.keys, key)

        if idx < len(self.keys) and self.keys[idx] == key:
            # Update existing
            self.values[idx] = value
        else:
            # Insert new
            self.keys.insert(idx, key)
            self.values.insert(idx, value)

    def search_exact(self, key: Any) -> Optional[Any]:
        """
        Search for exact key match
        Time: O(log n) using binary search
        """
        idx = bisect.bisect_left(self.keys, key)
        if idx < len(self.keys) and self.keys[idx] == key:
            return self.values[idx]
        return None

    def search_range(self, min_key: Any, max_key: Any) -> List[Any]:
        """
        Search for keys in range [min_key, max_key]
        Time: O(log n + m) where m is number of results
        """
        left_idx = bisect.bisect_left(self.keys, min_key)
        right_idx = bisect.bisect_right(self.keys, max_key)

        return self.values[left_idx:right_idx]

    def get_sorted(self) -> List[Any]:
        """
        Return all values in sorted key order
        Time: O(1) - already sorted
        """
        return self.values.copy()

    def size_bytes(self) -> int:
        """Estimate memory usage"""
        import sys

        return sys.getsizeof(self.keys) + sys.getsizeof(self.values)


class HashIndex:
    """
    Hash Index Implementation

    Characteristics:
    - O(1) average search, insert
    - No range query support
    - No sorted order
    - Best for equality comparisons
    """

    def __init__(self):
        self.hash_table: Dict[Any, Any] = {}

    def insert(self, key: Any, value: Any):
        """
        Insert key-value pair
        Time: O(1) average
        """
        self.hash_table[key] = value

    def search_exact(self, key: Any) -> Optional[Any]:
        """
        Search for exact key match
        Time: O(1) average
        """
        return self.hash_table.get(key)

    def search_range(self, min_key: Any, max_key: Any) -> List[Any]:
        """
        Range search NOT supported efficiently in hash index
        Must scan all entries: O(n)
        """
        results = []
        for key, value in self.hash_table.items():
            if min_key <= key <= max_key:
                results.append(value)
        return results

    def get_sorted(self) -> List[Any]:
        """
        Sorting NOT supported efficiently in hash index
        Must sort on retrieval: O(n log n)
        """
        sorted_keys = sorted(self.hash_table.keys())
        return [self.hash_table[k] for k in sorted_keys]

    def size_bytes(self) -> int:
        """Estimate memory usage"""
        import sys

        return sys.getsizeof(self.hash_table)


class BitmapIndex:
    """
    Bitmap Index Implementation

    Characteristics:
    - Bit array for each distinct value
    - Excellent for low cardinality columns (few distinct values)
    - Space efficient with compression
    - Fast boolean operations (AND, OR, NOT)
    - Poor for high cardinality
    - Slow updates (entire bitmap changes)

    Best for: OLAP, data warehouses, read-heavy workloads
    """

    def __init__(self):
        self.bitmaps: Dict[Any, List[bool]] = {}  # value -> bitmap
        self.row_count = 0

    def build_from_data(self, column_values: List[Any]):
        """
        Build bitmap index from column values
        """
        self.row_count = len(column_values)
        distinct_values = set(column_values)

        # Initialize bitmaps
        for value in distinct_values:
            self.bitmaps[value] = [False] * self.row_count

        # Set bits
        for row_idx, value in enumerate(column_values):
            self.bitmaps[value][row_idx] = True

    def search_exact(self, value: Any) -> List[int]:
        """
        Search for rows with exact value
        Time: O(n) - scan bitmap
        Returns: List of row indices
        """
        if value not in self.bitmaps:
            return []

        return [idx for idx, bit in enumerate(self.bitmaps[value]) if bit]

    def search_or(self, values: List[Any]) -> List[int]:
        """
        Search for rows matching ANY of the values (OR operation)
        Example: WHERE status='active' OR status='pending'
        """
        result_bitmap = [False] * self.row_count

        for value in values:
            if value in self.bitmaps:
                for idx, bit in enumerate(self.bitmaps[value]):
                    result_bitmap[idx] = result_bitmap[idx] or bit

        return [idx for idx, bit in enumerate(result_bitmap) if bit]

    def search_and(self, value1: Any, value2: Any, bitmap2: "BitmapIndex") -> List[int]:
        """
        Combine with another bitmap index (AND operation)
        Example: WHERE gender='F' AND status='active'
        """
        if value1 not in self.bitmaps or value2 not in bitmap2.bitmaps:
            return []

        result = []
        bitmap1 = self.bitmaps[value1]
        bitmap2_vals = bitmap2.bitmaps[value2]

        for idx in range(min(len(bitmap1), len(bitmap2_vals))):
            if bitmap1[idx] and bitmap2_vals[idx]:
                result.append(idx)

        return result

    def insert(self, value: Any, row_idx: int):
        """
        Insert is SLOW - must update entire bitmap
        This is why bitmap indexes are poor for OLTP
        """
        # Extend all bitmaps if needed
        if row_idx >= self.row_count:
            for bitmap in self.bitmaps.values():
                bitmap.extend([False] * (row_idx - self.row_count + 1))
            self.row_count = row_idx + 1

        # Add new bitmap for new value
        if value not in self.bitmaps:
            self.bitmaps[value] = [False] * self.row_count

        self.bitmaps[value][row_idx] = True

    def size_bytes(self) -> int:
        """Estimate memory usage"""
        import sys

        total = sys.getsizeof(self.bitmaps)
        for bitmap in self.bitmaps.values():
            total += sys.getsizeof(bitmap)
        return total

    def cardinality(self) -> int:
        """Return number of distinct values"""
        return len(self.bitmaps)


# ==================== BENCHMARK FUNCTIONS ====================


def benchmark_btree(data: List[int]) -> IndexStats:
    """Benchmark B-Tree index performance"""
    index = BTreeIndex()

    # Build index
    start = time.perf_counter()
    for i, value in enumerate(data):
        index.insert(value, i)
    build_time = time.perf_counter() - start

    # Equality query
    start = time.perf_counter()
    for _ in range(1000):
        index.search_exact(random.choice(data))
    equality_time = (time.perf_counter() - start) / 1000

    # Range query
    start = time.perf_counter()
    for _ in range(100):
        min_val = random.choice(data)
        max_val = min_val + 1000
        index.search_range(min_val, max_val)
    range_time = (time.perf_counter() - start) / 100

    # Insert
    start = time.perf_counter()
    for _ in range(100):
        index.insert(random.randint(0, 1000000), len(data))
    insert_time = (time.perf_counter() - start) / 100

    return IndexStats(
        build_time=build_time,
        space_bytes=index.size_bytes(),
        equality_query_time=equality_time,
        range_query_time=range_time,
        insert_time=insert_time,
    )


def benchmark_hash(data: List[int]) -> IndexStats:
    """Benchmark Hash index performance"""
    index = HashIndex()

    # Build index
    start = time.perf_counter()
    for i, value in enumerate(data):
        index.insert(value, i)
    build_time = time.perf_counter() - start

    # Equality query
    start = time.perf_counter()
    for _ in range(1000):
        index.search_exact(random.choice(data))
    equality_time = (time.perf_counter() - start) / 1000

    # Range query (inefficient for hash)
    start = time.perf_counter()
    for _ in range(100):
        min_val = random.choice(data)
        max_val = min_val + 1000
        index.search_range(min_val, max_val)
    range_time = (time.perf_counter() - start) / 100

    # Insert
    start = time.perf_counter()
    for _ in range(100):
        index.insert(random.randint(0, 1000000), len(data))
    insert_time = (time.perf_counter() - start) / 100

    return IndexStats(
        build_time=build_time,
        space_bytes=index.size_bytes(),
        equality_query_time=equality_time,
        range_query_time=range_time,
        insert_time=insert_time,
    )


def benchmark_bitmap(data: List[str]) -> IndexStats:
    """Benchmark Bitmap index performance (for low cardinality)"""
    index = BitmapIndex()

    # Build index
    start = time.perf_counter()
    index.build_from_data(data)
    build_time = time.perf_counter() - start

    # Equality query
    distinct_values = list(set(data))
    start = time.perf_counter()
    for _ in range(1000):
        index.search_exact(random.choice(distinct_values))
    equality_time = (time.perf_counter() - start) / 1000

    # OR query (bitmap strength)
    start = time.perf_counter()
    for _ in range(100):
        values = random.sample(distinct_values, min(3, len(distinct_values)))
        index.search_or(values)
    range_time = (time.perf_counter() - start) / 100

    # Insert (slow for bitmap)
    start = time.perf_counter()
    for _ in range(100):
        index.insert(random.choice(distinct_values), len(data))
    insert_time = (time.perf_counter() - start) / 100

    return IndexStats(
        build_time=build_time,
        space_bytes=index.size_bytes(),
        equality_query_time=equality_time,
        range_query_time=range_time,
        insert_time=insert_time,
    )


# ==================== DEMONSTRATION FUNCTIONS ====================


def demo_btree_vs_hash():
    """Compare B-Tree vs Hash for equality queries"""
    print("=" * 80)
    print("DEMO: B-Tree vs Hash Index - Equality Queries")
    print("=" * 80)

    # Generate random data
    data = [random.randint(1, 1000000) for _ in range(100000)]

    print(f"\nDataset: {len(data):,} records")
    print("Running benchmarks...\n")

    # Benchmark B-Tree
    btree_stats = benchmark_btree(data)

    # Benchmark Hash
    hash_stats = benchmark_hash(data)

    # Results
    print(f"{'Metric':<25} {'B-Tree':<15} {'Hash':<15} {'Winner':<10}")
    print("-" * 70)

    print(
        f"{'Build Time':<25} {btree_stats.build_time:>10.4f}s {hash_stats.build_time:>10.4f}s "
        f"{'Hash' if hash_stats.build_time < btree_stats.build_time else 'B-Tree':>10}"
    )

    print(
        f"{'Equality Query':<25} {btree_stats.equality_query_time * 1e6:>10.2f}µs "
        f"{hash_stats.equality_query_time * 1e6:>10.2f}µs "
        f"{'Hash' if hash_stats.equality_query_time < btree_stats.equality_query_time else 'B-Tree':>10}"
    )

    print(
        f"{'Range Query':<25} {btree_stats.range_query_time * 1e3:>10.2f}ms "
        f"{hash_stats.range_query_time * 1e3:>10.2f}ms "
        f"{'B-Tree' if btree_stats.range_query_time < hash_stats.range_query_time else 'Hash':>10}"
    )

    print(
        f"{'Insert':<25} {btree_stats.insert_time * 1e6:>10.2f}µs "
        f"{hash_stats.insert_time * 1e6:>10.2f}µs "
        f"{'Hash' if hash_stats.insert_time < btree_stats.insert_time else 'B-Tree':>10}"
    )

    print(
        f"{'Space':<25} {btree_stats.space_bytes / 1024:>10.1f}KB "
        f"{hash_stats.space_bytes / 1024:>10.1f}KB "
        f"{'Hash' if hash_stats.space_bytes < btree_stats.space_bytes else 'B-Tree':>10}"
    )

    print("\nConclusion:")
    print("  - Hash is faster for equality queries (O(1) vs O(log n))")
    print("  - B-Tree is MUCH faster for range queries")
    print("  - B-Tree supports sorting, Hash does not")
    print("  - Use Hash only if you NEVER need range queries or sorting")


def demo_bitmap_low_cardinality():
    """Demonstrate bitmap index for low cardinality columns"""
    print("\n" + "=" * 80)
    print("DEMO: Bitmap Index - Low Cardinality Columns")
    print("=" * 80)

    # Simulate a users table with low-cardinality columns
    genders = ["M", "F"]
    statuses = ["active", "inactive", "suspended"]

    # Generate 100k users
    gender_data = [random.choice(genders) for _ in range(100000)]
    status_data = [random.choice(statuses) for _ in range(100000)]

    print(f"\nDataset: {len(gender_data):,} records")
    print(f"Gender cardinality: {len(set(gender_data))} (very low)")
    print(f"Status cardinality: {len(set(status_data))} (very low)")

    # Build bitmap indexes
    gender_index = BitmapIndex()
    gender_index.build_from_data(gender_data)

    status_index = BitmapIndex()
    status_index.build_from_data(status_data)

    print("\n--- Bitmap Statistics ---")
    print(f"Gender index size: {gender_index.size_bytes() / 1024:.1f} KB")
    print(f"Status index size: {status_index.size_bytes() / 1024:.1f} KB")

    # Compare with B-Tree
    btree_gender = BTreeIndex()
    for i, gender in enumerate(gender_data):
        btree_gender.insert(gender, i)

    print(f"B-Tree gender size: {btree_gender.size_bytes() / 1024:.1f} KB")
    print(f"Space savings: {(1 - gender_index.size_bytes() / btree_gender.size_bytes()) * 100:.1f}%")

    # Query performance
    print("\n--- Query: WHERE gender='F' ---")

    start = time.perf_counter()
    bitmap_result = gender_index.search_exact("F")
    bitmap_time = time.perf_counter() - start

    start = time.perf_counter()
    btree_result = [v for k, v in zip(btree_gender.keys, btree_gender.values) if k == "F"]
    btree_time = time.perf_counter() - start

    print(f"Bitmap: {len(bitmap_result):,} results in {bitmap_time * 1000:.3f}ms")
    print(f"B-Tree: {len(btree_result):,} results in {btree_time * 1000:.3f}ms")

    # Complex boolean query
    print("\n--- Query: WHERE gender='F' AND status='active' ---")

    start = time.perf_counter()
    result = gender_index.search_and("F", "active", status_index)
    bitmap_and_time = time.perf_counter() - start

    print(f"Bitmap AND: {len(result):,} results in {bitmap_and_time * 1000:.3f}ms")
    print("Bitmap indexes excel at complex boolean queries!")

    print("\n--- Query: WHERE status IN ('active', 'suspended') ---")

    start = time.perf_counter()
    result = status_index.search_or(["active", "suspended"])
    bitmap_or_time = time.perf_counter() - start

    print(f"Bitmap OR: {len(result):,} results in {bitmap_or_time * 1000:.3f}ms")


def demo_index_selection():
    """Demonstrate when to use each index type"""
    print("\n" + "=" * 80)
    print("DEMO: Index Type Selection Guide")
    print("=" * 80)

    scenarios = [
        {
            "scenario": "User lookup by email",
            "query": "SELECT * FROM users WHERE email = 'user@example.com'",
            "cardinality": "High (unique)",
            "pattern": "Equality only",
            "recommended": "Hash or B-Tree",
            "reasoning": "Hash for max speed, B-Tree if you also need sorting",
        },
        {
            "scenario": "Find users by age range",
            "query": "SELECT * FROM users WHERE age BETWEEN 25 AND 35",
            "cardinality": "Medium",
            "pattern": "Range queries",
            "recommended": "B-Tree",
            "reasoning": "B-Tree excels at range queries",
        },
        {
            "scenario": "Filter by gender",
            "query": "SELECT * FROM users WHERE gender = 'F'",
            "cardinality": "Very low (2-3 values)",
            "pattern": "Equality, boolean ops",
            "recommended": "Bitmap (OLAP) or B-Tree (OLTP)",
            "reasoning": "Bitmap if read-heavy analytics, B-Tree if frequent updates",
        },
        {
            "scenario": "Order users by signup date",
            "query": "SELECT * FROM users ORDER BY created_at DESC LIMIT 10",
            "cardinality": "High",
            "pattern": "Sorting",
            "recommended": "B-Tree",
            "reasoning": "B-Tree maintains sort order, Hash cannot sort",
        },
        {
            "scenario": "Analytics: Active female users",
            "query": "SELECT COUNT(*) FROM users WHERE gender='F' AND status='active'",
            "cardinality": "Low (both columns)",
            "pattern": "Complex boolean AND/OR",
            "recommended": "Bitmap",
            "reasoning": "Bitmap indexes can combine with bitwise operations",
        },
        {
            "scenario": "Product catalog search",
            "query": "SELECT * FROM products WHERE category = 'electronics' AND price > 100",
            "cardinality": "Mixed (category: low, price: high)",
            "pattern": "Equality + range",
            "recommended": "Composite B-Tree (category, price)",
            "reasoning": "Single index can handle both conditions efficiently",
        },
    ]

    for i, s in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {s['scenario']} ---")
        print(f"Query:        {s['query']}")
        print(f"Cardinality:  {s['cardinality']}")
        print(f"Pattern:      {s['pattern']}")
        print(f"Recommended:  {s['recommended']}")
        print(f"Reasoning:    {s['reasoning']}")


def demo_composite_index():
    """Demonstrate composite (multi-column) indexes"""
    print("\n" + "=" * 80)
    print("DEMO: Composite Index (Multi-Column)")
    print("=" * 80)

    print("\n--- Index: (city, age) ---")
    print("Index can be used for:")
    print("  ✓ WHERE city = 'NYC'")
    print("  ✓ WHERE city = 'NYC' AND age > 25")
    print("  ✓ WHERE city = 'NYC' AND age = 30")
    print("  ✗ WHERE age > 25  (cannot use index - age not left-most)")

    print("\n--- Index Column Order Matters ---")
    print("Index (city, age):")
    print("  - Sorted first by city, then by age within each city")
    print("  - Like a phone book: Last Name, First Name")

    print("\n--- Covering Index ---")
    print("Index: (email, name, age)")
    print("Query: SELECT name, age FROM users WHERE email = 'user@example.com'")
    print("  → All columns in index (no table lookup needed)")
    print("  → Faster query execution")


if __name__ == "__main__":
    # Run all demos
    demo_btree_vs_hash()
    demo_bitmap_low_cardinality()
    demo_index_selection()
    demo_composite_index()

    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. B-Tree Index (Default):
   - General purpose, handles most use cases
   - Supports: equality, range, sorting, prefix search
   - Time: O(log n) for all operations
   - When: Default choice unless specific reason for other types

2. Hash Index:
   - Fastest for exact matches: O(1)
   - NO support for: range queries, sorting, prefix search
   - When: High-performance key-value lookups, never need ranges

3. Bitmap Index:
   - Best for low cardinality (few distinct values)
   - Excellent for complex boolean queries (AND, OR, NOT)
   - Space efficient with compression
   - Poor for: OLTP (slow updates), high cardinality
   - When: Data warehouses, OLAP, analytics, read-heavy

4. Index Selection Criteria:
   - Query patterns (equality, range, sort)
   - Cardinality (high/low distinct values)
   - Read vs write ratio
   - Space constraints

5. Best Practices:
   - Don't over-index (each index costs storage and write performance)
   - Monitor index usage (remove unused indexes)
   - Composite indexes: left-most prefix rule
   - Covering indexes: include all query columns

Real-World Examples:
- PostgreSQL default: B-Tree (also supports Hash, GIN, GiST, BRIN)
- MySQL InnoDB: B+Tree (clustered primary key)
- Oracle: B-Tree (default), Bitmap (data warehouses)
- Redis: Hash tables for O(1) lookups
    """)
