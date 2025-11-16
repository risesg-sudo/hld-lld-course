"""
Polling vs Streaming - Communication Patterns

This module demonstrates different real-time communication patterns:
1. Short Polling
2. Long Polling
3. Server-Sent Events (SSE)
4. WebSockets (simulated)

Author: HLD Course
"""

import time
import threading
import queue
import random
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from collections import deque


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Message:
    """Message model"""
    id: str
    content: str
    sender: str
    timestamp: datetime

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class StockPrice:
    """Stock price update"""
    symbol: str
    price: float
    change: float
    timestamp: datetime

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'price': self.price,
            'change': self.change,
            'timestamp': self.timestamp.isoformat()
        }


# ============================================================================
# Message Queue (Simulated Backend)
# ============================================================================

class MessageQueue:
    """
    Simulates a message queue or event stream
    Multiple clients can subscribe to receive messages
    """

    def __init__(self):
        self.messages: deque = deque(maxlen=100)
        self.subscribers: List[queue.Queue] = []
        self.lock = threading.Lock()
        self.message_counter = 0

    def publish(self, message: Message):
        """Publish message to all subscribers"""
        with self.lock:
            self.messages.append(message)

            # Notify all subscribers
            for subscriber_queue in self.subscribers:
                try:
                    subscriber_queue.put_nowait(message)
                except queue.Full:
                    pass  # Subscriber queue is full, skip

    def subscribe(self) -> queue.Queue:
        """Subscribe to message queue"""
        subscriber_queue = queue.Queue(maxsize=50)
        with self.lock:
            self.subscribers.append(subscriber_queue)
        return subscriber_queue

    def unsubscribe(self, subscriber_queue: queue.Queue):
        """Unsubscribe from message queue"""
        with self.lock:
            if subscriber_queue in self.subscribers:
                self.subscribers.remove(subscriber_queue)

    def get_messages_since(self, last_id: Optional[str] = None) -> List[Message]:
        """Get messages since last_id (for polling)"""
        with self.lock:
            if last_id is None:
                return list(self.messages)

            # Find messages after last_id
            result = []
            found_last = False
            for msg in self.messages:
                if found_last:
                    result.append(msg)
                elif msg.id == last_id:
                    found_last = True

            return result

    def generate_random_message(self):
        """Generate random message for demo"""
        self.message_counter += 1
        senders = ['Alice', 'Bob', 'Charlie', 'Diana']
        contents = [
            'Hello!',
            'How are you?',
            'Check out this new feature!',
            'Meeting at 3pm',
            'Great job on the project!',
        ]

        message = Message(
            id=f"msg_{self.message_counter}",
            content=random.choice(contents),
            sender=random.choice(senders),
            timestamp=datetime.utcnow()
        )

        self.publish(message)
        return message


# ============================================================================
# 1. Short Polling
# ============================================================================

class ShortPollingClient:
    """
    Short Polling Implementation

    Client repeatedly requests updates at fixed intervals.
    Server responds immediately (even if no new data).

    Pros:
    - Simple to implement
    - Works with any HTTP infrastructure
    - Easy to debug

    Cons:
    - High latency (interval between polls)
    - Wasteful (many empty responses)
    - High server load

    Use Cases:
    - Non-critical updates
    - Low-frequency data changes
    - Simple requirements
    """

    def __init__(self, message_queue: MessageQueue, interval: float = 5.0):
        """
        Initialize short polling client

        Args:
            message_queue: Message queue to poll
            interval: Polling interval in seconds
        """
        self.message_queue = message_queue
        self.interval = interval
        self.last_message_id = None
        self.running = False
        self.messages_received = 0
        self.empty_responses = 0

    def start(self, duration: float = 30.0):
        """
        Start polling

        Args:
            duration: How long to poll (seconds)
        """
        print(f"\n[Short Polling] Starting (interval: {self.interval}s)")
        self.running = True
        start_time = time.time()

        while self.running and (time.time() - start_time) < duration:
            # Make request to server
            request_time = time.time()
            new_messages = self.message_queue.get_messages_since(self.last_message_id)

            if new_messages:
                self.messages_received += len(new_messages)
                for msg in new_messages:
                    print(f"  ✓ [{msg.sender}] {msg.content}")
                    self.last_message_id = msg.id
            else:
                self.empty_responses += 1

            # Wait for next poll
            elapsed = time.time() - request_time
            sleep_time = max(0, self.interval - elapsed)
            time.sleep(sleep_time)

        self.stop()

    def stop(self):
        """Stop polling"""
        self.running = False
        print(f"\n[Short Polling] Stopped")
        print(f"  Messages received: {self.messages_received}")
        print(f"  Empty responses: {self.empty_responses}")
        efficiency = (self.messages_received / (self.messages_received + self.empty_responses) * 100)
        print(f"  Efficiency: {efficiency:.1f}%")


