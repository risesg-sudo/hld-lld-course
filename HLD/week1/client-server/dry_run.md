# Dry Run: TCP Client-Server Communication

This dry run traces the execution of a TCP client-server interaction, showing exactly what happens at each step.

## Scenario

A client connects to a server and sends an "echo" request with the message "Hello".

## Initial State

**Server**:
```
State: Not started
Socket: None
Listening: No
Connected Clients: []
```

**Client**:
```
State: Not started
Socket: None
Connected: No
```

## Step 1: Server Starts

**Action**: `server.start()`

**Server Process**:
```python
1. Create socket: socket.socket(AF_INET, SOCK_STREAM)
2. Set socket options: SO_REUSEADDR = 1
3. Bind to address: bind(('127.0.0.1', 8888))
4. Listen for connections: listen(5)
```

**Server State After**:
```
State: Running
Socket: <socket object at 0x...>
Listening: Yes (Port 8888)
Connected Clients: []
Server Output: "[SERVER] Started on 127.0.0.1:8888"
              "[SERVER] Waiting for connections..."
```

**Explanation**: The server creates a TCP socket and binds it to port 8888. The `listen(5)` call sets the backlog queue size to 5, meaning up to 5 connection requests can wait while the server is busy.

## Step 2: Client Initiates Connection

**Action**: `client.connect()`

**Client Process**:
```python
1. Create socket: socket.socket(AF_INET, SOCK_STREAM)
2. Connect to server: connect(('127.0.0.1', 8888))
```

**TCP Three-Way Handshake** (happens automatically in OS):
```
Client                           Server
  |                                 |
  |--- SYN (seq=100) -------------->|
  |                                 |
  |<-- SYN-ACK (seq=300, ack=101) --|
  |                                 |
  |--- ACK (ack=301) -------------->|
  |                                 |
  [Connection Established]
```

**Client State After**:
```
State: Connected
Socket: <socket object at 0x...>
Connected: Yes
Client Output: "[CLIENT] Connected to 127.0.0.1:8888"
```

**Server State After**:
```
State: Running
Socket: <socket object at 0x...>
Listening: Yes
Connected Clients: [('127.0.0.1', 54321)]
Active Threads: 2 (main + client handler)
Server Output: "[SERVER] New connection from ('127.0.0.1', 54321)"
```

**Explanation**: The client initiates a TCP connection. The OS handles the three-way handshake automatically. Once established, the server's `accept()` call returns a new socket for this client and spawns a thread to handle it.

## Step 3: Client Sends Echo Request

**Action**: `client.send_request('echo', message='Hello')`

**Client Process**:
```python
Step 1: Build request dictionary
request_data = {
    'action': 'echo',
    'message': 'Hello'
}

Step 2: Convert to JSON string
request_json = '{"action": "echo", "message": "Hello"}'

Step 3: Encode to bytes
request_bytes = b'{"action": "echo", "message": "Hello"}'

Step 4: Send over socket
socket.send(request_bytes)
```

**Network Transmission**:
```
Client Socket Buffer: [request_bytes] --> TCP Packet --> Server Socket Buffer
```

**Client Output**:
```
"[CLIENT] Sending: {"action": "echo", "message": "Hello"}"
```

**Explanation**: JSON is used as a structured data format. The string is encoded to bytes (UTF-8) before transmission over the network.

## Step 4: Server Receives Request

**Server Process** (in client handler thread):
```python
Step 1: Receive data
data = client_socket.recv(1024)  # Max 1024 bytes
data = b'{"action": "echo", "message": "Hello"}'

Step 2: Decode bytes to string
data_str = data.decode('utf-8')
data_str = '{"action": "echo", "message": "Hello"}'

Step 3: Parse JSON
request_data = json.loads(data_str)
request_data = {'action': 'echo', 'message': 'Hello'}
```

**Server State**:
```
Received Request: {'action': 'echo', 'message': 'Hello'}
Client Address: ('127.0.0.1', 54321)
```

**Server Output**:
```
"[SERVER] Received from ('127.0.0.1', 54321): {"action": "echo", "message": "Hello"}"
```

**Explanation**: The server reads bytes from the socket buffer, decodes them to a string, and parses the JSON to extract the action and message.

