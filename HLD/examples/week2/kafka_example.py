"""
Apache Kafka Concepts and Simulation

This module demonstrates Kafka concepts including:
- Topics and Partitions
- Producers and Consumers
- Consumer Groups
- Offsets and Commits
- Message ordering guarantees
- Partition assignment

Note: This is a simplified simulation for educational purposes.
For production use, install kafka-python: pip install kafka-python
"""

import time
import hashlib
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import threading
import random


# ============================================================================
# Core Kafka Concepts
# ============================================================================

@dataclass
class Message:
    """Represents a Kafka message."""
    key: Optional[str]
    value: Any
    timestamp: float = field(default_factory=time.time)
    offset: int = 0
    partition: int = 0
    headers: Dict[str, str] = field(default_factory=dict)

    def __repr__(self):
        return f"Message(key={self.key}, value={self.value}, partition={self.partition}, offset={self.offset})"


class Partition:
    """
    Kafka Partition - Ordered, immutable sequence of messages.

    Key Concepts:
    - Messages appended to end (append-only log)
    - Each message has an offset (position in partition)
    - Messages in a partition are ordered
    - Retention policy determines how long messages are kept
    """

    def __init__(self, partition_id: int, retention_messages: int = 1000):
        self.partition_id = partition_id
        self.messages: deque = deque(maxlen=retention_messages)
        self.current_offset = 0
        self.lock = threading.Lock()

    def append(self, message: Message) -> int:
        """
        Append message to partition.

        Returns:
            Offset of appended message
        """
        with self.lock:
            message.offset = self.current_offset
            message.partition = self.partition_id
            self.messages.append(message)
            offset = self.current_offset
            self.current_offset += 1
            return offset

    def read(self, offset: int, max_messages: int = 1) -> List[Message]:
        """
        Read messages starting from offset.

        Args:
            offset: Starting offset
            max_messages: Maximum messages to read

        Returns:
            List of messages
        """
        with self.lock:
            # Find starting position
            start_idx = None
            for idx, msg in enumerate(self.messages):
                if msg.offset >= offset:
                    start_idx = idx
                    break

            if start_idx is None:
                return []

            # Read up to max_messages
            end_idx = min(start_idx + max_messages, len(self.messages))
            return list(self.messages)[start_idx:end_idx]

    def get_latest_offset(self) -> int:
        """Get latest offset (high water mark)."""
        with self.lock:
            return self.current_offset

    def get_size(self) -> int:
        """Get number of messages in partition."""
        return len(self.messages)

    def __repr__(self):
        return f"Partition({self.partition_id}, messages={len(self.messages)}, offset={self.current_offset})"


class Topic:
    """
    Kafka Topic - Logical channel for messages.

    Key Concepts:
    - Topic split into multiple partitions for parallelism
    - Each partition is ordered
    - Messages with same key go to same partition (ordering guarantee)
    - Partitions distributed across brokers
    """

    def __init__(self, name: str, num_partitions: int = 3):
        self.name = name
        self.partitions = [Partition(i) for i in range(num_partitions)]
        self.num_partitions = num_partitions

    def get_partition(self, key: Optional[str] = None) -> Partition:
        """
        Get partition for a message.

        If key provided: hash(key) % num_partitions (same key → same partition)
        If no key: round-robin or random
        """
        if key:
            # Hash key to partition (ensures same key → same partition)
            hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
            partition_id = hash_value % self.num_partitions
        else:
            # Random partition if no key
            partition_id = random.randint(0, self.num_partitions - 1)

        return self.partitions[partition_id]

    def get_partition_by_id(self, partition_id: int) -> Optional[Partition]:
        """Get specific partition by ID."""
        if 0 <= partition_id < self.num_partitions:
            return self.partitions[partition_id]
        return None

    def get_stats(self) -> dict:
        """Get topic statistics."""
        total_messages = sum(p.get_size() for p in self.partitions)
        return {
            "name": self.name,
            "partitions": self.num_partitions,
            "total_messages": total_messages,
            "partition_details": [
                {
                    "partition_id": p.partition_id,
                    "messages": p.get_size(),
                    "latest_offset": p.get_latest_offset()
                }
                for p in self.partitions
            ]
        }

    def __repr__(self):
        return f"Topic({self.name}, partitions={self.num_partitions})"