# ============================================================================
# 2. Long Polling
# ============================================================================

class LongPollingServer:
    """
    Long Polling Server

    Server holds connection open until new data available or timeout.
    More efficient than short polling.
    """

    def __init__(self, message_queue: MessageQueue, timeout: float = 30.0):
        """
        Initialize long polling server

        Args:
            message_queue: Message queue
            timeout: Maximum time to hold connection (seconds)
        """
        self.message_queue = message_queue
        self.timeout = timeout

    def wait_for_messages(self, last_id: Optional[str] = None) -> List[Message]:
        """
        Wait for new messages (long polling endpoint)

        Args:
            last_id: ID of last received message

        Returns:
            List of new messages
        """
        start_time = time.time()
        subscriber_queue = self.message_queue.subscribe()

        try:
            # First, check if there are already new messages
            existing = self.message_queue.get_messages_since(last_id)
            if existing:
                return existing

            # Wait for new messages
            while time.time() - start_time < self.timeout:
                try:
                    # Wait for message with timeout
                    remaining_time = self.timeout - (time.time() - start_time)
                    if remaining_time <= 0:
                        break

                    message = subscriber_queue.get(timeout=remaining_time)
                    return [message]

                except queue.Empty:
                    break

            # Timeout - no new messages
            return []

        finally:
            self.message_queue.unsubscribe(subscriber_queue)


class LongPollingClient:
    """
    Long Polling Client

    Client makes request and waits for response.
    Immediately makes new request after receiving response.
    """

    def __init__(self, server: LongPollingServer):
        """
        Initialize long polling client

        Args:
            server: Long polling server
        """
        self.server = server
        self.last_message_id = None
        self.running = False
        self.messages_received = 0
        self.requests_made = 0

    def start(self, duration: float = 30.0):
        """Start long polling"""
        print(f"\n[Long Polling] Starting")
        self.running = True
        start_time = time.time()

        while self.running and (time.time() - start_time) < duration:
            self.requests_made += 1

            # Make long polling request
            new_messages = self.server.wait_for_messages(self.last_message_id)

            if new_messages:
                self.messages_received += len(new_messages)
                for msg in new_messages:
                    print(f"  ✓ [{msg.sender}] {msg.content}")
                    self.last_message_id = msg.id

            # Immediately reconnect (no wait)

        self.stop()

    def stop(self):
        """Stop long polling"""
        self.running = False
        print(f"\n[Long Polling] Stopped")
        print(f"  Messages received: {self.messages_received}")
        print(f"  Requests made: {self.requests_made}")
        if self.requests_made > 0:
            avg = self.messages_received / self.requests_made
            print(f"  Average messages per request: {avg:.2f}")


# ============================================================================
# 3. Server-Sent Events (SSE)
# ============================================================================

class SSEServer:
    """
    Server-Sent Events (SSE) Server

    Unidirectional streaming from server to client.
    Connection stays open, server pushes data as available.

    Pros:
    - Efficient for server-to-client updates
    - Auto-reconnection built-in
    - Simple protocol over HTTP

    Cons:
    - One-way communication only
    - Browser connection limits
    - Limited by HTTP connection limits

    Use Cases:
    - Live feeds
    - Stock tickers
    - Real-time notifications
    - Live sports scores
    """

    def __init__(self, message_queue: MessageQueue):
        """
        Initialize SSE server

        Args:
            message_queue: Message queue
        """
        self.message_queue = message_queue

    def stream_events(self, client_queue: queue.Queue, stop_event: threading.Event):
        """
        Stream events to client

        Args:
            client_queue: Queue to send events
            stop_event: Event to signal stop
        """
        subscriber_queue = self.message_queue.subscribe()

        try:
            while not stop_event.is_set():
                try:
                    message = subscriber_queue.get(timeout=1.0)

                    # Format as SSE event
                    event_data = {
                        'event': 'message',
                        'data': message.to_dict()
                    }

                    client_queue.put(event_data)

                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    client_queue.put({'event': 'heartbeat', 'data': {}})

        finally:
            self.message_queue.unsubscribe(subscriber_queue)


