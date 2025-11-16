"""
Database Replication Demonstration

This module simulates different database replication strategies:
1. Master-Slave (Primary-Replica) Replication
2. Master-Master (Multi-Primary) Replication
3. Replication Lag and Consistency Issues
4. Failover Scenarios

Real-World Applications:
- MySQL: Master-Slave with async/semi-sync replication
- PostgreSQL: Streaming replication with hot standby
- MongoDB: Replica sets with automatic failover
- Redis: Master-replica for read scaling

Key Concepts:
- Asynchronous vs Synchronous replication
- Replication lag
- Read-your-own-writes consistency
- Conflict resolution in multi-master
"""

import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ReplicationMode(Enum):
    ASYNC = "asynchronous"
    SYNC = "synchronous"
    SEMI_SYNC = "semi-synchronous"


@dataclass
class WriteOperation:
    """Represents a database write operation"""

    timestamp: float
    key: str
    value: Any
    version: int = 1
    source: str = "master"


@dataclass
class ReplicationLog:
    """Represents replication log entry"""

    operation: WriteOperation
    replicated_at: Optional[float] = None
    acknowledged: bool = False


class DatabaseNode:
    """Simulates a database node (master or slave)"""

    def __init__(self, name: str, is_master: bool = False):
        self.name = name
        self.is_master = is_master
        self.data: Dict[str, WriteOperation] = {}
        self.replication_queue: List[ReplicationLog] = []
        self.replication_lag_ms = 0  # Simulated network lag

    def write(self, key: str, value: Any, version: int = 1, source: str = None) -> WriteOperation:
        """Write data to this node"""
        op = WriteOperation(
            timestamp=time.time(), key=key, value=value, version=version, source=source or self.name
        )
        self.data[key] = op
        return op

    def read(self, key: str) -> Optional[Any]:
        """Read data from this node"""
        op = self.data.get(key)
        return op.value if op else None

    def get_operation(self, key: str) -> Optional[WriteOperation]:
        """Get full operation details"""
        return self.data.get(key)

    def set_replication_lag(self, lag_ms: int):
        """Set simulated replication lag in milliseconds"""
        self.replication_lag_ms = lag_ms


