"""
Database Sharding Strategies Demonstration

This module demonstrates various database sharding techniques used to scale
databases horizontally by distributing data across multiple servers.

Sharding Types:
1. Horizontal Sharding (split rows across databases)
2. Vertical Sharding (split tables/columns across databases)
3. Geo-Based Sharding (split by geographic location)

Sharding Strategies:
- Range-Based Sharding
- Hash-Based Sharding
- Directory-Based Sharding
- Consistent Hashing

Real-World Examples:
- Instagram: Shard by user_id with custom ID generation
- Discord: Cassandra with channel_id partitioning
- Uber: Geo-hash based sharding for location data
"""

import hashlib
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime
import random


class RangeBasedSharding:
    """
    Range-Based Sharding: Distribute data based on key ranges

    Example: user_id 1-1M -> Shard1, 1M-2M -> Shard2, etc.

    Pros:
    - Simple implementation
    - Range queries within shard are efficient
    - Easy to add new ranges

    Cons:
    - Uneven distribution (hotspots)
    - Recent data on same shard (temporal hotspot)
    - Difficult to rebalance existing ranges
    """

    def __init__(self):
        self.shards: Dict[str, Tuple[int, int]] = {}  # shard_name -> (min, max)

    def add_shard(self, shard_name: str, min_id: int, max_id: int):
        """Define a shard with its key range"""
        self.shards[shard_name] = (min_id, max_id)
        print(f"Added {shard_name}: range [{min_id}, {max_id}]")

    def get_shard(self, user_id: int) -> Optional[str]:
        """Find which shard contains the user_id"""
        for shard_name, (min_id, max_id) in self.shards.items():
            if min_id <= user_id <= max_id:
                return shard_name
        return None

    def analyze_distribution(self, user_ids: List[int]) -> Dict[str, int]:
        """Analyze how users are distributed across shards"""
        distribution = defaultdict(int)
        for user_id in user_ids:
            shard = self.get_shard(user_id)
            if shard:
                distribution[shard] += 1
        return dict(distribution)


