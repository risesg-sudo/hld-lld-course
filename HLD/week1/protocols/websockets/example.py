"""
WebSocket Communication Demo
=============================

Demonstrates full-duplex, bi-directional WebSocket communication.
Perfect for real-time applications like chat, notifications, live updates.

Requirements:
    pip install websockets

Usage:
    # Terminal 1 (Server)
    python websocket_demo.py server

    # Terminal 2 (Client)
    python websocket_demo.py client

    # Multiple clients can connect simultaneously
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime


class WebSocketServer:
    """
    WebSocket server supporting multiple concurrent clients.
    Demonstrates real-time bi-directional communication.
    """

    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.message_history = []

    async def register(self, websocket):
        """Register a new client."""
        self.clients.add(websocket)
        client_id = id(websocket)
        print(f"[SERVER] Client {client_id} connected. Total clients: {len(self.clients)}")

        # Send welcome message
        welcome_msg = {
            "type": "welcome",
            "message": "Connected to WebSocket server",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send(json.dumps(welcome_msg))

        # Send recent message history
        if self.message_history:
            history_msg = {
                "type": "history",
                "messages": self.message_history[-10:],  # Last 10 messages
            }
            await websocket.send(json.dumps(history_msg))

    async def unregister(self, websocket):
        """Unregister a client."""
        self.clients.remove(websocket)
        client_id = id(websocket)
        print(f"[SERVER] Client {client_id} disconnected. Total clients: {len(self.clients)}")

    async def broadcast(self, message, exclude=None):
        """
        Broadcast message to all connected clients.
        Exclude specific websocket if provided.
        """
        if self.clients:
            # Create list of clients to send to
            recipients = self.clients if exclude is None else self.clients - {exclude}

            # Send to all recipients
            tasks = [client.send(message) for client in recipients]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def handle_client(self, websocket, path):
        """
        Handle individual client connection.
        Processes incoming messages and broadcasts to other clients.
        """
        client_id = id(websocket)

        # Register client
        await self.register(websocket)

        try:
            # Listen for messages from this client
            async for message in websocket:
                print(f"[SERVER] Received from client {client_id}: {message}")

                try:
                    # Parse message
                    data = json.loads(message)
                    await self.process_message(websocket, data)

                except json.JSONDecodeError:
                    error_msg = {
                        "type": "error",
                        "message": "Invalid JSON format"
                    }
                    await websocket.send(json.dumps(error_msg))

        except websockets.exceptions.ConnectionClosed:
            print(f"[SERVER] Client {client_id} connection closed")
        finally:
            await self.unregister(websocket)

    async def process_message(self, websocket, data):
        """Process different types of messages."""
        msg_type = data.get('type', 'message')
        client_id = id(websocket)

        if msg_type == 'chat':
            # Chat message - broadcast to all clients
            chat_msg = {
                "type": "chat",
                "client_id": client_id,
                "message": data.get('message', ''),
                "username": data.get('username', f'User{client_id}'),
                "timestamp": datetime.now().isoformat()
            }

            # Store in history
            self.message_history.append(chat_msg)

            # Broadcast to all clients
            await self.broadcast(json.dumps(chat_msg))

        elif msg_type == 'ping':
            # Ping-pong for keep-alive
            pong_msg = {
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(pong_msg))

        elif msg_type == 'stats':
            # Server statistics
            stats_msg = {
                "type": "stats",
                "active_clients": len(self.clients),
                "total_messages": len(self.message_history),
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(stats_msg))

        else:
            # Echo back unknown message types
            echo_msg = {
                "type": "echo",
                "original": data,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(echo_msg))

    async def start(self):
        """Start the WebSocket server."""
        print(f"""
╔════════════════════════════════════════════════════╗
║         WebSocket Server Started                   ║
╚════════════════════════════════════════════════════╝

Server: ws://{self.host}:{self.port}

