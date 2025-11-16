"""
gRPC Client Implementation
===========================

Demonstrates how to call all four types of gRPC services:
1. Unary RPC
2. Server Streaming
3. Client Streaming
4. Bidirectional Streaming

Run:
    python client.py
"""

import grpc
import time
from datetime import datetime
import threading
import sys

# Import generated protobuf code
try:
    import user_service_pb2
    import user_service_pb2_grpc
except ImportError:
    print("""
    Error: Generated protobuf files not found.

    Please generate them first:
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user_service.proto
    """)
    exit(1)


class UserServiceClient:
    """
    Client for UserService.
    Demonstrates all gRPC communication patterns.
    """

    def __init__(self, host='localhost', port='50051'):
        # Create a channel to the server
        self.channel = grpc.insecure_channel(f'{host}:{port}')

        # Create a stub (client)
        self.stub = user_service_pb2_grpc.UserServiceStub(self.channel)

        print(f"[CLIENT] Connected to {host}:{port}")

    def get_user(self, user_id):
        """
        Unary RPC: Get a single user
        """
        print(f"\n=== Unary RPC: GetUser({user_id}) ===")

        # Create request
        request = user_service_pb2.GetUserRequest(id=user_id)

        try:
            # Make the call
            response = self.stub.GetUser(request)

            print(f"Response received:")
            print(f"  ID: {response.id}")
            print(f"  Name: {response.name}")
            print(f"  Email: {response.email}")
            print(f"  Age: {response.age}")

            return response

        except grpc.RpcError as e:
            print(f"Error: {e.code()}: {e.details()}")
            return None

    def create_user(self, name, email, age):
        """
        Unary RPC: Create a new user
        """
        print(f"\n=== Unary RPC: CreateUser ===")

        # Create request
        request = user_service_pb2.CreateUserRequest(
            name=name,
            email=email,
            age=age
        )

        try:
            # Make the call
            response = self.stub.CreateUser(request)

            print(f"User created:")
            print(f"  ID: {response.id}")
            print(f"  Name: {response.name}")
            print(f"  Email: {response.email}")

            return response

        except grpc.RpcError as e:
            print(f"Error: {e.code()}: {e.details()}")
            return None

    def list_users(self, page=1, page_size=10, filter_name=''):
        """
        Server Streaming RPC: Receive stream of users
        """
        print(f"\n=== Server Streaming RPC: ListUsers ===")

        # Create request
        request = user_service_pb2.ListUsersRequest(
            page=page,
            page_size=page_size,
            filter=filter_name
        )

        try:
            # Receive stream of responses
            print("Receiving user stream...")

            for response in self.stub.ListUsers(request):
                print(f"  - {response.name} ({response.email}), Age: {response.age}")

                # Process each user as it arrives
                # This demonstrates streaming - we get results immediately,
                # not waiting for all users

        except grpc.RpcError as e:
            print(f"Error: {e.code()}: {e.details()}")

    def batch_create_users(self, users_data):
        """
        Client Streaming RPC: Send stream of users to create
        """
        print(f"\n=== Client Streaming RPC: BatchCreateUsers ===")

        def generate_requests():
            """Generator that yields user creation requests"""
            for user_data in users_data:
                request = user_service_pb2.CreateUserRequest(
                    name=user_data['name'],
                    email=user_data['email'],
                    age=user_data['age']
                )
                print(f"Sending: {user_data['name']}")
                yield request
                time.sleep(0.3)  # Simulate some delay

        try:
            # Send stream of requests, get single response
            response = self.stub.BatchCreateUsers(generate_requests())

            print(f"\nBatch creation completed:")
            print(f"  Created {response.created_count} users")

            for user in response.users:
                print(f"  - {user.name} (ID: {user.id})")

            return response

        except grpc.RpcError as e:
            print(f"Error: {e.code()}: {e.details()}")
            return None

    def chat(self, username):
        """
        Bidirectional Streaming RPC: Real-time chat
        """
        print(f"\n=== Bidirectional Streaming RPC: Chat ===")
        print(f"Joined chat as {username}")
        print("Type messages (or 'quit' to exit):")

        def generate_messages():
            """Generator that yields chat messages from user input"""
            while True:
                try:
                    # Get input from user
                    message_text = input()

                    if message_text.lower() == 'quit':
                        break

                    # Create chat message
                    message = user_service_pb2.ChatMessage(
                        username=username,
                        message=message_text,
                        timestamp=datetime.now().isoformat()
                    )

                    yield message

                except EOFError:
                    break

        try:
            # Start bidirectional stream
            responses = self.stub.Chat(generate_messages())

            # Receive messages from server
            for response in responses:
                print(f"[{response.timestamp[:19]}] {response.username}: {response.message}")

        except grpc.RpcError as e:
            print(f"Error: {e.code()}: {e.details()}")

    def close(self):
        """Close the connection."""
        self.channel.close()
        print("\n[CLIENT] Connection closed")


