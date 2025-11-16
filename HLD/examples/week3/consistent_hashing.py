"""
Consistent Hashing Implementation with Virtual Nodes

This module demonstrates consistent hashing, a technique used in distributed systems
to minimize data movement when nodes are added or removed.

Key Concepts:
- Hash Ring: Maps both keys and servers to a circular space
- Virtual Nodes: Multiple positions per physical server for better distribution
- Minimal Disruption: Only K/n keys move when adding/removing a server (K=total keys, n=servers)

Real-World Usage:
- Distributed caches (Memcached, Redis Cluster)
- Load balancers (consistent session routing)
- Distributed databases (DynamoDB, Cassandra)
- CDNs (routing requests to edge servers)
"""

import hashlib
import bisect
from typing import Dict, List, Optional, Set
from collections import defaultdict


class SimpleHash:
    """Simple modulo-based hashing (traditional approach)"""

    def __init__(self, num_servers: int):
        self.num_servers = num_servers

    def get_server(self, key: str) -> int:
        """
        Traditional hash: server = hash(key) % num_servers

        Problem: When num_servers changes, most keys rehash to different servers
        Example: 3 servers -> 4 servers = 75% of keys move
        """
        return hash(key) % self.num_servers

    def calculate_redistribution(self, old_num_servers: int, new_num_servers: int, keys: List[str]) -> float:
        """Calculate percentage of keys that move when servers change"""
        old_hash = SimpleHash(old_num_servers)
        new_hash = SimpleHash(new_num_servers)

        moved = 0
        for key in keys:
            if old_hash.get_server(key) != new_hash.get_server(key):
                moved += 1

        return (moved / len(keys)) * 100 if keys else 0


class ConsistentHash:
    """
    Consistent Hashing without Virtual Nodes

    Uses a hash ring where both servers and keys are hashed to positions.
    Each key is assigned to the first server clockwise on the ring.
    """

    def __init__(self):
        self.ring: Dict[int, str] = {}  # hash_position -> server_name
        self.sorted_keys: List[int] = []  # sorted hash positions

    def _hash(self, key: str) -> int:
        """Hash function that maps to 32-bit space"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)

    def add_server(self, server: str):
        """Add a server to the hash ring"""
        hash_val = self._hash(server)
        self.ring[hash_val] = server
        bisect.insort(self.sorted_keys, hash_val)
        print(f"Added server '{server}' at position {hash_val}")

    def remove_server(self, server: str):
        """Remove a server from the hash ring"""
        hash_val = self._hash(server)
        if hash_val in self.ring:
            del self.ring[hash_val]
            self.sorted_keys.remove(hash_val)
            print(f"Removed server '{server}' from position {hash_val}")

    def get_server(self, key: str) -> Optional[str]:
        """
        Find the server responsible for a key.
        Returns the first server clockwise from the key's hash position.
        """
        if not self.ring:
            return None

        hash_val = self._hash(key)

        # Binary search for first server >= hash_val
        idx = bisect.bisect(self.sorted_keys, hash_val)

        if idx == len(self.sorted_keys):
            # Wrap around to first server
            idx = 0

        return self.ring[self.sorted_keys[idx]]

    def get_distribution(self, keys: List[str]) -> Dict[str, int]:
        """Analyze key distribution across servers"""
        distribution = defaultdict(int)
        for key in keys:
            server = self.get_server(key)
            if server:
                distribution[server] += 1
        return dict(distribution)

    def calculate_moves(self, keys: List[str], old_mapping: Dict[str, str]) -> int:
        """Calculate how many keys moved after a server change"""
        moves = 0
        for key in keys:
            new_server = self.get_server(key)
            if key in old_mapping and old_mapping[key] != new_server:
                moves += 1
        return moves


class ConsistentHashWithVNodes:
    """
    Consistent Hashing with Virtual Nodes

    Each physical server is mapped to multiple positions on the ring (virtual nodes).
    This provides:
    - More even distribution of keys
    - Better load balancing
    - Smoother rebalancing when servers are added/removed

    Industry Standard: 150-200 virtual nodes per physical server
    """

    def __init__(self, num_vnodes: int = 150):
        self.num_vnodes = num_vnodes
        self.ring: Dict[int, str] = {}  # hash_position -> physical_server
        self.sorted_keys: List[int] = []
        self.servers: Set[str] = set()

    def _hash(self, key: str) -> int:
        """Hash function that maps to 32-bit space"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)

    def add_server(self, server: str):
        """
        Add a server to the hash ring with multiple virtual nodes.

        For each virtual node, we create a unique hash position by appending
        a virtual node index to the server name.
        """
        self.servers.add(server)
        for i in range(self.num_vnodes):
            vnode_key = f"{server}:vnode{i}"
            hash_val = self._hash(vnode_key)
            self.ring[hash_val] = server
            bisect.insort(self.sorted_keys, hash_val)

        print(f"Added server '{server}' with {self.num_vnodes} virtual nodes")

    def remove_server(self, server: str):
        """Remove a server and all its virtual nodes from the ring"""
        if server not in self.servers:
            return

        self.servers.remove(server)
        # Remove all virtual nodes for this server
        positions_to_remove = [pos for pos, srv in self.ring.items() if srv == server]

        for pos in positions_to_remove:
            del self.ring[pos]
            self.sorted_keys.remove(pos)

        print(f"Removed server '{server}' and its {len(positions_to_remove)} virtual nodes")

    def get_server(self, key: str) -> Optional[str]:
        """Find the server responsible for a key"""
        if not self.ring:
            return None

        hash_val = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_val)

        if idx == len(self.sorted_keys):
            idx = 0

        return self.ring[self.sorted_keys[idx]]

    def get_distribution(self, keys: List[str]) -> Dict[str, int]:
        """Analyze key distribution across physical servers"""
        distribution = defaultdict(int)
        for key in keys:
            server = self.get_server(key)
            if server:
                distribution[server] += 1
        return dict(distribution)

    def calculate_moves(self, keys: List[str], old_mapping: Dict[str, str]) -> int:
        """Calculate how many keys moved after a server change"""
        moves = 0
        for key in keys:
            new_server = self.get_server(key)
            if key in old_mapping and old_mapping[key] != new_server:
                moves += 1
        return moves

    def get_load_balance_stats(self, keys: List[str]) -> Dict[str, any]:
        """Calculate load balancing statistics"""
        distribution = self.get_distribution(keys)

        if not distribution:
            return {}

        counts = list(distribution.values())
        avg = sum(counts) / len(counts)
        max_load = max(counts)
        min_load = min(counts)
        std_dev = (sum((x - avg) ** 2 for x in counts) / len(counts)) ** 0.5

        return {
            "average": avg,
            "max": max_load,
            "min": min_load,
            "std_dev": std_dev,
            "balance_ratio": min_load / max_load if max_load > 0 else 0,
        }


