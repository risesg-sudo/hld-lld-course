# Dry Run: Decorator Pattern

## Operation: Build Coffee with Milk and Sugar

```python
coffee = SugarDecorator(MilkDecorator(SimpleCoffee()))
cost = coffee.get_cost()
```

### Step 1: Create SimpleCoffee
```
SimpleCoffee() created at 0x5001
  get_cost() returns: 2.00
  get_description() returns: "Simple Coffee"
```

### Step 2: Wrap in MilkDecorator
```
MilkDecorator created at 0x5002
  _beverage = <SimpleCoffee at 0x5001>

Structure:
  MilkDecorator (0x5002)
    └── SimpleCoffee (0x5001)
```

### Step 3: Wrap in SugarDecorator
```
SugarDecorator created at 0x5003
  _beverage = <MilkDecorator at 0x5002>

Final Structure:
  SugarDecorator (0x5003)
    └── MilkDecorator (0x5002)
        └── SimpleCoffee (0x5001)
```

### Step 4: Call get_cost()

**Call**: `coffee.get_cost()` where `coffee = SugarDecorator`

**Execution Chain**:
```
1. SugarDecorator.get_cost()
   └─> self._beverage.get_cost() + 0.25
       └─> MilkDecorator.get_cost() + 0.25
           └─> self._beverage.get_cost() + 0.50 + 0.25
               └─> SimpleCoffee.get_cost() + 0.50 + 0.25
                   └─> 2.00 + 0.50 + 0.25
                   └─> 2.75
```

**Unwinding**:
```
SimpleCoffee.get_cost() returns 2.00
MilkDecorator adds 0.50 → returns 2.50
SugarDecorator adds 0.25 → returns 2.75
```

**Final Result**: `2.75`

## Key Observations

1. **Layered Wrapping**: Each decorator wraps the previous component
2. **Recursive Delegation**: Each get_cost() calls wrapped component's get_cost()
3. **Behavior Addition**: Each layer adds its own behavior to the result
4. **No Subclass Explosion**: 3 decorators instead of 8 subclasses for all combinations
5. **Runtime Composition**: Build different combinations dynamically

## Comparison: Decorator vs Inheritance

**With Inheritance** (subclass explosion):
- CoffeWithMilk extends Coffee
- CoffeeWithSugar extends Coffee
- CoffeeWithMilkAndSugar extends Coffee
- Result: 3 add-ons = 8 classes (2^3)

**With Decorator**:
- SimpleCoffee base
- MilkDecorator wraps any Beverage
- SugarDecorator wraps any Beverage
- Result: 3 add-ons = 4 classes (1 base + 3 decorators)