class Producer:
    """
    Kafka Producer - Publishes messages to topics.

    Key Concepts:
    - Sends messages to specific topic
    - Can specify partition key for ordering
    - Batching for efficiency
    - Async or sync sends
    """

    def __init__(self, producer_id: str):
        self.producer_id = producer_id
        self.message_count = 0

    def send(self, topic: Topic, key: Optional[str], value: Any,
             headers: Optional[Dict[str, str]] = None) -> Message:
        """
        Send message to topic.

        Args:
            topic: Target topic
            key: Message key (for partition assignment)
            value: Message value
            headers: Optional headers

        Returns:
            Sent message with partition and offset info
        """
        # Create message
        message = Message(
            key=key,
            value=value,
            headers=headers or {}
        )

        # Get partition (based on key)
        partition = topic.get_partition(key)

        # Append to partition
        offset = partition.append(message)

        self.message_count += 1
        return message

    def send_batch(self, topic: Topic, messages: List[tuple]) -> List[Message]:
        """
        Send batch of messages.

        Args:
            topic: Target topic
            messages: List of (key, value) tuples

        Returns:
            List of sent messages
        """
        sent_messages = []
        for key, value in messages:
            msg = self.send(topic, key, value)
            sent_messages.append(msg)
        return sent_messages

    def __repr__(self):
        return f"Producer({self.producer_id}, sent={self.message_count})"


class Consumer:
    """
    Kafka Consumer - Reads messages from topics.

    Key Concepts:
    - Subscribes to topics
    - Assigned partitions (from consumer group)
    - Tracks offsets (position in partition)
    - Can commit offsets manually or automatically
    """

    def __init__(self, consumer_id: str, group_id: str):
        self.consumer_id = consumer_id
        self.group_id = group_id
        self.assigned_partitions: List[tuple] = []  # (topic, partition_id)
        self.offsets: Dict[tuple, int] = {}  # (topic_name, partition_id) -> offset
        self.message_count = 0

    def assign_partitions(self, assignments: List[tuple]):
        """
        Assign partitions to this consumer.

        Args:
            assignments: List of (topic, partition_id) tuples
        """
        self.assigned_partitions = assignments

        # Initialize offsets to 0
        for topic, partition_id in assignments:
            key = (topic.name, partition_id)
            if key not in self.offsets:
                self.offsets[key] = 0

    def poll(self, topic: Topic, max_messages: int = 10) -> List[Message]:
        """
        Poll for new messages from assigned partitions.

        Args:
            topic: Topic to poll from
            max_messages: Maximum messages to fetch per partition

        Returns:
            List of messages
        """
        messages = []

        for topic_obj, partition_id in self.assigned_partitions:
            if topic_obj.name != topic.name:
                continue

            # Get partition
            partition = topic.get_partition_by_id(partition_id)
            if not partition:
                continue

            # Get current offset for this partition
            key = (topic.name, partition_id)
            current_offset = self.offsets.get(key, 0)

            # Read messages
            new_messages = partition.read(current_offset, max_messages)
            messages.extend(new_messages)

            # Update offset (but don't commit yet)
            if new_messages:
                last_offset = new_messages[-1].offset
                self.offsets[key] = last_offset + 1
                self.message_count += len(new_messages)

        return messages

    def commit(self):
        """
        Commit current offsets.

        In real Kafka, this persists offsets to __consumer_offsets topic.
        Here, we just keep them in memory.
        """
        # In real implementation, this would persist to Kafka
        pass

    def seek(self, topic: Topic, partition_id: int, offset: int):
        """
        Seek to specific offset in partition.

        Args:
            topic: Topic
            partition_id: Partition ID
            offset: Target offset
        """
        key = (topic.name, partition_id)
        self.offsets[key] = offset

    def get_stats(self) -> dict:
        """Get consumer statistics."""
        return {
            "consumer_id": self.consumer_id,
            "group_id": self.group_id,
            "assigned_partitions": len(self.assigned_partitions),
            "messages_consumed": self.message_count,
            "current_offsets": dict(self.offsets)
        }

    def __repr__(self):
        return f"Consumer({self.consumer_id}, group={self.group_id}, consumed={self.message_count})"


