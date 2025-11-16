"""
Circuit Breaker Pattern Implementation

The Circuit Breaker pattern prevents cascading failures in distributed systems
by wrapping service calls and monitoring for failures. Like an electrical circuit
breaker, it stops the flow when too many failures occur.

States:
- CLOSED: Normal operation, requests flow through
- OPEN: Too many failures, requests fail immediately
- HALF_OPEN: Testing if service recovered

Author: HLD Course
"""

import time
import random
from enum import Enum
from threading import Lock, Thread
from typing import Callable, Optional, Any, Dict
from datetime import datetime, timedelta
from collections import deque
from functools import wraps


# ============================================================================
# Circuit Breaker States
# ============================================================================

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


# ============================================================================
# Circuit Breaker Exceptions
# ============================================================================

class CircuitBreakerError(Exception):
    """Base exception for circuit breaker"""
    pass


class CircuitOpenError(CircuitBreakerError):
    """Raised when circuit is open"""
    def __init__(self, message="Circuit breaker is OPEN"):
        self.message = message
        super().__init__(self.message)


class CircuitHalfOpenError(CircuitBreakerError):
    """Raised when circuit is half-open and limit reached"""
    def __init__(self, message="Circuit breaker HALF_OPEN limit reached"):
        self.message = message
        super().__init__(self.message)


# ============================================================================
# Basic Circuit Breaker
# ============================================================================