def run_demo():
    """Run a comprehensive demo of all gRPC features."""
    client = UserServiceClient()

    try:
        # 1. Unary RPC: Get User
        print("\n" + "="*60)
        print("1. Testing Unary RPC")
        print("="*60)
        client.get_user(1)
        client.get_user(2)

        # 2. Unary RPC: Create User
        print("\n" + "="*60)
        print("2. Testing Unary RPC - Create User")
        print("="*60)
        client.create_user("David", "david@example.com", 28)
        client.create_user("Eve", "eve@example.com", 32)

        # 3. Server Streaming: List Users
        print("\n" + "="*60)
        print("3. Testing Server Streaming RPC")
        print("="*60)
        client.list_users(page=1, page_size=10)

        # 4. Client Streaming: Batch Create
        print("\n" + "="*60)
        print("4. Testing Client Streaming RPC")
        print("="*60)
        new_users = [
            {"name": "Frank", "email": "frank@example.com", "age": 29},
            {"name": "Grace", "email": "grace@example.com", "age": 27},
            {"name": "Henry", "email": "henry@example.com", "age": 31},
        ]
        client.batch_create_users(new_users)

        # 5. Bidirectional Streaming: Chat
        print("\n" + "="*60)
        print("5. Testing Bidirectional Streaming RPC")
        print("="*60)
        print("Starting chat mode...")
        print("(This is interactive - type messages or skip with Ctrl+C)")
        print()

        try:
            client.chat("DemoUser")
        except KeyboardInterrupt:
            print("\nSkipping chat demo...")

    except Exception as e:
        print(f"Error in demo: {e}")
    finally:
        client.close()


def interactive_mode():
    """Run client in interactive mode."""
    client = UserServiceClient()

    print("""
╔════════════════════════════════════════════════════╗
║          gRPC Client Interactive Mode              ║
╚════════════════════════════════════════════════════╝

Commands:
  1 <id>                  - Get user by ID
  2 <name> <email> <age>  - Create user
  3 [filter]              - List users
  4                       - Batch create sample users
  5 <username>            - Join chat
  demo                    - Run full demo
  quit                    - Exit

    """)

    try:
        while True:
            try:
                command = input("\n> ").strip()

                if not command:
                    continue

                if command == 'quit':
                    break

                if command == 'demo':
                    run_demo()
                    client = UserServiceClient()  # Reconnect
                    continue

                parts = command.split()
                cmd = parts[0]

                if cmd == '1' and len(parts) >= 2:
                    user_id = int(parts[1])
                    client.get_user(user_id)

                elif cmd == '2' and len(parts) >= 4:
                    name = parts[1]
                    email = parts[2]
                    age = int(parts[3])
                    client.create_user(name, email, age)

                elif cmd == '3':
                    filter_name = parts[1] if len(parts) > 1 else ''
                    client.list_users(filter_name=filter_name)

                elif cmd == '4':
                    users = [
                        {"name": "User1", "email": "user1@example.com", "age": 25},
                        {"name": "User2", "email": "user2@example.com", "age": 30},
                    ]
                    client.batch_create_users(users)

                elif cmd == '5' and len(parts) >= 2:
                    username = parts[1]
                    client.chat(username)

                else:
                    print("Invalid command. Type 'quit' to exit.")

            except ValueError as e:
                print(f"Invalid input: {e}")
            except Exception as e:
                print(f"Error: {e}")

    except KeyboardInterrupt:
        print("\n")
    finally:
        client.close()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'demo':
        run_demo()
    else:
        interactive_mode()