class SSEClient:
    """
    Server-Sent Events (SSE) Client

    Maintains persistent connection to receive server-pushed events.
    """

    def __init__(self, server: SSEServer):
        """
        Initialize SSE client

        Args:
            server: SSE server
        """
        self.server = server
        self.running = False
        self.messages_received = 0
        self.heartbeats_received = 0

    def start(self, duration: float = 30.0):
        """Start SSE client"""
        print(f"\n[SSE] Starting")
        self.running = True

        client_queue = queue.Queue()
        stop_event = threading.Event()

        # Start server streaming in background thread
        stream_thread = threading.Thread(
            target=self.server.stream_events,
            args=(client_queue, stop_event)
        )
        stream_thread.start()

        start_time = time.time()

        try:
            while self.running and (time.time() - start_time) < duration:
                try:
                    event = client_queue.get(timeout=1.0)

                    if event['event'] == 'message':
                        self.messages_received += 1
                        msg_data = event['data']
                        print(f"  ✓ [{msg_data['sender']}] {msg_data['content']}")
                    elif event['event'] == 'heartbeat':
                        self.heartbeats_received += 1

                except queue.Empty:
                    pass

        finally:
            stop_event.set()
            stream_thread.join()
            self.stop()

    def stop(self):
        """Stop SSE client"""
        self.running = False
        print(f"\n[SSE] Stopped")
        print(f"  Messages received: {self.messages_received}")
        print(f"  Heartbeats received: {self.heartbeats_received}")


# ============================================================================
# 4. WebSocket (Simulated)
# ============================================================================

class WebSocketServer:
    """
    Simulated WebSocket Server

    Full-duplex bidirectional communication.
    Persistent connection with low overhead.

    Pros:
    - True real-time, bidirectional
    - Low latency
    - Efficient for high-frequency updates

    Cons:
    - More complex to implement
    - Stateful (harder to scale)
    - Firewall/proxy issues

    Use Cases:
    - Real-time gaming
    - Collaborative editing
    - Live chat
    - Trading platforms
    """

    def __init__(self, message_queue: MessageQueue):
        """
        Initialize WebSocket server

        Args:
            message_queue: Message queue
        """
        self.message_queue = message_queue

    def handle_connection(self, client_send_queue: queue.Queue,
                         client_receive_queue: queue.Queue,
                         stop_event: threading.Event):
        """
        Handle WebSocket connection

        Args:
            client_send_queue: Queue to send messages to client
            client_receive_queue: Queue to receive messages from client
            stop_event: Event to signal stop
        """
        # Subscribe to message queue
        subscriber_queue = self.message_queue.subscribe()

        try:
            while not stop_event.is_set():
                # Check for messages from message queue
                try:
                    message = subscriber_queue.get(timeout=0.1)
                    client_send_queue.put({
                        'type': 'message',
                        'data': message.to_dict()
                    })
                except queue.Empty:
                    pass

                # Check for messages from client
                try:
                    client_message = client_receive_queue.get_nowait()
                    # Echo back or process
                    if client_message['type'] == 'ping':
                        client_send_queue.put({'type': 'pong'})
                except queue.Empty:
                    pass

        finally:
            self.message_queue.unsubscribe(subscriber_queue)


class WebSocketClient:
    """
    Simulated WebSocket Client

    Bidirectional communication with server.
    """

    def __init__(self, server: WebSocketServer):
        """
        Initialize WebSocket client

        Args:
            server: WebSocket server
        """
        self.server = server
        self.running = False
        self.messages_received = 0
        self.messages_sent = 0

    def start(self, duration: float = 30.0):
        """Start WebSocket client"""
        print(f"\n[WebSocket] Starting")
        self.running = True

        send_queue = queue.Queue()
        receive_queue = queue.Queue()
        stop_event = threading.Event()

        # Start server handler in background thread
        server_thread = threading.Thread(
            target=self.server.handle_connection,
            args=(send_queue, receive_queue, stop_event)
        )
        server_thread.start()

        start_time = time.time()

        try:
            while self.running and (time.time() - start_time) < duration:
                # Receive messages
                try:
                    message = send_queue.get(timeout=0.1)

                    if message['type'] == 'message':
                        self.messages_received += 1
                        msg_data = message['data']
                        print(f"  ✓ [{msg_data['sender']}] {msg_data['content']}")
                    elif message['type'] == 'pong':
                        print(f"  ← Pong received")

                except queue.Empty:
                    pass

                # Send ping every 10 seconds
                if int(time.time() - start_time) % 10 == 0:
                    receive_queue.put({'type': 'ping'})
                    self.messages_sent += 1
                    print(f"  → Ping sent")
                    time.sleep(1)  # Avoid spamming

        finally:
            stop_event.set()
            server_thread.join()
            self.stop()

    def stop(self):
        """Stop WebSocket client"""
        self.running = False
        print(f"\n[WebSocket] Stopped")
        print(f"  Messages received: {self.messages_received}")
        print(f"  Messages sent: {self.messages_sent}")


