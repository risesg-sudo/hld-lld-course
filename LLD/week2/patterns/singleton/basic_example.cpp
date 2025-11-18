/**
 * Basic Singleton Implementation
 *
 * This file demonstrates a simple singleton pattern using C++.
 * Shows both eager and lazy initialization approaches.
 * Uses Meyer's Singleton (C++11 guarantees thread-safe static local initialization).
 */

#include <iostream>
#include <string>
#include <unordered_map>
#include <stdexcept>
#include <memory>

/**
 * Simple singleton for database connection management.
 *
 * Uses lazy initialization - instance created only when first requested.
 * Thread-safe by default (C++11+ guarantees thread-safe static local initialization).
 */
class DatabaseConnection {
private:
    // Connection details
    std::string host;
    int port;
    std::string database;
    bool connected;
    int connectionCount;

    // Private constructor - prevents external instantiation
    DatabaseConnection()
        : host("localhost")
        , port(5432)
        , database("myapp_db")
        , connected(false)
        , connectionCount(0) {
    }

public:
    // Delete copy constructor and assignment operator
    DatabaseConnection(const DatabaseConnection&) = delete;
    DatabaseConnection& operator=(const DatabaseConnection&) = delete;

    // Delete move constructor and assignment operator
    DatabaseConnection(DatabaseConnection&&) = delete;
    DatabaseConnection& operator=(DatabaseConnection&&) = delete;

    /**
     * Get the singleton instance.
     * Meyer's Singleton: thread-safe lazy initialization.
     *
     * @return Reference to the singleton instance
     */
    static DatabaseConnection& getInstance() {
        static DatabaseConnection instance;
        static bool firstCall = true;

        if (firstCall) {
            std::cout << "Created new DatabaseConnection instance: "
                      << &instance << std::endl;
            firstCall = false;
        }

        return instance;
    }

    /**
     * Simulate connecting to database.
     */
    void connect() {
        if (!connected) {
            connected = true;
            connectionCount++;
            std::cout << "Connected to " << host << ":" << port
                      << "/" << database << std::endl;
        } else {
            std::cout << "Already connected" << std::endl;
        }
    }

    /**
     * Simulate disconnecting from database.
     */
    void disconnect() {
        if (connected) {
            connected = false;
            std::cout << "Disconnected from database" << std::endl;
        }
    }

    /**
     * Execute a database query.
     */
    std::string executeQuery(const std::string& query) {
        if (!connected) {
            throw std::runtime_error("Not connected to database");
        }
        std::cout << "Executing query: " << query << std::endl;
        return "Result of: " + query;
    }

    bool isConnected() const { return connected; }
    int getConnectionCount() const { return connectionCount; }
};


/**
 * Singleton configuration manager with eager initialization.
 *
 * Instance created immediately when first accessed.
 * Thread-safe by default (C++11+ guarantees thread-safe static local initialization).
 */
class ConfigurationManager {
private:
    std::unordered_map<std::string, std::string> config;

    // Private constructor
    ConfigurationManager() {
        // Load configuration
        config["app_name"] = "MyApplication";
        config["version"] = "1.0.0";
        config["debug"] = "true";
        config["max_connections"] = "100";
        config["timeout"] = "30";
        std::cout << "Configuration loaded" << std::endl;
    }

public:
    // Delete copy constructor and assignment operator
    ConfigurationManager(const ConfigurationManager&) = delete;
    ConfigurationManager& operator=(const ConfigurationManager&) = delete;

    // Delete move constructor and assignment operator
    ConfigurationManager(ConfigurationManager&&) = delete;
    ConfigurationManager& operator=(ConfigurationManager&&) = delete;

    /**
     * Get the singleton instance.
     */
    static ConfigurationManager& getInstance() {
        static ConfigurationManager instance;
        return instance;
    }

    /**
     * Get configuration value.
     */
    std::string get(const std::string& key, const std::string& defaultValue = "") const {
        auto it = config.find(key);
        return (it != config.end()) ? it->second : defaultValue;
    }

    /**
     * Set configuration value.
     */
    void set(const std::string& key, const std::string& value) {
        config[key] = value;
        std::cout << "Config updated: " << key << " = " << value << std::endl;
    }
};


void demonstrateBasicSingleton() {
    std::cout << std::string(70, '=') << std::endl;
    std::cout << "BASIC SINGLETON DEMONSTRATION" << std::endl;
    std::cout << std::string(70, '=') << std::endl;

    std::cout << "\n1. Getting first database connection instance:" << std::endl;
    DatabaseConnection& db1 = DatabaseConnection::getInstance();
    std::cout << "   Instance address: " << &db1 << std::endl;

    std::cout << "\n2. Getting second database connection instance:" << std::endl;
    DatabaseConnection& db2 = DatabaseConnection::getInstance();
    std::cout << "   Instance address: " << &db2 << std::endl;

    std::cout << "\n3. Checking if instances are identical:" << std::endl;
    std::cout << "   db1 and db2 same address: " << (&db1 == &db2 ? "true" : "false") << std::endl;
    std::cout << "   Same memory address: " << (&db1 == &db2) << std::endl;

    std::cout << "\n4. Connecting via first instance:" << std::endl;
    db1.connect();

    std::cout << "\n5. Checking connection status via second instance:" << std::endl;
    std::cout << "   db2.isConnected(): " << (db2.isConnected() ? "true" : "false") << std::endl;
    std::cout << "   (State is shared because it's the same instance!)" << std::endl;

    std::cout << "\n6. Cannot create instance directly (prevented by private constructor)" << std::endl;
    std::cout << "   Uncommenting 'DatabaseConnection db3;' would cause compilation error" << std::endl;
    // DatabaseConnection db3;  // Compilation error - constructor is private
}


void demonstrateConfigurationSingleton() {
    std::cout << "\n" << std::string(70, '=') << std::endl;
    std::cout << "CONFIGURATION SINGLETON DEMONSTRATION" << std::endl;
    std::cout << std::string(70, '=') << std::endl;

    std::cout << "\n1. Getting first config instance:" << std::endl;
    ConfigurationManager& config1 = ConfigurationManager::getInstance();
    std::cout << "   App Name: " << config1.get("app_name") << std::endl;
    std::cout << "   Instance address: " << &config1 << std::endl;

    std::cout << "\n2. Modifying config via first instance:" << std::endl;
    config1.set("debug", "false");

    std::cout << "\n3. Getting second config instance:" << std::endl;
    ConfigurationManager& config2 = ConfigurationManager::getInstance();
    std::cout << "   Instance address: " << &config2 << std::endl;
    std::cout << "   Debug mode: " << config2.get("debug") << std::endl;
    std::cout << "   (Change visible through second reference!)" << std::endl;

    std::cout << "\n4. Verifying instances are identical:" << std::endl;
    std::cout << "   config1 and config2 same: " << (&config1 == &config2 ? "true" : "false") << std::endl;
}


int main() {
    demonstrateBasicSingleton();
    demonstrateConfigurationSingleton();

    std::cout << "\n" << std::string(70, '=') << std::endl;
    std::cout << "KEY POINTS" << std::endl;
    std::cout << std::string(70, '=') << std::endl;
    std::cout << R"(
1. Only one instance exists for the entire application
2. All references point to the same object in memory
3. State changes are visible through all references
4. Direct instantiation is prevented (private constructor)
5. Access controlled through getInstance() static method
6. Meyer's Singleton provides thread-safe lazy initialization (C++11+)
    )" << std::endl;

    return 0;
}
