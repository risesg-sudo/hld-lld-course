"""
Rate Limiting Algorithms Implementation

This module demonstrates various rate limiting algorithms used in production systems:
1. Token Bucket
2. Leaky Bucket
3. Fixed Window Counter
4. Sliding Window Log
5. Sliding Window Counter
6. Distributed Rate Limiter (Redis-based)

Author: HLD Course
"""

import time
import redis
from collections import deque
from threading import Lock
from typing import Dict, Optional
from datetime import datetime
from abc import ABC, abstractmethod


# ============================================================================
# Abstract Rate Limiter Interface
# ============================================================================

class RateLimiter(ABC):
    """Abstract base class for rate limiters"""

    @abstractmethod
    def allow_request(self, key: str = "default") -> bool:
        """
        Check if request should be allowed

        Args:
            key: Identifier for the client (user_id, ip_address, etc.)

        Returns:
            True if request allowed, False otherwise
        """
        pass

    @abstractmethod
    def get_stats(self, key: str = "default") -> Dict:
        """Get current statistics for the key"""
        pass


# ============================================================================
# 1. Token Bucket Algorithm
# ============================================================================

class TokenBucket(RateLimiter):
    """
    Token Bucket Rate Limiter

    - Bucket has maximum capacity of tokens
    - Tokens added at fixed rate (refill_rate)
    - Each request consumes one token
    - Request allowed if token available

    Pros:
    - Allows burst traffic (up to bucket capacity)
    - Smooth rate limiting
    - Memory efficient

    Cons:
    - Bursts can overwhelm downstream services

    Use Cases:
    - API rate limiting (AWS API Gateway)
    - Network traffic shaping
    - Allowing controlled bursts
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize Token Bucket

        Args:
            capacity: Maximum number of tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Dict] = {}
        self.lock = Lock()

    def allow_request(self, key: str = "default") -> bool:
        with self.lock:
            now = time.time()

            # Initialize bucket if doesn't exist
            if key not in self.buckets:
                self.buckets[key] = {
                    'tokens': self.capacity,
                    'last_refill': now
                }

            bucket = self.buckets[key]

            # Refill tokens based on time elapsed
            elapsed = now - bucket['last_refill']
            tokens_to_add = elapsed * self.refill_rate
            bucket['tokens'] = min(self.capacity, bucket['tokens'] + tokens_to_add)
            bucket['last_refill'] = now

            # Check if request can be allowed
            if bucket['tokens'] >= 1:
                bucket['tokens'] -= 1
                return True

            return False

    def get_stats(self, key: str = "default") -> Dict:
        with self.lock:
            if key not in self.buckets:
                return {
                    'tokens': self.capacity,
                    'capacity': self.capacity,
                    'refill_rate': self.refill_rate
                }

            bucket = self.buckets[key]
            return {
                'tokens': bucket['tokens'],
                'capacity': self.capacity,
                'refill_rate': self.refill_rate,
                'last_refill': bucket['last_refill']
            }


# ============================================================================
# 2. Leaky Bucket Algorithm
# ============================================================================

class LeakyBucket(RateLimiter):
    """
    Leaky Bucket Rate Limiter

    - Requests added to queue (bucket)
    - Processed at fixed rate (leak_rate)
    - If bucket full, request rejected

    Pros:
    - Smooth, constant outgoing rate
    - Protects downstream services
    - Simple to understand

    Cons:
    - No burst handling
    - Queue can fill quickly during spikes

    Use Cases:
    - Network traffic shaping
    - Protecting backend services
    - Enforcing steady request rate
    """

    def __init__(self, capacity: int, leak_rate: float):
        """
        Initialize Leaky Bucket

        Args:
            capacity: Maximum queue size
            leak_rate: Requests processed per second
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.buckets: Dict[str, Dict] = {}
        self.lock = Lock()

    def allow_request(self, key: str = "default") -> bool:
        with self.lock:
            now = time.time()

            # Initialize bucket if doesn't exist
            if key not in self.buckets:
                self.buckets[key] = {
                    'queue': deque(),
                    'last_leak': now
                }

            bucket = self.buckets[key]

            # Leak requests based on time elapsed
            elapsed = now - bucket['last_leak']
            leaks = int(elapsed * self.leak_rate)

            for _ in range(min(leaks, len(bucket['queue']))):
                bucket['queue'].popleft()

            bucket['last_leak'] = now

            # Check if request can be added to queue
            if len(bucket['queue']) < self.capacity:
                bucket['queue'].append(now)
                return True

            return False

    def get_stats(self, key: str = "default") -> Dict:
        with self.lock:
            if key not in self.buckets:
                return {
                    'queue_size': 0,
                    'capacity': self.capacity,
                    'leak_rate': self.leak_rate
                }

            bucket = self.buckets[key]
            return {
                'queue_size': len(bucket['queue']),
                'capacity': self.capacity,
                'leak_rate': self.leak_rate,
                'last_leak': bucket['last_leak']
            }


