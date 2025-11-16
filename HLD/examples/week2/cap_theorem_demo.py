"""
CAP Theorem Demonstration

Demonstrates the CAP theorem trade-offs:
- Consistency (C): All nodes see the same data
- Availability (A): Every request gets a response
- Partition Tolerance (P): System works despite network failures

In distributed systems, you can only guarantee 2 out of 3.
In practice, partition tolerance is mandatory, so choose between CP or AP.
"""

import time
import random
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import threading


class NodeState(Enum):
    """State of a node in the system."""
    HEALTHY = "healthy"
    PARTITIONED = "partitioned"
    DOWN = "down"


@dataclass
class DataItem:
    """Represents a data item with version."""
    key: str
    value: Any
    version: int = 1
    timestamp: float = field(default_factory=time.time)

    def __repr__(self):
        return f"DataItem({self.key}={self.value}, v{self.version})"


class Node:
    """Represents a node in a distributed system."""

    def __init__(self, node_id: str, latency_ms: int = 50):
        self.node_id = node_id
        self.latency_ms = latency_ms
        self.state = NodeState.HEALTHY
        self.data: Dict[str, DataItem] = {}
        self.read_count = 0
        self.write_count = 0
        self.rejected_count = 0

    def read(self, key: str) -> Optional[DataItem]:
        """Read data from this node."""
        time.sleep(self.latency_ms / 1000.0)
        self.read_count += 1

        if self.state == NodeState.DOWN:
            return None

        return self.data.get(key)

    def write(self, key: str, value: Any, version: int = 1) -> bool:
        """Write data to this node."""
        time.sleep(self.latency_ms / 1000.0)

        if self.state == NodeState.DOWN:
            return False

        self.write_count += 1
        self.data[key] = DataItem(key, value, version)
        return True

    def can_communicate_with(self, other_node: 'Node') -> bool:
        """Check if this node can communicate with another node."""
        if self.state == NodeState.DOWN or other_node.state == NodeState.DOWN:
            return False

        if self.state == NodeState.PARTITIONED or other_node.state == NodeState.PARTITIONED:
            return False

        return True

    def set_state(self, state: NodeState):
        """Set node state."""
        self.state = state

    def get_stats(self) -> dict:
        """Get node statistics."""
        return {
            "node_id": self.node_id,
            "state": self.state.value,
            "data_items": len(self.data),
            "reads": self.read_count,
            "writes": self.write_count,
            "rejected": self.rejected_count
        }

    def __repr__(self):
        return f"Node({self.node_id}, {self.state.value})"


# ============================================================================
# CP System: Consistency + Partition Tolerance (Sacrifice Availability)
# ============================================================================