class MasterSlaveReplication:
    """
    Master-Slave Replication Simulation

    Architecture:
        Master (Read/Write) -> Slave1 (Read Only)
                            -> Slave2 (Read Only)
                            -> Slave3 (Read Only)

    Characteristics:
    - Single master handles all writes
    - Multiple slaves handle reads
    - Replication can be async or sync
    """

    def __init__(self, num_slaves: int = 3, mode: ReplicationMode = ReplicationMode.ASYNC):
        self.master = DatabaseNode("master", is_master=True)
        self.slaves = [DatabaseNode(f"slave_{i}") for i in range(num_slaves)]
        self.mode = mode
        self.replication_logs: List[ReplicationLog] = []

    def write(self, key: str, value: Any) -> bool:
        """
        Write to master and replicate to slaves

        Async: Return immediately, replicate in background
        Sync: Wait for all slaves to acknowledge
        Semi-Sync: Wait for at least one slave
        """
        # Write to master
        operation = self.master.write(key, value, source="master")

        # Create replication logs
        logs = [ReplicationLog(operation=operation) for _ in self.slaves]
        self.replication_logs.extend(logs)

        if self.mode == ReplicationMode.ASYNC:
            # Replicate asynchronously (don't wait)
            self._replicate_async(operation)
            return True

        elif self.mode == ReplicationMode.SYNC:
            # Replicate synchronously (wait for all)
            return self._replicate_sync(operation)

        elif self.mode == ReplicationMode.SEMI_SYNC:
            # Wait for at least one slave
            return self._replicate_semi_sync(operation)

    def _replicate_async(self, operation: WriteOperation):
        """Replicate to all slaves without waiting"""
        for slave in self.slaves:
            # Simulate network delay
            time.sleep(slave.replication_lag_ms / 1000.0)
            slave.write(operation.key, operation.value, operation.version, operation.source)

    def _replicate_sync(self, operation: WriteOperation) -> bool:
        """Replicate to all slaves and wait for acknowledgment"""
        success_count = 0
        for slave in self.slaves:
            time.sleep(slave.replication_lag_ms / 1000.0)
            slave.write(operation.key, operation.value, operation.version, operation.source)
            success_count += 1

        return success_count == len(self.slaves)

    def _replicate_semi_sync(self, operation: WriteOperation) -> bool:
        """Wait for at least one slave to acknowledge"""
        for slave in self.slaves:
            time.sleep(slave.replication_lag_ms / 1000.0)
            slave.write(operation.key, operation.value, operation.version, operation.source)
            return True  # Success after first slave

        return False

    def read(self, key: str, prefer_master: bool = False) -> Optional[Any]:
        """
        Read data (can specify master or random slave)

        prefer_master: Read from master (strong consistency)
        else: Read from random slave (eventual consistency, may be stale)
        """
        if prefer_master:
            return self.master.read(key)
        else:
            # Load balance reads across slaves
            slave = random.choice(self.slaves)
            return slave.read(key)

    def get_replication_status(self) -> Dict[str, Any]:
        """Check replication lag across slaves"""
        status = {}
        for slave in self.slaves:
            lag_keys = []
            for key, master_op in self.master.data.items():
                slave_op = slave.get_operation(key)
                if not slave_op or slave_op.timestamp < master_op.timestamp:
                    lag_keys.append(key)

            status[slave.name] = {"lagging_keys": lag_keys, "lag_count": len(lag_keys)}

        return status

    def set_slave_lag(self, slave_index: int, lag_ms: int):
        """Set replication lag for a specific slave"""
        if 0 <= slave_index < len(self.slaves):
            self.slaves[slave_index].set_replication_lag(lag_ms)

    def failover_to_slave(self, slave_index: int):
        """Simulate failover: promote slave to master"""
        if 0 <= slave_index < len(self.slaves):
            new_master = self.slaves[slave_index]
            new_master.is_master = True
            print(f"Failover: {new_master.name} promoted to master")
            print(f"Note: Data on new master may be stale (replication lag)")
            return new_master
        return None


class MasterMasterReplication:
    """
    Master-Master (Multi-Primary) Replication Simulation

    Architecture:
        Master1 (Read/Write) <-> Master2 (Read/Write)

    Characteristics:
    - Both nodes accept writes
    - Bi-directional replication
    - Conflict resolution needed
    - Active-active configuration
    """

    def __init__(self, conflict_strategy: str = "last_write_wins"):
        self.master1 = DatabaseNode("master1", is_master=True)
        self.master2 = DatabaseNode("master2", is_master=True)
        self.conflict_strategy = conflict_strategy  # "last_write_wins" or "custom"
        self.conflicts: List[Dict[str, Any]] = []

    def write(self, key: str, value: Any, master_node: int = 1, version: int = 1) -> bool:
        """
        Write to specified master and replicate to other master

        master_node: 1 or 2
        """
        if master_node == 1:
            primary = self.master1
            replica = self.master2
        else:
            primary = self.master2
            replica = self.master1

        # Write to primary master
        operation = primary.write(key, value, version=version, source=primary.name)

        # Simulate network delay before replication
        time.sleep(0.001)  # 1ms delay

        # Check for conflicts
        existing_op = replica.get_operation(key)
        if existing_op and existing_op.timestamp > operation.timestamp - 0.01:
            # Concurrent write detected (within 10ms window)
            self._handle_conflict(key, operation, existing_op, replica)
        else:
            # No conflict, replicate normally
            replica.write(key, value, version=version, source=operation.source)

        return True

    def _handle_conflict(self, key: str, op1: WriteOperation, op2: WriteOperation, node: DatabaseNode):
        """Handle write conflicts between masters"""
        conflict = {
            "key": key,
            "operation1": {"value": op1.value, "timestamp": op1.timestamp, "source": op1.source},
            "operation2": {"value": op2.value, "timestamp": op2.timestamp, "source": op2.source},
        }
        self.conflicts.append(conflict)

        if self.conflict_strategy == "last_write_wins":
            # Keep the operation with latest timestamp
            if op1.timestamp > op2.timestamp:
                node.write(key, op1.value, op1.version, op1.source)
                print(f"Conflict on '{key}': {op1.source} wins (last write wins)")
            else:
                print(f"Conflict on '{key}': {op2.source} wins (last write wins)")

        elif self.conflict_strategy == "version_vector":
            # Use version vectors (simplified)
            winner_op = op1 if op1.version > op2.version else op2
            node.write(key, winner_op.value, winner_op.version, winner_op.source)
            print(f"Conflict on '{key}': version {winner_op.version} wins")

    def read(self, key: str, master_node: int = 1) -> Optional[Any]:
        """Read from specified master"""
        master = self.master1 if master_node == 1 else self.master2
        return master.read(key)

    def get_conflicts(self) -> List[Dict[str, Any]]:
        """Get list of detected conflicts"""
        return self.conflicts

    def check_consistency(self) -> bool:
        """Check if both masters have consistent data"""
        all_keys = set(self.master1.data.keys()) | set(self.master2.data.keys())

        inconsistent_keys = []
        for key in all_keys:
            val1 = self.master1.read(key)
            val2 = self.master2.read(key)
            if val1 != val2:
                inconsistent_keys.append(key)

        if inconsistent_keys:
            print(f"Inconsistent keys: {inconsistent_keys}")
            return False
        return True


