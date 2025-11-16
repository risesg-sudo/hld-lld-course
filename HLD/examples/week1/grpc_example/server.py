"""
gRPC Server Implementation
===========================

Demonstrates all four types of gRPC communication:
1. Unary RPC (Request-Response)
2. Server Streaming
3. Client Streaming
4. Bidirectional Streaming

Requirements:
    pip install grpcio grpcio-tools

Generate Python code from proto file:
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user_service.proto

Run:
    python server.py
"""

import grpc
from concurrent import futures
import time
from datetime import datetime
import threading

# Import generated protobuf code
# Note: You need to generate these files first using the command above
try:
    import user_service_pb2
    import user_service_pb2_grpc
except ImportError:
    print("""
    Error: Generated protobuf files not found.

    Please generate them first:
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user_service.proto

    Or install grpcio-tools:
    pip install grpcio-tools
    """)
    exit(1)


class UserServiceServicer(user_service_pb2_grpc.UserServiceServicer):
    """
    Implementation of UserService.
    Demonstrates all gRPC communication patterns.
    """

    def __init__(self):
        # In-memory user database
        self.users = {
            1: {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
            2: {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25},
            3: {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 35},
        }
        self.next_id = 4
        self.lock = threading.Lock()

        # Chat room for bidirectional streaming
        self.chat_messages = []
        self.chat_lock = threading.Lock()

    def GetUser(self, request, context):
        """
        Unary RPC: Simple request-response
        Client sends one request, server sends one response
        """
        print(f"[GetUser] Request for user ID: {request.id}")

        user_id = request.id

        with self.lock:
            if user_id in self.users:
                user = self.users[user_id]

                response = user_service_pb2.UserResponse(
                    id=user['id'],
                    name=user['name'],
                    email=user['email'],
                    age=user['age'],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )

                print(f"[GetUser] Returning user: {user['name']}")
                return response
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'User with id {user_id} not found')
                print(f"[GetUser] User {user_id} not found")
                return user_service_pb2.UserResponse()

    def CreateUser(self, request, context):
        """
        Unary RPC: Create a new user
        """
        print(f"[CreateUser] Creating user: {request.name}")

        with self.lock:
            user = {
                "id": self.next_id,
                "name": request.name,
                "email": request.email,
                "age": request.age
            }

            self.users[self.next_id] = user
            user_id = self.next_id
            self.next_id += 1

        response = user_service_pb2.UserResponse(
            id=user_id,
            name=user['name'],
            email=user['email'],
            age=user['age'],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        print(f"[CreateUser] Created user ID: {user_id}")
        return response

    def ListUsers(self, request, context):
        """
        Server Streaming RPC: Server sends multiple responses
        Client sends one request, server streams multiple responses
        """
        print(f"[ListUsers] Streaming users (page: {request.page}, size: {request.page_size})")

        with self.lock:
            users_list = list(self.users.values())

        # Apply filtering if provided
        if request.filter:
            filter_lower = request.filter.lower()
            users_list = [u for u in users_list if filter_lower in u['name'].lower()]

        # Pagination
        page = request.page if request.page > 0 else 1
        page_size = request.page_size if request.page_size > 0 else 10

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_users = users_list[start_idx:end_idx]

        # Stream users one by one
        for user in paginated_users:
            response = user_service_pb2.UserResponse(
                id=user['id'],
                name=user['name'],
                email=user['email'],
                age=user['age'],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )

            print(f"[ListUsers] Streaming user: {user['name']}")
            yield response

            # Simulate some processing time
            time.sleep(0.5)

    def BatchCreateUsers(self, request_iterator, context):
        """
        Client Streaming RPC: Client sends multiple requests
        Client streams multiple requests, server sends one response
        """
        print("[BatchCreateUsers] Receiving batch of users...")

        created_users = []
        count = 0

        # Receive all users from client stream
        for create_request in request_iterator:
            print(f"[BatchCreateUsers] Received: {create_request.name}")

            with self.lock:
                user = {
                    "id": self.next_id,
                    "name": create_request.name,
                    "email": create_request.email,
                    "age": create_request.age
                }

                self.users[self.next_id] = user

                user_response = user_service_pb2.UserResponse(
                    id=self.next_id,
                    name=user['name'],
                    email=user['email'],
                    age=user['age'],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )

                created_users.append(user_response)
                self.next_id += 1
                count += 1

        # Send single response with all created users
        response = user_service_pb2.BatchCreateResponse(
            created_count=count,
            users=created_users
        )

        print(f"[BatchCreateUsers] Created {count} users")
        return response

    def Chat(self, request_iterator, context):
        """
        Bidirectional Streaming RPC: Both send multiple messages
        Client and server can send messages simultaneously
        """
        print("[Chat] Client joined chat")

        # Thread to receive messages from client
        def receive_messages():
            try:
                for message in request_iterator:
                    print(f"[Chat] Received: {message.username}: {message.message}")

                    # Add to chat history
                    with self.chat_lock:
                        self.chat_messages.append({
                            "username": message.username,
                            "message": message.message,
                            "timestamp": datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"[Chat] Error receiving messages: {e}")

        # Start receiving in background
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        # Send chat history and new messages
        last_sent = 0

        try:
            while context.is_active():
                with self.chat_lock:
                    # Send any new messages
                    while last_sent < len(self.chat_messages):
                        msg = self.chat_messages[last_sent]

                        response = user_service_pb2.ChatMessage(
                            username=msg['username'],
                            message=msg['message'],
                            timestamp=msg['timestamp']
                        )

                        yield response
                        last_sent += 1

                time.sleep(0.1)

        except Exception as e:
            print(f"[Chat] Client disconnected: {e}")


def serve():
    """Start the gRPC server."""
    # Create server with thread pool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add our service to the server
    user_service_pb2_grpc.add_UserServiceServicer_to_server(
        UserServiceServicer(), server
    )

    # Listen on port 50051
    port = '50051'
    server.add_insecure_port(f'[::]:{port}')

    server.start()

    print(f"""
╔════════════════════════════════════════════════════╗
║             gRPC Server Started                    ║
╚════════════════════════════════════════════════════╝

Server listening on port {port}

gRPC Features Demonstrated:
✓ Unary RPC (GetUser, CreateUser)
✓ Server Streaming (ListUsers)
✓ Client Streaming (BatchCreateUsers)
✓ Bidirectional Streaming (Chat)
✓ Protocol Buffers serialization
✓ HTTP/2 transport
✓ Strong typing

Available Services:
- GetUser: Get user by ID
- CreateUser: Create new user
- ListUsers: Stream all users
- BatchCreateUsers: Create multiple users
- Chat: Real-time chat

Run the client:
    python client.py

Press Ctrl+C to stop the server.
    """)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
        server.stop(0)


if __name__ == '__main__':
    serve()