class CPSystem:
    """
    CP System: Prioritizes Consistency and Partition Tolerance

    - Strong consistency: All nodes see same data
    - Partition tolerant: Handles network partitions
    - May reject requests to maintain consistency (sacrifice availability)

    Examples: MongoDB, HBase, ZooKeeper, Redis (sync replication)
    Use Case: Financial transactions, inventory management
    """

    def __init__(self, nodes: List[Node], quorum_size: int = 2):
        """
        Initialize CP system.

        Args:
            nodes: List of nodes
            quorum_size: Number of nodes needed for quorum (majority)
        """
        self.nodes = nodes
        self.quorum_size = quorum_size
        self.total_reads = 0
        self.total_writes = 0
        self.rejected_reads = 0
        self.rejected_writes = 0

    def read(self, key: str) -> Optional[Any]:
        """
        Read with strong consistency.

        Requires quorum of nodes to respond.
        Rejects request if quorum not available.
        """
        self.total_reads += 1

        # Get healthy, reachable nodes
        available_nodes = [n for n in self.nodes if n.state == NodeState.HEALTHY]

        # Check if we have quorum
        if len(available_nodes) < self.quorum_size:
            self.rejected_reads += 1
            print(f"   ✗ Read rejected: Quorum not available ({len(available_nodes)}/{self.quorum_size})")
            return None

        # Read from quorum nodes
        values = []
        for node in available_nodes[:self.quorum_size]:
            data = node.read(key)
            if data:
                values.append(data)

        if not values:
            return None

        # Return most recent version (strong consistency)
        latest = max(values, key=lambda d: d.version)
        print(f"   ✓ Read successful: {key}={latest.value} (v{latest.version})")
        return latest.value

    def write(self, key: str, value: Any) -> bool:
        """
        Write with strong consistency.

        Requires quorum of nodes to acknowledge.
        Rejects request if quorum not available.
        """
        self.total_writes += 1

        # Get healthy, reachable nodes
        available_nodes = [n for n in self.nodes if n.state == NodeState.HEALTHY]

        # Check if we have quorum
        if len(available_nodes) < self.quorum_size:
            self.rejected_writes += 1
            print(f"   ✗ Write rejected: Quorum not available ({len(available_nodes)}/{self.quorum_size})")
            return False

        # Get next version
        version = 1
        existing = available_nodes[0].read(key)
        if existing:
            version = existing.version + 1

        # Write to quorum nodes
        success_count = 0
        for node in available_nodes:
            if node.write(key, value, version):
                success_count += 1

        if success_count >= self.quorum_size:
            print(f"   ✓ Write successful: {key}={value} to {success_count} nodes")
            return True
        else:
            self.rejected_writes += 1
            print(f"   ✗ Write failed: Only {success_count}/{self.quorum_size} nodes acknowledged")
            return False

    def get_stats(self) -> dict:
        """Get system statistics."""
        availability = ((self.total_reads + self.total_writes - self.rejected_reads - self.rejected_writes) /
                       max(1, self.total_reads + self.total_writes) * 100)

        return {
            "system_type": "CP (Consistency + Partition Tolerance)",
            "total_reads": self.total_reads,
            "total_writes": self.total_writes,
            "rejected_reads": self.rejected_reads,
            "rejected_writes": self.rejected_writes,
            "availability": f"{availability:.1f}%"
        }


# ============================================================================
# AP System: Availability + Partition Tolerance (Sacrifice Consistency)
# ============================================================================

class APSystem:
    """
    AP System: Prioritizes Availability and Partition Tolerance

    - Always available: Every request gets a response
    - Partition tolerant: Handles network partitions
    - Eventual consistency: May return stale data temporarily

    Examples: Cassandra, DynamoDB, Riak, CouchDB
    Use Case: Social media, shopping carts, product catalogs
    """

    def __init__(self, nodes: List[Node], read_repair: bool = True):
        """
        Initialize AP system.

        Args:
            nodes: List of nodes
            read_repair: Enable read repair for eventual consistency
        """
        self.nodes = nodes
        self.read_repair = read_repair
        self.total_reads = 0
        self.total_writes = 0
        self.stale_reads = 0
        self.background_sync_thread = None

    def read(self, key: str) -> Optional[Any]:
        """
        Read with high availability.

        Returns data from any available node.
        May return stale data if nodes not in sync.
        """
        self.total_reads += 1

        # Try each node until one responds
        for node in self.nodes:
            if node.state != NodeState.DOWN:
                data = node.read(key)
                if data:
                    # Check if this might be stale (for demo)
                    versions = []
                    for n in self.nodes:
                        if n.state == NodeState.HEALTHY:
                            d = n.data.get(key)
                            if d:
                                versions.append(d.version)

                    if versions and data.version < max(versions):
                        self.stale_reads += 1
                        print(f"   ⚠ Read (stale): {key}={data.value} (v{data.version}, latest: v{max(versions)})")
                    else:
                        print(f"   ✓ Read: {key}={data.value} (v{data.version})")

                    return data.value

        # Even if all nodes down, try to return something (high availability)
        print(f"   ⚠ Read: {key}=None (no data available)")
        return None

    def write(self, key: str, value: Any) -> bool:
        """
        Write with high availability.

        Writes to any available node(s).
        Asynchronously replicates to other nodes.
        """
        self.total_writes += 1

        # Get next version
        version = 1
        for node in self.nodes:
            if node.state == NodeState.HEALTHY:
                existing = node.read(key)
                if existing:
                    version = max(version, existing.version + 1)
                break

        # Write to all available nodes
        success_count = 0
        for node in self.nodes:
            if node.state != NodeState.DOWN:
                if node.write(key, value, version):
                    success_count += 1

        # Accept write as long as at least one node succeeded
        if success_count > 0:
            print(f"   ✓ Write accepted: {key}={value} to {success_count}/{len(self.nodes)} nodes")

            # Async replication happens in background
            if success_count < len([n for n in self.nodes if n.state != NodeState.DOWN]):
                print(f"   ⏳ Async replication in progress...")

            return True
        else:
            print(f"   ✗ Write failed: No nodes available")
            return False

    def sync_nodes(self):
        """Background process to sync nodes (eventual consistency)."""
        # Simulate eventual consistency by syncing data
        for key in set().union(*[n.data.keys() for n in self.nodes]):
            # Find latest version
            latest_data = None
            latest_version = 0

            for node in self.nodes:
                if node.state == NodeState.HEALTHY:
                    data = node.data.get(key)
                    if data and data.version > latest_version:
                        latest_data = data
                        latest_version = data.version

            # Update all nodes with latest version
            if latest_data:
                for node in self.nodes:
                    if node.state == NodeState.HEALTHY:
                        current = node.data.get(key)
                        if not current or current.version < latest_version:
                            node.write(key, latest_data.value, latest_data.version)

    def get_stats(self) -> dict:
        """Get system statistics."""
        consistency = ((self.total_reads - self.stale_reads) /
                      max(1, self.total_reads) * 100)

        return {
            "system_type": "AP (Availability + Partition Tolerance)",
            "total_reads": self.total_reads,
            "total_writes": self.total_writes,
            "stale_reads": self.stale_reads,
            "consistency_rate": f"{consistency:.1f}%",
            "availability": "100% (always responds)"
        }


