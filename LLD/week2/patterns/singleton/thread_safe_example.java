/**
 * Thread-Safe Singleton Implementation
 *
 * This file demonstrates thread-safe singleton patterns for multi-threaded environments.
 * Shows both simple locking and double-checked locking approaches.
 */

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Thread-safe singleton using simple locking (synchronized method).
 *
 * Every call to getInstance() acquires a lock, which ensures thread safety
 * but introduces overhead even after instance is created.
 */
class ThreadSafeSingleton {
    private static ThreadSafeSingleton instance = null;

    private String createdByThread;
    private long creationTime;
    private AtomicInteger accessCount;

    /**
     * Private constructor.
     */
    private ThreadSafeSingleton() {
        this.createdByThread = Thread.currentThread().getName();
        this.creationTime = System.currentTimeMillis();
        this.accessCount = new AtomicInteger(0);
        System.out.println("Instance created by thread: " + createdByThread);
    }

    /**
     * Get singleton instance with thread safety.
     * Uses synchronized for every access - simple but has performance overhead.
     */
    public static synchronized ThreadSafeSingleton getInstance() {
        if (instance == null) {
            instance = new ThreadSafeSingleton();
        }
        instance.accessCount.incrementAndGet();
        return instance;
    }

    public String getCreatedByThread() {
        return createdByThread;
    }

    public int getAccessCount() {
        return accessCount.get();
    }
}


/**
 * Thread-safe singleton using double-checked locking.
 *
 * Optimizes performance by checking instance existence before acquiring lock.
 * Lock acquired only during initial creation, not for subsequent access.
 */
class DoubleCheckedLockingSingleton {
    // volatile ensures visibility across threads
    private static volatile DoubleCheckedLockingSingleton instance = null;
    private static final Object lock = new Object();

    private String createdByThread;
    private long creationTime;
    private AtomicInteger accessCount;

    /**
     * Private constructor.
     */
    private DoubleCheckedLockingSingleton() {
        this.createdByThread = Thread.currentThread().getName();
        this.creationTime = System.currentTimeMillis();
        this.accessCount = new AtomicInteger(0);
        System.out.println("Instance created by thread: " + createdByThread);
    }

    /**
     * Get singleton instance with optimized thread safety.
     *
     * Double-checked locking pattern:
     * 1. First check (without lock) - fast path for already-created instance
     * 2. Acquire lock only if instance doesn't exist
     * 3. Second check (with lock) - ensure another thread didn't create it
     * 4. Create instance if still null
     */
    public static DoubleCheckedLockingSingleton getInstance() {
        // First check (without lock)
        if (instance == null) {
            synchronized (lock) {
                // Second check (with lock)
                if (instance == null) {
                    instance = new DoubleCheckedLockingSingleton();
                }
            }
        }

        instance.accessCount.incrementAndGet();
        return instance;
    }

    public String getCreatedByThread() {
        return createdByThread;
    }

    public int getAccessCount() {
        return accessCount.get();
    }
}


/**
 * Practical example: Thread-safe logger singleton.
 *
 * Demonstrates a real-world use case with actual logging functionality.
 */
class Logger {
    private static volatile Logger instance = null;
    private static final Object instanceLock = new Object();

    private final List<String> logEntries;
    private final Object logLock;

    /**
     * Private constructor.
     */
    private Logger() {
        this.logEntries = new CopyOnWriteArrayList<>();
        this.logLock = new Object();
        System.out.println("Logger initialized");
    }

    /**
     * Get logger instance (double-checked locking).
     */
    public static Logger getInstance() {
        if (instance == null) {
            synchronized (instanceLock) {
                if (instance == null) {
                    instance = new Logger();
                }
            }
        }
        return instance;
    }

    /**
     * Thread-safe logging method.
     *
     * Uses separate lock for log operations to allow concurrent
     * instance access and logging.
     */
    public void log(String level, String message) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String timestamp = LocalDateTime.now().format(formatter);
        String threadName = Thread.currentThread().getName();
        String logEntry = String.format("[%s] [%s] %s: %s",
                                       timestamp, threadName, level, message);

        synchronized (logLock) {
            logEntries.add(logEntry);
            System.out.println(logEntry);
        }
    }

    /**
     * Get all log entries (thread-safe).
     */
    public List<String> getLogs() {
        synchronized (logLock) {
            return new ArrayList<>(logEntries);
        }
    }
}


/**
 * Demonstration class for thread-safe singleton patterns.
 */
public class thread_safe_example {