# ============================================================================
# 3. Fixed Window Counter Algorithm
# ============================================================================

class FixedWindowCounter(RateLimiter):
    """
    Fixed Window Counter Rate Limiter

    - Time divided into fixed windows
    - Counter tracks requests in current window
    - Counter resets at window boundary

    Pros:
    - Simple to implement
    - Memory efficient
    - Easy to understand

    Cons:
    - Burst at window boundaries
    - Can allow 2x limit at boundary

    Use Cases:
    - Simple rate limiting
    - Analytics and reporting
    - Non-critical rate limiting

    Boundary Problem:
    - Window 1: [00:00-01:00] - 1000 requests at 00:59
    - Window 2: [01:00-02:00] - 1000 requests at 01:01
    - Total in 2 seconds: 2000 requests (2x limit!)
    """

    def __init__(self, limit: int, window_size: float):
        """
        Initialize Fixed Window Counter

        Args:
            limit: Maximum requests per window
            window_size: Window size in seconds
        """
        self.limit = limit
        self.window_size = window_size
        self.windows: Dict[str, Dict] = {}
        self.lock = Lock()

    def allow_request(self, key: str = "default") -> bool:
        with self.lock:
            now = time.time()

            # Initialize window if doesn't exist
            if key not in self.windows:
                self.windows[key] = {
                    'count': 0,
                    'window_start': now
                }

            window = self.windows[key]

            # Check if we're in a new window
            if now - window['window_start'] >= self.window_size:
                window['count'] = 0
                window['window_start'] = now

            # Check if request can be allowed
            if window['count'] < self.limit:
                window['count'] += 1
                return True

            return False

    def get_stats(self, key: str = "default") -> Dict:
        with self.lock:
            if key not in self.windows:
                return {
                    'count': 0,
                    'limit': self.limit,
                    'window_size': self.window_size,
                    'time_remaining': self.window_size
                }

            window = self.windows[key]
            now = time.time()
            time_remaining = self.window_size - (now - window['window_start'])

            return {
                'count': window['count'],
                'limit': self.limit,
                'window_size': self.window_size,
                'time_remaining': max(0, time_remaining),
                'window_start': window['window_start']
            }


# ============================================================================
# 4. Sliding Window Log Algorithm
# ============================================================================

class SlidingWindowLog(RateLimiter):
    """
    Sliding Window Log Rate Limiter

    - Store timestamp of each request
    - Count requests in sliding window
    - Remove old timestamps outside window

    Pros:
    - Accurate rate limiting
    - No boundary issue
    - Precise control

    Cons:
    - High memory usage (stores all timestamps)
    - Expensive for high traffic

    Use Cases:
    - Precise rate limiting needed
    - Low to medium traffic
    - Compliance requirements
    """

    def __init__(self, limit: int, window_size: float):
        """
        Initialize Sliding Window Log

        Args:
            limit: Maximum requests per window
            window_size: Window size in seconds
        """
        self.limit = limit
        self.window_size = window_size
        self.logs: Dict[str, deque] = {}
        self.lock = Lock()

    def allow_request(self, key: str = "default") -> bool:
        with self.lock:
            now = time.time()

            # Initialize log if doesn't exist
            if key not in self.logs:
                self.logs[key] = deque()

            log = self.logs[key]

            # Remove old entries outside window
            while log and log[0] <= now - self.window_size:
                log.popleft()

            # Check if request can be allowed
            if len(log) < self.limit:
                log.append(now)
                return True

            return False

    def get_stats(self, key: str = "default") -> Dict:
        with self.lock:
            if key not in self.logs:
                return {
                    'count': 0,
                    'limit': self.limit,
                    'window_size': self.window_size
                }

            now = time.time()
            log = self.logs[key]

            # Clean old entries
            while log and log[0] <= now - self.window_size:
                log.popleft()

            oldest_request = log[0] if log else now

            return {
                'count': len(log),
                'limit': self.limit,
                'window_size': self.window_size,
                'oldest_request': oldest_request,
                'remaining': max(0, self.limit - len(log))
            }


