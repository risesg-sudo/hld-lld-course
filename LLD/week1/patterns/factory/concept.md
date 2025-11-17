# Factory Pattern

## The Hook

You need to create different types of database connections based on configuration. Without a factory:

```python
if db_type == "mysql":
    db = MySQLDatabase(config)
elif db_type == "postgres":
    db = PostgreSQLDatabase(config)
elif db_type == "mongo":
    db = MongoDatabase(config)
# Repeated everywhere you create databases!
```

Factory pattern centralizes this logic.

## The Problem

Object creation logic scattered across codebase:
1. **Duplication**: Creation code repeated everywhere
2. **Hard to Change**: Must update all creation points
3. **Tight Coupling**: Code depends on concrete classes
4. **Difficult to Test**: Hard to inject test objects

## The Solution

Factory Pattern provides an interface for creating objects without specifying their exact classes.

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

Now create databases with:
```python
db = DatabaseFactory.create(db_type, config)
```

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