# ==================== DEMONSTRATION FUNCTIONS ====================


def demo_master_slave_async():
    """Demonstrate asynchronous master-slave replication"""
    print("=" * 80)
    print("DEMO: Master-Slave Asynchronous Replication")
    print("=" * 80)

    repl = MasterSlaveReplication(num_slaves=3, mode=ReplicationMode.ASYNC)

    # Set different replication lags for slaves
    repl.set_slave_lag(0, 10)  # 10ms lag
    repl.set_slave_lag(1, 50)  # 50ms lag
    repl.set_slave_lag(2, 100)  # 100ms lag

    print("\n--- Writing to Master ---")
    repl.write("user:1", {"name": "Alice", "balance": 1000})
    repl.write("user:2", {"name": "Bob", "balance": 2000})

    print("Writes committed to master (async replication in progress)")

    print("\n--- Reading Immediately After Write ---")
    print(f"Read from master: {repl.read('user:1', prefer_master=True)}")
    print(f"Read from slave (may be stale): {repl.read('user:1', prefer_master=False)}")

    print("\n--- Replication Status ---")
    status = repl.get_replication_status()
    for slave_name, info in status.items():
        print(f"{slave_name}: {info['lag_count']} keys lagging")

    # Wait for replication to complete
    time.sleep(0.15)  # Wait for slowest slave

    print("\n--- After Replication Complete ---")
    status = repl.get_replication_status()
    for slave_name, info in status.items():
        print(f"{slave_name}: {info['lag_count']} keys lagging")

    print("\nPros: Low write latency, high read throughput")
    print("Cons: Eventual consistency, possible data loss on master failure")


def demo_master_slave_sync():
    """Demonstrate synchronous master-slave replication"""
    print("\n" + "=" * 80)
    print("DEMO: Master-Slave Synchronous Replication")
    print("=" * 80)

    repl = MasterSlaveReplication(num_slaves=2, mode=ReplicationMode.SYNC)
    repl.set_slave_lag(0, 20)
    repl.set_slave_lag(1, 30)

    print("\n--- Writing to Master (Synchronous) ---")
    start = time.time()
    repl.write("user:1", {"name": "Alice", "balance": 1000})
    duration = time.time() - start

    print(f"Write completed in {duration * 1000:.0f}ms")
    print("Master waited for ALL slaves to acknowledge")

    print("\n--- Immediate Read from Slave ---")
    print(f"Read from slave: {repl.read('user:1', prefer_master=False)}")
    print("Data is immediately available (strong consistency)")

    print("\nPros: Strong consistency, no data loss")
    print("Cons: Higher write latency (waits for slowest slave)")