# ============================================================================
# 5. Sliding Window Counter Algorithm
# ============================================================================

class SlidingWindowCounter(RateLimiter):
    """
    Sliding Window Counter Rate Limiter

    - Combines fixed window and sliding window
    - Uses weighted count from previous and current window
    - More accurate than fixed, more efficient than log

    Formula:
    Requests in sliding window =
        (Previous window count × Overlap %) + Current window count

    Pros:
    - Good approximation of sliding window
    - Memory efficient
    - No boundary issue

    Cons:
    - Approximation (not exact)
    - Slightly complex logic

    Use Cases:
    - Most production systems
    - Good balance of accuracy and efficiency
    - Used by Cloudflare, Stripe
    """

    def __init__(self, limit: int, window_size: float):
        """
        Initialize Sliding Window Counter

        Args:
            limit: Maximum requests per window
            window_size: Window size in seconds
        """
        self.limit = limit
        self.window_size = window_size
        self.windows: Dict[str, Dict] = {}
        self.lock = Lock()

    def allow_request(self, key: str = "default") -> bool:
        with self.lock:
            now = time.time()

            # Initialize window if doesn't exist
            if key not in self.windows:
                self.windows[key] = {
                    'current_count': 0,
                    'previous_count': 0,
                    'current_window_start': now
                }

            window = self.windows[key]
            elapsed = now - window['current_window_start']

            # Move to next window if needed
            if elapsed >= self.window_size:
                windows_passed = int(elapsed / self.window_size)
                if windows_passed == 1:
                    window['previous_count'] = window['current_count']
                else:
                    window['previous_count'] = 0

                window['current_count'] = 0
                window['current_window_start'] = now
                elapsed = 0

            # Calculate weighted count
            previous_weight = 1 - (elapsed / self.window_size)
            estimated_count = (window['previous_count'] * previous_weight) + window['current_count']

            # Check if request can be allowed
            if estimated_count < self.limit:
                window['current_count'] += 1
                return True

            return False

    def get_stats(self, key: str = "default") -> Dict:
        with self.lock:
            if key not in self.windows:
                return {
                    'estimated_count': 0,
                    'limit': self.limit,
                    'window_size': self.window_size
                }

            now = time.time()
            window = self.windows[key]
            elapsed = now - window['current_window_start']

            previous_weight = max(0, 1 - (elapsed / self.window_size))
            estimated_count = (window['previous_count'] * previous_weight) + window['current_count']

            return {
                'estimated_count': estimated_count,
                'current_count': window['current_count'],
                'previous_count': window['previous_count'],
                'limit': self.limit,
                'window_size': self.window_size,
                'remaining': max(0, self.limit - estimated_count)
            }


# ============================================================================
# 6. Distributed Rate Limiter (Redis-based)
# ============================================================================

class DistributedRateLimiter:
    """
    Distributed Rate Limiter using Redis

    - Uses Redis for shared state across multiple servers
    - Implements sliding window log with sorted sets
    - Thread-safe and distributed-safe

    Pros:
    - Works across multiple servers
    - Accurate
    - Persistent

    Cons:
    - Requires Redis
    - Network latency
    - More complex

    Use Cases:
    - Microservices architecture
    - Multiple server instances
    - High availability requirements
    """

    def __init__(self, redis_client: redis.Redis, key_prefix: str,
                 limit: int, window_size: float):
        """
        Initialize Distributed Rate Limiter

        Args:
            redis_client: Redis client instance
            key_prefix: Prefix for Redis keys
            limit: Maximum requests per window
            window_size: Window size in seconds
        """
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.limit = limit
        self.window_size = window_size

    def allow_request(self, user_id: str) -> bool:
        """
        Check if request should be allowed using Redis

        Args:
            user_id: User identifier

        Returns:
            True if request allowed, False otherwise
        """
        key = f"{self.key_prefix}:{user_id}"
        now = time.time()
        window_start = now - self.window_size

        try:
            pipe = self.redis.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)

            # Count requests in window
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {now: now})

            # Set expiry
            pipe.expire(key, int(self.window_size) + 1)

            results = pipe.execute()
            request_count = results[1]

            return request_count < self.limit

        except redis.RedisError as e:
            print(f"Redis error: {e}")
            # Fail open (allow request) or fail closed (deny request)
            return True  # Fail open for availability

    def get_stats(self, user_id: str) -> Dict:
        """Get current statistics for user"""
        key = f"{self.key_prefix}:{user_id}"
        now = time.time()
        window_start = now - self.window_size

        try:
            # Clean old entries and count
            pipe = self.redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            results = pipe.execute()

            count = results[1]

            return {
                'count': count,
                'limit': self.limit,
                'window_size': self.window_size,
                'remaining': max(0, self.limit - count)
            }
        except redis.RedisError:
            return {
                'count': 0,
                'limit': self.limit,
                'window_size': self.window_size,
                'remaining': self.limit
            }


