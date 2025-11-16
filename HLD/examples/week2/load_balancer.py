"""
Load Balancer Implementations

This module demonstrates different load balancing algorithms:
- Round Robin
- Weighted Round Robin
- Least Connections
- IP Hash
- Random
"""

import hashlib
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Server:
    """Represents a backend server."""
    id: str
    host: str
    port: int
    weight: int = 1
    connections: int = 0
    total_requests: int = 0
    is_healthy: bool = True

    def __str__(self):
        return f"Server({self.id}, {self.host}:{self.port}, connections={self.connections})"

    def handle_request(self):
        """Simulate handling a request."""
        self.connections += 1
        self.total_requests += 1

    def release_connection(self):
        """Simulate releasing a connection."""
        if self.connections > 0:
            self.connections -= 1


class LoadBalancer:
    """Base class for load balancers."""

    def __init__(self, servers: List[Server]):
        self.servers = servers
        self.healthy_servers = [s for s in servers if s.is_healthy]

    def get_server(self, client_id: Optional[str] = None) -> Optional[Server]:
        """Get next server based on algorithm."""
        raise NotImplementedError

    def add_server(self, server: Server):
        """Add a new server to the pool."""
        self.servers.append(server)
        if server.is_healthy:
            self.healthy_servers.append(server)

    def remove_server(self, server_id: str):
        """Remove a server from the pool."""
        self.servers = [s for s in self.servers if s.id != server_id]
        self.healthy_servers = [s for s in self.servers if s.is_healthy]

    def mark_unhealthy(self, server_id: str):
        """Mark a server as unhealthy."""
        for server in self.servers:
            if server.id == server_id:
                server.is_healthy = False
                self.healthy_servers = [s for s in self.servers if s.is_healthy]
                break

    def mark_healthy(self, server_id: str):
        """Mark a server as healthy."""
        for server in self.servers:
            if server.id == server_id:
                server.is_healthy = True
                self.healthy_servers = [s for s in self.servers if s.is_healthy]
                break

    def get_stats(self) -> Dict:
        """Get load balancer statistics."""
        return {
            "total_servers": len(self.servers),
            "healthy_servers": len(self.healthy_servers),
            "server_stats": [
                {
                    "id": s.id,
                    "connections": s.connections,
                    "total_requests": s.total_requests,
                    "is_healthy": s.is_healthy
                }
                for s in self.servers
            ]
        }


class RoundRobinLoadBalancer(LoadBalancer):
    """
    Round Robin Load Balancer

    Distributes requests sequentially across all healthy servers.
    Simple and fair distribution when servers have equal capacity.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    def __init__(self, servers: List[Server]):
        super().__init__(servers)
        self.current_index = 0

    def get_server(self, client_id: Optional[str] = None) -> Optional[Server]:
        """Get next server in round-robin fashion."""
        if not self.healthy_servers:
            return None

        server = self.healthy_servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.healthy_servers)

        return server


class WeightedRoundRobinLoadBalancer(LoadBalancer):
    """
    Weighted Round Robin Load Balancer

    Distributes requests based on server weights.
    Servers with higher weights receive more requests.

    Example: weights [3, 2, 1]
    Distribution: S1, S1, S1, S2, S2, S3, repeat...

    Time Complexity: O(1)
    Space Complexity: O(n) where n is total weight
    """

    def __init__(self, servers: List[Server]):
        super().__init__(servers)
        self.weighted_servers = []
        self._build_weighted_list()
        self.current_index = 0

    def _build_weighted_list(self):
        """Build weighted server list."""
        self.weighted_servers = []
        for server in self.healthy_servers:
            self.weighted_servers.extend([server] * server.weight)

    def add_server(self, server: Server):
        """Override to rebuild weighted list."""
        super().add_server(server)
        self._build_weighted_list()

    def remove_server(self, server_id: str):
        """Override to rebuild weighted list."""
        super().remove_server(server_id)
        self._build_weighted_list()

    def get_server(self, client_id: Optional[str] = None) -> Optional[Server]:
        """Get next server based on weights."""
        if not self.weighted_servers:
            return None

        server = self.weighted_servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.weighted_servers)

        return server


class LeastConnectionsLoadBalancer(LoadBalancer):
    """
    Least Connections Load Balancer

    Routes requests to the server with fewest active connections.
    Best for long-lived connections with varying request durations.

    Use Cases:
    - WebSocket servers
    - Database connection pools
    - Streaming servers

    Time Complexity: O(n) where n is number of servers
    Space Complexity: O(1)
    """

    def get_server(self, client_id: Optional[str] = None) -> Optional[Server]:
        """Get server with least connections."""
        if not self.healthy_servers:
            return None

        return min(self.healthy_servers, key=lambda s: s.connections)


class WeightedLeastConnectionsLoadBalancer(LoadBalancer):
    """
    Weighted Least Connections Load Balancer

    Considers both server capacity (weight) and current load (connections).
    Routes to server with lowest connections/weight ratio.

    Formula: score = connections / weight (choose lowest)

    Time Complexity: O(n)
    Space Complexity: O(1)
    """

    def get_server(self, client_id: Optional[str] = None) -> Optional[Server]:
        """Get server with lowest connections/weight ratio."""
        if not self.healthy_servers:
            return None

        return min(
            self.healthy_servers,
            key=lambda s: s.connections / s.weight if s.weight > 0 else float('inf')
        )


class IPHashLoadBalancer(LoadBalancer):
    """
    IP Hash Load Balancer

    Routes requests from same client IP to same server.
    Provides session persistence without storing session data.

    Advantages:
    - Session affinity (sticky sessions)
    - Server-side caching benefits
    - No session storage needed

    Disadvantages:
    - Uneven distribution with NAT/proxies
    - Server failure affects specific clients
    - Difficult to rebalance

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    def get_server(self, client_id: Optional[str] = None) -> Optional[Server]:
        """Get server based on client IP hash."""
        if not self.healthy_servers:
            return None

        if client_id is None:
            # Fallback to round-robin
            return self.healthy_servers[0]

        # Hash client IP to server index
        hash_value = int(hashlib.md5(client_id.encode()).hexdigest(), 16)
        index = hash_value % len(self.healthy_servers)

        return self.healthy_servers[index]