# ============================================================================
# Demonstrations
# ============================================================================

def demonstrate_cp_system():
    """Demonstrate CP system behavior."""
    print("="*60)
    print("CP SYSTEM DEMONSTRATION")
    print("="*60)
    print("\nSystem: Prioritizes Consistency + Partition Tolerance")
    print("Trade-off: May reject requests (sacrifice availability)")

    # Create nodes
    nodes = [
        Node("node-1"),
        Node("node-2"),
        Node("node-3")
    ]

    cp_system = CPSystem(nodes, quorum_size=2)

    # Normal operation
    print("\n1. Normal Operation (All nodes healthy):")
    cp_system.write("balance", 1000)
    cp_system.read("balance")

    # Network partition
    print("\n2. Network Partition (1 node partitioned):")
    nodes[2].set_state(NodeState.PARTITIONED)
    print(f"   Node-3 partitioned (2/3 nodes available)")

    cp_system.write("balance", 900)  # Still works (quorum available)
    cp_system.read("balance")

    # More nodes fail
    print("\n3. More Nodes Fail (Quorum lost):")
    nodes[1].set_state(NodeState.DOWN)
    print(f"   Node-2 down (1/3 nodes available)")

    cp_system.write("balance", 800)  # Rejected (no quorum)
    cp_system.read("balance")  # Rejected (no quorum)

    # Recovery
    print("\n4. Recovery (Nodes come back):")
    nodes[1].set_state(NodeState.HEALTHY)
    nodes[2].set_state(NodeState.HEALTHY)
    print(f"   All nodes healthy")

    cp_system.read("balance")  # Works again

    # Statistics
    print("\n5. Statistics:")
    stats = cp_system.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


