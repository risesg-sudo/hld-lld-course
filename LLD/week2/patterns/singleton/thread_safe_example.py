"""
Thread-Safe Singleton Implementation

This module demonstrates thread-safe singleton patterns for multi-threaded environments.
Shows both simple locking and double-checked locking approaches.
"""

import threading
import time


class ThreadSafeSingleton:
    """
    Thread-safe singleton using simple locking.

    Every call to get_instance() acquires a lock, which ensures thread safety
    but introduces overhead even after instance is created.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        """Private constructor."""
        if ThreadSafeSingleton._instance is not None:
            raise RuntimeError("Use get_instance() to access ThreadSafeSingleton")

        self.created_by_thread = threading.current_thread().name
        self.creation_time = time.time()
        self.access_count = 0
        print(f"Instance created by thread: {self.created_by_thread}")

    @classmethod
    def get_instance(cls):
        """
        Get singleton instance with thread safety.

        Uses lock for every access - simple but has performance overhead.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = ThreadSafeSingleton()
            cls._instance.access_count += 1
            return cls._instance


class DoubleCheckedLockingSingleton:
    """
    Thread-safe singleton using double-checked locking.

    Optimizes performance by checking instance existence before acquiring lock.
    Lock acquired only during initial creation, not for subsequent access.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        """Private constructor."""
        if DoubleCheckedLockingSingleton._instance is not None:
            raise RuntimeError("Use get_instance()")

        self.created_by_thread = threading.current_thread().name
        self.creation_time = time.time()
        self.access_count = 0
        print(f"Instance created by thread: {self.created_by_thread}")

    @classmethod
    def get_instance(cls):
        """
        Get singleton instance with optimized thread safety.

        Double-checked locking pattern:
        1. First check (without lock) - fast path for already-created instance
        2. Acquire lock only if instance doesn't exist
        3. Second check (with lock) - ensure another thread didn't create it
        4. Create instance if still None
        """
        # First check (without lock)
        if cls._instance is None:
            with cls._lock:
                # Second check (with lock)
                if cls._instance is None:
                    cls._instance = DoubleCheckedLockingSingleton()

        cls._instance.access_count += 1
        return cls._instance


class Logger:
    """
    Practical example: Thread-safe logger singleton.

    Demonstrates a real-world use case with actual logging functionality.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        """Private constructor."""
        if Logger._instance is not None:
            raise RuntimeError("Use get_instance()")

        self.log_entries = []
        self.log_lock = threading.Lock()
        print("Logger initialized")

    @classmethod
    def get_instance(cls):
        """Get logger instance (double-checked locking)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = Logger()
        return cls._instance

    def log(self, level: str, message: str):
        """
        Thread-safe logging method.

        Uses separate lock for log operations to allow concurrent
        instance access and logging.
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        thread_name = threading.current_thread().name
        log_entry = f"[{timestamp}] [{thread_name}] {level}: {message}"

        with self.log_lock:
            self.log_entries.append(log_entry)
            print(log_entry)

    def get_logs(self):
        """Get all log entries (thread-safe)."""
        with self.log_lock:
            return self.log_entries.copy()


def test_thread_safety():
    """Test that singleton is truly thread-safe."""
    print("="*70)
    print("THREAD SAFETY TEST")
    print("="*70)

    instance_ids = []
    lock = threading.Lock()

    def worker():
        """Worker thread that gets singleton instance."""
        instance = DoubleCheckedLockingSingleton.get_instance()
        thread_name = threading.current_thread().name

        with lock:
            instance_ids.append(id(instance))

        print(f"  Thread {thread_name}: Got instance {id(instance)}")

    print("\n1. Creating 10 threads to access singleton simultaneously:")
    threads = []
    for i in range(10):
        thread = threading.Thread(target=worker, name=f"Worker-{i+1}")
        threads.append(thread)

    # Start all threads at roughly the same time
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print(f"\n2. Analysis:")
    unique_ids = set(instance_ids)
    print(f"   Total threads: {len(threads)}")
    print(f"   Total instance IDs collected: {len(instance_ids)}")
    print(f"   Unique instance IDs: {len(unique_ids)}")
    print(f"   All same instance: {len(unique_ids) == 1}")

    instance = DoubleCheckedLockingSingleton.get_instance()
    print(f"\n3. Instance details:")
    print(f"   Created by: {instance.created_by_thread}")
    print(f"   Access count: {instance.access_count}")


def test_logger_singleton():
    """Test logger singleton with concurrent logging."""
    print("\n" + "="*70)
    print("LOGGER SINGLETON TEST")
    print("="*70)

    def log_worker(worker_id: int):
        """Worker thread that logs messages."""
        logger = Logger.get_instance()
        for i in range(3):
            logger.log("INFO", f"Message {i+1} from worker {worker_id}")
            time.sleep(0.01)  # Small delay to simulate work

    print("\n1. Creating 5 threads to log concurrently:")
    threads = []
    for i in range(5):
        thread = threading.Thread(target=log_worker, args=(i+1,), name=f"Logger-{i+1}")
        threads.append(thread)
        thread.start()

    # Wait for all logging to complete
    for thread in threads:
        thread.join()

    logger = Logger.get_instance()
    print(f"\n2. Total log entries: {len(logger.get_logs())}")
    print(f"   Expected: {5 * 3} (5 threads * 3 messages each)")


def compare_performance():
    """Compare performance of different singleton approaches."""
    print("\n" + "="*70)
    print("PERFORMANCE COMPARISON")
    print("="*70)

    iterations = 100000

    # Test simple locking
    print("\n1. Testing simple locking singleton:")
    start = time.time()
    for _ in range(iterations):
        ThreadSafeSingleton.get_instance()
    simple_lock_time = time.time() - start
    print(f"   Time for {iterations} accesses: {simple_lock_time:.4f}s")

    # Test double-checked locking
    print("\n2. Testing double-checked locking singleton:")
    start = time.time()
    for _ in range(iterations):
        DoubleCheckedLockingSingleton.get_instance()
    double_check_time = time.time() - start
    print(f"   Time for {iterations} accesses: {double_check_time:.4f}s")

    print("\n3. Performance difference:")
    speedup = simple_lock_time / double_check_time
    print(f"   Double-checked locking is {speedup:.2f}x faster")
    print("   (Lock acquired only once vs. every access)")


if __name__ == "__main__":
    test_thread_safety()
    test_logger_singleton()
    compare_performance()

    print("\n" + "="*70)
    print("KEY POINTS")
    print("="*70)
    print("""
1. Simple Locking:
   - Lock acquired on every access
   - Safe but slower performance
   - Easier to understand and implement

2. Double-Checked Locking:
   - First check without lock (fast path)
   - Lock acquired only for creation
   - Significantly better performance
   - More complex but worth it for frequent access

3. Practical Considerations:
   - Always use locking in multi-threaded environments
   - Choose approach based on access frequency
   - Consider separate locks for instance creation vs. operations
   - Test thread safety thoroughly
    """)
