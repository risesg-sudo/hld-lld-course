/**
 * Thread-Safe Singleton Implementation
 *
 * This file demonstrates thread-safe singleton patterns for multi-threaded environments.
 * Shows both simple locking and double-checked locking approaches.
 */

#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <chrono>
#include <atomic>
#include <iomanip>
#include <sstream>
#include <algorithm>

/**
 * Thread-safe singleton using simple locking.
 *
 * Every call to getInstance() acquires a lock, which ensures thread safety
 * but introduces overhead even after instance is created.
 */
class ThreadSafeSingleton {
private:
    static ThreadSafeSingleton* instance;
    static std::mutex mutex_;

    std::string createdByThread;
    std::chrono::system_clock::time_point creationTime;
    std::atomic<int> accessCount;

    // Private constructor
    ThreadSafeSingleton()
        : accessCount(0) {
        std::stringstream ss;
        ss << std::this_thread::get_id();
        createdByThread = ss.str();
        creationTime = std::chrono::system_clock::now();
        std::cout << "Instance created by thread: " << createdByThread << std::endl;
    }

public:
    // Delete copy and move operations
    ThreadSafeSingleton(const ThreadSafeSingleton&) = delete;
    ThreadSafeSingleton& operator=(const ThreadSafeSingleton&) = delete;
    ThreadSafeSingleton(ThreadSafeSingleton&&) = delete;
    ThreadSafeSingleton& operator=(ThreadSafeSingleton&&) = delete;

    /**
     * Get singleton instance with thread safety.
     * Uses lock for every access - simple but has performance overhead.
     */
    static ThreadSafeSingleton& getInstance() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (instance == nullptr) {
            instance = new ThreadSafeSingleton();
        }
        instance->accessCount++;
        return *instance;
    }

    std::string getCreatedByThread() const { return createdByThread; }
    int getAccessCount() const { return accessCount.load(); }
};

// Static member initialization
ThreadSafeSingleton* ThreadSafeSingleton::instance = nullptr;
std::mutex ThreadSafeSingleton::mutex_;


/**
 * Thread-safe singleton using double-checked locking.
 *
 * Optimizes performance by checking instance existence before acquiring lock.
 * Lock acquired only during initial creation, not for subsequent access.
 */
class DoubleCheckedLockingSingleton {
private:
    static std::atomic<DoubleCheckedLockingSingleton*> instance;
    static std::mutex mutex_;

    std::string createdByThread;
    std::chrono::system_clock::time_point creationTime;
    std::atomic<int> accessCount;

    // Private constructor
    DoubleCheckedLockingSingleton()
        : accessCount(0) {
        std::stringstream ss;
        ss << std::this_thread::get_id();
        createdByThread = ss.str();
        creationTime = std::chrono::system_clock::now();
        std::cout << "Instance created by thread: " << createdByThread << std::endl;
    }

public:
    // Delete copy and move operations
    DoubleCheckedLockingSingleton(const DoubleCheckedLockingSingleton&) = delete;
    DoubleCheckedLockingSingleton& operator=(const DoubleCheckedLockingSingleton&) = delete;
    DoubleCheckedLockingSingleton(DoubleCheckedLockingSingleton&&) = delete;
    DoubleCheckedLockingSingleton& operator=(DoubleCheckedLockingSingleton&&) = delete;

    /**
     * Get singleton instance with optimized thread safety.
     *
     * Double-checked locking pattern:
     * 1. First check (without lock) - fast path for already-created instance
     * 2. Acquire lock only if instance doesn't exist
     * 3. Second check (with lock) - ensure another thread didn't create it
     * 4. Create instance if still nullptr
     */
    static DoubleCheckedLockingSingleton& getInstance() {
        DoubleCheckedLockingSingleton* tmp = instance.load(std::memory_order_acquire);

        // First check (without lock)
        if (tmp == nullptr) {
            std::lock_guard<std::mutex> lock(mutex_);
            tmp = instance.load(std::memory_order_relaxed);

            // Second check (with lock)
            if (tmp == nullptr) {
                tmp = new DoubleCheckedLockingSingleton();
                instance.store(tmp, std::memory_order_release);
            }
        }

        tmp->accessCount++;
        return *tmp;
    }

    std::string getCreatedByThread() const { return createdByThread; }
    int getAccessCount() const { return accessCount.load(); }
};

// Static member initialization
std::atomic<DoubleCheckedLockingSingleton*> DoubleCheckedLockingSingleton::instance{nullptr};
std::mutex DoubleCheckedLockingSingleton::mutex_;


/**
 * Practical example: Thread-safe logger singleton.
 *
 * Demonstrates a real-world use case with actual logging functionality.
 */
class Logger {
private:
    static std::atomic<Logger*> instance;
    static std::mutex instanceMutex_;

    std::vector<std::string> logEntries;
    std::mutex logMutex_;

    // Private constructor
    Logger() {
        std::cout << "Logger initialized" << std::endl;
    }

public:
    // Delete copy and move operations
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
    Logger(Logger&&) = delete;
    Logger& operator=(Logger&&) = delete;

    /**
     * Get logger instance (double-checked locking).
     */
    static Logger& getInstance() {
        Logger* tmp = instance.load(std::memory_order_acquire);

        if (tmp == nullptr) {
            std::lock_guard<std::mutex> lock(instanceMutex_);
            tmp = instance.load(std::memory_order_relaxed);

            if (tmp == nullptr) {
                tmp = new Logger();
                instance.store(tmp, std::memory_order_release);
            }
        }

        return *tmp;
    }

    /**
     * Thread-safe logging method.
     *
     * Uses separate lock for log operations to allow concurrent
     * instance access and logging.
     */
    void log(const std::string& level, const std::string& message) {
        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);