class DistributedTokenBucket:
    """
    Distributed Token Bucket using Redis with Lua script

    - Atomic operations using Lua script
    - More efficient than multiple Redis commands
    """

    # Lua script for atomic token bucket operations
    LUA_SCRIPT = """
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
    """

    def __init__(self, redis_client: redis.Redis, key_prefix: str,
                 capacity: int, refill_rate: float):
        """
        Initialize Distributed Token Bucket

        Args:
            redis_client: Redis client instance
            key_prefix: Prefix for Redis keys
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.script = self.redis.register_script(self.LUA_SCRIPT)

    def allow_request(self, user_id: str) -> bool:
        """Check if request should be allowed"""
        key = f"{self.key_prefix}:{user_id}"
        now = time.time()

        try:
            result = self.script(
                keys=[key],
                args=[self.capacity, self.refill_rate, now]
            )
            return bool(result)
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return True  # Fail open


# ============================================================================
# Decorator for Rate Limiting
# ============================================================================

class RateLimitDecorator:
    """Decorator for applying rate limiting to functions"""

    def __init__(self, limiter: RateLimiter, key_func=None):
        """
        Initialize decorator

        Args:
            limiter: Rate limiter instance
            key_func: Function to extract key from request (default: "default")
        """
        self.limiter = limiter
        self.key_func = key_func or (lambda *args, **kwargs: "default")

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            key = self.key_func(*args, **kwargs)

            if not self.limiter.allow_request(key):
                raise Exception(f"Rate limit exceeded for key: {key}")

            return func(*args, **kwargs)

        return wrapper


# ============================================================================
# Demo and Testing
# ============================================================================

def demo_token_bucket():
    """Demonstrate Token Bucket algorithm"""
    print("\n=== Token Bucket Demo ===")
    print("Capacity: 5, Refill Rate: 1 token/second")

    limiter = TokenBucket(capacity=5, refill_rate=1)

    # Burst of 5 requests (should all succeed)
    print("\nBurst of 5 requests:")
    for i in range(5):
        allowed = limiter.allow_request("user1")
        stats = limiter.get_stats("user1")
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Denied'}, "
              f"Tokens: {stats['tokens']:.2f}")

    # Next request should fail
    print("\n6th request (should fail):")
    allowed = limiter.allow_request("user1")
    stats = limiter.get_stats("user1")
    print(f"Request 6: {'✓ Allowed' if allowed else '✗ Denied'}, "
          f"Tokens: {stats['tokens']:.2f}")

    # Wait and try again
    print("\nWaiting 2 seconds (2 tokens refilled)...")
    time.sleep(2)

    print("Requests after waiting:")
    for i in range(3):
        allowed = limiter.allow_request("user1")
        stats = limiter.get_stats("user1")
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Denied'}, "
              f"Tokens: {stats['tokens']:.2f}")


def demo_sliding_window_counter():
    """Demonstrate Sliding Window Counter algorithm"""
    print("\n=== Sliding Window Counter Demo ===")
    print("Limit: 5 requests, Window: 10 seconds")

    limiter = SlidingWindowCounter(limit=5, window_size=10)

    print("\n5 requests at start:")
    for i in range(5):
        allowed = limiter.allow_request("user1")
        stats = limiter.get_stats("user1")
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Denied'}, "
              f"Estimated count: {stats['estimated_count']:.2f}")

    print("\n6th request (should fail):")
    allowed = limiter.allow_request("user1")
    stats = limiter.get_stats("user1")
    print(f"Request 6: {'✓ Allowed' if allowed else '✗ Denied'}, "
          f"Estimated count: {stats['estimated_count']:.2f}")

    print("\nWaiting 5 seconds (50% of window)...")
    time.sleep(5)

    print("Requests after 5 seconds:")
    for i in range(3):
        allowed = limiter.allow_request("user1")
        stats = limiter.get_stats("user1")
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Denied'}, "
              f"Estimated count: {stats['estimated_count']:.2f}")


def demo_fixed_window_boundary_problem():
    """Demonstrate Fixed Window boundary problem"""
    print("\n=== Fixed Window Boundary Problem Demo ===")
    print("Limit: 3 requests, Window: 5 seconds")

    limiter = FixedWindowCounter(limit=3, window_size=5)

    print("\n3 requests near end of window:")
    for i in range(3):
        allowed = limiter.allow_request("user1")
        stats = limiter.get_stats("user1")
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Denied'}, "
              f"Count: {stats['count']}, Time remaining: {stats['time_remaining']:.2f}s")

    print("\nWaiting for new window (6 seconds)...")
    time.sleep(6)

    print("3 more requests in new window:")
    for i in range(3):
        allowed = limiter.allow_request("user1")
        stats = limiter.get_stats("user1")
        print(f"Request {i+1}: {'✓ Allowed' if allowed else '✗ Denied'}, "
              f"Count: {stats['count']}, Time remaining: {stats['time_remaining']:.2f}s")

    print("\nNote: If previous 3 requests were at end of window,")
    print("and these 3 at start, we'd have 6 requests in ~1 second!")


def compare_algorithms():
    """Compare different rate limiting algorithms"""
    print("\n=== Algorithm Comparison ===")

    algorithms = {
        'Token Bucket': TokenBucket(capacity=10, refill_rate=2),
        'Leaky Bucket': LeakyBucket(capacity=10, leak_rate=2),
        'Fixed Window': FixedWindowCounter(limit=10, window_size=5),
        'Sliding Window Log': SlidingWindowLog(limit=10, window_size=5),
        'Sliding Window Counter': SlidingWindowCounter(limit=10, window_size=5)
    }

    print("\nSending 15 requests rapidly:")
    for name, limiter in algorithms.items():
        allowed_count = 0
        for i in range(15):
            if limiter.allow_request("user1"):
                allowed_count += 1
        print(f"{name:25}: {allowed_count}/15 requests allowed")

    print("\n\nMemory Usage (approximate):")
    print(f"{'Token Bucket':25}: O(1) per user (2 numbers)")
    print(f"{'Leaky Bucket':25}: O(n) per user (queue of timestamps)")
    print(f"{'Fixed Window':25}: O(1) per user (counter + timestamp)")
    print(f"{'Sliding Window Log':25}: O(n) per user (all timestamps)")
    print(f"{'Sliding Window Counter':25}: O(1) per user (2 counters + timestamp)")

    print("\n\nAccuracy:")
    print(f"{'Token Bucket':25}: Good (allows bursts)")
    print(f"{'Leaky Bucket':25}: Excellent (smooth rate)")
    print(f"{'Fixed Window':25}: Poor (boundary problem)")
    print(f"{'Sliding Window Log':25}: Excellent (exact)")
    print(f"{'Sliding Window Counter':25}: Very Good (approximation)")


if __name__ == "__main__":
    print("=" * 70)
    print("Rate Limiting Algorithms - Comprehensive Demo")
    print("=" * 70)

    # Run demos
    demo_token_bucket()
    demo_sliding_window_counter()
    demo_fixed_window_boundary_problem()
    compare_algorithms()

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)

    # Example usage with decorator
    print("\n\n=== Decorator Example ===")

    limiter = TokenBucket(capacity=3, refill_rate=0.5)

    @RateLimitDecorator(limiter, key_func=lambda user_id: user_id)
    def api_endpoint(user_id: str, data: str):
        return f"Processing: {data} for user {user_id}"

    print("\nCalling API endpoint with rate limiting:")
    for i in range(5):
        try:
            result = api_endpoint("user123", f"request_{i+1}")
            print(f"✓ {result}")
        except Exception as e:
            print(f"✗ {e}")
