# Dry Run: Vehicle Inheritance

This trace shows how inheritance enables code reuse and method overriding through a vehicle hierarchy.

## Class Hierarchy

```
Vehicle (base)
    |
    |-- Car
    |      |
    |      |-- ElectricCar
    |
    |-- Motorcycle
```

---

## Operation 1: Creating a Car Instance

```python
car = Car("Toyota", "Camry", 2023, 4)
```

### Execution Steps

**Step 1**: `Car.__init__()` is called

**Step 2**: Calls `super().__init__(brand, model, year)`
- This calls `Vehicle.__init__("Toyota", "Camry", 2023)`

**Step 3**: Vehicle constructor executes
- Sets `self.brand = "Toyota"`
- Sets `self.model = "Camry"`
- Sets `self.year = 2023`
- Sets `self.is_running = False`

**Step 4**: Control returns to Car constructor
- Sets `self.num_doors = 4`
- Sets `self.trunk_open = False`

### Memory State

```
car (instance of Car, which IS-A Vehicle)
├── brand: "Toyota"          ← From Vehicle
├── model: "Camry"           ← From Vehicle
├── year: 2023               ← From Vehicle
├── is_running: False        ← From Vehicle
├── num_doors: 4             ← From Car
└── trunk_open: False        ← From Car
```

---

## Operation 2: Calling Inherited Method

```python
car.start()
```

### Execution Steps

**Step 1**: Python looks for `start()` method in Car class
- Not found in Car

**Step 2**: Python looks in parent class Vehicle
- Found in Vehicle

**Step 3**: Executes `Vehicle.start(self)`
- Checks: `if not self.is_running` → True
- Sets: `self.is_running = True`
- Returns: "Toyota Camry started"

### Memory State After Operation

```
car
├── brand: "Toyota"
├── model: "Camry"
├── year: 2023
├── is_running: True         ← Changed by inherited method
├── num_doors: 4
└── trunk_open: False
```

**Key Point**: Car inherits `start()` from Vehicle without needing to reimplement it.

---

## Operation 3: Calling Car-Specific Method

```python
car.open_trunk()
```

### Execution Steps

**Step 1**: Python looks for `open_trunk()` in Car class
- Found in Car (not in Vehicle)

**Step 2**: Executes `Car.open_trunk(self)`
- Checks: `if not self.trunk_open` → True
- Sets: `self.trunk_open = True`
- Returns: "Trunk opened"

### Memory State After Operation

```
car
├── brand: "Toyota"
├── model: "Camry"
├── year: 2023
├── is_running: True
├── num_doors: 4
└── trunk_open: True         ← Changed
```

---

## Operation 4: Method Overriding

```python
info = car.get_info()
```

### Execution Steps