class HashBasedSharding:
    """
    Hash-Based Sharding: Distribute data using hash function

    Example: shard = hash(user_id) % num_shards

    Pros:
    - Even distribution
    - No hotspots
    - Simple logic

    Cons:
    - Adding/removing shards requires rehashing (expensive)
    - Range queries must check all shards
    - Cross-shard queries are expensive
    """

    def __init__(self, num_shards: int):
        self.num_shards = num_shards
        self.shards = [f"shard_{i}" for i in range(num_shards)]

    def _hash(self, key: str) -> int:
        """Hash function using MD5"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def get_shard(self, key: str) -> str:
        """Determine shard for a given key"""
        return self.shards[self._hash(key) % self.num_shards]

    def analyze_distribution(self, keys: List[str]) -> Dict[str, int]:
        """Analyze key distribution across shards"""
        distribution = defaultdict(int)
        for key in keys:
            shard = self.get_shard(key)
            distribution[shard] += 1
        return dict(distribution)

    def calculate_rehash_impact(self, keys: List[str], new_num_shards: int) -> float:
        """Calculate percentage of keys that move when resharding"""
        new_sharder = HashBasedSharding(new_num_shards)

        moved = 0
        for key in keys:
            old_shard = self.get_shard(key)
            new_shard = new_sharder.get_shard(key)
            if old_shard != new_shard:
                moved += 1

        return (moved / len(keys)) * 100 if keys else 0


class DirectoryBasedSharding:
    """
    Directory-Based Sharding: Use lookup table to map keys to shards

    Example: directory["user_123"] = "shard_2"

    Pros:
    - Flexible routing
    - Easy to move individual records
    - Can implement custom logic

    Cons:
    - Directory is single point of failure
    - Directory itself needs to scale
    - Additional lookup overhead
    """

    def __init__(self):
        self.directory: Dict[str, str] = {}  # key -> shard_name
        self.shards: set = set()

    def add_shard(self, shard_name: str):
        """Add a new shard"""
        self.shards.add(shard_name)
        print(f"Added shard: {shard_name}")

    def assign_key(self, key: str, shard_name: str):
        """Assign a key to a specific shard"""
        if shard_name not in self.shards:
            raise ValueError(f"Shard {shard_name} does not exist")
        self.directory[key] = shard_name

    def get_shard(self, key: str) -> Optional[str]:
        """Lookup shard for a key"""
        return self.directory.get(key)

    def move_key(self, key: str, new_shard: str):
        """Move a key to a different shard (for rebalancing)"""
        if new_shard not in self.shards:
            raise ValueError(f"Shard {new_shard} does not exist")
        old_shard = self.directory.get(key)
        self.directory[key] = new_shard
        print(f"Moved {key}: {old_shard} -> {new_shard}")

    def analyze_distribution(self) -> Dict[str, int]:
        """Analyze key distribution across shards"""
        distribution = defaultdict(int)
        for shard in self.directory.values():
            distribution[shard] += 1
        return dict(distribution)


class GeoBasedSharding:
    """
    Geo-Based Sharding: Distribute data by geographic region

    Benefits:
    - Low latency (data close to users)
    - Data residency compliance (GDPR, etc.)
    - Natural isolation by region

    Challenges:
    - Cross-region queries are slow
    - User migration (if user moves)
    - Uneven distribution (population differences)
    """

    def __init__(self):
        self.region_shards: Dict[str, str] = {}  # country_code -> shard_name
        self.shards: set = set()

    def add_shard(self, shard_name: str, countries: List[str]):
        """Create a regional shard for specific countries"""
        self.shards.add(shard_name)
        for country in countries:
            self.region_shards[country] = shard_name
        print(f"Added {shard_name} for countries: {countries}")

    def get_shard(self, country_code: str) -> Optional[str]:
        """Find shard for a country"""
        return self.region_shards.get(country_code, "shard_default")

    def analyze_distribution(self, user_countries: List[str]) -> Dict[str, int]:
        """Analyze user distribution across regional shards"""
        distribution = defaultdict(int)
        for country in user_countries:
            shard = self.get_shard(country)
            distribution[shard] += 1
        return dict(distribution)


class InstagramStyleSharding:
    """
    Instagram-Style ID-Based Sharding

    Instagram generates 64-bit IDs with embedded shard information:
    - 41 bits: Timestamp (milliseconds since epoch)
    - 13 bits: Shard ID (8192 shards)
    - 10 bits: Auto-increment sequence (1024 per ms per shard)

    Benefits:
    - IDs are time-sortable
    - Shard information embedded in ID
    - No central ID generator needed
    - Guaranteed uniqueness across shards
    """

    EPOCH = 1609459200000  # Jan 1, 2021 00:00:00 UTC in milliseconds

    def __init__(self, shard_id: int):
        if shard_id >= 2**13:
            raise ValueError("Shard ID must be less than 8192 (13 bits)")
        self.shard_id = shard_id
        self.sequence = 0

    def generate_id(self, timestamp_ms: Optional[int] = None) -> int:
        """
        Generate a 64-bit ID with embedded shard information

        Format: [41-bit timestamp][13-bit shard_id][10-bit sequence]
        """
        if timestamp_ms is None:
            timestamp_ms = int(datetime.now().timestamp() * 1000)

        # Calculate timestamp offset from epoch
        timestamp = timestamp_ms - self.EPOCH

        # Increment sequence (wrap around at 1024)
        self.sequence = (self.sequence + 1) % 1024

        # Combine: timestamp(41) | shard_id(13) | sequence(10)
        photo_id = (timestamp << 23) | (self.shard_id << 10) | self.sequence

        return photo_id

    @staticmethod
    def extract_shard_id(photo_id: int) -> int:
        """Extract shard ID from a photo ID"""
        return (photo_id >> 10) & 0x1FFF  # 13 bits

    @staticmethod
    def extract_timestamp(photo_id: int) -> int:
        """Extract timestamp from a photo ID"""
        timestamp = (photo_id >> 23) + InstagramStyleSharding.EPOCH
        return timestamp

    @staticmethod
    def get_shard_from_id(photo_id: int) -> str:
        """Determine which shard stores this photo"""
        shard_id = InstagramStyleSharding.extract_shard_id(photo_id)
        return f"shard_{shard_id}"


class ShardingCoordinator:
    """
    High-level coordinator for managing multiple sharding strategies

    Demonstrates how an application might route queries to appropriate shards
    """

    def __init__(self, strategy: str, **kwargs):
        self.strategy = strategy
        if strategy == "range":
            self.sharder = RangeBasedSharding()
        elif strategy == "hash":
            self.sharder = HashBasedSharding(kwargs.get("num_shards", 4))
        elif strategy == "directory":
            self.sharder = DirectoryBasedSharding()
        elif strategy == "geo":
            self.sharder = GeoBasedSharding()
        else:
            raise ValueError(f"Unknown sharding strategy: {strategy}")

    def route_query(self, key: Any) -> Optional[str]:
        """Route a query to the appropriate shard"""
        return self.sharder.get_shard(key)


# ==================== DEMONSTRATION FUNCTIONS ====================


def demo_range_sharding():
    """Demonstrate range-based sharding with hotspot issues"""
    print("=" * 80)
    print("DEMO: Range-Based Sharding")
    print("=" * 80)

    sharder = RangeBasedSharding()

    # Set up shards
    sharder.add_shard("shard_1", 1, 1_000_000)
    sharder.add_shard("shard_2", 1_000_001, 2_000_000)
    sharder.add_shard("shard_3", 2_000_001, 3_000_000)
    sharder.add_shard("shard_4", 3_000_001, 4_000_000)

    # Simulate users (biased towards recent IDs - common in reality)
    # 70% of users in most recent range (hotspot)
    recent_bias_users = (
        [random.randint(1, 1_000_000) for _ in range(100)]
        + [random.randint(1_000_001, 2_000_000) for _ in range(150)]
        + [random.randint(2_000_001, 3_000_000) for _ in range(250)]
        + [random.randint(3_000_001, 4_000_000) for _ in range(700)]
    )

    distribution = sharder.analyze_distribution(recent_bias_users)

    print("\n--- User Distribution (Recent Bias - Hotspot Issue) ---")
    for shard, count in sorted(distribution.items()):
        percentage = (count / len(recent_bias_users)) * 100
        bar = "█" * (count // 10)
        print(f"{shard}: {count:4d} users ({percentage:5.1f}%) {bar}")

    print("\nProblem: shard_4 has 70% of load (temporal hotspot)")
    print("Solution: Use hash-based or consistent hashing")


def demo_hash_sharding():
    """Demonstrate hash-based sharding and rehashing cost"""
    print("\n" + "=" * 80)
    print("DEMO: Hash-Based Sharding")
    print("=" * 80)

    # Initial setup with 4 shards
    sharder = HashBasedSharding(num_shards=4)

    users = [f"user_{i}" for i in range(10000)]

    distribution = sharder.analyze_distribution(users)

    print("\n--- User Distribution (4 shards) ---")
    for shard, count in sorted(distribution.items()):
        percentage = (count / len(users)) * 100
        bar = "█" * (count // 50)
        print(f"{shard}: {count:4d} users ({percentage:5.1f}%) {bar}")

    print("\nObservation: Even distribution across shards")

    # Simulate adding a shard (rehashing required)
    print("\n--- Adding New Shard (4 -> 5 shards) ---")
    rehash_percentage = sharder.calculate_rehash_impact(users, new_num_shards=5)
    print(f"Keys that need to move: {rehash_percentage:.1f}%")
    print("Problem: Most keys need to be redistributed!")
    print("Solution: Use consistent hashing to minimize movement")


def demo_geo_sharding():
    """Demonstrate geographic sharding for global applications"""
    print("\n" + "=" * 80)
    print("DEMO: Geo-Based Sharding (Global Social Network)")
    print("=" * 80)

    sharder = GeoBasedSharding()

    # Set up regional shards
    sharder.add_shard("shard_us_east", ["US", "CA", "MX"])
    sharder.add_shard("shard_eu_west", ["GB", "FR", "DE", "IT", "ES"])
    sharder.add_shard("shard_asia_pacific", ["JP", "CN", "IN", "AU", "SG"])
    sharder.add_shard("shard_south_america", ["BR", "AR", "CL"])

    # Simulate user distribution
    user_countries = (
        ["US"] * 300
        + ["GB"] * 150
        + ["FR"] * 100
        + ["DE"] * 120
        + ["JP"] * 180
        + ["CN"] * 250
        + ["IN"] * 200
        + ["BR"] * 80
        + ["CA"] * 50
        + ["AU"] * 70
    )

    distribution = sharder.analyze_distribution(user_countries)

    print("\n--- User Distribution by Region ---")
    for shard, count in sorted(distribution.items(), key=lambda x: -x[1]):
        percentage = (count / len(user_countries)) * 100
        bar = "█" * (count // 10)
        print(f"{shard}: {count:4d} users ({percentage:5.1f}%) {bar}")

    print("\nBenefits:")
    print("  - Low latency (users access nearby shard)")
    print("  - GDPR compliance (EU data stays in EU)")
    print("  - Regional failure isolation")

    print("\nChallenges:")
    print("  - Cross-region queries (e.g., global search) are expensive")
    print("  - User migration if they move countries")


def demo_instagram_sharding():
    """Demonstrate Instagram's ID-based sharding approach"""
    print("\n" + "=" * 80)
    print("DEMO: Instagram-Style ID Generation & Sharding")
    print("=" * 80)

    # Create ID generators for different shards
    shard_generators = {
        0: InstagramStyleSharding(shard_id=0),
        100: InstagramStyleSharding(shard_id=100),
        500: InstagramStyleSharding(shard_id=500),
    }

    print("\n--- Generated Photo IDs ---")
    for shard_id, generator in shard_generators.items():
        photo_id = generator.generate_id()
        extracted_shard = InstagramStyleSharding.extract_shard_id(photo_id)
        timestamp = InstagramStyleSharding.extract_timestamp(photo_id)
        dt = datetime.fromtimestamp(timestamp / 1000)

        print(f"\nShard {shard_id}:")
        print(f"  Photo ID: {photo_id}")
        print(f"  Extracted Shard ID: {extracted_shard}")
        print(f"  Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Shard Location: {InstagramStyleSharding.get_shard_from_id(photo_id)}")

    print("\n--- Benefits of This Approach ---")
    print("  ✓ IDs are time-sortable (can ORDER BY id for chronological feed)")
    print("  ✓ Shard information embedded (no lookup needed)")
    print("  ✓ Decentralized ID generation (no single point of failure)")
    print("  ✓ Guaranteed uniqueness across all shards")
    print("  ✓ Can handle 8192 shards with 1024 IDs/ms/shard")


