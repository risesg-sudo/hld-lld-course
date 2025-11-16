"""
Pub/Sub (Publish-Subscribe) System Implementation

A simple implementation demonstrating the publish-subscribe messaging pattern.

Components:
- Message Broker: Routes messages between publishers and subscribers
- Topics: Named channels for messages
- Publishers: Send messages to topics
- Subscribers: Receive messages from topics they subscribe to

Features:
- Multiple topics
- Multiple subscribers per topic
- Message filtering
- Persistent subscriptions
- Message history
"""

import time
import threading
from typing import Any, Callable, Dict, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque
from enum import Enum
import json


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Message:
    """Represents a message in the pub/sub system."""
    id: str
    topic: str
    payload: Any
    timestamp: float = field(default_factory=time.time)
    priority: MessagePriority = MessagePriority.NORMAL
    headers: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "topic": self.topic,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "priority": self.priority.name,
            "headers": self.headers
        }

    def __repr__(self):
        return f"Message(id={self.id}, topic={self.topic}, priority={self.priority.name})"


class Subscriber:
    """Represents a subscriber to topics."""

    def __init__(self, name: str, callback: Callable[[Message], None]):
        """
        Initialize subscriber.

        Args:
            name: Subscriber name/ID
            callback: Function to call when message received
        """
        self.name = name
        self.callback = callback
        self.subscribed_topics: Set[str] = set()
        self.message_count = 0
        self.filter_func: Optional[Callable[[Message], bool]] = None

    def receive_message(self, message: Message):
        """
        Receive and process a message.

        Args:
            message: Message to process
        """
        # Apply filter if set
        if self.filter_func and not self.filter_func(message):
            return

        try:
            self.callback(message)
            self.message_count += 1
        except Exception as e:
            print(f"Error in subscriber {self.name}: {e}")

    def set_filter(self, filter_func: Callable[[Message], bool]):
        """
        Set message filter.

        Args:
            filter_func: Function that returns True for messages to receive
        """
        self.filter_func = filter_func

    def __repr__(self):
        return f"Subscriber(name={self.name}, topics={self.subscribed_topics})"


class Topic:
    """Represents a topic in the pub/sub system."""

    def __init__(self, name: str, max_history: int = 100):
        """
        Initialize topic.

        Args:
            name: Topic name
            max_history: Maximum messages to keep in history
        """
        self.name = name
        self.subscribers: List[Subscriber] = []
        self.message_history: deque = deque(maxlen=max_history)
        self.message_count = 0
        self.created_at = time.time()

    def add_subscriber(self, subscriber: Subscriber):
        """Add subscriber to topic."""
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)
            subscriber.subscribed_topics.add(self.name)

    def remove_subscriber(self, subscriber: Subscriber):
        """Remove subscriber from topic."""
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)
            subscriber.subscribed_topics.discard(self.name)

    def publish(self, message: Message):
        """
        Publish message to all subscribers.

        Args:
            message: Message to publish
        """
        self.message_history.append(message)
        self.message_count += 1

        # Send to all subscribers
        for subscriber in self.subscribers:
            try:
                subscriber.receive_message(message)
            except Exception as e:
                print(f"Error sending to {subscriber.name}: {e}")

    def get_subscriber_count(self) -> int:
        """Get number of active subscribers."""
        return len(self.subscribers)

    def get_stats(self) -> dict:
        """Get topic statistics."""
        return {
            "name": self.name,
            "subscribers": len(self.subscribers),
            "total_messages": self.message_count,
            "history_size": len(self.message_history),
            "created_at": datetime.fromtimestamp(self.created_at).isoformat()
        }

    def __repr__(self):
        return f"Topic(name={self.name}, subscribers={len(self.subscribers)})"


