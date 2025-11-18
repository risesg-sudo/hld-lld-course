/**
 * Basic Singleton Implementation
 *
 * This file demonstrates a simple singleton pattern using Java.
 * Shows both eager and lazy initialization approaches.
 */

import java.util.HashMap;
import java.util.Map;

/**
 * Simple singleton for database connection management.
 *
 * Uses lazy initialization - instance created only when first requested.
 * Not thread-safe - suitable for single-threaded applications only.
 */
class DatabaseConnection {
    private static DatabaseConnection instance = null;

    // Connection details
    private String host;
    private int port;
    private String database;
    private boolean connected;
    private int connectionCount;

    /**
     * Private constructor - prevents external instantiation.
     */
    private DatabaseConnection() {
        this.host = "localhost";
        this.port = 5432;
        this.database = "myapp_db";
        this.connected = false;
        this.connectionCount = 0;
    }

    /**
     * Get the singleton instance.
     *
     * @return The singleton instance
     */
    public static DatabaseConnection getInstance() {
        if (instance == null) {
            instance = new DatabaseConnection();
            System.out.println("Created new DatabaseConnection instance: " +
                             System.identityHashCode(instance));
        }
        return instance;
    }

    /**
     * Simulate connecting to database.
     */
    public void connect() {
        if (!connected) {
            connected = true;
            connectionCount++;
            System.out.println("Connected to " + host + ":" + port + "/" + database);
        } else {
            System.out.println("Already connected");
        }
    }

    /**
     * Simulate disconnecting from database.
     */
    public void disconnect() {
        if (connected) {
            connected = false;
            System.out.println("Disconnected from database");
        }
    }

    /**
     * Execute a database query.
     */
    public String executeQuery(String query) {
        if (!connected) {
            throw new RuntimeException("Not connected to database");
        }
        System.out.println("Executing query: " + query);
        return "Result of: " + query;
    }

    public boolean isConnected() {
        return connected;
    }

    public int getConnectionCount() {
        return connectionCount;
    }
}


/**
 * Singleton configuration manager with eager initialization.
 *
 * Instance created immediately when class loads.
 * Thread-safe by default (Java class loading is thread-safe).
 */
class ConfigurationManager {
    // Eager initialization - instance created immediately
    private static ConfigurationManager instance = null;

    private Map<String, String> config;

    /**
     * Private constructor.
     */
    private ConfigurationManager() {
        // Load configuration
        config = new HashMap<>();
        config.put("app_name", "MyApplication");
        config.put("version", "1.0.0");
        config.put("debug", "true");
        config.put("max_connections", "100");
        config.put("timeout", "30");
        System.out.println("Configuration loaded");
    }

    /**
     * Get the singleton instance.
     */
    public static ConfigurationManager getInstance() {
        if (instance == null) {
            instance = new ConfigurationManager();
        }
        return instance;
    }

    /**
     * Get configuration value.
     */
    public String get(String key) {
        return config.getOrDefault(key, null);
    }

    /**
     * Get configuration value with default.
     */
    public String get(String key, String defaultValue) {
        return config.getOrDefault(key, defaultValue);
    }

    /**
     * Set configuration value.
     */
    public void set(String key, String value) {
        config.put(key, value);
        System.out.println("Config updated: " + key + " = " + value);
    }
}


/**
 * Demonstration class for basic singleton patterns.
 */
public class basic_example {

    public static void demonstrateBasicSingleton() {
        System.out.println("=".repeat(70));
        System.out.println("BASIC SINGLETON DEMONSTRATION");
        System.out.println("=".repeat(70));

        System.out.println("\n1. Getting first database connection instance:");
        DatabaseConnection db1 = DatabaseConnection.getInstance();
        System.out.println("   Instance ID: " + System.identityHashCode(db1));

        System.out.println("\n2. Getting second database connection instance:");
        DatabaseConnection db2 = DatabaseConnection.getInstance();
        System.out.println("   Instance ID: " + System.identityHashCode(db2));

        System.out.println("\n3. Checking if instances are identical:");
        System.out.println("   db1 == db2: " + (db1 == db2));
        System.out.println("   Same memory address: " +
                         (System.identityHashCode(db1) == System.identityHashCode(db2)));

        System.out.println("\n4. Connecting via first instance:");
        db1.connect();

        System.out.println("\n5. Checking connection status via second instance:");
        System.out.println("   db2.isConnected(): " + db2.isConnected());
        System.out.println("   (State is shared because it's the same instance!)");

        System.out.println("\n6. Cannot create instance directly (prevented by private constructor)");
        System.out.println("   Uncommenting 'DatabaseConnection db3 = new DatabaseConnection();' would cause compilation error");
        // DatabaseConnection db3 = new DatabaseConnection();  // Compilation error
    }

    public static void demonstrateConfigurationSingleton() {
        System.out.println("\n" + "=".repeat(70));
        System.out.println("CONFIGURATION SINGLETON DEMONSTRATION");
        System.out.println("=".repeat(70));

        System.out.println("\n1. Getting first config instance:");
        ConfigurationManager config1 = ConfigurationManager.getInstance();
        System.out.println("   App Name: " + config1.get("app_name"));
        System.out.println("   Instance ID: " + System.identityHashCode(config1));

        System.out.println("\n2. Modifying config via first instance:");
        config1.set("debug", "false");

        System.out.println("\n3. Getting second config instance:");
        ConfigurationManager config2 = ConfigurationManager.getInstance();
        System.out.println("   Instance ID: " + System.identityHashCode(config2));
        System.out.println("   Debug mode: " + config2.get("debug"));
        System.out.println("   (Change visible through second reference!)");

        System.out.println("\n4. Verifying instances are identical:");
        System.out.println("   config1 == config2: " + (config1 == config2));
    }

    public static void main(String[] args) {
        demonstrateBasicSingleton();
        demonstrateConfigurationSingleton();

        System.out.println("\n" + "=".repeat(70));
        System.out.println("KEY POINTS");
        System.out.println("=".repeat(70));
        System.out.println("""

1. Only one instance exists for the entire application
2. All references point to the same object in memory
3. State changes are visible through all references
4. Direct instantiation is prevented (raises error)
5. Access controlled through getInstance() static method
        """);
    }
}