class ConsumerGroup:
    """
    Consumer Group - Group of consumers working together.

    Key Concepts:
    - Each partition assigned to exactly one consumer in group
    - Enables parallel processing
    - Automatic rebalancing when consumers join/leave
    - Multiple groups can consume same topic independently
    """

    def __init__(self, group_id: str):
        self.group_id = group_id
        self.consumers: List[Consumer] = []

    def add_consumer(self, consumer: Consumer):
        """Add consumer to group."""
        if consumer.group_id == self.group_id:
            self.consumers.append(consumer)

    def remove_consumer(self, consumer: Consumer):
        """Remove consumer from group."""
        if consumer in self.consumers:
            self.consumers.remove(consumer)

    def rebalance(self, topic: Topic):
        """
        Rebalance partitions among consumers.

        Uses simple round-robin assignment strategy.
        In real Kafka, this is more sophisticated (range, sticky, etc.)
        """
        if not self.consumers:
            return

        # Clear current assignments
        for consumer in self.consumers:
            consumer.assigned_partitions = []

        # Assign partitions round-robin
        for partition_id in range(topic.num_partitions):
            consumer_idx = partition_id % len(self.consumers)
            consumer = self.consumers[consumer_idx]
            consumer.assign_partitions([(topic, partition_id)])

        print(f"Rebalanced {topic.name}: {topic.num_partitions} partitions "
              f"among {len(self.consumers)} consumers")

    def get_stats(self) -> dict:
        """Get consumer group statistics."""
        return {
            "group_id": self.group_id,
            "consumers": len(self.consumers),
            "consumer_details": [c.get_stats() for c in self.consumers]
        }

    def __repr__(self):
        return f"ConsumerGroup({self.group_id}, consumers={len(self.consumers)})"


# ============================================================================
# Demonstrations
# ============================================================================

def demonstrate_basic_pubsub():
    """Demonstrate basic publish-subscribe."""
    print("="*60)
    print("BASIC KAFKA PUB/SUB")
    print("="*60)

    # Create topic
    topic = Topic("orders", num_partitions=3)
    print(f"\n1. Created topic: {topic}")

    # Create producer
    producer = Producer("producer-1")

    # Publish messages
    print("\n2. Publishing messages:")
    orders = [
        ("user-1", {"order_id": 101, "amount": 99.99}),
        ("user-2", {"order_id": 102, "amount": 149.99}),
        ("user-1", {"order_id": 103, "amount": 49.99}),  # Same user → same partition
    ]

    for key, value in orders:
        msg = producer.send(topic, key, value)
        print(f"   Sent: {msg}")

    # Show topic stats
    print("\n3. Topic Statistics:")
    stats = topic.get_stats()
    print(f"   Total messages: {stats['total_messages']}")
    for p in stats['partition_details']:
        print(f"   Partition {p['partition_id']}: {p['messages']} messages, "
              f"offset: {p['latest_offset']}")


def demonstrate_consumer_groups():
    """Demonstrate consumer groups and partition assignment."""
    print("\n" + "="*60)
    print("CONSUMER GROUPS & PARTITION ASSIGNMENT")
    print("="*60)

    # Create topic
    topic = Topic("events", num_partitions=6)

    # Publish messages
    producer = Producer("producer-1")
    print("\n1. Publishing 60 messages:")
    for i in range(60):
        producer.send(topic, f"key-{i % 10}", f"event-{i}")
    print(f"   Published 60 messages to {topic.num_partitions} partitions")

    # Create consumer group
    group = ConsumerGroup("group-1")

    # Add 3 consumers
    print("\n2. Creating consumer group with 3 consumers:")
    for i in range(3):
        consumer = Consumer(f"consumer-{i}", "group-1")
        group.add_consumer(consumer)

    # Rebalance (assign partitions)
    group.rebalance(topic)

    # Show assignments
    print("\n3. Partition Assignments:")
    for consumer in group.consumers:
        partitions = [p[1] for p in consumer.assigned_partitions]
        print(f"   {consumer.consumer_id}: partitions {partitions}")

    # Consume messages
    print("\n4. Consuming messages:")
    for consumer in group.consumers:
        messages = consumer.poll(topic, max_messages=100)
        print(f"   {consumer.consumer_id}: consumed {len(messages)} messages")


