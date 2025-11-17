"""
TCP Client-Server Implementation

This example demonstrates a basic TCP-based client-server system.
Shows how clients connect to a server, send requests, and receive responses.

Usage:
    # Terminal 1 (Server)
    python tcp_example.py server

    # Terminal 2 (Client)
    python tcp_example.py client

Key Concepts:
- TCP three-way handshake for connection establishment
- Socket programming for network communication
- Multi-threading to handle multiple clients
- Request-response pattern using JSON
"""

import socket
import sys
import threading
import json
from datetime import datetime


class TCPServer:
    """
    A basic TCP server that handles multiple client connections.

    Each client connection is handled in a separate thread, allowing
    the server to process multiple requests concurrently.
    """

    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def start(self):
        """Initialize server socket and start accepting connections."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            print(f"[SERVER] Started on {self.host}:{self.port}")
            print(f"[SERVER] Waiting for connections...")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"[SERVER] New connection from {client_address}")

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
        """Process requests from a connected client."""
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')

                if not data:
                    print(f"[SERVER] Client {client_address} disconnected")
                    break

                print(f"[SERVER] Received from {client_address}: {data}")

                response = self.process_request(data, client_address)
                client_socket.send(response.encode('utf-8'))

        except Exception as e:
            print(f"[SERVER] Error handling client {client_address}: {e}")
        finally:
            client_socket.close()

    def process_request(self, request, client_address):
        """
        Parse request and generate appropriate response.

        Supports the following actions:
        - echo: Returns the message sent by client
        - time: Returns current server time
        - stats: Returns server statistics
        """
        try:
            request_data = json.loads(request)
            action = request_data.get('action', '')

            response_data = {
                'timestamp': datetime.now().isoformat(),
                'client': str(client_address)
            }

            if action == 'echo':
                response_data['status'] = 'success'
                response_data['message'] = request_data.get('message', '')

            elif action == 'time':
                response_data['status'] = 'success'
                response_data['server_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            elif action == 'stats':
                response_data['status'] = 'success'
                response_data['stats'] = {
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


class TCPClient:
    """
    A basic TCP client that connects to the server.

    Sends JSON-formatted requests and processes responses.
    """

    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """Establish connection to the server."""
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

        Args:
            action: The action to perform (echo, time, stats)
            **kwargs: Additional parameters for the request

        Returns:
            Response data as dictionary, or None on error
        """
        if not self.socket:
            print("[CLIENT] Not connected to server")
            return None

        try:
            request_data = {
                'action': action,
                **kwargs
            }
            request_json = json.dumps(request_data)

            print(f"[CLIENT] Sending: {request_json}")

            self.socket.send(request_json.encode('utf-8'))

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
    """Start the TCP server."""
    server = TCPServer(host='127.0.0.1', port=8888)
    server.start()


def run_client():
    """Start interactive client session."""
    client = TCPClient(host='127.0.0.1', port=8888)

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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tcp_example.py server    - Run server")
        print("  python tcp_example.py client    - Run client")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'server':
        run_server()
    elif mode == 'client':
        run_client()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