**Step 1**: Python looks for `get_info()` in Car class
- Found (Car overrides Vehicle's version)

**Step 2**: Executes `Car.get_info(self)`

**Step 3**: Inside Car.get_info(), calls `super().get_info()`
- This calls `Vehicle.get_info(self)`
- Returns: "2023 Toyota Camry"

**Step 4**: Car.get_info() continues
- Takes parent result: "2023 Toyota Camry"
- Adds car-specific info: `f"{base_info} - {self.num_doors} doors"`
- Returns: "2023 Toyota Camry - 4 doors"

### Method Resolution Path

```
car.get_info()
    → Car.get_info()
        → super().get_info()
            → Vehicle.get_info()
                returns "2023 Toyota Camry"
        → add " - 4 doors"
        returns "2023 Toyota Camry - 4 doors"
```

---

## Operation 5: Multi-Level Inheritance

```python
tesla = ElectricCar("Tesla", "Model 3", 2023, 4, 75)
```

### Execution Steps

**Step 1**: `ElectricCar.__init__()` is called

**Step 2**: Calls `super().__init__(brand, model, year, num_doors)`
- This calls `Car.__init__("Tesla", "Model 3", 2023, 4)`

**Step 3**: `Car.__init__()` executes
- Calls `super().__init__("Tesla", "Model 3", 2023)`
- This calls `Vehicle.__init__("Tesla", "Model 3", 2023)`

**Step 4**: `Vehicle.__init__()` executes
- Sets brand, model, year, is_running

**Step 5**: Control returns to `Car.__init__()`
- Sets num_doors, trunk_open

**Step 6**: Control returns to `ElectricCar.__init__()`
- Sets battery_capacity = 75
- Sets charge_level = 100

### Memory State

```
tesla (instance of ElectricCar → Car → Vehicle)
├── brand: "Tesla"               ← From Vehicle
├── model: "Model 3"             ← From Vehicle
├── year: 2023                   ← From Vehicle
├── is_running: False            ← From Vehicle
├── num_doors: 4                 ← From Car
├── trunk_open: False            ← From Car
├── battery_capacity: 75         ← From ElectricCar
└── charge_level: 100            ← From ElectricCar
```

**Constructor Chain**: ElectricCar → Car → Vehicle (going up)
**Initialization Order**: Vehicle → Car → ElectricCar (coming down)

---

## Operation 6: Overriding in Multi-Level Hierarchy

```python
tesla.start()
```

### Execution Steps

**Step 1**: Python looks for `start()` in ElectricCar
- Found (ElectricCar overrides it)

**Step 2**: Executes `ElectricCar.start(self)`
- Checks: `if self.charge_level < 10` → `100 < 10` → False
- Checks: `if not self.is_running` → True
- Sets: `self.is_running = True`
- Returns: "Tesla Model 3 powered on (silent, battery at 100%)"

### Memory State

```
tesla
├── brand: "Tesla"
├── model: "Model 3"
├── year: 2023
├── is_running: True             ← Changed
├── num_doors: 4
├── trunk_open: False
├── battery_capacity: 75
└── charge_level: 100
```

**Method Resolution**: ElectricCar.start() is called directly
- Does NOT call Vehicle.start() (complete override, no super() call)
- Different behavior for electric vehicles

---

## Operation 7: Calling get_info() on ElectricCar

```python
tesla.get_info()
```

### Execution Steps

**Step 1**: Look for `get_info()` in ElectricCar
- Found

**Step 2**: Execute `ElectricCar.get_info()`
- Calls `super().get_info()`

**Step 3**: This calls `Car.get_info()`
- Which calls `super().get_info()`

**Step 4**: This calls `Vehicle.get_info()`
- Returns: "2023 Tesla Model 3"

**Step 5**: Back to `Car.get_info()`
- Appends: " - 4 doors"
- Returns: "2023 Tesla Model 3 - 4 doors"

**Step 6**: Back to `ElectricCar.get_info()`
- Appends: " - 75kWh battery at 100%"
- Returns: "2023 Tesla Model 3 - 4 doors - 75kWh battery at 100%"

### Method Resolution Chain

```
tesla.get_info()
    → ElectricCar.get_info()
        → super().get_info()
            → Car.get_info()
                → super().get_info()
                    → Vehicle.get_info()
                        returns "2023 Tesla Model 3"
                returns "2023 Tesla Model 3 - 4 doors"
        returns "2023 Tesla Model 3 - 4 doors - 75kWh battery at 100%"
```

---

## Operation 8: Polymorphism in Action

```python
vehicles = [car, motorcycle, tesla]
for vehicle in vehicles:
    vehicle.stop()
```

### Execution for Each Vehicle

**For car (Car instance)**:
- Looks for `stop()` → not in Car → found in Vehicle
- Calls `Vehicle.stop()`

**For motorcycle (Motorcycle instance)**:
- Looks for `stop()` → not in Motorcycle → found in Vehicle
- Calls `Vehicle.stop()`

**For tesla (ElectricCar instance)**:
- Looks for `stop()` → not in ElectricCar → not in Car → found in Vehicle
- Calls `Vehicle.stop()`

**Result**: All three call the same `Vehicle.stop()` method

### This Demonstrates

1. **Code Reuse**: `stop()` implemented once in Vehicle, used by all
2. **Polymorphism**: Different types treated uniformly through common interface
3. **Inheritance Chain**: Python walks up the hierarchy to find methods

---

## Key Observations

1. **Constructor Chaining**: Child calls parent constructor with `super().__init__()`
2. **Method Resolution**: Python searches class → parent → grandparent
3. **Method Overriding**: Child can replace parent's method
4. **Extending with super()**: Child can call parent method and add to it
5. **Code Reuse**: Common code in parent, specific code in children
6. **Polymorphism**: All vehicles can be treated as Vehicle type
7. **Multi-Level**: ElectricCar inherits from Car which inherits from Vehicle

This demonstrates how inheritance creates hierarchical relationships while enabling code reuse and polymorphic behavior.