def demonstrate_message_ordering():
    """Demonstrate message ordering guarantees."""
    print("\n" + "="*60)
    print("MESSAGE ORDERING GUARANTEES")
    print("="*60)

    topic = Topic("user-actions", num_partitions=3)
    producer = Producer("producer-1")

    print("\n1. User actions (same user → same partition → ordered):")

    # User-1 actions (will go to same partition)
    user1_actions = [
        "login",
        "view_product",
        "add_to_cart",
        "checkout",
        "logout"
    ]

    for action in user1_actions:
        msg = producer.send(topic, key="user-1", value=action)
        print(f"   user-1: {action} → partition {msg.partition}, offset {msg.offset}")

    # User-2 actions (will go to different partition)
    print("\n2. Different user (different partition):")
    user2_actions = ["login", "view_product", "logout"]

    for action in user2_actions:
        msg = producer.send(topic, key="user-2", value=action)
        print(f"   user-2: {action} → partition {msg.partition}, offset {msg.offset}")

    print("\n3. Ordering guarantee:")
    print("   ✓ Messages with same key are ordered within partition")
    print("   ✓ user-1 actions: ordered (same partition)")
    print("   ✓ user-2 actions: ordered (same partition)")
    print("   ✗ No ordering guarantee across partitions")


def demonstrate_offset_management():
    """Demonstrate offset tracking and seeking."""
    print("\n" + "="*60)
    print("OFFSET MANAGEMENT")
    print("="*60)

    topic = Topic("logs", num_partitions=1)
    producer = Producer("producer-1")

    # Publish messages
    print("\n1. Publishing 10 log messages:")
    for i in range(10):
        producer.send(topic, key=None, value=f"log-{i}")
    print(f"   Published 10 messages")

    # Create consumer
    consumer = Consumer("consumer-1", "group-1")
    consumer.assign_partitions([(topic, 0)])

    # Read first 5 messages
    print("\n2. Read first 5 messages:")
    messages = consumer.poll(topic, max_messages=5)
    for msg in messages:
        print(f"   offset {msg.offset}: {msg.value}")

    print(f"\n3. Current offset: {consumer.offsets[(topic.name, 0)]}")

    # Commit offset
    consumer.commit()
    print(f"   Committed offset")

    # Read next 5 messages
    print("\n4. Read next 5 messages:")
    messages = consumer.poll(topic, max_messages=5)
    for msg in messages:
        print(f"   offset {msg.offset}: {msg.value}")

    # Seek to beginning
    print("\n5. Seek to beginning (offset 0):")
    consumer.seek(topic, 0, 0)
    messages = consumer.poll(topic, max_messages=3)
    for msg in messages:
        print(f"   offset {msg.offset}: {msg.value}")


def demonstrate_multiple_consumer_groups():
    """Demonstrate multiple independent consumer groups."""
    print("\n" + "="*60)
    print("MULTIPLE CONSUMER GROUPS")
    print("="*60)

    topic = Topic("notifications", num_partitions=2)
    producer = Producer("producer-1")

    # Publish messages
    print("\n1. Publishing 10 notification messages:")
    for i in range(10):
        producer.send(topic, key=f"user-{i}", value=f"notification-{i}")

    # Create two consumer groups
    print("\n2. Creating two independent consumer groups:")

    # Group 1: Email service
    email_group = ConsumerGroup("email-service")
    email_consumer = Consumer("email-1", "email-service")
    email_group.add_consumer(email_consumer)
    email_group.rebalance(topic)

    # Group 2: SMS service
    sms_group = ConsumerGroup("sms-service")
    sms_consumer = Consumer("sms-1", "sms-service")
    sms_group.add_consumer(sms_consumer)
    sms_group.rebalance(topic)

    # Both groups consume all messages independently
    print("\n3. Both groups consume same messages:")

    email_messages = email_consumer.poll(topic, max_messages=100)
    print(f"   Email service consumed: {len(email_messages)} messages")

    sms_messages = sms_consumer.poll(topic, max_messages=100)
    print(f"   SMS service consumed: {len(sms_messages)} messages")

    print("\n4. Key insight:")
    print("   Each consumer group maintains independent offsets")
    print("   Both groups can consume all messages from topic")


def demonstrate_rebalancing():
    """Demonstrate consumer group rebalancing."""
    print("\n" + "="*60)
    print("CONSUMER GROUP REBALANCING")
    print("="*60)

    topic = Topic("tasks", num_partitions=6)
    group = ConsumerGroup("workers")

    # Start with 2 consumers
    print("\n1. Initial: 2 consumers, 6 partitions:")
    for i in range(2):
        consumer = Consumer(f"worker-{i}", "workers")
        group.add_consumer(consumer)

    group.rebalance(topic)

    for consumer in group.consumers:
        partitions = [p[1] for p in consumer.assigned_partitions]
        print(f"   {consumer.consumer_id}: partitions {partitions} "
              f"({len(partitions)} partitions)")

    # Add third consumer
    print("\n2. Add worker-2 (rebalance triggered):")
    new_consumer = Consumer("worker-2", "workers")
    group.add_consumer(new_consumer)
    group.rebalance(topic)

    for consumer in group.consumers:
        partitions = [p[1] for p in consumer.assigned_partitions]
        print(f"   {consumer.consumer_id}: partitions {partitions} "
              f"({len(partitions)} partitions)")

    # Remove a consumer
    print("\n3. Remove worker-1 (rebalance triggered):")
    group.remove_consumer(group.consumers[0])
    group.rebalance(topic)

    for consumer in group.consumers:
        partitions = [p[1] for p in consumer.assigned_partitions]
        print(f"   {consumer.consumer_id}: partitions {partitions} "
              f"({len(partitions)} partitions)")