class ConsistentHashLoadBalancer(LoadBalancer):
    """
    Consistent Hashing Load Balancer

    Uses consistent hashing to minimize redistribution when servers change.
    Only K/n keys need to be remapped when adding/removing servers.

    Virtual nodes improve distribution uniformity.

    Time Complexity: O(log n) with virtual nodes
    Space Complexity: O(n * virtual_nodes)
    """

    def __init__(self, servers: List[Server], virtual_nodes: int = 150):
        super().__init__(servers)
        self.virtual_nodes = virtual_nodes
        self.hash_ring = {}
        self.sorted_keys = []
        self._build_hash_ring()

    def _hash(self, key: str) -> int:
        """Generate hash for a key."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def _build_hash_ring(self):
        """Build consistent hash ring with virtual nodes."""
        self.hash_ring = {}

        for server in self.healthy_servers:
            for i in range(self.virtual_nodes):
                virtual_key = f"{server.id}:{i}"
                hash_value = self._hash(virtual_key)
                self.hash_ring[hash_value] = server

        self.sorted_keys = sorted(self.hash_ring.keys())

    def add_server(self, server: Server):
        """Override to rebuild hash ring."""
        super().add_server(server)
        self._build_hash_ring()

    def remove_server(self, server_id: str):
        """Override to rebuild hash ring."""
        super().remove_server(server_id)
        self._build_hash_ring()

    def get_server(self, client_id: Optional[str] = None) -> Optional[Server]:
        """Get server using consistent hashing."""
        if not self.healthy_servers or not self.sorted_keys:
            return None

        if client_id is None:
            return self.healthy_servers[0]

        hash_value = self._hash(client_id)

        # Binary search for next server on ring
        for key in self.sorted_keys:
            if hash_value <= key:
                return self.hash_ring[key]

        # Wrap around to first server
        return self.hash_ring[self.sorted_keys[0]]


class RandomLoadBalancer(LoadBalancer):
    """
    Random Load Balancer

    Randomly selects a healthy server for each request.

    Pros:
    - Simplest implementation
    - No state to maintain
    - Works well with uniform access patterns

    Cons:
    - Unpredictable distribution
    - May not balance perfectly

    Time Complexity: O(1)
    Space Complexity: O(1)
    """

    def get_server(self, client_id: Optional[str] = None) -> Optional[Server]:
        """Get random server."""
        if not self.healthy_servers:
            return None

        return random.choice(self.healthy_servers)


# ============================================================================
# Demonstration and Testing
# ============================================================================

def simulate_requests(lb: LoadBalancer, num_requests: int, client_ids: List[str]):
    """Simulate requests to the load balancer."""
    print(f"\n{'='*60}")
    print(f"Testing: {lb.__class__.__name__}")
    print(f"{'='*60}")

    request_distribution = defaultdict(int)

    for i in range(num_requests):
        client_id = random.choice(client_ids)
        server = lb.get_server(client_id)

        if server:
            server.handle_request()
            request_distribution[server.id] += 1

            if i < 10:  # Show first 10 requests
                print(f"Request {i+1}: Client {client_id} → {server.id}")

    # Show distribution
    print(f"\n{'Distribution':<20} {'Requests':<15} {'Connections'}")
    print("-" * 60)
    for server in lb.servers:
        percentage = (request_distribution[server.id] / num_requests) * 100
        print(f"{server.id:<20} {request_distribution[server.id]:<15} "
              f"{server.connections:<15} ({percentage:.1f}%)")

    # Release connections for next test
    for server in lb.servers:
        server.connections = 0


def demonstrate_algorithms():
    """Demonstrate all load balancing algorithms."""

    # Create server pool
    servers = [
        Server("server-1", "192.168.1.1", 8001, weight=3),
        Server("server-2", "192.168.1.2", 8002, weight=2),
        Server("server-3", "192.168.1.3", 8003, weight=1),
        Server("server-4", "192.168.1.4", 8004, weight=2),
    ]

    client_ids = ["client-A", "client-B", "client-C", "client-D", "client-E"]
    num_requests = 100

    # Test each algorithm
    algorithms = [
        RoundRobinLoadBalancer(servers[:]),
        WeightedRoundRobinLoadBalancer(servers[:]),
        LeastConnectionsLoadBalancer(servers[:]),
        WeightedLeastConnectionsLoadBalancer(servers[:]),
        IPHashLoadBalancer(servers[:]),
        ConsistentHashLoadBalancer(servers[:], virtual_nodes=150),
        RandomLoadBalancer(servers[:]),
    ]

    for lb in algorithms:
        # Reset server stats
        for server in lb.servers:
            server.connections = 0
            server.total_requests = 0

        simulate_requests(lb, num_requests, client_ids)


def demonstrate_failover():
    """Demonstrate server failure and recovery."""
    print(f"\n{'='*60}")
    print("FAILOVER DEMONSTRATION")
    print(f"{'='*60}")

    servers = [
        Server("server-1", "192.168.1.1", 8001),
        Server("server-2", "192.168.1.2", 8002),
        Server("server-3", "192.168.1.3", 8003),
    ]

    lb = RoundRobinLoadBalancer(servers)

    # Normal operation
    print("\n1. Normal Operation (3 servers):")
    for i in range(6):
        server = lb.get_server()
        print(f"   Request {i+1} → {server.id}")

    # Server failure
    print("\n2. Server-2 Fails:")
    lb.mark_unhealthy("server-2")
    print(f"   Healthy servers: {[s.id for s in lb.healthy_servers]}")
    for i in range(6):
        server = lb.get_server()
        print(f"   Request {i+1} → {server.id}")

    # Server recovery
    print("\n3. Server-2 Recovers:")
    lb.mark_healthy("server-2")
    print(f"   Healthy servers: {[s.id for s in lb.healthy_servers]}")
    for i in range(6):
        server = lb.get_server()
        print(f"   Request {i+1} → {server.id}")


def demonstrate_session_persistence():
    """Demonstrate session persistence with IP Hash."""
    print(f"\n{'='*60}")
    print("SESSION PERSISTENCE (IP Hash)")
    print(f"{'='*60}")

    servers = [
        Server("server-1", "192.168.1.1", 8001),
        Server("server-2", "192.168.1.2", 8002),
        Server("server-3", "192.168.1.3", 8003),
    ]

    lb = IPHashLoadBalancer(servers)

    clients = ["192.168.100.1", "192.168.100.2", "192.168.100.3"]

    print("\nSame client always goes to same server:")
    for _ in range(2):  # Two rounds
        print()
        for client_ip in clients:
            server = lb.get_server(client_ip)
            print(f"   Client {client_ip} → {server.id}")


def compare_algorithms():
    """Compare algorithms with metrics."""
    print(f"\n{'='*60}")
    print("ALGORITHM COMPARISON")
    print(f"{'='*60}")

    comparison = {
        "Round Robin": {
            "Complexity": "O(1)",
            "Distribution": "Equal",
            "Session": "No",
            "Best For": "Equal servers, stateless"
        },
        "Weighted RR": {
            "Complexity": "O(1)",
            "Distribution": "By weight",
            "Session": "No",
            "Best For": "Different capacity servers"
        },
        "Least Conn": {
            "Complexity": "O(n)",
            "Distribution": "By load",
            "Session": "No",
            "Best For": "Long connections, varying duration"
        },
        "IP Hash": {
            "Complexity": "O(1)",
            "Distribution": "Uneven",
            "Session": "Yes",
            "Best For": "Session persistence, caching"
        },
        "Consistent Hash": {
            "Complexity": "O(log n)",
            "Distribution": "Uniform",
            "Session": "Yes",
            "Best For": "Dynamic server pool, caching"
        },
    }

    print(f"\n{'Algorithm':<20} {'Complexity':<12} {'Distribution':<15} "
          f"{'Session':<10} {'Best For'}")
    print("-" * 100)

    for algo, metrics in comparison.items():
        print(f"{algo:<20} {metrics['Complexity']:<12} {metrics['Distribution']:<15} "
              f"{metrics['Session']:<10} {metrics['Best For']}")


if __name__ == "__main__":
    print("Load Balancer Algorithms Demonstration")
    print("=" * 60)

    # Run all demonstrations
    demonstrate_algorithms()
    demonstrate_failover()
    demonstrate_session_persistence()
    compare_algorithms()

    print(f"\n{'='*60}")
    print("Demonstration Complete!")
    print(f"{'='*60}\n")