def demo_cross_shard_challenges():
    """Demonstrate challenges with cross-shard operations"""
    print("\n" + "=" * 80)
    print("DEMO: Cross-Shard Query Challenges")
    print("=" * 80)

    sharder = HashBasedSharding(num_shards=4)

    # Users distributed across shards
    users = {f"user_{i}": {"id": f"user_{i}", "name": f"User {i}", "age": random.randint(18, 65)} for i in range(20)}

    # Posts distributed across shards (by post_id, not user_id)
    posts = {
        f"post_{i}": {"id": f"post_{i}", "user_id": f"user_{random.randint(0, 19)}", "content": f"Post {i}"}
        for i in range(50)
    }

    print("\n--- Scenario: JOIN users and posts ---")
    print("SQL Query: SELECT u.name, p.content FROM users u JOIN posts p ON u.id = p.user_id")

    # Show which shards contain which data
    user_distribution = defaultdict(list)
    post_distribution = defaultdict(list)

    for user_id in users.keys():
        shard = sharder.get_shard(user_id)
        user_distribution[shard].append(user_id)

    for post_id, post in posts.items():
        shard = sharder.get_shard(post_id)
        post_distribution[shard].append(post_id)

    print("\n--- Users Distribution ---")
    for shard in sorted(user_distribution.keys()):
        print(f"{shard}: {len(user_distribution[shard])} users")

    print("\n--- Posts Distribution ---")
    for shard in sorted(post_distribution.keys()):
        print(f"{shard}: {len(post_distribution[shard])} posts")

    print("\n--- Problem ---")
    print("Users and posts are on different shards (sharded by different keys)")
    print("Cannot do efficient JOIN - need to query all shards!")

    print("\n--- Solutions ---")
    print("1. Denormalization: Include user info in posts table")
    print("   posts: {id, user_id, user_name, content}")
    print("   Trade-off: Duplicate data, but single-shard queries")

    print("\n2. Application-Level Join:")
    print("   - Query user shard for user data")
    print("   - Query all post shards for user's posts")
    print("   - Merge in application")
    print("   Trade-off: Multiple queries, application complexity")

    print("\n3. Co-location: Shard both by user_id")
    print("   - All user's data on same shard")
    print("   Trade-off: May not work for all access patterns")