def demonstrate_ap_system():
    """Demonstrate AP system behavior."""
    print("\n" + "="*60)
    print("AP SYSTEM DEMONSTRATION")
    print("="*60)
    print("\nSystem: Prioritizes Availability + Partition Tolerance")
    print("Trade-off: May return stale data (eventual consistency)")

    # Create nodes
    nodes = [
        Node("node-1"),
        Node("node-2"),
        Node("node-3")
    ]

    ap_system = APSystem(nodes)

    # Normal operation
    print("\n1. Normal Operation (All nodes healthy):")
    ap_system.write("user:1", {"name": "Alice", "status": "active"})
    ap_system.read("user:1")

    # Network partition
    print("\n2. Network Partition (Nodes isolated):")
    nodes[2].set_state(NodeState.PARTITIONED)
    print(f"   Node-3 partitioned")

    # Update on available nodes
    ap_system.write("user:1", {"name": "Alice", "status": "premium"})

    # Partitioned node has stale data
    print("\n3. Reading from partitioned node (stale data):")
    nodes[2].set_state(NodeState.HEALTHY)
    print(f"   Node-3 reconnected (may have stale data)")

    # This read might get stale data
    for _ in range(2):
        ap_system.read("user:1")

    # Eventual consistency
    print("\n4. Eventual Consistency (Background sync):")
    print(f"   Running background sync...")
    ap_system.sync_nodes()
    print(f"   All nodes now have consistent data")

    ap_system.read("user:1")

    # High availability even with failures
    print("\n5. High Availability (Even with node failures):")
    nodes[1].set_state(NodeState.DOWN)
    print(f"   Node-2 down (2/3 nodes available)")

    ap_system.write("user:2", {"name": "Bob"})  # Still works
    ap_system.read("user:2")  # Still works

    # Statistics
    print("\n6. Statistics:")
    stats = ap_system.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


def demonstrate_cap_tradeoffs():
    """Demonstrate CAP theorem trade-offs side by side."""
    print("\n" + "="*60)
    print("CAP THEOREM TRADE-OFFS COMPARISON")
    print("="*60)

    # Scenario: Network partition occurs
    print("\nScenario: 3-node cluster, 1 node gets partitioned")

    # CP System
    print("\n" + "-"*60)
    print("CP System (Banking Application)")
    print("-"*60)

    cp_nodes = [Node(f"cp-node-{i}") for i in range(3)]
    cp_system = CPSystem(cp_nodes, quorum_size=2)

    print("\n1. Initial balance: $1000")
    cp_system.write("account:123:balance", 1000)

    print("\n2. Node-3 partitioned:")
    cp_nodes[2].set_state(NodeState.PARTITIONED)

    print("\n3. Try to withdraw $100 (quorum available):")
    if cp_system.write("account:123:balance", 900):
        print("   Transaction: APPROVED")
    else:
        print("   Transaction: REJECTED")

    print("\n4. Node-2 goes down (no quorum):")
    cp_nodes[1].set_state(NodeState.DOWN)

    print("\n5. Try to withdraw $100 (no quorum):")
    if cp_system.write("account:123:balance", 800):
        print("   Transaction: APPROVED")
    else:
        print("   Transaction: REJECTED (Sacrificing Availability for Consistency)")

    # AP System
    print("\n" + "-"*60)
    print("AP System (Social Media Application)")
    print("-"*60)

    ap_nodes = [Node(f"ap-node-{i}") for i in range(3)]
    ap_system = APSystem(ap_nodes)

    print("\n1. Initial post likes: 100")
    ap_system.write("post:456:likes", 100)

    print("\n2. Node-3 partitioned:")
    ap_nodes[2].set_state(NodeState.PARTITIONED)

    print("\n3. User likes post (writes to available nodes):")
    if ap_system.write("post:456:likes", 101):
        print("   Like: ACCEPTED")
    else:
        print("   Like: REJECTED")

    print("\n4. Node-2 goes down (only 1 node available):")
    ap_nodes[1].set_state(NodeState.DOWN)

    print("\n5. User likes post (only 1 node available):")
    if ap_system.write("post:456:likes", 102):
        print("   Like: ACCEPTED (Sacrificing Consistency for Availability)")
    else:
        print("   Like: REJECTED")

    print("\n6. Read like count (may be stale):")
    likes = ap_system.read("post:456:likes")
    print(f"   Displayed to user: {likes} likes")