# ============================================================================
# Demo and Comparison
# ============================================================================

def demo_short_polling():
    """Demonstrate short polling"""
    print("\n" + "=" * 70)
    print("SHORT POLLING DEMO")
    print("=" * 70)

    message_queue = MessageQueue()

    # Start message generator
    def generate_messages():
        for _ in range(5):
            time.sleep(random.uniform(2, 8))
            message_queue.generate_random_message()

    generator_thread = threading.Thread(target=generate_messages)
    generator_thread.start()

    # Start client
    client = ShortPollingClient(message_queue, interval=3.0)
    client.start(duration=30)

    generator_thread.join()


def demo_long_polling():
    """Demonstrate long polling"""
    print("\n" + "=" * 70)
    print("LONG POLLING DEMO")
    print("=" * 70)

    message_queue = MessageQueue()
    server = LongPollingServer(message_queue, timeout=10.0)

    # Start message generator
    def generate_messages():
        for _ in range(5):
            time.sleep(random.uniform(2, 8))
            message_queue.generate_random_message()

    generator_thread = threading.Thread(target=generate_messages)
    generator_thread.start()

    # Start client
    client = LongPollingClient(server)
    client.start(duration=30)

    generator_thread.join()


def demo_sse():
    """Demonstrate Server-Sent Events"""
    print("\n" + "=" * 70)
    print("SERVER-SENT EVENTS (SSE) DEMO")
    print("=" * 70)

    message_queue = MessageQueue()
    server = SSEServer(message_queue)

    # Start message generator
    def generate_messages():
        for _ in range(5):
            time.sleep(random.uniform(2, 6))
            message_queue.generate_random_message()

    generator_thread = threading.Thread(target=generate_messages)
    generator_thread.start()

    # Start client
    client = SSEClient(server)
    client.start(duration=30)

    generator_thread.join()


def demo_websocket():
    """Demonstrate WebSocket"""
    print("\n" + "=" * 70)
    print("WEBSOCKET DEMO")
    print("=" * 70)

    message_queue = MessageQueue()
    server = WebSocketServer(message_queue)

    # Start message generator
    def generate_messages():
        for _ in range(5):
            time.sleep(random.uniform(2, 6))
            message_queue.generate_random_message()

    generator_thread = threading.Thread(target=generate_messages)
    generator_thread.start()

    # Start client
    client = WebSocketClient(server)
    client.start(duration=30)

    generator_thread.join()


def print_comparison_table():
    """Print comparison table"""
    print("\n" + "=" * 70)
    print("COMPARISON TABLE")
    print("=" * 70)

    table = """
| Feature           | Short Poll | Long Poll | SSE    | WebSocket |
|-------------------|------------|-----------|--------|-----------|
| Latency           | High       | Medium    | Low    | Very Low  |
| Server Load       | High       | Medium    | Low    | Low       |
| Real-time         | No         | Near      | Yes    | Yes       |
| Bidirectional     | Yes        | Yes       | No     | Yes       |
| Complexity        | Low        | Medium    | Medium | High      |
| Browser Support   | All        | All       | Modern | Modern    |
| Scalability       | Poor       | Medium    | Good   | Good      |
| Use HTTP          | Yes        | Yes       | Yes    | Upgrade   |

Use Cases:

1. Short Polling:
   - Updates every few minutes acceptable
   - Simple requirements
   - Legacy systems

2. Long Polling:
   - Near real-time updates needed
   - HTTP-only infrastructure
   - Moderate update frequency

3. SSE:
   - Server-to-client updates only
   - Live feeds/notifications
   - Auto-reconnection needed

4. WebSocket:
   - True bidirectional real-time
   - High-frequency updates
   - Gaming, chat, collaboration
    """

    print(table)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("POLLING VS STREAMING - COMPREHENSIVE DEMONSTRATION")
    print("=" * 70)

    # Run all demos
    demo_short_polling()
    time.sleep(2)

    demo_long_polling()
    time.sleep(2)

    demo_sse()
    time.sleep(2)

    demo_websocket()

    # Print comparison
    print_comparison_table()

    print("\n" + "=" * 70)
    print("All Demos Complete!")
    print("=" * 70)

    print("\n📝 Key Takeaways:")
    print("1. Short polling: Simple but inefficient")
    print("2. Long polling: Better than short polling, but still has overhead")
    print("3. SSE: Efficient for server-to-client streaming")
    print("4. WebSocket: Best for bidirectional real-time communication")
    print("5. Choose based on your use case and requirements")
    print("=" * 70)