class MessageBroker:
    """
    Message Broker - Central hub for pub/sub system.

    Manages topics, routes messages, and coordinates publishers/subscribers.
    """

    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.subscribers: Dict[str, Subscriber] = {}
        self.message_id_counter = 0
        self.lock = threading.Lock()
        self.total_messages = 0

    def create_topic(self, topic_name: str, max_history: int = 100) -> Topic:
        """
        Create a new topic.

        Args:
            topic_name: Name of the topic
            max_history: Maximum messages to keep in history

        Returns:
            Created topic
        """
        with self.lock:
            if topic_name not in self.topics:
                self.topics[topic_name] = Topic(topic_name, max_history)
            return self.topics[topic_name]

    def delete_topic(self, topic_name: str) -> bool:
        """
        Delete a topic.

        Args:
            topic_name: Name of the topic to delete

        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if topic_name in self.topics:
                # Remove topic from all subscribers
                topic = self.topics[topic_name]
                for subscriber in topic.subscribers:
                    subscriber.subscribed_topics.discard(topic_name)

                del self.topics[topic_name]
                return True
            return False

    def register_subscriber(self, name: str, callback: Callable[[Message], None]) -> Subscriber:
        """
        Register a new subscriber.

        Args:
            name: Subscriber name
            callback: Function to call when message received

        Returns:
            Created subscriber
        """
        with self.lock:
            if name not in self.subscribers:
                self.subscribers[name] = Subscriber(name, callback)
            return self.subscribers[name]

    def unregister_subscriber(self, name: str) -> bool:
        """
        Unregister a subscriber.

        Args:
            name: Subscriber name

        Returns:
            True if unregistered, False if not found
        """
        with self.lock:
            if name in self.subscribers:
                subscriber = self.subscribers[name]

                # Unsubscribe from all topics
                for topic_name in list(subscriber.subscribed_topics):
                    self.unsubscribe(name, topic_name)

                del self.subscribers[name]
                return True
            return False

    def subscribe(self, subscriber_name: str, topic_name: str):
        """
        Subscribe to a topic.

        Args:
            subscriber_name: Name of subscriber
            topic_name: Name of topic
        """
        with self.lock:
            # Create topic if doesn't exist
            if topic_name not in self.topics:
                self.create_topic(topic_name)

            # Get subscriber
            if subscriber_name not in self.subscribers:
                raise ValueError(f"Subscriber {subscriber_name} not registered")

            subscriber = self.subscribers[subscriber_name]
            topic = self.topics[topic_name]

            topic.add_subscriber(subscriber)

    def unsubscribe(self, subscriber_name: str, topic_name: str):
        """
        Unsubscribe from a topic.

        Args:
            subscriber_name: Name of subscriber
            topic_name: Name of topic
        """
        with self.lock:
            if topic_name in self.topics and subscriber_name in self.subscribers:
                topic = self.topics[topic_name]
                subscriber = self.subscribers[subscriber_name]
                topic.remove_subscriber(subscriber)

    def publish(self, topic_name: str, payload: Any,
                priority: MessagePriority = MessagePriority.NORMAL,
                headers: Optional[Dict[str, Any]] = None) -> Message:
        """
        Publish a message to a topic.

        Args:
            topic_name: Name of topic
            payload: Message payload
            priority: Message priority
            headers: Optional message headers

        Returns:
            Published message
        """
        with self.lock:
            # Create topic if doesn't exist
            if topic_name not in self.topics:
                self.create_topic(topic_name)

            # Create message
            self.message_id_counter += 1
            message = Message(
                id=f"msg_{self.message_id_counter}",
                topic=topic_name,
                payload=payload,
                priority=priority,
                headers=headers or {}
            )

            # Publish to topic
            topic = self.topics[topic_name]
            topic.publish(message)

            self.total_messages += 1
            return message

    def get_topic(self, topic_name: str) -> Optional[Topic]:
        """Get topic by name."""
        return self.topics.get(topic_name)

    def get_subscriber(self, subscriber_name: str) -> Optional[Subscriber]:
        """Get subscriber by name."""
        return self.subscribers.get(subscriber_name)

    def get_stats(self) -> dict:
        """Get broker statistics."""
        return {
            "total_topics": len(self.topics),
            "total_subscribers": len(self.subscribers),
            "total_messages": self.total_messages,
            "topics": {
                name: topic.get_stats()
                for name, topic in self.topics.items()
            }
        }

    def __repr__(self):
        return f"MessageBroker(topics={len(self.topics)}, subscribers={len(self.subscribers)})"


# ============================================================================
# Advanced Features
# ============================================================================

class PersistentMessageBroker(MessageBroker):
    """
    Message Broker with persistence support.

    Saves messages to disk for durability.
    """

    def __init__(self, storage_file: str = "messages.jsonl"):
        super().__init__()
        self.storage_file = storage_file

    def publish(self, topic_name: str, payload: Any,
                priority: MessagePriority = MessagePriority.NORMAL,
                headers: Optional[Dict[str, Any]] = None) -> Message:
        """Publish message and persist to disk."""
        message = super().publish(topic_name, payload, priority, headers)

        # Persist message
        try:
            with open(self.storage_file, 'a') as f:
                f.write(json.dumps(message.to_dict()) + '\n')
        except Exception as e:
            print(f"Error persisting message: {e}")

        return message

    def load_history(self):
        """Load message history from disk."""
        try:
            with open(self.storage_file, 'r') as f:
                for line in f:
                    msg_dict = json.loads(line)
                    # Reconstruct message
                    topic_name = msg_dict['topic']
                    if topic_name in self.topics:
                        message = Message(
                            id=msg_dict['id'],
                            topic=msg_dict['topic'],
                            payload=msg_dict['payload'],
                            timestamp=msg_dict['timestamp'],
                            priority=MessagePriority[msg_dict['priority']],
                            headers=msg_dict['headers']
                        )
                        self.topics[topic_name].message_history.append(message)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading history: {e}")


# ============================================================================
# Demonstration and Testing
# ============================================================================

def demonstrate_basic_pubsub():
    """Demonstrate basic pub/sub functionality."""
    print("="*60)
    print("BASIC PUB/SUB DEMONSTRATION")
    print("="*60)

    broker = MessageBroker()

    # Create topics
    print("\n1. Creating topics:")
    broker.create_topic("news")
    broker.create_topic("sports")
    broker.create_topic("weather")
    print(f"   Topics: {list(broker.topics.keys())}")

    # Register subscribers
    print("\n2. Registering subscribers:")

    def print_message(msg: Message):
        print(f"   [{msg.topic}] {msg.payload}")

    alice = broker.register_subscriber("alice", print_message)
    bob = broker.register_subscriber("bob", print_message)
    charlie = broker.register_subscriber("charlie", print_message)

    print(f"   Subscribers: {list(broker.subscribers.keys())}")

    # Subscribe to topics
    print("\n3. Subscribing to topics:")
    broker.subscribe("alice", "news")
    broker.subscribe("alice", "weather")
    print(f"   Alice subscribed to: {alice.subscribed_topics}")

    broker.subscribe("bob", "sports")
    broker.subscribe("bob", "news")
    print(f"   Bob subscribed to: {bob.subscribed_topics}")

    broker.subscribe("charlie", "weather")
    print(f"   Charlie subscribed to: {charlie.subscribed_topics}")

    # Publish messages
    print("\n4. Publishing messages:")
    print("\n   Publishing to 'news' topic:")
    broker.publish("news", "Breaking: New discovery!")

    print("\n   Publishing to 'sports' topic:")
    broker.publish("sports", "Game result: Team A wins!")

    print("\n   Publishing to 'weather' topic:")
    broker.publish("weather", "Sunny with 25°C")

    # Show statistics
    print("\n5. Statistics:")
    print(f"   Alice received {alice.message_count} messages")
    print(f"   Bob received {bob.message_count} messages")
    print(f"   Charlie received {charlie.message_count} messages")


def demonstrate_message_filtering():
    """Demonstrate message filtering."""
    print("\n" + "="*60)
    print("MESSAGE FILTERING DEMONSTRATION")
    print("="*60)

    broker = MessageBroker()

    # Create subscribers with different filters
    print("\n1. Creating filtered subscribers:")

    high_priority_messages = []
    normal_priority_messages = []

    def high_priority_handler(msg: Message):
        high_priority_messages.append(msg)
        print(f"   [HIGH PRIORITY] {msg.payload}")

    def normal_handler(msg: Message):
        normal_priority_messages.append(msg)
        print(f"   [NORMAL] {msg.payload}")

    # Register subscribers
    high_sub = broker.register_subscriber("high_priority_sub", high_priority_handler)
    normal_sub = broker.register_subscriber("normal_sub", normal_handler)

    # Set filters
    high_sub.set_filter(lambda msg: msg.priority == MessagePriority.HIGH or
                                    msg.priority == MessagePriority.CRITICAL)

    # Subscribe to topic
    broker.subscribe("high_priority_sub", "alerts")
    broker.subscribe("normal_sub", "alerts")

    # Publish messages with different priorities
    print("\n2. Publishing messages with different priorities:")

    broker.publish("alerts", "System update available", MessagePriority.NORMAL)
    broker.publish("alerts", "Security patch required", MessagePriority.HIGH)
    broker.publish("alerts", "Server maintenance scheduled", MessagePriority.NORMAL)
    broker.publish("alerts", "CRITICAL: Security breach detected!", MessagePriority.CRITICAL)

    print(f"\n3. Results:")
    print(f"   High priority subscriber received: {len(high_priority_messages)} messages")
    print(f"   Normal subscriber received: {len(normal_priority_messages)} messages")


def demonstrate_dynamic_subscriptions():
    """Demonstrate dynamic subscribe/unsubscribe."""
    print("\n" + "="*60)
    print("DYNAMIC SUBSCRIPTIONS DEMONSTRATION")
    print("="*60)

    broker = MessageBroker()

    received_messages = []

    def message_handler(msg: Message):
        received_messages.append(msg)
        print(f"   Received: {msg.payload}")

    subscriber = broker.register_subscriber("dynamic_sub", message_handler)

    print("\n1. Initially subscribed to 'updates':")
    broker.subscribe("dynamic_sub", "updates")
    broker.publish("updates", "Update 1")
    broker.publish("updates", "Update 2")

    print(f"\n2. Unsubscribe from 'updates':")
    broker.unsubscribe("dynamic_sub", "updates")
    broker.publish("updates", "Update 3 (not received)")

    print(f"\n3. Subscribe to 'notifications':")
    broker.subscribe("dynamic_sub", "notifications")
    broker.publish("notifications", "Notification 1")

    print(f"\n4. Total messages received: {len(received_messages)}")
    print(f"   Messages: {[msg.payload for msg in received_messages]}")


def demonstrate_fanout_pattern():
    """Demonstrate fan-out pattern (one publisher, multiple subscribers)."""
    print("\n" + "="*60)
    print("FAN-OUT PATTERN DEMONSTRATION")
    print("="*60)

    broker = MessageBroker()

    # Create multiple subscribers for same topic
    print("\n1. Creating multiple subscribers for 'broadcast' topic:")

    subscribers = []
    for i in range(5):
        name = f"subscriber_{i+1}"
        sub = broker.register_subscriber(
            name,
            lambda msg, n=name: print(f"   {n} received: {msg.payload}")
        )
        broker.subscribe(name, "broadcast")
        subscribers.append(sub)

    print(f"   Created {len(subscribers)} subscribers")

    # Publish one message
    print("\n2. Publishing one message:")
    broker.publish("broadcast", "Hello to all subscribers!")

    print(f"\n3. Result: All {len(subscribers)} subscribers received the message")


def demonstrate_topic_patterns():
    """Demonstrate different topic organization patterns."""
    print("\n" + "="*60)
    print("TOPIC PATTERNS DEMONSTRATION")
    print("="*60)

    broker = MessageBroker()

    # Hierarchical topics
    print("\n1. Hierarchical Topics:")
    topics = [
        "orders.created",
        "orders.updated",
        "orders.completed",
        "users.registered",
        "users.updated",
        "payments.processed",
        "payments.failed"
    ]

    for topic in topics:
        broker.create_topic(topic)
    print(f"   Created {len(topics)} topics with hierarchical names")

    # Subscribe to patterns
    def order_handler(msg: Message):
        print(f"   Order event: {msg.topic} - {msg.payload}")

    def payment_handler(msg: Message):
        print(f"   Payment event: {msg.topic} - {msg.payload}")

    # Subscribe order subscriber to all order topics
    order_sub = broker.register_subscriber("order_processor", order_handler)
    for topic in [t for t in topics if t.startswith("orders.")]:
        broker.subscribe("order_processor", topic)

    # Subscribe payment subscriber to payment topics
    payment_sub = broker.register_subscriber("payment_processor", payment_handler)
    for topic in [t for t in topics if t.startswith("payments.")]:
        broker.subscribe("payment_processor", topic)

    print("\n2. Publishing events:")
    broker.publish("orders.created", {"order_id": 123, "amount": 99.99})
    broker.publish("payments.processed", {"payment_id": 456, "status": "success"})
    broker.publish("orders.completed", {"order_id": 123, "status": "shipped"})

    print(f"\n3. Statistics:")
    stats = broker.get_stats()
    print(f"   Total topics: {stats['total_topics']}")
    print(f"   Total messages: {stats['total_messages']}")


def demonstrate_message_history():
    """Demonstrate message history feature."""
    print("\n" + "="*60)
    print("MESSAGE HISTORY DEMONSTRATION")
    print("="*60)

    broker = MessageBroker()
    broker.create_topic("logs", max_history=5)

    print("\n1. Publishing 10 messages (history limit=5):")
    for i in range(10):
        broker.publish("logs", f"Log entry {i+1}")
        print(f"   Published: Log entry {i+1}")

    print("\n2. Checking message history:")
    topic = broker.get_topic("logs")
    print(f"   History size: {len(topic.message_history)}")
    print(f"   Messages in history:")
    for msg in topic.message_history:
        print(f"     - {msg.payload}")

    print("\n3. Late subscriber can access history:")
    late_sub = broker.register_subscriber(
        "late_subscriber",
        lambda msg: print(f"   Late sub received: {msg.payload}")
    )
    broker.subscribe("late_subscriber", "logs")

    # Manually send history to late subscriber
    print("\n   Sending history to late subscriber:")
    for msg in topic.message_history:
        late_sub.receive_message(msg)


def run_performance_test():
    """Run performance test."""
    print("\n" + "="*60)
    print("PERFORMANCE TEST")
    print("="*60)

    broker = MessageBroker()

    # Create topic
    broker.create_topic("performance_test")

    # Create subscribers
    num_subscribers = 100
    message_count = 0

    def counter_handler(msg: Message):
        nonlocal message_count
        message_count += 1

    print(f"\n1. Creating {num_subscribers} subscribers...")
    for i in range(num_subscribers):
        sub_name = f"sub_{i}"
        broker.register_subscriber(sub_name, counter_handler)
        broker.subscribe(sub_name, "performance_test")

    # Publish messages
    num_messages = 1000
    print(f"\n2. Publishing {num_messages} messages...")

    start_time = time.time()
    for i in range(num_messages):
        broker.publish("performance_test", f"Message {i}")
    end_time = time.time()

    elapsed = end_time - start_time
    throughput = num_messages / elapsed
    messages_delivered = message_count

    print(f"\n3. Results:")
    print(f"   Time elapsed: {elapsed:.4f} seconds")
    print(f"   Throughput: {throughput:.0f} messages/second")
    print(f"   Total messages delivered: {messages_delivered:,}")
    print(f"   Average: {messages_delivered / num_messages:.0f} subscribers per message")


if __name__ == "__main__":
    print("\nPub/Sub System Implementation and Demonstration")
    print("="*60)

    demonstrate_basic_pubsub()
    demonstrate_message_filtering()
    demonstrate_dynamic_subscriptions()
    demonstrate_fanout_pattern()
    demonstrate_topic_patterns()
    demonstrate_message_history()
    run_performance_test()

    print("\n" + "="*60)
    print("Demonstration Complete!")
    print("="*60 + "\n")