def demo_simple_vs_consistent():
    """Demonstrate the problem with simple hashing vs consistent hashing"""
    print("=" * 80)
    print("DEMO: Simple Hashing vs Consistent Hashing")
    print("=" * 80)

    # Generate sample keys
    keys = [f"key_{i}" for i in range(1000)]

    # Simple Hashing
    print("\n--- Simple Hashing (Modulo) ---")
    simple_3 = SimpleHash(3)
    redistribution = simple_3.calculate_redistribution(3, 4, keys)
    print(f"Adding 1 server (3 -> 4): {redistribution:.1f}% of keys move")

    redistribution = simple_3.calculate_redistribution(4, 3, keys)
    print(f"Removing 1 server (4 -> 3): {redistribution:.1f}% of keys move")

    # Consistent Hashing
    print("\n--- Consistent Hashing ---")
    ch = ConsistentHash()
    ch.add_server("server1")
    ch.add_server("server2")
    ch.add_server("server3")

    # Get initial mapping
    old_mapping = {key: ch.get_server(key) for key in keys}

    # Add a server
    ch.add_server("server4")
    moves = ch.calculate_moves(keys, old_mapping)
    print(f"Adding server4: {(moves / len(keys)) * 100:.1f}% of keys move ({moves}/{len(keys)})")

    # Update mapping
    old_mapping = {key: ch.get_server(key) for key in keys}

    # Remove a server
    ch.remove_server("server2")
    moves = ch.calculate_moves(keys, old_mapping)
    print(f"Removing server2: {(moves / len(keys)) * 100:.1f}% of keys move ({moves}/{len(keys)})")


