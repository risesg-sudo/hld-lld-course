# Dry Run: Factory Pattern

## Operation: Create Vehicle

```python
vehicle = VehicleFactory.create("car")
```

### Execution Steps

**Step 1**: Call VehicleFactory.create("car")

**Step 2**: Factory checks type
- Matches "car"
- Creates Car() instance

**Step 3**: Returns Car object

**Result**: Client has Car, doesn't know concrete class

### Without Factory (Bad)

```python
if type == "car": v = Car()
elif type == "motorcycle": v = Motorcycle()
# Repeated everywhere!
```

### With Factory (Good)

```python
v = VehicleFactory.create(type)
# Creation logic in one place
```

## Benefits

1. **Centralized**: Creation logic in factory
2. **Flexible**: Add new types easily
3. **Decoupled**: Client doesn't know concrete types
4. **Testable**: Easy to mock factory

Factory pattern simplifies object creation and improves maintainability.