def demo_replication_lag():
    """Demonstrate the impact of replication lag"""
    print("\n" + "=" * 80)
    print("DEMO: Replication Lag & Read-Your-Own-Writes Problem")
    print("=" * 80)

    repl = MasterSlaveReplication(num_slaves=1, mode=ReplicationMode.ASYNC)
    repl.set_slave_lag(0, 100)  # 100ms lag

    print("\n--- Scenario: User updates profile ---")
    print("1. User writes: name = 'Alice Updated'")
    repl.write("user:1", {"name": "Alice Updated"})

    print("2. Immediately redirect to profile page (reads from slave)")
    immediate_read = repl.read("user:1", prefer_master=False)
    print(f"   Slave shows: {immediate_read}")

    if immediate_read is None:
        print("   Problem: User sees old data or no data!")

    print("\n--- Solution 1: Read from Master ---")
    master_read = repl.read("user:1", prefer_master=True)
    print(f"   Master shows: {master_read}")
    print("   User sees updated data (but less scalable)")

    print("\n--- Solution 2: Cache-Aside Pattern ---")
    print("   1. Write to master")
    print("   2. Write to cache (Redis)")
    print("   3. Read from cache for recent writes")
    print("   4. Fall back to slave after cache expiry")

    # Wait for replication
    time.sleep(0.15)

    print("\n--- After Replication Lag ---")
    slave_read = repl.read("user:1", prefer_master=False)
    print(f"   Slave shows: {slave_read}")
    print("   Data is now consistent")


def demo_master_master():
    """Demonstrate master-master replication with conflicts"""
    print("\n" + "=" * 80)
    print("DEMO: Master-Master Replication & Conflict Resolution")
    print("=" * 80)

    repl = MasterMasterReplication(conflict_strategy="last_write_wins")

    print("\n--- Scenario 1: Sequential Writes (No Conflict) ---")
    repl.write("counter", 1, master_node=1)
    time.sleep(0.02)  # Wait for replication
    repl.write("counter", 2, master_node=2)

    print(f"Master 1 value: {repl.read('counter', master_node=1)}")
    print(f"Master 2 value: {repl.read('counter', master_node=2)}")

    print("\n--- Scenario 2: Concurrent Writes (Conflict) ---")
    print("Both masters write to 'balance' at nearly same time")

    # Simulate concurrent writes
    import threading

    def write_master1():
        repl.write("balance", 1000, master_node=1, version=1)

    def write_master2():
        repl.write("balance", 2000, master_node=2, version=1)

    t1 = threading.Thread(target=write_master1)
    t2 = threading.Thread(target=write_master2)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    time.sleep(0.02)  # Wait for conflict resolution

    print(f"\nMaster 1 value: {repl.read('balance', master_node=1)}")
    print(f"Master 2 value: {repl.read('balance', master_node=2)}")

    conflicts = repl.get_conflicts()
    if conflicts:
        print(f"\nConflicts detected: {len(conflicts)}")
        for conflict in conflicts:
            print(f"  Key: {conflict['key']}")
            print(f"    {conflict['operation1']['source']}: {conflict['operation1']['value']}")
            print(f"    {conflict['operation2']['source']}: {conflict['operation2']['value']}")

    print("\nConflict Resolution: Last Write Wins")
    print("Alternative strategies: Version Vectors, CRDTs, Application Logic")