def demo_virtual_nodes():
    """Demonstrate the benefit of virtual nodes for load balancing"""
    print("\n" + "=" * 80)
    print("DEMO: Consistent Hashing WITHOUT Virtual Nodes")
    print("=" * 80)

    keys = [f"key_{i}" for i in range(10000)]

    # Without virtual nodes
    ch_no_vnodes = ConsistentHash()
    for i in range(4):
        ch_no_vnodes.add_server(f"server{i}")

    distribution = ch_no_vnodes.get_distribution(keys)
    print("\nKey Distribution (No Virtual Nodes):")
    for server, count in sorted(distribution.items()):
        bar = "█" * (count // 50)
        print(f"  {server}: {count:5d} keys {bar}")

    avg = sum(distribution.values()) / len(distribution)
    max_load = max(distribution.values())
    min_load = min(distribution.values())
    print(f"\n  Average: {avg:.0f}, Min: {min_load}, Max: {max_load}")
    print(f"  Load Balance Ratio: {min_load / max_load:.2f} (closer to 1.0 is better)")

    # With virtual nodes
    print("\n" + "=" * 80)
    print("DEMO: Consistent Hashing WITH Virtual Nodes (150 vnodes per server)")
    print("=" * 80)

    ch_vnodes = ConsistentHashWithVNodes(num_vnodes=150)
    for i in range(4):
        ch_vnodes.add_server(f"server{i}")

    distribution = ch_vnodes.get_distribution(keys)
    print("\nKey Distribution (With Virtual Nodes):")
    for server, count in sorted(distribution.items()):
        bar = "█" * (count // 50)
        print(f"  {server}: {count:5d} keys {bar}")

    stats = ch_vnodes.get_load_balance_stats(keys)
    print(f"\n  Average: {stats['average']:.0f}, Min: {stats['min']}, Max: {stats['max']}")
    print(f"  Standard Deviation: {stats['std_dev']:.2f}")
    print(f"  Load Balance Ratio: {stats['balance_ratio']:.2f} (closer to 1.0 is better)")


def demo_real_world_scenario():
    """Simulate a real-world caching scenario"""
    print("\n" + "=" * 80)
    print("DEMO: Real-World Scenario - Distributed Cache")
    print("=" * 80)
    print("\nScenario: Memcached cluster with 5 servers caching user sessions")

    # Simulate cache with 50,000 user sessions
    user_sessions = [f"session_{i}" for i in range(50000)]

    ch = ConsistentHashWithVNodes(num_vnodes=150)

    # Initial cluster
    print("\n1. Initial cluster setup (5 servers):")
    for i in range(1, 6):
        ch.add_server(f"cache-server-{i}")

    old_mapping = {session: ch.get_server(session) for session in user_sessions}
    initial_dist = ch.get_distribution(user_sessions)

    print("\n   Initial Distribution:")
    for server, count in sorted(initial_dist.items()):
        percentage = (count / len(user_sessions)) * 100
        print(f"     {server}: {count:6d} sessions ({percentage:5.2f}%)")

    # Scale up: Add 2 servers
    print("\n2. Scale up: Adding 2 more servers (5 -> 7 servers)")
    ch.add_server("cache-server-6")
    ch.add_server("cache-server-7")

    moves = ch.calculate_moves(user_sessions, old_mapping)
    print(f"\n   Keys moved: {moves} ({(moves / len(user_sessions)) * 100:.2f}%)")
    print(f"   Theoretical minimum: {len(user_sessions) / 5 * 2:.0f} ({(2 / 7) * 100:.2f}%)")

    new_dist = ch.get_distribution(user_sessions)
    print("\n   New Distribution:")
    for server, count in sorted(new_dist.items()):
        percentage = (count / len(user_sessions)) * 100
        print(f"     {server}: {count:6d} sessions ({percentage:5.2f}%)")

    # Update mapping
    old_mapping = {session: ch.get_server(session) for session in user_sessions}

    # Server failure: Remove 1 server
    print("\n3. Server failure: cache-server-3 crashes")
    ch.remove_server("cache-server-3")

    moves = ch.calculate_moves(user_sessions, old_mapping)
    print(f"\n   Keys redistributed: {moves} ({(moves / len(user_sessions)) * 100:.2f}%)")
    print(f"   Theoretical: ~{len(user_sessions) / 7:.0f} ({(1 / 7) * 100:.2f}%)")

    final_dist = ch.get_distribution(user_sessions)
    print("\n   Final Distribution (6 servers):")
    for server, count in sorted(final_dist.items()):
        percentage = (count / len(user_sessions)) * 100
        print(f"     {server}: {count:6d} sessions ({percentage:5.2f}%)")

    stats = ch.get_load_balance_stats(user_sessions)
    print(f"\n   Load Balance Ratio: {stats['balance_ratio']:.3f}")
    print(f"   Standard Deviation: {stats['std_dev']:.2f}")


def demo_vnode_comparison():
    """Compare different numbers of virtual nodes"""
    print("\n" + "=" * 80)
    print("DEMO: Impact of Virtual Node Count on Load Balancing")
    print("=" * 80)

    keys = [f"key_{i}" for i in range(10000)]
    vnode_counts = [1, 10, 50, 150, 500]

    print(f"\nServers: 5, Keys: {len(keys)}\n")
    print(f"{'VNodes':<10} {'Min':<8} {'Max':<8} {'Avg':<8} {'StdDev':<10} {'Balance':<10}")
    print("-" * 70)

    for vnode_count in vnode_counts:
        ch = ConsistentHashWithVNodes(num_vnodes=vnode_count)
        for i in range(5):
            ch.add_server(f"server{i}")

        stats = ch.get_load_balance_stats(keys)
        print(
            f"{vnode_count:<10} {stats['min']:<8} {stats['max']:<8} "
            f"{stats['average']:<8.1f} {stats['std_dev']:<10.2f} {stats['balance_ratio']:<10.3f}"
        )

    print("\nObservation: More virtual nodes = better distribution, but diminishing returns after ~150")


if __name__ == "__main__":
    # Run all demos
    demo_simple_vs_consistent()
    demo_virtual_nodes()
    demo_vnode_comparison()
    demo_real_world_scenario()

    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. Simple hashing (modulo) causes ~75% key movement when servers change
2. Consistent hashing reduces movement to ~1/n (n = number of servers)
3. Virtual nodes improve load distribution significantly
4. Industry standard: 150-200 virtual nodes per physical server
5. Trade-off: More vnodes = better distribution but more memory overhead

Real-World Applications:
- Amazon DynamoDB: Consistent hashing for partition placement
- Apache Cassandra: Token ring with ~256 virtual nodes per server
- Redis Cluster: Hash slots (16384) mapped to nodes
- Memcached clients: Consistent hashing for server selection
- Load Balancers: Session affinity with consistent hashing
    """)
