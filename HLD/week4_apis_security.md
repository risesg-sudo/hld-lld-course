# Week 4: System Design - APIs & Security

## Table of Contents
1. [Capacity Estimation](#capacity-estimation)
2. [Polling vs Streaming vs Long-polling](#polling-vs-streaming-vs-long-polling)
3. [Rate Limiting](#rate-limiting)
4. [API Design Best Practices](#api-design-best-practices)
5. [Authentication & Authorization](#authentication--authorization)
6. [Security Best Practices](#security-best-practices)
7. [Logging and Monitoring](#logging-and-monitoring)
8. [Fault Tolerance and Circuit Breakers](#fault-tolerance-and-circuit-breakers)

---

## 1. Capacity Estimation

### Why Capacity Estimation Matters
Before designing any system, you need to estimate:
- **QPS (Queries Per Second)**: How many requests will the system handle?
- **Storage**: How much data needs to be stored?
- **Bandwidth**: How much data is transferred over the network?
- **Memory**: How much RAM is needed for caching?

### Key Metrics to Know
```
1 Million = 10^6
1 Billion = 10^9
1 KB = 10^3 bytes
1 MB = 10^6 bytes
1 GB = 10^9 bytes
1 TB = 10^12 bytes
1 PB = 10^15 bytes

Time:
1 day = 86,400 seconds ≈ 10^5 seconds
1 month = 30 days ≈ 2.5 million seconds
1 year = 365 days ≈ 31.5 million seconds
```

### Estimation Framework

#### Step 1: Define Assumptions
- Daily Active Users (DAU)
- Monthly Active Users (MAU)
- User behavior (reads vs writes)
- Data retention period

#### Step 2: Calculate Traffic (QPS)
```
Write QPS = (Total Writes per Day) / (Seconds in a Day)
Read QPS = (Total Reads per Day) / (Seconds in a Day)
Peak QPS = Average QPS × 2 (or 3, depending on traffic pattern)
```

#### Step 3: Calculate Storage
```
Storage per Year = (Writes per Day) × (Size per Write) × 365
Total Storage = Storage per Year × Years
```

#### Step 4: Calculate Bandwidth
```
Write Bandwidth = Write QPS × Size per Write
Read Bandwidth = Read QPS × Size per Read
```

#### Step 5: Calculate Memory (Cache)
```
Cache Size = 20% of Daily Reads × Size per Read (80/20 rule)
```

### Example: Twitter-like System

**Assumptions:**
- 500M DAU
- Each user posts 2 tweets/day on average
- Each user reads 50 tweets/day
- Each tweet is 280 chars + metadata ≈ 500 bytes
- Each image is 500 KB
- 20% of tweets have an image

**Traffic Estimation:**
```
Writes (Tweets):
- Total tweets/day = 500M × 2 = 1B tweets/day
- Write QPS = 1B / 86,400 ≈ 11,600 QPS
- Peak Write QPS = 11,600 × 3 = 34,800 QPS

Reads (Timeline):
- Total reads/day = 500M × 50 = 25B reads/day
- Read QPS = 25B / 86,400 ≈ 289,000 QPS
- Peak Read QPS = 289,000 × 3 = 867,000 QPS
```

**Storage Estimation:**
```
Text Storage:
- Per day = 1B tweets × 500 bytes = 500 GB/day
- Per year = 500 GB × 365 = 182.5 TB/year

Image Storage:
- Images per day = 1B × 0.2 = 200M images
- Per day = 200M × 500 KB = 100 TB/day
- Per year = 100 TB × 365 = 36.5 PB/year

Total Storage (5 years) = (182.5 TB + 36,500 TB) × 5 ≈ 183 PB
```

**Bandwidth Estimation:**
```
Ingress (Write):
- Text: 11,600 QPS × 500 bytes = 5.8 MB/s
- Images: 2,320 QPS × 500 KB = 1.16 GB/s
- Total Ingress ≈ 1.17 GB/s

Egress (Read):
- Text: 289,000 QPS × 500 bytes = 144.5 MB/s
- Images: 57,800 QPS × 500 KB = 28.9 GB/s
- Total Egress ≈ 29 GB/s
```

**Memory/Cache Estimation:**
```
Using 80/20 rule (20% of tweets generate 80% of traffic):
- Daily read data = 25B × 500 bytes = 12.5 TB
- Cache 20% = 2.5 TB
```

### Example: Instagram-like System

See `/HLD/examples/week4/capacity_estimation_guide.md` for detailed calculations.

---

## 2. Polling vs Streaming vs Long-polling

### Short Polling

**How it works:**
- Client sends requests to server at regular intervals
- Server responds immediately (even with empty data)
- Client waits, then sends another request

**Pros:**
- Simple to implement
- Works with any HTTP infrastructure
- Easy to debug

**Cons:**
- Inefficient (many empty responses)
- High latency (delay between polls)
- Wastes bandwidth and server resources

**Use Cases:**
- Non-critical updates
- Systems with predictable update intervals
- Low-frequency data changes

**Example:**
```python
import time
import requests

def short_polling(url, interval=5):
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                process_data(data)
        time.sleep(interval)  # Wait before next poll
```

### Long Polling

**How it works:**
- Client sends request to server
- Server holds request open until new data is available
- Server responds when data arrives (or timeout)
- Client immediately sends new request

**Pros:**
- Lower latency than short polling
- Reduces unnecessary requests
- Works with standard HTTP

**Cons:**
- Server resources tied up holding connections
- Timeout management complexity
- Not true real-time

**Use Cases:**
- Chat applications
- Notification systems
- Live updates with moderate frequency

**Example:**
```python
# Server side (Flask)
from flask import Flask, jsonify
import time

app = Flask(__name__)
message_queue = []

@app.route('/long-poll')
def long_poll():
    timeout = 30  # 30 seconds
    start_time = time.time()

    while time.time() - start_time < timeout:
        if message_queue:
            return jsonify(message_queue.pop(0))
        time.sleep(0.1)

    return jsonify({}), 204  # No content

# Client side
def long_polling_client(url):
    while True:
        response = requests.get(url, timeout=35)
        if response.status_code == 200:
            data = response.json()
            process_data(data)
        # Immediately reconnect
```

### Server-Sent Events (SSE)

**How it works:**
- Client establishes connection
- Server pushes data to client as it becomes available
- Connection stays open
- Unidirectional (server to client only)

**Pros:**
- Efficient for server-to-client updates
- Auto-reconnection built-in
- Simple protocol over HTTP

**Cons:**
- One-way communication only
- Limited by HTTP connection limits
- Browser connection limits (6 per domain)

**Use Cases:**
- Live feeds
- Stock tickers
- Real-time notifications
- Live sports scores

### WebSockets

**How it works:**
- Starts as HTTP, upgrades to WebSocket protocol
- Full-duplex, bidirectional communication
- Persistent connection
- Low overhead after connection established

**Pros:**
- True real-time, bidirectional communication
- Low latency
- Efficient for high-frequency updates

**Cons:**
- More complex to implement
- Requires WebSocket support
- Stateful (harder to scale)
- Firewall/proxy issues

**Use Cases:**
- Real-time gaming
- Collaborative editing
- Live chat
- Trading platforms

### Comparison Table

| Feature | Short Polling | Long Polling | SSE | WebSockets |
|---------|--------------|--------------|-----|------------|
| Latency | High | Medium | Low | Very Low |
| Server Load | High | Medium | Low | Low |
| Real-time | No | Near | Yes | Yes |
| Bidirectional | Yes | Yes | No | Yes |
| Complexity | Low | Medium | Medium | High |
| Browser Support | All | All | Modern | Modern |
| Scalability | Poor | Medium | Good | Good |
| Use HTTP | Yes | Yes | Yes | Upgrade from HTTP |

### When to Use What?

1. **Short Polling**:
   - Updates every few minutes acceptable
   - Simple requirements
   - Legacy systems

2. **Long Polling**:
   - Near real-time updates needed
   - HTTP-only infrastructure
   - Moderate update frequency

3. **SSE**:
   - Server-to-client updates only
   - Live feeds/notifications
   - Auto-reconnection needed

4. **WebSockets**:
   - True bidirectional real-time needed
   - High-frequency updates
   - Gaming, chat, collaboration

See `/HLD/examples/week4/polling_vs_streaming.py` for implementations.

---

## 3. Rate Limiting

### Why Rate Limiting?

Rate limiting protects your system from:
- **Abuse**: Prevent malicious users from overwhelming your service
- **DoS Attacks**: Mitigate denial of service attempts
- **Cost Control**: Limit expensive operations
- **Fair Usage**: Ensure fair resource distribution
- **API Monetization**: Enforce tier-based usage limits

### Common Rate Limiting Algorithms

#### 1. Token Bucket

**How it works:**
- Bucket has maximum capacity of tokens
- Tokens added at fixed rate
- Each request consumes one token
- Request allowed if token available, denied otherwise

**Pros:**
- Allows burst traffic up to bucket size
- Smooth rate limiting
- Memory efficient

**Cons:**
- Can allow bursts that might overwhelm downstream

**Parameters:**
- Bucket capacity (max tokens)
- Refill rate (tokens per second)

**Example:**
```python
import time

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def allow_request(self):
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
```

**Use Cases:**
- API rate limiting (AWS API Gateway uses this)
- Network traffic shaping
- Allowing burst traffic

#### 2. Leaky Bucket

**How it works:**
- Requests added to queue (bucket)
- Processed at fixed rate (leak)
- If bucket full, request rejected

**Pros:**
- Smooth outgoing rate
- Simple to understand
- Protects downstream services

**Cons:**
- No burst handling
- Queue can fill up quickly during traffic spikes

**Parameters:**
- Bucket capacity (queue size)
- Leak rate (requests per second)

**Example:**
```python
from collections import deque
import time

class LeakyBucket:
    def __init__(self, capacity, leak_rate):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.queue = deque()
        self.last_leak = time.time()

    def allow_request(self):
        self._leak()
        if len(self.queue) < self.capacity:
            self.queue.append(time.time())
            return True
        return False

    def _leak(self):
        now = time.time()
        elapsed = now - self.last_leak
        leaks = int(elapsed * self.leak_rate)

        for _ in range(min(leaks, len(self.queue))):
            self.queue.popleft()

        self.last_leak = now
```

**Use Cases:**
- Network traffic shaping
- Protecting backend services
- Enforcing steady request rate

#### 3. Fixed Window Counter

**How it works:**
- Time divided into fixed windows
- Counter tracks requests in current window
- Counter resets at window boundary
- Allow request if counter < limit

**Pros:**
- Simple to implement
- Memory efficient
- Easy to understand

**Cons:**
- Burst at window boundaries
- Can allow 2x limit at boundary (boundary issue)

**Parameters:**
- Window size (e.g., 1 minute)
- Request limit per window

**Example:**
```python
import time

class FixedWindowCounter:
    def __init__(self, limit, window_size):
        self.limit = limit
        self.window_size = window_size
        self.counter = 0
        self.window_start = time.time()

    def allow_request(self):
        now = time.time()

        # Reset if new window
        if now - self.window_start >= self.window_size:
            self.counter = 0
            self.window_start = now

        if self.counter < self.limit:
            self.counter += 1
            return True
        return False
```

**Boundary Problem Example:**
```
Window 1: [00:00-01:00] - 1000 requests at 00:59
Window 2: [01:00-02:00] - 1000 requests at 01:01
Total in 2 seconds: 2000 requests (2x limit!)
```

**Use Cases:**
- Simple rate limiting
- Analytics and reporting
- Systems where precision not critical

#### 4. Sliding Window Log

**How it works:**
- Store timestamp of each request
- Count requests in sliding window
- Remove old timestamps outside window
- Allow if count < limit

**Pros:**
- Accurate rate limiting
- No boundary issue
- Precise control

**Cons:**
- High memory usage (stores all timestamps)
- Expensive for high traffic

**Parameters:**
- Window size
- Request limit

**Example:**
```python
import time
from collections import deque

class SlidingWindowLog:
    def __init__(self, limit, window_size):
        self.limit = limit
        self.window_size = window_size
        self.log = deque()

    def allow_request(self):
        now = time.time()

        # Remove old entries
        while self.log and self.log[0] <= now - self.window_size:
            self.log.popleft()

        if len(self.log) < self.limit:
            self.log.append(now)
            return True
        return False
```

**Use Cases:**
- Precise rate limiting needed
- Low to medium traffic
- Compliance requirements

#### 5. Sliding Window Counter

**How it works:**
- Combines fixed window and sliding window
- Uses weighted count from previous and current window
- More accurate than fixed, more efficient than log

**Formula:**
```
Requests in sliding window =
    (Previous window count × Overlap percentage) + Current window count
```

**Pros:**
- Good approximation of sliding window
- Memory efficient
- No boundary issue

**Cons:**
- Approximation (not exact)
- Slightly complex logic

**Example:**
```python
import time

class SlidingWindowCounter:
    def __init__(self, limit, window_size):
        self.limit = limit
        self.window_size = window_size
        self.current_window_start = time.time()
        self.current_count = 0
        self.previous_count = 0

    def allow_request(self):
        now = time.time()
        elapsed = now - self.current_window_start

        # Move to next window if needed
        if elapsed >= self.window_size:
            self.previous_count = self.current_count
            self.current_count = 0
            self.current_window_start = now
            elapsed = 0

        # Calculate weighted count
        previous_weight = 1 - (elapsed / self.window_size)
        estimated_count = (self.previous_count * previous_weight) + self.current_count

        if estimated_count < self.limit:
            self.current_count += 1
            return True
        return False
```

**Use Cases:**
- Most production systems
- Good balance of accuracy and efficiency
- Cloudflare, Stripe use this

### Rate Limiting in Distributed Systems

**Challenges:**
- Race conditions across servers
- Synchronization overhead
- Network latency

**Solutions:**

1. **Redis-based Rate Limiting**
```python
import redis
import time

class DistributedRateLimiter:
    def __init__(self, redis_client, key_prefix, limit, window):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.limit = limit
        self.window = window

    def allow_request(self, user_id):
        key = f"{self.key_prefix}:{user_id}"
        now = time.time()

        # Sliding window with Redis sorted set
        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, now - self.window)

        # Count requests in window
        pipe.zcard(key)

        # Add current request
        pipe.zadd(key, {now: now})

        # Set expiry
        pipe.expire(key, int(self.window) + 1)

        results = pipe.execute()
        request_count = results[1]

        return request_count < self.limit
```

2. **Token Bucket with Redis**
```lua
-- Lua script for atomic token bucket in Redis
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local info = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(info[1]) or capacity
local last_refill = tonumber(info[2]) or now

-- Refill tokens
local elapsed = now - last_refill
local new_tokens = math.min(capacity, tokens + (elapsed * rate))

if new_tokens >= 1 then
    redis.call('HMSET', key, 'tokens', new_tokens - 1, 'last_refill', now)
    redis.call('EXPIRE', key, 3600)
    return 1
else
    return 0
end
```

### Rate Limiting Strategies

1. **User-based**: Limit per user ID
2. **IP-based**: Limit per IP address
3. **API key-based**: Limit per API key
4. **Endpoint-based**: Different limits for different endpoints
5. **Tiered**: Different limits for different subscription tiers

### HTTP Headers for Rate Limiting

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 500
X-RateLimit-Reset: 1699999999
Retry-After: 3600
```

### Response Codes

- **429 Too Many Requests**: Rate limit exceeded
- **503 Service Unavailable**: System overloaded

See `/HLD/examples/week4/rate_limiter.py` for complete implementations.

---

## 4. API Design Best Practices

### RESTful API Principles

#### 1. Resource-Based URLs

**Good:**
```
GET /users/123
POST /users
PUT /users/123
DELETE /users/123

GET /users/123/posts
POST /users/123/posts
GET /posts/456/comments
```

**Bad:**
```
GET /getUser?id=123
POST /createUser
POST /user/delete/123
GET /getAllUserPosts?userId=123
```

**Rules:**
- Use nouns, not verbs
- Use plural nouns for collections
- Use HTTP methods for actions
- Nest resources logically

#### 2. HTTP Methods (CRUD)

| Method | Action | Idempotent | Safe |
|--------|--------|------------|------|
| GET | Read | Yes | Yes |
| POST | Create | No | No |
| PUT | Update/Replace | Yes | No |
| PATCH | Partial Update | No | No |
| DELETE | Delete | Yes | No |

**Idempotent**: Multiple identical requests have same effect as single request
**Safe**: Does not modify resource

#### 3. Status Codes

**2xx Success:**
- **200 OK**: Request succeeded
- **201 Created**: Resource created successfully
- **204 No Content**: Success, no response body

**3xx Redirection:**
- **301 Moved Permanently**: Resource moved
- **304 Not Modified**: Cached version still valid

**4xx Client Error:**
- **400 Bad Request**: Invalid request
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Request conflicts with current state
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded

**5xx Server Error:**
- **500 Internal Server Error**: Server error
- **502 Bad Gateway**: Invalid response from upstream
- **503 Service Unavailable**: Temporarily unavailable
- **504 Gateway Timeout**: Upstream timeout

#### 4. Versioning

**URL Path Versioning (Recommended):**
```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

**Header Versioning:**
```
GET /users
Accept: application/vnd.example.v1+json
```

**Query Parameter:**
```
https://api.example.com/users?version=1
```

**Best Practices:**
- Version from the start
- Support multiple versions
- Deprecate gracefully
- Document breaking changes

#### 5. Pagination

**Offset-based:**
```
GET /users?limit=20&offset=40
```

**Cursor-based (better for large datasets):**
```
GET /users?limit=20&cursor=xyz123

Response:
{
  "data": [...],
  "next_cursor": "abc456",
  "has_more": true
}
```

**Page-based:**
```
GET /users?page=3&per_page=20
```

#### 6. Filtering, Sorting, Searching

**Filtering:**
```
GET /users?status=active&role=admin
GET /posts?author_id=123&published=true
```

**Sorting:**
```
GET /users?sort=created_at&order=desc
GET /posts?sort=-created_at,+title  (- for desc, + for asc)
```

**Searching:**
```
GET /users?q=john
GET /posts?search=api design
```

**Field Selection:**
```
GET /users?fields=id,name,email
```

#### 7. Request/Response Format

**Request:**
```json
POST /users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

**Response (Success):**
```json
HTTP/1.1 201 Created
Content-Type: application/json
Location: /users/123

{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Response (Error):**
```json
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

#### 8. HATEOAS (Hypermedia)

```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "_links": {
    "self": { "href": "/users/123" },
    "posts": { "href": "/users/123/posts" },
    "friends": { "href": "/users/123/friends" }
  }
}
```

#### 9. API Documentation

**OpenAPI/Swagger Example:**
```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
```

#### 10. Best Practices Summary

1. **Consistency**: Same patterns across all endpoints
2. **Simplicity**: Keep it simple and intuitive
3. **Documentation**: Comprehensive and up-to-date
4. **Validation**: Validate all inputs
5. **Error Handling**: Meaningful error messages
6. **Security**: Authentication, authorization, encryption
7. **Performance**: Caching, pagination, compression
8. **Monitoring**: Log requests, track metrics
9. **Backward Compatibility**: Don't break existing clients
10. **Standards**: Follow REST, HTTP, JSON standards

See `/HLD/examples/week4/api_design_examples.md` for more examples.

---

## 5. Authentication & Authorization

### Authentication vs Authorization

- **Authentication**: Verifying identity (Who are you?)
- **Authorization**: Verifying permissions (What can you do?)

### Authentication Methods

#### 1. API Keys

**How it works:**
- Client includes API key in request
- Server validates key
- Simple, stateless

**Example:**
```
GET /api/users
X-API-Key: sk_live_abc123xyz456
```

**Pros:**
- Simple to implement
- Stateless
- Easy to rotate

**Cons:**
- No user context
- Hard to implement fine-grained permissions
- Can be leaked easily

**Use Cases:**
- Service-to-service authentication
- Public APIs with simple access control
- Non-user-specific operations

#### 2. Basic Authentication

**How it works:**
- Username and password encoded in Base64
- Sent in Authorization header
- Must use HTTPS

**Example:**
```
GET /api/users
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

**Pros:**
- Simple
- Built into HTTP

**Cons:**
- Credentials sent with every request
- No logout mechanism
- Not secure without HTTPS

**Use Cases:**
- Internal tools
- Development/testing
- Simple services

#### 3. Session-Based Authentication

**How it works:**
1. User logs in with credentials
2. Server creates session, stores in database/cache
3. Returns session ID in cookie
4. Client sends cookie with each request
5. Server validates session

**Pros:**
- Server-side session control
- Easy to revoke
- User context available

**Cons:**
- Stateful (harder to scale)
- CSRF vulnerability
- Requires session storage

**Example:**
```python
# Login
@app.route('/login', methods=['POST'])
def login():
    user = authenticate(request.json['username'], request.json['password'])
    if user:
        session['user_id'] = user.id
        return jsonify({'message': 'Logged in'})
    return jsonify({'error': 'Invalid credentials'}), 401

# Protected route
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.get(session['user_id'])
    return jsonify(user.to_dict())
```

#### 4. JWT (JSON Web Token)

**Structure:**
```
header.payload.signature

Example:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "exp": 1516242622,
  "roles": ["admin", "user"]
}
```

**Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

**How it works:**
1. User logs in
2. Server creates JWT, signs it
3. Client stores JWT (localStorage/cookie)
4. Client sends JWT with each request
5. Server validates signature and expiry

**Pros:**
- Stateless (scalable)
- Self-contained (all info in token)
- Works across domains
- No server-side storage

**Cons:**
- Cannot revoke before expiry
- Token size (sent with every request)
- XSS vulnerability if stored in localStorage

**Best Practices:**
- Short expiry time (15 mins for access token)
- Use refresh tokens
- Store in httpOnly cookies (not localStorage)
- Always use HTTPS
- Validate signature and expiry
- Include minimal data in payload

**Example:**
```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your-secret-key'

# Generate JWT
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=15),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# Verify JWT
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
```

See `/HLD/examples/week4/jwt_auth_example.py` for complete implementation.

#### 5. OAuth 2.0

**How it works:**
1. User redirected to OAuth provider (Google, Facebook)
2. User grants permissions
3. Provider redirects back with authorization code
4. App exchanges code for access token
5. App uses access token to access resources

**Roles:**
- **Resource Owner**: User
- **Client**: Your application
- **Authorization Server**: OAuth provider
- **Resource Server**: API server

**Grant Types:**

1. **Authorization Code** (most secure, for web apps)
```
1. Client → Authorization Server: Redirect user
   https://oauth.provider.com/authorize?
     client_id=abc123&
     redirect_uri=https://yourapp.com/callback&
     response_type=code&
     scope=read_user

2. User logs in and grants permission

3. Authorization Server → Client: Redirect with code
   https://yourapp.com/callback?code=xyz789

4. Client → Authorization Server: Exchange code for token
   POST /token
   {
     "grant_type": "authorization_code",
     "code": "xyz789",
     "client_id": "abc123",
     "client_secret": "secret",
     "redirect_uri": "https://yourapp.com/callback"
   }

5. Authorization Server → Client: Access token
   {
     "access_token": "token123",
     "token_type": "Bearer",
     "expires_in": 3600,
     "refresh_token": "refresh456"
   }
```

2. **Implicit** (deprecated, don't use)
3. **Client Credentials** (service-to-service)
4. **Resource Owner Password** (only for trusted apps)

**Pros:**
- Secure delegation
- No password sharing
- Granular permissions (scopes)
- Industry standard

**Cons:**
- Complex to implement
- Requires HTTPS
- Multiple redirects

**Use Cases:**
- "Login with Google/Facebook"
- Third-party app access
- API access delegation

### Authorization Patterns

#### 1. Role-Based Access Control (RBAC)

**Concept:**
- Users assigned to roles
- Roles have permissions
- Check user's role for access

**Example:**
```python
class User:
    def __init__(self, id, roles):
        self.id = id
        self.roles = roles

class RBACService:
    def __init__(self):
        self.permissions = {
            'admin': ['read', 'write', 'delete', 'manage_users'],
            'editor': ['read', 'write'],
            'viewer': ['read']
        }

    def has_permission(self, user, permission):
        for role in user.roles:
            if permission in self.permissions.get(role, []):
                return True
        return False

# Usage
rbac = RBACService()
user = User(123, ['editor'])
if rbac.has_permission(user, 'write'):
    # Allow write operation
    pass
```

#### 2. Attribute-Based Access Control (ABAC)

**Concept:**
- Access based on attributes (user, resource, environment)
- More flexible than RBAC
- Policy-based decisions

**Example:**
```python
def can_access(user, resource, action, context):
    # User attributes
    if user.department == resource.department:
        return True

    # Time-based
    if context.time.hour < 9 or context.time.hour > 17:
        return False

    # Resource attributes
    if resource.classification == 'public':
        return True

    # User role + resource owner
    if 'manager' in user.roles and resource.owner == user.id:
        return True

    return False
```

#### 3. Access Control Lists (ACL)

**Concept:**
- Each resource has list of allowed users/groups
- Direct mapping of users to resources

**Example:**
```python
class Document:
    def __init__(self, id, owner):
        self.id = id
        self.owner = owner
        self.acl = {
            owner: ['read', 'write', 'delete'],
        }

    def grant(self, user_id, permissions):
        self.acl[user_id] = permissions

    def can_access(self, user_id, permission):
        return permission in self.acl.get(user_id, [])
```

---

## 6. Security Best Practices

### 1. HTTPS/TLS

**Always use HTTPS:**
- Encrypts data in transit
- Prevents man-in-the-middle attacks
- Required for secure cookies

**Best Practices:**
- Use TLS 1.2 or higher
- Strong cipher suites
- Valid SSL certificates
- HTTP Strict Transport Security (HSTS)

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 2. Input Validation

**Validate Everything:**
```python
from typing import Optional
import re

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_user_input(data):
    errors = []

    # Email validation
    if not validate_email(data.get('email', '')):
        errors.append('Invalid email format')

    # Length validation
    if len(data.get('name', '')) > 100:
        errors.append('Name too long')

    # Type validation
    if not isinstance(data.get('age'), int):
        errors.append('Age must be integer')

    # Range validation
    if data.get('age', 0) < 0 or data.get('age', 0) > 150:
        errors.append('Age out of range')

    return errors
```

### 3. SQL Injection Prevention

**Bad (vulnerable):**
```python
# NEVER DO THIS
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)
```

**Good (safe):**
```python
# Use parameterized queries
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))

# Or use ORM
user = User.query.filter_by(username=username).first()
```

### 4. XSS (Cross-Site Scripting) Prevention

**Types:**
- **Stored XSS**: Malicious script stored in database
- **Reflected XSS**: Script in URL parameters
- **DOM XSS**: Client-side script manipulation

**Prevention:**
```python
import html

# Escape output
def escape_html(text):
    return html.escape(text)

# Use Content Security Policy
@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = \
        "default-src 'self'; script-src 'self'; style-src 'self'"
    return response
```

**CSP Header:**
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; object-src 'none'
```

### 5. CSRF (Cross-Site Request Forgery) Prevention

**How it works:**
- Attacker tricks user into making unwanted request
- User's browser sends cookies automatically

**Prevention:**
```python
import secrets

# Generate CSRF token
def generate_csrf_token():
    return secrets.token_hex(32)

# Validate CSRF token
def validate_csrf_token(token, session_token):
    return token == session_token

# In form
@app.route('/profile', methods=['GET'])
def profile_form():
    csrf_token = generate_csrf_token()
    session['csrf_token'] = csrf_token
    return render_template('profile.html', csrf_token=csrf_token)

# Validate on submission
@app.route('/profile', methods=['POST'])
def update_profile():
    if not validate_csrf_token(
        request.form.get('csrf_token'),
        session.get('csrf_token')
    ):
        return 'Invalid CSRF token', 403
    # Process form
```

**Headers:**
```
Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict
```

### 6. Password Security

**Hashing:**
```python
import bcrypt

# Hash password
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

# Verify password
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

**Best Practices:**
- Never store plain text passwords
- Use bcrypt, scrypt, or Argon2
- Salt passwords
- Enforce strong password policies
- Rate limit login attempts
- Implement account lockout

### 7. Secure Headers

```python
@app.after_request
def set_security_headers(response):
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'

    # XSS protection
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # HTTPS only
    response.headers['Strict-Transport-Security'] = \
        'max-age=31536000; includeSubDomains'

    # CSP
    response.headers['Content-Security-Policy'] = \
        "default-src 'self'"

    # Referrer policy
    response.headers['Referrer-Policy'] = 'no-referrer'

    # Permissions policy
    response.headers['Permissions-Policy'] = \
        'geolocation=(), microphone=()'

    return response
```

### 8. Common Vulnerabilities

#### OWASP Top 10 (2021):

1. **Broken Access Control**
   - Always verify user permissions
   - Implement proper authorization
   - Don't rely on client-side checks

2. **Cryptographic Failures**
   - Use strong encryption
   - Proper key management
   - TLS for data in transit

3. **Injection**
   - Parameterized queries
   - Input validation
   - Output encoding

4. **Insecure Design**
   - Threat modeling
   - Security requirements
   - Secure defaults

5. **Security Misconfiguration**
   - Remove default accounts
   - Disable unnecessary features
   - Keep software updated

6. **Vulnerable Components**
   - Track dependencies
   - Regular updates
   - Security scanning

7. **Authentication Failures**
   - Strong password policies
   - Multi-factor authentication
   - Session management

8. **Data Integrity Failures**
   - Verify software updates
   - CI/CD security
   - Digital signatures

9. **Logging Failures**
   - Log security events
   - Monitor logs
   - Incident response

10. **Server-Side Request Forgery (SSRF)**
    - Validate URLs
    - Whitelist allowed hosts
    - Network segmentation

### 9. API Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Implement authentication
- [ ] Implement authorization
- [ ] Validate all inputs
- [ ] Use parameterized queries
- [ ] Implement rate limiting
- [ ] Set security headers
- [ ] Encrypt sensitive data
- [ ] Log security events
- [ ] Keep dependencies updated
- [ ] Use CORS properly
- [ ] Implement CSRF protection
- [ ] Use secure session management
- [ ] Implement proper error handling
- [ ] Regular security audits

---

## 7. Logging and Monitoring

### Why Logging?

- **Debugging**: Find and fix issues
- **Auditing**: Track user actions
- **Security**: Detect attacks
- **Analytics**: Understand usage patterns
- **Compliance**: Meet regulatory requirements

### What to Log?

**DO Log:**
- Request/response metadata
- Authentication attempts
- Authorization failures
- Errors and exceptions
- Performance metrics
- Security events

**DON'T Log:**
- Passwords
- Credit card numbers
- Personal identification info (PII)
- API keys/secrets
- Session tokens

### Log Levels

```python
import logging

# Levels (lowest to highest)
logging.DEBUG     # Detailed diagnostic info
logging.INFO      # General informational messages
logging.WARNING   # Warning messages
logging.ERROR     # Error messages
logging.CRITICAL  # Critical errors
```

**When to use:**
- **DEBUG**: Development only, very detailed
- **INFO**: Normal operations, milestones
- **WARNING**: Something unexpected, but not an error
- **ERROR**: Error occurred, but app still running
- **CRITICAL**: Serious error, app might crash

### Structured Logging

**Bad (unstructured):**
```python
logger.info(f"User {user_id} logged in from {ip_address}")
```

**Good (structured):**
```python
logger.info("User logged in", extra={
    'user_id': user_id,
    'ip_address': ip_address,
    'timestamp': datetime.utcnow().isoformat(),
    'event': 'login'
})

# JSON output:
{
  "level": "INFO",
  "message": "User logged in",
  "user_id": 123,
  "ip_address": "192.168.1.1",
  "timestamp": "2025-01-15T10:30:00Z",
  "event": "login"
}
```

**Benefits:**
- Easy to parse
- Easy to search
- Easy to aggregate
- Machine-readable

### Correlation IDs

Track requests across services:

```python
import uuid
from flask import request, g

@app.before_request
def before_request():
    g.correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))

@app.after_request
def after_request(response):
    response.headers['X-Correlation-ID'] = g.correlation_id
    return response

# In logging
logger.info("Processing request", extra={
    'correlation_id': g.correlation_id,
    'endpoint': request.endpoint
})
```

### Centralized Logging

**Architecture:**
```
Applications → Log Shipper → Log Aggregator → Storage → Visualization

Examples:
Apps → Filebeat → Logstash → Elasticsearch → Kibana (ELK Stack)
Apps → Fluentd → Kafka → Elasticsearch → Grafana
Apps → CloudWatch Agent → CloudWatch Logs → CloudWatch Insights
```

**Benefits:**
- Single source of truth
- Cross-service correlation
- Powerful querying
- Alerting
- Dashboards

### Monitoring Metrics

**Golden Signals (Google SRE):**

1. **Latency**: Time to serve request
```python
import time

start_time = time.time()
# Process request
duration = time.time() - start_time
metrics.record('request.duration', duration)
```

2. **Traffic**: Request rate
```python
metrics.increment('request.count')
metrics.increment(f'request.count.{endpoint}')
```

3. **Errors**: Error rate
```python
if response.status_code >= 500:
    metrics.increment('request.errors')
```

4. **Saturation**: Resource utilization
```python
import psutil

cpu_percent = psutil.cpu_percent()
memory_percent = psutil.virtual_memory().percent
metrics.gauge('system.cpu', cpu_percent)
metrics.gauge('system.memory', memory_percent)
```

### RED Metrics (for services)

- **Rate**: Requests per second
- **Errors**: Failed requests per second
- **Duration**: Response time distribution

### USE Metrics (for resources)

- **Utilization**: % time resource is busy
- **Saturation**: Queue length or wait time
- **Errors**: Error count

### Application Performance Monitoring (APM)

**Distributed Tracing:**
```python
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Initialize tracer
tracer = trace.get_tracer(__name__)

# Trace function
@app.route('/api/users/<user_id>')
def get_user(user_id):
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("user_id", user_id)

        with tracer.start_as_current_span("fetch_from_db"):
            user = db.get_user(user_id)

        with tracer.start_as_current_span("fetch_posts"):
            posts = db.get_user_posts(user_id)

        return jsonify({'user': user, 'posts': posts})
```

**Trace example:**
```
Request: GET /api/users/123 (total: 150ms)
  ├─ get_user (150ms)
      ├─ fetch_from_db (50ms)
      └─ fetch_posts (90ms)
```

### Alerting

**Alert on:**
- Error rate spikes
- Latency degradation
- Resource saturation
- Service downtime
- Security events

**Example:**
```yaml
# Prometheus alert rule
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "95th percentile latency > 1s"
```

### Dashboards

**Key Metrics Dashboard:**
- Request rate
- Error rate
- Response time (p50, p95, p99)
- Active users
- System resources

**Tools:**
- Grafana
- Kibana
- Datadog
- New Relic
- CloudWatch

See `/HLD/examples/week4/logging_system.py` and `/HLD/examples/week4/monitoring_metrics.py` for implementations.

---

## 8. Fault Tolerance and Circuit Breakers

### Why Fault Tolerance?

Distributed systems fail. You need to:
- Prevent cascading failures
- Gracefully degrade
- Recover automatically
- Maintain availability

### Circuit Breaker Pattern

**Concept:**
Like electrical circuit breaker - stops flow when fault detected.

**States:**

1. **CLOSED** (Normal)
   - Requests flow through
   - Failures tracked
   - If failures exceed threshold → OPEN

2. **OPEN** (Failing)
   - Requests fail immediately
   - No calls to downstream service
   - After timeout → HALF_OPEN

3. **HALF_OPEN** (Testing)
   - Limited requests allowed
   - If successful → CLOSED
   - If failed → OPEN

**State Diagram:**
```
         Success
CLOSED ←---------- HALF_OPEN
  │                    ↑
  │ Failure           │ Timeout
  │ Threshold         │
  ↓                    │
OPEN ─────────────────┘
       (Wait timeout)
```

**Implementation:**
```python
from enum import Enum
import time
from threading import Lock

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60, half_open_max_calls=3):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        self.lock = Lock()

    def call(self, func, *args, **kwargs):
        with self.lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                else:
                    raise Exception("Circuit breaker is OPEN")

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    raise Exception("Circuit breaker HALF_OPEN limit reached")
                self.half_open_calls += 1

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e

    def on_success(self):
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.failure_count = 0

    def on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
```

See `/HLD/examples/week4/circuit_breaker.py` for complete implementation.

### Retry Strategies

#### 1. Fixed Retry
```python
def retry_fixed(func, max_attempts=3, delay=1):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            time.sleep(delay)
```

#### 2. Exponential Backoff
```python
def retry_exponential_backoff(func, max_attempts=5, base_delay=1, max_delay=60):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            delay = min(base_delay * (2 ** attempt), max_delay)
            time.sleep(delay)
```

#### 3. Exponential Backoff with Jitter
```python
import random

def retry_with_jitter(func, max_attempts=5, base_delay=1, max_delay=60):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            delay = min(base_delay * (2 ** attempt), max_delay)
            jittered_delay = delay * (0.5 + random.random() * 0.5)
            time.sleep(jittered_delay)
```

### Bulkhead Pattern

**Concept:**
Isolate resources to prevent total system failure (like ship compartments).

**Implementation:**
```python
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore

class Bulkhead:
    def __init__(self, max_concurrent_calls):
        self.semaphore = Semaphore(max_concurrent_calls)

    def call(self, func, *args, **kwargs):
        if not self.semaphore.acquire(blocking=False):
            raise Exception("Bulkhead is full")
        try:
            return func(*args, **kwargs)
        finally:
            self.semaphore.release()

# Usage
payment_bulkhead = Bulkhead(max_concurrent_calls=10)
search_bulkhead = Bulkhead(max_concurrent_calls=100)

def process_payment(amount):
    return payment_bulkhead.call(payment_service.charge, amount)
```

### Timeout Pattern

**Implementation:**
```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds}s")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# Usage
try:
    with timeout(5):
        result = slow_operation()
except TimeoutError:
    logger.error("Operation timed out")
    return default_value
```

### Fallback Pattern

**Implementation:**
```python
def get_user_recommendations(user_id):
    try:
        # Try personalized recommendations
        return ml_service.get_recommendations(user_id)
    except Exception as e:
        logger.warning(f"ML service failed: {e}")
        try:
            # Fallback to cached recommendations
            return cache.get(f"recommendations:{user_id}")
        except Exception:
            # Final fallback to popular items
            return db.get_popular_items()
```

### Health Checks

**Implementation:**
```python
@app.route('/health')
def health():
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {}
    }

    # Database check
    try:
        db.execute("SELECT 1")
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    # Redis check
    try:
        redis_client.ping()
        health_status['checks']['redis'] = 'healthy'
    except Exception as e:
        health_status['checks']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@app.route('/ready')
def readiness():
    # Check if app is ready to serve traffic
    if app_initialized and not shutting_down:
        return jsonify({'status': 'ready'}), 200
    return jsonify({'status': 'not ready'}), 503
```

### Graceful Degradation

**Example:**
```python
def get_product_page(product_id):
    product = db.get_product(product_id)

    # Try to get recommendations (not critical)
    try:
        recommendations = recommendation_service.get(product_id, timeout=1)
    except Exception:
        logger.warning("Recommendations unavailable")
        recommendations = []

    # Try to get reviews (not critical)
    try:
        reviews = review_service.get(product_id, timeout=1)
    except Exception:
        logger.warning("Reviews unavailable")
        reviews = []

    # Product data is critical - fail if unavailable
    return {
        'product': product,
        'recommendations': recommendations,
        'reviews': reviews
    }
```

### Chaos Engineering

**Principles:**
- Test in production
- Inject failures
- Minimize blast radius
- Learn and improve

**Tools:**
- Chaos Monkey (Netflix)
- Gremlin
- Chaos Toolkit

---

## Summary

This week covered essential system design concepts:

1. **Capacity Estimation**: Calculate QPS, storage, bandwidth for large-scale systems
2. **Communication Patterns**: Choose between polling, long-polling, SSE, WebSockets
3. **Rate Limiting**: Protect systems with Token Bucket, Sliding Window, etc.
4. **API Design**: RESTful principles, versioning, pagination, documentation
5. **Authentication**: API keys, JWT, OAuth 2.0, session management
6. **Authorization**: RBAC, ABAC, ACL patterns
7. **Security**: HTTPS, input validation, CSRF, XSS, password hashing
8. **Logging**: Structured logging, correlation IDs, centralized logging
9. **Monitoring**: Golden signals, metrics, distributed tracing, alerting
10. **Fault Tolerance**: Circuit breakers, retries, bulkheads, graceful degradation

## Practice Problems

1. Design rate limiting for a Twitter-like API
2. Implement JWT authentication with refresh tokens
3. Calculate capacity for Instagram Stories feature
4. Design logging system for microservices
5. Implement circuit breaker for payment service
6. Design API for e-commerce platform
7. Implement OAuth 2.0 authorization code flow
8. Design monitoring dashboard for web application

## Resources

- [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [Web Architecture 101](https://engineering.videoblocks.com/web-architecture-101-a3224e126947)
- [OAuth 2.0 Spec](https://oauth.net/2/)
- [JWT.io](https://jwt.io/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)

---

## Next Steps

Week 5 will cover:
- Caching strategies
- Database scaling (sharding, replication)
- Message queues
- Microservices architecture
- Design patterns for distributed systems