def demo_failover():
    """Demonstrate failover from master to slave"""
    print("\n" + "=" * 80)
    print("DEMO: Failover Scenario")
    print("=" * 80)

    repl = MasterSlaveReplication(num_slaves=2, mode=ReplicationMode.ASYNC)
    repl.set_slave_lag(0, 10)
    repl.set_slave_lag(1, 50)

    print("\n--- Normal Operation ---")
    repl.write("user:1", {"name": "Alice", "balance": 1000})
    repl.write("user:2", {"name": "Bob", "balance": 2000})
    repl.write("user:3", {"name": "Charlie", "balance": 3000})

    print("Master is healthy, processing writes")

    print("\n--- Master Failure ---")
    print("Master database crashed!")
    print("Most recent write may not be replicated yet (async mode)")

    print("\n--- Promoting Slave to Master ---")
    new_master = repl.failover_to_slave(0)  # Promote slave_0

    print(f"\nNew master data:")
    print(f"  user:1 -> {new_master.read('user:1')}")
    print(f"  user:2 -> {new_master.read('user:2')}")
    print(f"  user:3 -> {new_master.read('user:3')}")

    print("\n--- Failover Considerations ---")
    print("1. Data Loss Risk:")
    print("   - Async replication: Recent writes may be lost")
    print("   - Sync replication: No data loss")

    print("\n2. Failover Time:")
    print("   - Manual: Minutes to hours (human intervention)")
    print("   - Automatic: Seconds (consensus protocols like Raft)")

    print("\n3. Split-Brain Prevention:")
    print("   - Ensure only one master at a time")
    print("   - Use quorum-based systems (e.g., ZooKeeper)")


def demo_read_scaling():
    """Demonstrate read scaling with replicas"""
    print("\n" + "=" * 80)
    print("DEMO: Read Scaling with Replicas")
    print("=" * 80)

    repl = MasterSlaveReplication(num_slaves=5, mode=ReplicationMode.ASYNC)

    # Populate data
    for i in range(100):
        repl.write(f"user:{i}", {"name": f"User{i}", "score": random.randint(0, 1000)})

    time.sleep(0.05)  # Wait for replication

    print("\n--- Load Distribution ---")
    print("Simulating 1000 read requests")

    slave_reads = {f"slave_{i}": 0 for i in range(5)}

    # Simulate random read distribution
    for _ in range(1000):
        key = f"user:{random.randint(0, 99)}"
        # Read from random slave
        slave = random.choice(repl.slaves)
        slave.read(key)
        slave_reads[slave.name] += 1

    print("\nReads per slave:")
    for slave_name, count in sorted(slave_reads.items()):
        bar = "█" * (count // 10)
        print(f"  {slave_name}: {count:3d} reads {bar}")

    print("\n--- Benefits ---")
    print(f"Master handles: 0 reads (only writes)")
    print(f"Slaves handle: 1000 reads (distributed)")
    print(f"Read throughput: {len(repl.slaves)}x compared to single server")

    print("\n--- Scaling Pattern ---")
    print("1 Master (Writes) + N Slaves (Reads)")
    print("Horizontal scaling for read-heavy workloads")
    print("Examples: News sites, blogs, analytics dashboards")


if __name__ == "__main__":
    # Run all demos
    demo_master_slave_async()
    demo_master_slave_sync()
    demo_replication_lag()
    demo_master_master()
    demo_failover()
    demo_read_scaling()

    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. Replication Modes:
   - Async: Low latency, eventual consistency, possible data loss
   - Sync: High latency, strong consistency, no data loss
   - Semi-sync: Balance between async and sync

2. Master-Slave:
   - Simple architecture
   - Read scaling
   - Single point of failure (master)
   - Replication lag issues

3. Master-Master:
   - High availability (no single point of failure)
   - Write distribution
   - Conflict resolution needed
   - More complex

4. Replication Lag:
   - Common in async replication
   - Causes stale reads
   - Solutions: read-from-master, caching, session affinity

5. Failover:
   - Manual: Slow, prone to errors
   - Automatic: Fast, requires consensus (Raft, Paxos)
   - Data loss risk with async replication

Real-World Implementations:
- MySQL: Async/Semi-sync master-slave, Group Replication
- PostgreSQL: Streaming replication, hot standby
- MongoDB: Replica sets with automatic failover
- Redis: Master-replica with sentinel for failover
- Cassandra: Multi-master (peer-to-peer) with tunable consistency
    """)