## Step 5: Server Processes Request

**Server Process**:
```python
Step 1: Extract action
action = request_data.get('action', '')  # 'echo'

Step 2: Build response
response_data = {
    'timestamp': '2024-11-17T10:30:45.123456',
    'client': "('127.0.0.1', 54321)"
}

Step 3: Handle 'echo' action
response_data['status'] = 'success'
response_data['message'] = 'Hello'

Step 4: Final response
response_data = {
    'timestamp': '2024-11-17T10:30:45.123456',
    'client': "('127.0.0.1', 54321)",
    'status': 'success',
    'message': 'Hello'
}

Step 5: Convert to JSON string
response_json = '{"timestamp": "...", "client": "...", "status": "success", "message": "Hello"}'
```

**Explanation**: The server processes the request based on the action. For 'echo', it simply includes the received message in the response along with metadata.

## Step 6: Server Sends Response

**Server Process**:
```python
Step 1: Encode response to bytes
response_bytes = response_json.encode('utf-8')

Step 2: Send over socket
client_socket.send(response_bytes)
```

**Network Transmission**:
```
Server Socket Buffer: [response_bytes] --> TCP Packet --> Client Socket Buffer
```

**Explanation**: The response follows the same encoding pattern: Python dict -> JSON string -> bytes -> network.

## Step 7: Client Receives Response

**Client Process**:
```python
Step 1: Receive data
response = socket.recv(1024)
response = b'{"timestamp": "...", "client": "...", "status": "success", "message": "Hello"}'

Step 2: Decode to string
response_str = response.decode('utf-8')

Step 3: Parse JSON
response_data = json.loads(response_str)
response_data = {
    'timestamp': '2024-11-17T10:30:45.123456',
    'client': "('127.0.0.1', 54321)",
    'status': 'success',
    'message': 'Hello'
}
```

**Client Output**:
```
"[CLIENT] Received: {
  "timestamp": "2024-11-17T10:30:45.123456",
  "client": "('127.0.0.1', 54321)",
  "status": "success",
  "message": "Hello"
}"
```

**Client State**:
```
Last Response: {'status': 'success', 'message': 'Hello'}
Connected: Yes
```

**Explanation**: The client receives the bytes, decodes them, and parses the JSON to get a Python dictionary.

## Step 8: Client Closes Connection

**Action**: `client.close()`

**Client Process**:
```python
socket.close()
```

**TCP Connection Termination** (Four-way handshake):
```
Client                           Server
  |                                 |
  |--- FIN (seq=150) -------------->|
  |                                 |
  |<-- ACK (ack=151) ---------------|
  |                                 |
  |<-- FIN (seq=450) ---------------|
  |                                 |
  |--- ACK (ack=451) -------------->|
  |                                 |
  [Connection Closed]
```

**Client Output**:
```
"[CLIENT] Connection closed"
```

**Server Output**:
```
"[SERVER] Client ('127.0.0.1', 54321) disconnected"
```

**Final State**:
```
Client Socket: Closed
Server: Still running, waiting for new connections
Active Threads: 1 (main thread only)
```

**Explanation**: The client initiates connection closure. TCP performs a four-way handshake to ensure both sides cleanly close the connection. The server's client handler thread exits, but the main server thread continues running.

## Key Observations

1. **Encoding/Decoding**: Data is encoded to bytes before transmission and decoded after reception
2. **JSON Format**: Structured data format enables complex request/response patterns
3. **Threading**: Server handles each client in a separate thread for concurrency
4. **Reliable Delivery**: TCP guarantees data arrives in order and without corruption
5. **Stateful Connection**: The socket maintains state for the duration of the connection

## Performance Notes

**Latency Breakdown** for this request:
```
Client -> Network: ~0.1ms (local machine)
Network -> Server: ~0.1ms
Server Processing: ~0.5ms
Server -> Network: ~0.1ms
Network -> Client: ~0.1ms
Total: ~0.9ms
```

**Throughput**: Limited by:
- Network bandwidth
- Socket buffer sizes (1024 bytes in this example)
- Processing speed on both ends
- Number of concurrent connections

This dry run demonstrates the fundamental request-response pattern that underlies most client-server applications.
