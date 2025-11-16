"""
Client-Server Architecture Demo
================================

This demonstrates a basic TCP client-server implementation.
Shows the fundamental request-response pattern.

Usage:
    # Terminal 1 (Server)
    python client_server_demo.py server

    # Terminal 2 (Client)
    python client_server_demo.py client
"""

import socket
import sys
import threading
import json
from datetime import datetime


class SimpleServer:
    """
    A simple TCP server that handles multiple clients.
    Demonstrates basic server architecture patterns.
    """

    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def start(self):
        """Start the server and listen for connections."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse of address
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            print(f"[SERVER] Started on {self.host}:{self.port}")
            print(f"[SERVER] Waiting for connections...")

            while self.running:
                try:
                    # Accept new connection
                    client_socket, client_address = self.server_socket.accept()
                    print(f"[SERVER] New connection from {client_address}")

                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except KeyboardInterrupt:
                    print("\n[SERVER] Shutting down...")
                    self.running = False
                    break

        except Exception as e:
            print(f"[SERVER] Error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        """
        Handle individual client connection.
        Processes requests and sends responses.
        """
        try:
            while True:
                # Receive data from client
                data = client_socket.recv(1024).decode('utf-8')

                if not data:
                    print(f"[SERVER] Client {client_address} disconnected")
                    break

                print(f"[SERVER] Received from {client_address}: {data}")

                # Process request
                response = self.process_request(data, client_address)

                # Send response
                client_socket.send(response.encode('utf-8'))

        except Exception as e:
            print(f"[SERVER] Error handling client {client_address}: {e}")
        finally:
            client_socket.close()

    def process_request(self, request, client_address):
        """
        Process client request and generate response.
        Demonstrates business logic layer.
        """
        try:
            # Parse JSON request
            request_data = json.loads(request)
            action = request_data.get('action', '')

            response_data = {
                'timestamp': datetime.now().isoformat(),
                'client': str(client_address)
            }

            if action == 'echo':
                # Echo back the message
                response_data['status'] = 'success'
                response_data['message'] = request_data.get('message', '')

            elif action == 'time':
                # Return server time
                response_data['status'] = 'success'
                response_data['server_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            elif action == 'stats':
                # Return server statistics
                response_data['status'] = 'success'
                response_data['stats'] = {
                    'uptime': '100s',  # Simplified
                    'active_connections': threading.active_count() - 1
                }

            else:
                response_data['status'] = 'error'
                response_data['message'] = f"Unknown action: {action}"

            return json.dumps(response_data)

        except json.JSONDecodeError:
            error_response = {
                'status': 'error',
                'message': 'Invalid JSON format'
            }
            return json.dumps(error_response)


class SimpleClient:
    """
    A simple TCP client that connects to the server.
    Demonstrates basic client architecture patterns.
    """

    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """Connect to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"[CLIENT] Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[CLIENT] Connection failed: {e}")
            return False

    def send_request(self, action, **kwargs):
        """
        Send a request to the server and receive response.
        """
        if not self.socket:
            print("[CLIENT] Not connected to server")
            return None

        try:
            # Prepare request
            request_data = {
                'action': action,
                **kwargs
            }
            request_json = json.dumps(request_data)

            print(f"[CLIENT] Sending: {request_json}")

            # Send request
            self.socket.send(request_json.encode('utf-8'))

            # Receive response
            response = self.socket.recv(1024).decode('utf-8')
            response_data = json.loads(response)

            print(f"[CLIENT] Received: {json.dumps(response_data, indent=2)}")
            return response_data

        except Exception as e:
            print(f"[CLIENT] Error: {e}")
            return None

    def close(self):
        """Close connection to server."""
        if self.socket:
            self.socket.close()
            print("[CLIENT] Connection closed")


def run_server():
    """Run the server."""
    server = SimpleServer(host='127.0.0.1', port=8888)
    server.start()


def run_client():
    """Run the client with interactive commands."""
    client = SimpleClient(host='127.0.0.1', port=8888)

    if not client.connect():
        return

    print("\n[CLIENT] Available commands:")
    print("  1. echo <message>  - Echo a message")
    print("  2. time           - Get server time")
    print("  3. stats          - Get server statistics")
    print("  4. quit           - Exit")
    print()

    try:
        while True:
            command = input("[CLIENT] Enter command: ").strip()

            if not command:
                continue

            if command == 'quit':
                break

            parts = command.split(' ', 1)
            action = parts[0]

            if action == 'echo':
                message = parts[1] if len(parts) > 1 else "Hello, Server!"
                client.send_request('echo', message=message)

            elif action == 'time':
                client.send_request('time')

            elif action == 'stats':
                client.send_request('stats')

            else:
                print(f"[CLIENT] Unknown command: {action}")

    except KeyboardInterrupt:
        print("\n[CLIENT] Interrupted")
    finally:
        client.close()


def demonstrate_architecture():
    """
    Demonstrate client-server architecture concepts.
    Shows how multiple clients can connect to one server.
    """
    print("""
    Client-Server Architecture Demonstration
    =========================================

    Architecture Overview:

    ┌─────────────┐                    ┌─────────────┐
    │  Client 1   │ ──────────────────→│             │
    └─────────────┘                    │             │
                                        │   Server    │
    ┌─────────────┐                    │  (Port 8888)│
    │  Client 2   │ ──────────────────→│             │
    └─────────────┘                    │             │
                                        └─────────────┘
    ┌─────────────┐                           ↓
    │  Client 3   │ ──────────────────→ Thread per Client
    └─────────────┘

    Key Concepts:
    1. Server listens on a specific port (8888)
    2. Multiple clients can connect simultaneously
    3. Each client is handled in a separate thread
    4. Request-Response pattern using JSON
    5. TCP ensures reliable delivery

    Performance Considerations:
    - Thread per connection (suitable for < 1000 connections)
    - For high concurrency, use async I/O or thread pools
    - Connection pooling can improve performance
    - Consider load balancing for multiple server instances

    Best Practices:
    1. Use proper error handling
    2. Implement timeouts
    3. Validate all inputs
    4. Use structured data (JSON, Protobuf)
    5. Log all operations
    6. Implement graceful shutdown
    7. Handle connection failures
    8. Use connection pooling for clients

    Security Considerations:
    1. Use TLS/SSL for encryption (not shown here)
    2. Authenticate clients
    3. Rate limiting
    4. Input validation
    5. DDoS protection
    """)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python client_server_demo.py server    - Run server")
        print("  python client_server_demo.py client    - Run client")
        print("  python client_server_demo.py demo      - Show architecture info")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'server':
        run_server()
    elif mode == 'client':
        run_client()
    elif mode == 'demo':
        demonstrate_architecture()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