WebSocket Features Demonstrated:
✓ Bi-directional communication
✓ Full-duplex (simultaneous send/receive)
✓ Real-time message broadcasting
✓ Multiple concurrent clients
✓ Persistent connection
✓ Low latency
✓ Message history

Server running... Press Ctrl+C to stop.
        """)

        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever


class WebSocketClient:
    """
    WebSocket client for connecting to the server.
    Demonstrates client-side WebSocket implementation.
    """

    def __init__(self, uri='ws://localhost:8765', username=None):
        self.uri = uri
        self.username = username or f"User{id(self)}"
        self.websocket = None

    async def connect(self):
        """Connect to WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"[CLIENT] Connected to {self.uri}")
            return True
        except Exception as e:
            print(f"[CLIENT] Connection failed: {e}")
            return False

    async def send_message(self, message_type, **kwargs):
        """Send a message to the server."""
        if not self.websocket:
            print("[CLIENT] Not connected")
            return

        message = {
            "type": message_type,
            "username": self.username,
            **kwargs
        }

        await self.websocket.send(json.dumps(message))

    async def receive_messages(self):
        """Continuously receive messages from server."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("\n[CLIENT] Connection closed by server")
        except Exception as e:
            print(f"\n[CLIENT] Error: {e}")

    def handle_message(self, data):
        """Handle different types of messages from server."""
        msg_type = data.get('type', 'unknown')

        if msg_type == 'welcome':
            print(f"\n[SERVER] {data['message']}")
            print(f"[SERVER] Your client ID: {data['client_id']}")

        elif msg_type == 'history':
            print("\n[HISTORY] Recent messages:")
            for msg in data['messages']:
                self.print_chat_message(msg)

        elif msg_type == 'chat':
            self.print_chat_message(data)

        elif msg_type == 'stats':
            print(f"\n[STATS] Active clients: {data['active_clients']}")
            print(f"[STATS] Total messages: {data['total_messages']}")

        elif msg_type == 'pong':
            print(f"[PONG] Server responded at {data['timestamp']}")

        elif msg_type == 'error':
            print(f"\n[ERROR] {data['message']}")

        else:
            print(f"\n[MESSAGE] {json.dumps(data, indent=2)}")

    def print_chat_message(self, msg):
        """Format and print chat message."""
        username = msg.get('username', 'Unknown')
        message = msg.get('message', '')
        timestamp = msg.get('timestamp', '')[:19]  # Remove microseconds
        print(f"[{timestamp}] {username}: {message}")

    async def interactive_mode(self):
        """Run client in interactive mode."""
        # Start receiving messages in background
        receive_task = asyncio.create_task(self.receive_messages())

        print(f"\n[CLIENT] Interactive mode (username: {self.username})")
        print("Commands:")
        print("  /ping       - Send ping to server")
        print("  /stats      - Get server statistics")
        print("  /quit       - Disconnect and exit")
        print("  <message>   - Send chat message")
        print()

        try:
            # Read user input in a non-blocking way
            while True:
                # Use run_in_executor to make input non-blocking
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, f"[{self.username}] "
                )

                if not user_input:
                    continue

                if user_input == '/quit':
                    break
                elif user_input == '/ping':
                    await self.send_message('ping')
                elif user_input == '/stats':
                    await self.send_message('stats')
                else:
                    # Send chat message
                    await self.send_message('chat', message=user_input)

        except KeyboardInterrupt:
            print("\n[CLIENT] Interrupted")
        finally:
            receive_task.cancel()
            if self.websocket:
                await self.websocket.close()
                print("[CLIENT] Disconnected")


async def run_server():
    """Run the WebSocket server."""
    server = WebSocketServer(host='localhost', port=8765)
    await server.start()


async def run_client(username=None):
    """Run the WebSocket client."""
    client = WebSocketClient(uri='ws://localhost:8765', username=username)

    if await client.connect():
        await client.interactive_mode()


def demonstrate_websocket():
    """Print WebSocket architecture information."""
    print("""
