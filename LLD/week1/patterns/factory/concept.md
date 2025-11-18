# Factory Pattern

## The Hook

You need to create different types of database connections based on configuration. Without a factory:

:::multilang:::

```python
if db_type == "mysql":
    db = MySQLDatabase(config)
elif db_type == "postgres":
    db = PostgreSQLDatabase(config)
elif db_type == "mongo":
    db = MongoDatabase(config)
# Repeated everywhere you create databases!
```

```cpp
if (dbType == "mysql") {
    db = std::make_unique<MySQLDatabase>(config);
} else if (dbType == "postgres") {
    db = std::make_unique<PostgreSQLDatabase>(config);
} else if (dbType == "mongo") {
    db = std::make_unique<MongoDatabase>(config);
}
// Repeated everywhere you create databases!
```

```java
if (dbType.equals("mysql")) {
    db = new MySQLDatabase(config);
} else if (dbType.equals("postgres")) {
    db = new PostgreSQLDatabase(config);
} else if (dbType.equals("mongo")) {
    db = new MongoDatabase(config);
}
// Repeated everywhere you create databases!
```

:::

Factory pattern centralizes this logic.

## The Problem

Object creation logic scattered across codebase:
1. **Duplication**: Creation code repeated everywhere
2. **Hard to Change**: Must update all creation points
3. **Tight Coupling**: Code depends on concrete classes
4. **Difficult to Test**: Hard to inject test objects

## The Solution

Factory Pattern provides an interface for creating objects without specifying their exact classes.

:::multilang:::

```python
class DatabaseFactory:
    @staticmethod
    def create(db_type, config):
        if db_type == "mysql":
            return MySQLDatabase(config)
        elif db_type == "postgres":
            return PostgreSQLDatabase(config)
        elif db_type == "mongo":
            return MongoDatabase(config)
```

```cpp
class DatabaseFactory {
public:
    static std::unique_ptr<Database> create(const std::string& dbType, const Config& config) {
        if (dbType == "mysql") {
            return std::make_unique<MySQLDatabase>(config);
        } else if (dbType == "postgres") {
            return std::make_unique<PostgreSQLDatabase>(config);
        } else if (dbType == "mongo") {
            return std::make_unique<MongoDatabase>(config);
        }
        return nullptr;
    }
};
```

```java
class DatabaseFactory {
    public static Database create(String dbType, Config config) {
        if (dbType.equals("mysql")) {
            return new MySQLDatabase(config);
        } else if (dbType.equals("postgres")) {
            return new PostgreSQLDatabase(config);
        } else if (dbType.equals("mongo")) {
            return new MongoDatabase(config);
        }
        return null;
    }
}
```

:::

Now create databases with:

:::multilang:::

```python
db = DatabaseFactory.create(db_type, config)
```

```cpp
auto db = DatabaseFactory::create(dbType, config);
```

```java
Database db = DatabaseFactory.create(dbType, config);
```

:::

## Benefits

1. **Centralized Creation**: Logic in one place
2. **Easy to Extend**: Add new types in factory
3. **Loose Coupling**: Clients don't depend on concrete classes
4. **Testability**: Easy to inject mock objects

## When to Use

- Multiple classes share common interface
- Type to create depends on runtime conditions
- Want to centralize object creation logic

## Key Takeaways

- Factory centralizes object creation
- Decouples creation from usage
- Easy to add new types
- Follows Open/Closed Principle
