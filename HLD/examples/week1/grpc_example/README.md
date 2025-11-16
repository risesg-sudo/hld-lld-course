# gRPC Example

This example demonstrates gRPC with Protocol Buffers, showing all four types of gRPC communication patterns.

## Files

- `user_service.proto` - Protocol Buffer definition
- `server.py` - gRPC server implementation
- `client.py` - gRPC client implementation

## Setup

### 1. Install Dependencies

```bash
pip install grpcio grpcio-tools
```

### 2. Generate Python Code from Proto File

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user_service.proto
```

This generates:
- `user_service_pb2.py` - Message classes
- `user_service_pb2_grpc.py` - Service classes

### 3. Run the Server

```bash
python server.py
```

### 4. Run the Client (in another terminal)

```bash
# Interactive mode
python client.py

# Demo mode (automated demo)
python client.py demo
```

## gRPC Communication Patterns

### 1. Unary RPC (Request-Response)

**Server:**
```python
def GetUser(self, request, context):
    user = self.users[request.id]
    return UserResponse(
        id=user['id'],
        name=user['name'],
        email=user['email']
    )
```

**Client:**
```python
request = GetUserRequest(id=1)
response = stub.GetUser(request)
print(response.name)
```

**Flow:**
```
Client ──request──> Server
Client <─response── Server
```

### 2. Server Streaming RPC

**Server:**
```python
def ListUsers(self, request, context):
    for user in self.users.values():
        yield UserResponse(
            id=user['id'],
            name=user['name']
        )
```

**Client:**
```python
request = ListUsersRequest()
for response in stub.ListUsers(request):
    print(response.name)
```

**Flow:**
```
Client ──request──────> Server
Client <─response1───── Server
Client <─response2───── Server
Client <─response3───── Server
```

### 3. Client Streaming RPC

**Server:**
```python
def BatchCreateUsers(self, request_iterator, context):
    users = []
    for request in request_iterator:
        user = create_user(request)
        users.append(user)
    return BatchCreateResponse(users=users)
```

**Client:**
```python
def generate_requests():
    for user_data in users:
        yield CreateUserRequest(
            name=user_data['name'],
            email=user_data['email']
        )

response = stub.BatchCreateUsers(generate_requests())
```

**Flow:**
```
Client ──request1──> Server
Client ──request2──> Server
Client ──request3──> Server
Client <─response─── Server
```

### 4. Bidirectional Streaming RPC

**Server:**
```python
def Chat(self, request_iterator, context):
    for message in request_iterator:
        # Broadcast to others
        yield ChatMessage(
            username=message.username,
            message=message.message
        )
```

**Client:**
```python
def generate_messages():
    while True:
        message = input()
        yield ChatMessage(message=message)

for response in stub.Chat(generate_messages()):
    print(response.message)
```

**Flow:**
```
Client <──────────> Server
(simultaneous bidirectional streaming)
```

## Protocol Buffers

### Message Definition

```protobuf
message UserResponse {
  int32 id = 1;
  string name = 2;
  string email = 3;
  int32 age = 4;
}
```

### Service Definition

```protobuf
service UserService {
  rpc GetUser(GetUserRequest) returns (UserResponse) {}
  rpc ListUsers(ListUsersRequest) returns (stream UserResponse) {}
}
```

## Performance Comparison

### gRPC vs REST (JSON)

**Message Size:**
- JSON: ~100 bytes
- Protobuf: ~30 bytes
- **Savings: 70%**

**Serialization Speed:**
- JSON: ~100ms
- Protobuf: ~20ms
- **Speedup: 5x**

**HTTP/2 Features:**
- Multiplexing: Multiple requests on single connection
- Header compression: Reduces overhead
- Server push: Proactive data sending
- Binary framing: More efficient than text

## Use Cases

### When to Use gRPC

✅ **Microservices Communication**
- High performance internal APIs
- Service mesh architectures
- Multiple language environments

✅ **Real-time Streaming**
- Live data feeds
- Bidirectional communication
- IoT data collection

✅ **Mobile Applications**
- Bandwidth-constrained environments
- Battery efficiency important
- Multiple simultaneous requests

✅ **Polyglot Systems**
- Need code generation
- Strong typing required
- Multiple programming languages

### When NOT to Use gRPC

❌ **Browser Clients**
- Limited browser support
- gRPC-Web needed (adds complexity)
- REST is simpler

❌ **Public APIs**
- Developers expect REST
- Human-readable formats preferred
- Wide compatibility needed

❌ **Simple CRUD Applications**
- REST is sufficient
- Overhead not justified
- Team unfamiliar with gRPC

## Best Practices

1. **Define Clear Service Boundaries**
   - One service per .proto file
   - Group related operations

2. **Use Semantic Versioning**
   - Add fields, don't remove
   - Use field numbers carefully
   - Maintain backward compatibility

3. **Implement Proper Error Handling**
   - Use appropriate status codes
   - Provide detailed error messages
   - Handle network failures

4. **Add Interceptors for Cross-Cutting Concerns**
   - Authentication
   - Logging
   - Monitoring
   - Rate limiting

5. **Configure Timeouts and Retries**
   - Set reasonable deadlines
   - Implement exponential backoff
   - Handle transient failures

6. **Use Connection Pooling**
   - Reuse channels
   - Configure keep-alive
   - Monitor connection health

## Debugging Tips

### View Generated Code
```bash
ls -la *_pb2*.py
```

### Enable gRPC Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use grpcurl (like curl for gRPC)
```bash
# Install
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# List services
grpcurl -plaintext localhost:50051 list

# Call method
grpcurl -plaintext -d '{"id": 1}' localhost:50051 userservice.UserService/GetUser
```

## Further Reading

- [gRPC Documentation](https://grpc.io/docs/)
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers)
- [HTTP/2 Specification](https://http2.github.io/)
- [gRPC Best Practices](https://grpc.io/docs/guides/performance/)