def demonstrate_real_world_examples():
    """Show real-world database examples."""
    print("\n" + "="*60)
    print("REAL-WORLD DATABASE EXAMPLES")
    print("="*60)

    examples = {
        "CP Systems": {
            "MongoDB": "Strong consistency, may reject writes during partition",
            "HBase": "Consistent reads/writes, unavailable during partition",
            "ZooKeeper": "Coordination service, requires quorum",
            "Redis (sync)": "Synchronous replication, consistency over availability"
        },
        "AP Systems": {
            "Cassandra": "Always available, eventual consistency",
            "DynamoDB": "Highly available, tunable consistency",
            "Riak": "Available during partitions, conflict resolution",
            "CouchDB": "Master-master replication, eventual consistency"
        },
        "CA Systems": {
            "PostgreSQL": "Single node: consistent and available (no partition tolerance)",
            "MySQL": "Single node: ACID guarantees (not distributed)",
            "SQLite": "Embedded database (no distributed capability)"
        }
    }

    for category, databases in examples.items():
        print(f"\n{category}:")
        print("-" * 60)
        for db, description in databases.items():
            print(f"  • {db:<15} {description}")


def demonstrate_pacelc_theorem():
    """Demonstrate PACELC theorem (extension of CAP)."""
    print("\n" + "="*60)
    print("PACELC THEOREM")
    print("="*60)
    print("\nPACELC extends CAP for normal operation:")
    print("- If Partition: choose Availability or Consistency")
    print("- Else (normal): choose Latency or Consistency")

    pacelc_examples = {
        "Cassandra": {
            "Partition": "Availability (AP)",
            "Normal": "Latency (EL)",
            "Summary": "PA/EL - Always fast and available"
        },
        "MongoDB": {
            "Partition": "Consistency (CP)",
            "Normal": "Consistency (EC)",
            "Summary": "PC/EC - Always consistent"
        },
        "DynamoDB": {
            "Partition": "Availability (AP)",
            "Normal": "Latency (EL)",
            "Summary": "PA/EL - Fast and available"
        },
        "HBase": {
            "Partition": "Consistency (CP)",
            "Normal": "Consistency (EC)",
            "Summary": "PC/EC - Strong consistency"
        }
    }

    print(f"\n{'Database':<15} {'Partition':<20} {'Normal':<20} {'Summary'}")
    print("-" * 80)

    for db, choices in pacelc_examples.items():
        print(f"{db:<15} {choices['Partition']:<20} {choices['Normal']:<20} {choices['Summary']}")


def print_decision_guide():
    """Print decision guide for choosing CP vs AP."""
    print("\n" + "="*60)
    print("DECISION GUIDE: CP vs AP")
    print("="*60)

    print("\nChoose CP (Consistency + Partition Tolerance) when:")
    print("  ✓ Data correctness is critical")
    print("  ✓ Financial transactions")
    print("  ✓ Inventory management")
    print("  ✓ Booking systems")
    print("  ✓ User authentication")
    print("  ✓ Configuration management")
    print("  Examples: Banking, e-commerce checkout, ticket booking")

    print("\nChoose AP (Availability + Partition Tolerance) when:")
    print("  ✓ Availability is critical")
    print("  ✓ Eventual consistency acceptable")
    print("  ✓ Social media feeds")
    print("  ✓ Product catalogs")
    print("  ✓ Shopping carts")
    print("  ✓ Analytics/metrics")
    print("  Examples: Facebook, Twitter, Amazon product listings")

    print("\nRed Flags:")
    print("  ✗ Don't use AP for: Financial transactions, inventory counts")
    print("  ✗ Don't use CP for: High-traffic social features, caching")


if __name__ == "__main__":
    print("\nCAP Theorem Demonstration")
    print("="*60)

    demonstrate_cp_system()
    demonstrate_ap_system()
    demonstrate_cap_tradeoffs()
    demonstrate_real_world_examples()
    demonstrate_pacelc_theorem()
    print_decision_guide()

    print("\n" + "="*60)
    print("Demonstration Complete!")
    print("="*60 + "\n")