def demo_resharding_strategies():
    """Demonstrate strategies for adding/removing shards"""
    print("\n" + "=" * 80)
    print("DEMO: Resharding Strategies")
    print("=" * 80)

    print("\n--- Strategy 1: Stop-the-World (Offline) ---")
    print("1. Take database offline")
    print("2. Redistribute all data to new shards")
    print("3. Update routing configuration")
    print("4. Bring database online")
    print("\nPros: Simple, consistent")
    print("Cons: Downtime (unacceptable for most services)")

    print("\n--- Strategy 2: Dual-Write (Online) ---")
    print("1. Add new shards")
    print("2. Start writing to BOTH old and new shards")
    print("3. Backfill data from old to new shards")
    print("4. Switch reads to new shards")
    print("5. Stop writing to old shards")
    print("6. Decommission old shards")
    print("\nPros: No downtime")
    print("Cons: Complex, temporary dual-write overhead")

    print("\n--- Strategy 3: Consistent Hashing (Minimal Movement) ---")
    print("1. Use consistent hashing from the start")
    print("2. Adding shard: Only ~1/n data moves")
    print("3. Removing shard: Only affected keys move")
    print("\nPros: Minimal data movement, predictable")
    print("Cons: Requires initial setup, some movement still needed")

    print("\n--- Strategy 4: Virtual Shards (Logical Shards) ---")
    print("1. Create many virtual shards (e.g., 1024)")
    print("2. Map virtual shards to physical shards")
    print("3. Resharding = move virtual shards between physical shards")
    print("\nExample: 1024 virtual shards -> 4 physical shards (256 each)")
    print("         Add 5th physical shard -> move 51 virtual shards to it")
    print("\nPros: Fine-grained control, easier rebalancing")
    print("Cons: Additional mapping layer")


if __name__ == "__main__":
    # Run all demos
    demo_range_sharding()
    demo_hash_sharding()
    demo_geo_sharding()
    demo_instagram_sharding()
    demo_cross_shard_challenges()
    demo_resharding_strategies()

    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. Sharding is necessary when single database can't handle load/storage

2. Sharding Strategy Selection:
   - Range: Simple but prone to hotspots
   - Hash: Even distribution but expensive to reshard
   - Geo: Great for global apps, compliance
   - Consistent Hash: Best for elastic scaling

3. Shard Key Selection is Critical:
   - High cardinality (many unique values)
   - Even distribution
   - Aligns with query patterns
   - Examples: user_id (good), status (bad)

4. Cross-Shard Operations are Expensive:
   - Avoid JOINs across shards
   - Use denormalization
   - Consider co-location

5. Plan for Resharding:
   - Growth is inevitable
   - Choose strategy that supports resharding
   - Virtual shards provide flexibility

Real-World Examples:
- Instagram: 64-bit IDs with embedded shard info
- Discord: Cassandra partitioned by channel_id
- Uber: Geo-hash sharding for location data
- Pinterest: Shard by user_id with MySQL
    """)