def demonstrate_real_world_scenario():
    """Demonstrate real-world e-commerce order processing."""
    print("\n" + "="*60)
    print("REAL-WORLD SCENARIO: E-COMMERCE ORDER PROCESSING")
    print("="*60)

    # Create topic
    topic = Topic("orders", num_partitions=4)

    # Producer: Order service
    print("\n1. Order Service (Producer):")
    order_service = Producer("order-service")

    # Simulate orders from different users
    orders = [
        ("user-101", {"order_id": 1001, "items": 3, "total": 149.99}),
        ("user-102", {"order_id": 1002, "items": 1, "total": 49.99}),
        ("user-101", {"order_id": 1003, "items": 2, "total": 99.99}),  # Same user
        ("user-103", {"order_id": 1004, "items": 5, "total": 299.99}),
    ]

    for user_id, order_data in orders:
        msg = order_service.send(topic, key=user_id, value=order_data)
        print(f"   Order {order_data['order_id']} from {user_id} "
              f"→ partition {msg.partition}")

    # Consumer Group 1: Payment processing
    print("\n2. Payment Processing (Consumer Group):")
    payment_group = ConsumerGroup("payment-processors")

    for i in range(2):
        consumer = Consumer(f"payment-{i}", "payment-processors")
        payment_group.add_consumer(consumer)

    payment_group.rebalance(topic)

    for consumer in payment_group.consumers:
        messages = consumer.poll(topic, max_messages=100)
        print(f"   {consumer.consumer_id}: processing {len(messages)} payments")
        for msg in messages:
            print(f"     Payment for order {msg.value['order_id']}: ${msg.value['total']}")

    # Consumer Group 2: Inventory update
    print("\n3. Inventory Update (Consumer Group):")
    inventory_group = ConsumerGroup("inventory-updaters")

    inventory_consumer = Consumer("inventory-1", "inventory-updaters")
    inventory_group.add_consumer(inventory_consumer)
    inventory_group.rebalance(topic)

    messages = inventory_consumer.poll(topic, max_messages=100)
    print(f"   {inventory_consumer.consumer_id}: updating inventory for {len(messages)} orders")
    for msg in messages:
        print(f"     Reserve {msg.value['items']} items for order {msg.value['order_id']}")

    # Consumer Group 3: Notification service
    print("\n4. Notification Service (Consumer Group):")
    notification_group = ConsumerGroup("notifications")

    notification_consumer = Consumer("notification-1", "notifications")
    notification_group.add_consumer(notification_consumer)
    notification_group.rebalance(topic)

    messages = notification_consumer.poll(topic, max_messages=100)
    print(f"   {notification_consumer.consumer_id}: sending {len(messages)} notifications")

    print("\n5. Summary:")
    print("   ✓ Same order data consumed by 3 different services")
    print("   ✓ Each service maintains independent offset")
    print("   ✓ Orders from same user processed in order")
    print("   ✓ Parallel processing across partitions")


if __name__ == "__main__":
    print("\nKafka Concepts and Demonstration")
    print("="*60)

    demonstrate_basic_pubsub()
    demonstrate_consumer_groups()
    demonstrate_message_ordering()
    demonstrate_offset_management()
    demonstrate_multiple_consumer_groups()
    demonstrate_rebalancing()
    demonstrate_real_world_scenario()

    print("\n" + "="*60)
    print("Demonstration Complete!")
    print("="*60)
    print("\nKey Takeaways:")
    print("1. Topics are split into partitions for parallelism")
    print("2. Messages with same key go to same partition (ordering)")
    print("3. Consumer groups enable parallel processing")
    print("4. Each partition consumed by one consumer in a group")
    print("5. Multiple groups can consume same topic independently")
    print("6. Offsets track consumer position in partition")
    print("="*60 + "\n")