        std::stringstream ss;
        ss << std::this_thread::get_id();

        std::stringstream logEntry;
        logEntry << "[" << std::put_time(std::localtime(&time), "%Y-%m-%d %H:%M:%S")
                 << "] [Thread-" << ss.str() << "] "
                 << level << ": " << message;

        std::lock_guard<std::mutex> lock(logMutex_);
        logEntries.push_back(logEntry.str());
        std::cout << logEntry.str() << std::endl;
    }

    /**
     * Get all log entries (thread-safe).
     */
    std::vector<std::string> getLogs() const {
        std::lock_guard<std::mutex> lock(logMutex_);
        return logEntries;
    }
};

// Static member initialization
std::atomic<Logger*> Logger::instance{nullptr};
std::mutex Logger::instanceMutex_;


void testThreadSafety() {
    std::cout << std::string(70, '=') << std::endl;
    std::cout << "THREAD SAFETY TEST" << std::endl;
    std::cout << std::string(70, '=') << std::endl;

    std::vector<void*> instanceIds;
    std::mutex idsMutex;

    auto worker = [&instanceIds, &idsMutex]() {
        DoubleCheckedLockingSingleton& instance = DoubleCheckedLockingSingleton::getInstance();

        std::stringstream ss;
        ss << std::this_thread::get_id();

        {
            std::lock_guard<std::mutex> lock(idsMutex);
            instanceIds.push_back(&instance);
        }

        std::cout << "  Thread " << ss.str() << ": Got instance "
                  << &instance << std::endl;
    };

    std::cout << "\n1. Creating 10 threads to access singleton simultaneously:" << std::endl;
    std::vector<std::thread> threads;
    for (int i = 0; i < 10; i++) {
        threads.emplace_back(worker);
    }

    // Wait for all threads to complete
    for (auto& thread : threads) {
        thread.join();
    }

    std::cout << "\n2. Analysis:" << std::endl;
    std::cout << "   Total threads: " << threads.size() << std::endl;
    std::cout << "   Total instance IDs collected: " << instanceIds.size() << std::endl;

    // Count unique IDs
    std::sort(instanceIds.begin(), instanceIds.end());
    auto last = std::unique(instanceIds.begin(), instanceIds.end());
    size_t uniqueCount = std::distance(instanceIds.begin(), last);

    std::cout << "   Unique instance IDs: " << uniqueCount << std::endl;
    std::cout << "   All same instance: " << (uniqueCount == 1 ? "true" : "false") << std::endl;

    DoubleCheckedLockingSingleton& instance = DoubleCheckedLockingSingleton::getInstance();
    std::cout << "\n3. Instance details:" << std::endl;
    std::cout << "   Created by: Thread-" << instance.getCreatedByThread() << std::endl;
    std::cout << "   Access count: " << instance.getAccessCount() << std::endl;
}


void testLoggerSingleton() {
    std::cout << "\n" << std::string(70, '=') << std::endl;
    std::cout << "LOGGER SINGLETON TEST" << std::endl;
    std::cout << std::string(70, '=') << std::endl;

    auto logWorker = [](int workerId) {
        Logger& logger = Logger::getInstance();
        for (int i = 0; i < 3; i++) {
            logger.log("INFO", "Message " + std::to_string(i + 1) +
                              " from worker " + std::to_string(workerId));
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    };

    std::cout << "\n1. Creating 5 threads to log concurrently:" << std::endl;
    std::vector<std::thread> threads;
    for (int i = 0; i < 5; i++) {
        threads.emplace_back(logWorker, i + 1);
    }

    // Wait for all logging to complete
    for (auto& thread : threads) {
        thread.join();
    }

    Logger& logger = Logger::getInstance();
    std::cout << "\n2. Total log entries: " << logger.getLogs().size() << std::endl;
    std::cout << "   Expected: " << (5 * 3) << " (5 threads * 3 messages each)" << std::endl;
}


void comparePerformance() {
    std::cout << "\n" << std::string(70, '=') << std::endl;
    std::cout << "PERFORMANCE COMPARISON" << std::endl;
    std::cout << std::string(70, '=') << std::endl;

    const int iterations = 100000;

    // Test simple locking
    std::cout << "\n1. Testing simple locking singleton:" << std::endl;
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iterations; i++) {
        ThreadSafeSingleton::getInstance();
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto simpleLockTime = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    std::cout << "   Time for " << iterations << " accesses: "
              << simpleLockTime.count() / 1000.0 << "ms" << std::endl;

    // Test double-checked locking
    std::cout << "\n2. Testing double-checked locking singleton:" << std::endl;
    start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iterations; i++) {
        DoubleCheckedLockingSingleton::getInstance();
    }
    end = std::chrono::high_resolution_clock::now();
    auto doubleCheckTime = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    std::cout << "   Time for " << iterations << " accesses: "
              << doubleCheckTime.count() / 1000.0 << "ms" << std::endl;

    std::cout << "\n3. Performance difference:" << std::endl;
    double speedup = static_cast<double>(simpleLockTime.count()) / doubleCheckTime.count();
    std::cout << "   Double-checked locking is " << std::fixed << std::setprecision(2)
              << speedup << "x faster" << std::endl;
    std::cout << "   (Lock acquired only once vs. every access)" << std::endl;
}


int main() {
    testThreadSafety();
    testLoggerSingleton();
    comparePerformance();

    std::cout << "\n" << std::string(70, '=') << std::endl;
    std::cout << "KEY POINTS" << std::endl;
    std::cout << std::string(70, '=') << std::endl;
    std::cout << R"(
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

4. C++ Specific:
   - Meyer's Singleton (static local) is thread-safe in C++11+
   - Use std::atomic for double-checked locking
   - std::lock_guard provides RAII lock management
    )" << std::endl;

    return 0;
}