    public static void testThreadSafety() {
        System.out.println("=".repeat(70));
        System.out.println("THREAD SAFETY TEST");
        System.out.println("=".repeat(70));

        List<Integer> instanceIds = Collections.synchronizedList(new ArrayList<>());

        Runnable worker = () -> {
            DoubleCheckedLockingSingleton instance = DoubleCheckedLockingSingleton.getInstance();
            String threadName = Thread.currentThread().getName();

            synchronized (instanceIds) {
                instanceIds.add(System.identityHashCode(instance));
            }

            System.out.println("  Thread " + threadName + ": Got instance " +
                             System.identityHashCode(instance));
        };

        System.out.println("\n1. Creating 10 threads to access singleton simultaneously:");
        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            Thread thread = new Thread(worker, "Worker-" + (i + 1));
            threads.add(thread);
        }

        // Start all threads at roughly the same time
        for (Thread thread : threads) {
            thread.start();
        }

        // Wait for all threads to complete
        for (Thread thread : threads) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        System.out.println("\n2. Analysis:");
        Set<Integer> uniqueIds = new HashSet<>(instanceIds);
        System.out.println("   Total threads: " + threads.size());
        System.out.println("   Total instance IDs collected: " + instanceIds.size());
        System.out.println("   Unique instance IDs: " + uniqueIds.size());
        System.out.println("   All same instance: " + (uniqueIds.size() == 1));

        DoubleCheckedLockingSingleton instance = DoubleCheckedLockingSingleton.getInstance();
        System.out.println("\n3. Instance details:");
        System.out.println("   Created by: " + instance.getCreatedByThread());
        System.out.println("   Access count: " + instance.getAccessCount());
    }

    public static void testLoggerSingleton() {
        System.out.println("\n" + "=".repeat(70));
        System.out.println("LOGGER SINGLETON TEST");
        System.out.println("=".repeat(70));

        Runnable logWorker = () -> {
            Logger logger = Logger.getInstance();
            int workerId = Integer.parseInt(Thread.currentThread().getName().split("-")[1]);
            for (int i = 0; i < 3; i++) {
                logger.log("INFO", "Message " + (i + 1) + " from worker " + workerId);
                try {
                    Thread.sleep(10);  // Small delay to simulate work
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        };

        System.out.println("\n1. Creating 5 threads to log concurrently:");
        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < 5; i++) {
            Thread thread = new Thread(logWorker, "Logger-" + (i + 1));
            threads.add(thread);
            thread.start();
        }

        // Wait for all logging to complete
        for (Thread thread : threads) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        Logger logger = Logger.getInstance();
        System.out.println("\n2. Total log entries: " + logger.getLogs().size());
        System.out.println("   Expected: " + (5 * 3) + " (5 threads * 3 messages each)");
    }

    public static void comparePerformance() {
        System.out.println("\n" + "=".repeat(70));
        System.out.println("PERFORMANCE COMPARISON");
        System.out.println("=".repeat(70));

        int iterations = 100000;

        // Test simple locking
        System.out.println("\n1. Testing simple locking singleton:");
        long start = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            ThreadSafeSingleton.getInstance();
        }
        long simpleLockTime = System.nanoTime() - start;
        System.out.printf("   Time for %d accesses: %.4fs%n",
                         iterations, simpleLockTime / 1_000_000_000.0);

        // Test double-checked locking
        System.out.println("\n2. Testing double-checked locking singleton:");
        start = System.nanoTime();
        for (int i = 0; i < iterations; i++) {
            DoubleCheckedLockingSingleton.getInstance();
        }
        long doubleCheckTime = System.nanoTime() - start;
        System.out.printf("   Time for %d accesses: %.4fs%n",
                         iterations, doubleCheckTime / 1_000_000_000.0);

        System.out.println("\n3. Performance difference:");
        double speedup = (double) simpleLockTime / doubleCheckTime;
        System.out.printf("   Double-checked locking is %.2fx faster%n", speedup);
        System.out.println("   (Lock acquired only once vs. every access)");
    }

    public static void main(String[] args) {
        testThreadSafety();
        testLoggerSingleton();
        comparePerformance();

        System.out.println("\n" + "=".repeat(70));
        System.out.println("KEY POINTS");
        System.out.println("=".repeat(70));
        System.out.println("""

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

4. Java Specific:
   - Use 'volatile' keyword for double-checked locking
   - Consider Bill Pugh Singleton (static inner class) as alternative
   - Use enum for most robust singleton (prevents reflection attacks)
        """);
    }
}