WebSocket Communication Architecture
=====================================

1. Connection Establishment (HTTP Upgrade):

   Client                                Server
     │                                     │
     │──── HTTP GET (Upgrade) ───────────→│
     │     Upgrade: websocket              │
     │     Connection: Upgrade             │
     │     Sec-WebSocket-Key: ...          │
     │                                     │
     │←─── HTTP 101 Switching Protocols ──│
     │     Upgrade: websocket              │
     │     Connection: Upgrade             │
     │     Sec-WebSocket-Accept: ...       │
     │                                     │
     │    [WebSocket Connection Open]      │


2. Bi-directional Communication:

   Client                                Server
     │                                     │
     │──── Message ──────────────────────→│
     │                                     │
     │←─── Message ───────────────────────│
     │                                     │
     │←─── Message ───────────────────────│
     │                                     │
     │──── Message ──────────────────────→│
     │                                     │
   (Both can send/receive simultaneously)


3. Multi-Client Architecture:

   ┌──────────┐
   │ Client 1 │──┐
   └──────────┘  │
                 │     ┌──────────────┐
   ┌──────────┐ │     │              │
   │ Client 2 │─┼────→│  WebSocket   │
   └──────────┘ │     │    Server    │
                │     │              │
   ┌──────────┐ │     └──────────────┘
   │ Client 3 │──┘
   └──────────┘

   Server broadcasts messages to all connected clients


4. Use Cases:

   ✓ Real-time Chat Applications
     - Instant messaging
     - Group chat rooms
     - Customer support chat

   ✓ Live Notifications
     - Social media updates
     - Alert systems
     - Activity feeds

   ✓ Collaborative Tools
     - Google Docs-style editing
     - Whiteboard applications
     - Code editors (VS Code Live Share)

   ✓ Gaming
     - Multiplayer games
     - Live scoreboards
     - Game state synchronization

   ✓ Financial Applications
     - Stock tickers
     - Trading platforms
     - Cryptocurrency exchanges

   ✓ IoT Dashboards
     - Sensor data visualization
     - Device control
     - Real-time monitoring


5. Performance Characteristics:

   Latency:          1-10ms (very low)
   Throughput:       High (no HTTP overhead per message)
   Connection:       Persistent (stays open)
   Overhead:         Low (2-14 bytes per frame)
   Scalability:      Challenging (connection state)


6. WebSocket vs HTTP Polling:

   HTTP Polling:
   - Client repeatedly requests updates
   - High latency (poll interval)
   - Wasted requests (no new data)
   - Higher server load

   WebSocket:
   - Server pushes updates immediately
   - Low latency (instant)
   - Efficient (only send when needed)
   - Lower overhead


7. Best Practices:

   ✓ Implement heartbeat/ping-pong for keep-alive
   ✓ Handle reconnection gracefully
   ✓ Use message queues for reliability
   ✓ Implement authentication
   ✓ Validate all messages
   ✓ Set connection limits
   ✓ Use SSL/TLS (wss://)
   ✓ Implement backpressure handling
   ✓ Monitor connection health
   ✓ Log all events


8. Scaling Considerations:

   Single Server Limits:
   - ~65k connections per IP (OS limit)
   - Memory per connection (~10KB)
   - CPU for message processing

   Scaling Strategies:
   - Load balancing with sticky sessions
   - Redis Pub/Sub for multi-server
   - Message brokers (Kafka, RabbitMQ)
   - Horizontal scaling with service mesh
    """)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python websocket_demo.py server              - Run server")
        print("  python websocket_demo.py client [username]   - Run client")
        print("  python websocket_demo.py demo                - Show architecture info")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'server':
        asyncio.run(run_server())
    elif mode == 'client':
        username = sys.argv[2] if len(sys.argv) > 2 else None
        asyncio.run(run_client(username))
    elif mode == 'demo':
        demonstrate_websocket()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