class CircuitBreaker:
    """
    Basic Circuit Breaker Implementation

    Monitors failures and opens circuit when threshold exceeded.
    After timeout, enters half-open state to test recovery.

    Parameters:
    - failure_threshold: Number of failures before opening
    - timeout: Seconds to wait before trying again (OPEN -> HALF_OPEN)
    - half_open_max_calls: Max requests to allow in HALF_OPEN state

    Example:
        cb = CircuitBreaker(failure_threshold=5, timeout=60)
        result = cb.call(some_function, arg1, arg2)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60,
        half_open_max_calls: int = 3,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self.expected_exception = expected_exception

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        self.lock = Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args, **kwargs: Arguments for function

        Returns:
            Function result

        Raises:
            CircuitOpenError: If circuit is open
            CircuitHalfOpenError: If half-open limit reached
            Exception: Original exception from function
        """
        with self.lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    raise CircuitOpenError()

            # Check if HALF_OPEN limit reached
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    raise CircuitHalfOpenError()
                self.half_open_calls += 1

        # Execute function (outside lock to allow concurrent calls)
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if timeout has elapsed"""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.timeout

    def _transition_to_half_open(self):
        """Transition from OPEN to HALF_OPEN"""
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0
        print(f"[CircuitBreaker] OPEN -> HALF_OPEN (testing recovery)")

    def _on_success(self):
        """Handle successful call"""
        with self.lock:
            self.success_count += 1

            if self.state == CircuitState.HALF_OPEN:
                # Successful test in HALF_OPEN, reset to CLOSED
                self._transition_to_closed()
            else:
                # Reset failure count on success
                self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                # Failed test in HALF_OPEN, back to OPEN
                self._transition_to_open()
            elif self.failure_count >= self.failure_threshold:
                # Too many failures in CLOSED, transition to OPEN
                self._transition_to_open()

    def _transition_to_open(self):
        """Transition to OPEN state"""
        self.state = CircuitState.OPEN
        print(f"[CircuitBreaker] -> OPEN (failures: {self.failure_count})")

    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        print(f"[CircuitBreaker] -> CLOSED (recovered)")

    def get_state(self) -> Dict:
        """Get current circuit breaker state"""
        with self.lock:
            return {
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure_time': self.last_failure_time,
                'failure_threshold': self.failure_threshold,
                'timeout': self.timeout
            }


# ============================================================================
# Advanced Circuit Breaker with Sliding Window
# ============================================================================

class SlidingWindowCircuitBreaker:
    """
    Advanced Circuit Breaker with Sliding Window

    Uses sliding window to track failures more accurately.
    Opens circuit based on failure rate rather than count.

    Parameters:
    - failure_threshold: Failure rate (0.0 to 1.0) to trigger open
    - window_size: Time window in seconds
    - min_calls: Minimum calls before calculating failure rate
    - timeout: Seconds in OPEN state before testing recovery

    Example:
        # Open if >50% failures in last 60 seconds (min 10 calls)
        cb = SlidingWindowCircuitBreaker(
            failure_threshold=0.5,
            window_size=60,
            min_calls=10
        )
    """

    def __init__(
        self,
        failure_threshold: float = 0.5,
        window_size: float = 60,
        min_calls: int = 10,
        timeout: float = 60,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.window_size = window_size
        self.min_calls = min_calls
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls

        self.state = CircuitState.CLOSED
        self.call_log = deque()  # (timestamp, success: bool)
        self.last_state_change = time.time()
        self.half_open_calls = 0
        self.lock = Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self.lock:
            self._remove_old_calls()

            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    raise CircuitOpenError()

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    raise CircuitHalfOpenError()
                self.half_open_calls += 1

        # Execute function
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise e

    def _remove_old_calls(self):
        """Remove calls outside the sliding window"""
        now = time.time()
        while self.call_log and self.call_log[0][0] < now - self.window_size:
            self.call_log.popleft()

    def _should_attempt_reset(self) -> bool:
        """Check if timeout has elapsed"""
        return time.time() - self.last_state_change >= self.timeout

    def _record_success(self):
        """Record successful call"""
        with self.lock:
            now = time.time()
            self.call_log.append((now, True))

            if self.state == CircuitState.HALF_OPEN:
                self._transition_to_closed()

    def _record_failure(self):
        """Record failed call"""
        with self.lock:
            now = time.time()
            self.call_log.append((now, False))

            if self.state == CircuitState.HALF_OPEN:
                self._transition_to_open()
            elif self.state == CircuitState.CLOSED:
                if self._should_open():
                    self._transition_to_open()

    def _should_open(self) -> bool:
        """Check if circuit should open based on failure rate"""
        total_calls = len(self.call_log)

        if total_calls < self.min_calls:
            return False

        failures = sum(1 for _, success in self.call_log if not success)
        failure_rate = failures / total_calls

        return failure_rate >= self.failure_threshold

    def _transition_to_open(self):
        """Transition to OPEN state"""
        self.state = CircuitState.OPEN
        self.last_state_change = time.time()
        failure_rate = self._get_failure_rate()
        print(f"[CircuitBreaker] -> OPEN (failure rate: {failure_rate:.2%})")

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0
        self.last_state_change = time.time()
        print(f"[CircuitBreaker] OPEN -> HALF_OPEN (testing recovery)")

    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self.state = CircuitState.CLOSED
        self.last_state_change = time.time()
        print(f"[CircuitBreaker] -> CLOSED (recovered)")

    def _get_failure_rate(self) -> float:
        """Calculate current failure rate"""
        if not self.call_log:
            return 0.0
        failures = sum(1 for _, success in self.call_log if not success)
        return failures / len(self.call_log)

    def get_state(self) -> Dict:
        """Get current circuit breaker state"""
        with self.lock:
            self._remove_old_calls()
            total = len(self.call_log)
            failures = sum(1 for _, success in self.call_log if not success)

            return {
                'state': self.state.value,
                'total_calls': total,
                'failures': failures,
                'failure_rate': failures / total if total > 0 else 0.0,
                'failure_threshold': self.failure_threshold,
                'min_calls': self.min_calls,
                'window_size': self.window_size
            }


# ============================================================================
# Circuit Breaker Decorator
# ============================================================================

class CircuitBreakerDecorator:
    """
    Decorator for applying circuit breaker to functions

    Example:
        cb = CircuitBreaker(failure_threshold=3, timeout=30)

        @CircuitBreakerDecorator(cb)
        def call_external_api():
            return requests.get('https://api.example.com/data')
    """

    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.circuit_breaker.call(func, *args, **kwargs)
        return wrapper


# ============================================================================
# Circuit Breaker with Fallback
# ============================================================================

class CircuitBreakerWithFallback:
    """
    Circuit Breaker with Fallback Function

    If circuit is open, executes fallback instead of failing.

    Example:
        def get_recommendations(user_id):
            return ml_service.get_recommendations(user_id)

        def fallback_recommendations(user_id):
            return cache.get_popular_items()

        cb = CircuitBreakerWithFallback(
            failure_threshold=5,
            fallback=fallback_recommendations
        )

        recommendations = cb.call(get_recommendations, user_id)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60,
        fallback: Optional[Callable] = None
    ):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            timeout=timeout
        )
        self.fallback = fallback

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker and fallback"""
        try:
            return self.circuit_breaker.call(func, *args, **kwargs)
        except CircuitOpenError:
            if self.fallback:
                print(f"[CircuitBreaker] Using fallback")
                return self.fallback(*args, **kwargs)
            raise

    def get_state(self) -> Dict:
        """Get circuit breaker state"""
        return self.circuit_breaker.get_state()


# ============================================================================
# Demo and Testing
# ============================================================================

class UnreliableService:
    """Simulates an unreliable external service for testing"""

    def __init__(self, failure_rate: float = 0.5):
        self.failure_rate = failure_rate
        self.call_count = 0

    def call(self, data: str) -> str:
        """Simulate service call that may fail"""
        self.call_count += 1

        # Simulate network delay
        time.sleep(0.1)

        # Random failure based on failure rate
        if random.random() < self.failure_rate:
            raise Exception(f"Service failed (call #{self.call_count})")

        return f"Success: {data} (call #{self.call_count})"


def demo_basic_circuit_breaker():
    """Demonstrate basic circuit breaker"""
    print("\n" + "=" * 70)
    print("Basic Circuit Breaker Demo")
    print("=" * 70)

    # Create unreliable service (70% failure rate)
    service = UnreliableService(failure_rate=0.7)

    # Create circuit breaker (open after 3 failures, timeout 5 seconds)
    cb = CircuitBreaker(failure_threshold=3, timeout=5, half_open_max_calls=2)

    print(f"\nService failure rate: 70%")
    print(f"Circuit breaker threshold: 3 failures")
    print(f"Timeout: 5 seconds\n")

    # Make calls
    for i in range(10):
        try:
            result = cb.call(service.call, f"request_{i+1}")
            print(f"✓ Call {i+1}: {result}")
        except CircuitOpenError:
            state = cb.get_state()
            print(f"✗ Call {i+1}: Circuit is OPEN (failures: {state['failure_count']})")
        except Exception as e:
            state = cb.get_state()
            print(f"✗ Call {i+1}: {e} (failures: {state['failure_count']})")

        time.sleep(0.2)

    # Wait for timeout
    print("\n⏳ Waiting 5 seconds for circuit to test recovery...")
    time.sleep(5)

    # Try again
    print("\nRetrying after timeout:")
    for i in range(5):
        try:
            result = cb.call(service.call, f"retry_{i+1}")
            print(f"✓ Call {i+1}: {result}")
        except CircuitOpenError:
            state = cb.get_state()
            print(f"✗ Call {i+1}: Circuit is OPEN")
        except CircuitHalfOpenError:
            print(f"✗ Call {i+1}: Circuit is HALF_OPEN, limit reached")
        except Exception as e:
            print(f"✗ Call {i+1}: {e}")

        time.sleep(0.2)


def demo_sliding_window_circuit_breaker():
    """Demonstrate sliding window circuit breaker"""
    print("\n" + "=" * 70)
    print("Sliding Window Circuit Breaker Demo")
    print("=" * 70)

    # Create service with 40% failure rate
    service = UnreliableService(failure_rate=0.4)

    # Open if >50% failures in last 10 seconds (min 5 calls)
    cb = SlidingWindowCircuitBreaker(
        failure_threshold=0.5,
        window_size=10,
        min_calls=5,
        timeout=5
    )

    print(f"\nService failure rate: 40%")
    print(f"Circuit opens at: 50% failure rate")
    print(f"Window size: 10 seconds")
    print(f"Minimum calls: 5\n")

    for i in range(15):
        try:
            result = cb.call(service.call, f"request_{i+1}")
            print(f"✓ Call {i+1}: {result}")
        except CircuitOpenError:
            state = cb.get_state()
            print(f"✗ Call {i+1}: Circuit is OPEN "
                  f"(failure rate: {state['failure_rate']:.2%})")
        except Exception as e:
            state = cb.get_state()
            print(f"✗ Call {i+1}: Failed "
                  f"(failure rate: {state['failure_rate']:.2%})")

        time.sleep(0.3)


def demo_circuit_breaker_with_fallback():
    """Demonstrate circuit breaker with fallback"""
    print("\n" + "=" * 70)
    print("Circuit Breaker with Fallback Demo")
    print("=" * 70)

    # Unreliable primary service
    primary_service = UnreliableService(failure_rate=0.8)

    # Fallback function
    def fallback_service(data: str) -> str:
        return f"Fallback: {data} (from cache)"

    # Circuit breaker with fallback
    cb = CircuitBreakerWithFallback(
        failure_threshold=3,
        timeout=5,
        fallback=fallback_service
    )

    print(f"\nPrimary service failure rate: 80%")
    print(f"Fallback: Return cached data\n")

    for i in range(10):
        try:
            result = cb.call(primary_service.call, f"request_{i+1}")
            print(f"✓ Call {i+1}: {result}")
        except Exception as e:
            print(f"✗ Call {i+1}: {e}")

        time.sleep(0.2)


def demo_decorator():
    """Demonstrate circuit breaker decorator"""
    print("\n" + "=" * 70)
    print("Circuit Breaker Decorator Demo")
    print("=" * 70)

    service = UnreliableService(failure_rate=0.6)
    cb = CircuitBreaker(failure_threshold=3, timeout=3)

    @CircuitBreakerDecorator(cb)
    def call_api(request_id: str) -> str:
        return service.call(request_id)

    print(f"\nService failure rate: 60%")
    print(f"Using decorator pattern\n")

    for i in range(8):
        try:
            result = call_api(f"request_{i+1}")
            print(f"✓ Call {i+1}: {result}")
        except CircuitOpenError:
            print(f"✗ Call {i+1}: Circuit is OPEN")
        except Exception as e:
            print(f"✗ Call {i+1}: {e}")

        time.sleep(0.3)


def demo_real_world_scenario():
    """Demonstrate real-world payment service scenario"""
    print("\n" + "=" * 70)
    print("Real-World Scenario: Payment Service")
    print("=" * 70)

    class PaymentService:
        def __init__(self):
            self.is_down = False

        def process_payment(self, user_id: str, amount: float) -> Dict:
            if self.is_down:
                raise Exception("Payment service unavailable")

            # Simulate occasional failures
            if random.random() < 0.2:
                raise Exception("Payment processing failed")

            return {
                'status': 'success',
                'user_id': user_id,
                'amount': amount,
                'transaction_id': f"TXN-{random.randint(1000, 9999)}"
            }

    def fallback_payment(user_id: str, amount: float) -> Dict:
        """Queue payment for later processing"""
        return {
            'status': 'queued',
            'user_id': user_id,
            'amount': amount,
            'message': 'Payment queued for processing'
        }

    payment_service = PaymentService()
    cb = CircuitBreakerWithFallback(
        failure_threshold=5,
        timeout=10,
        fallback=fallback_payment
    )

    print("\nProcessing payments with circuit breaker protection:")
    print("- Primary: Payment service (20% random failure)")
    print("- Fallback: Queue payment for later\n")

    # Process some payments successfully
    for i in range(8):
        try:
            result = cb.call(
                payment_service.process_payment,
                f"user_{i+1}",
                100.0 + i
            )
            if result['status'] == 'success':
                print(f"✓ Payment {i+1}: Processed ${result['amount']:.2f} "
                      f"- {result['transaction_id']}")
            else:
                print(f"⚠ Payment {i+1}: {result['message']}")
        except Exception as e:
            print(f"✗ Payment {i+1}: {e}")

        time.sleep(0.2)

    # Simulate service going down
    print("\n⚠️  Payment service is now DOWN\n")
    payment_service.is_down = True

    for i in range(5):
        try:
            result = cb.call(
                payment_service.process_payment,
                f"user_{i+10}",
                100.0 + i
            )
            if result['status'] == 'queued':
                print(f"⚠ Payment {i+1}: Queued ${result['amount']:.2f}")
            else:
                print(f"✓ Payment {i+1}: Processed ${result['amount']:.2f}")
        except Exception as e:
            print(f"✗ Payment {i+1}: {e}")

        time.sleep(0.2)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("CIRCUIT BREAKER PATTERN - COMPREHENSIVE DEMONSTRATION")
    print("=" * 70)

    # Run all demos
    demo_basic_circuit_breaker()
    demo_sliding_window_circuit_breaker()
    demo_circuit_breaker_with_fallback()
    demo_decorator()
    demo_real_world_scenario()

    print("\n" + "=" * 70)
    print("All Demos Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("1. Circuit breaker prevents cascading failures")
    print("2. Three states: CLOSED, OPEN, HALF_OPEN")
    print("3. Automatically retries after timeout")
    print("4. Fallback provides graceful degradation")
    print("5. Sliding window gives more accurate failure tracking")
    print("=" * 70)
