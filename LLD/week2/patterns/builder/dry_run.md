# Dry Run: Builder Pattern Execution

This document traces the step-by-step execution of the Builder pattern, showing how a complex object is constructed method by method.

## Scenario: Building a Custom Pizza

**Code:**
```python
pizza = (PizzaBuilder()
         .set_size(PizzaSize.LARGE)
         .set_crust("thin")
         .add_topping("pepperoni")
         .add_topping("mushrooms")
         .set_extra_cheese(True)
         .build())
```

### Initial State

```
No objects exist yet
```

### Execution Steps

**Step 1: Create PizzaBuilder instance**
```
Execution: PizzaBuilder()
Action: Call __init__() constructor

Builder state after __init__:
  _size = PizzaSize.MEDIUM (default)
  _crust = "regular" (default)
  _sauce = "tomato" (default)
  _cheese = "mozzarella" (default)
  _toppings = [] (empty list)
  _extra_cheese = False (default)
  _gluten_free = False (default)

Returns: PizzaBuilder@0x7f8a1c
```

**Step 2: Call set_size(PizzaSize.LARGE)**
```
Object: PizzaBuilder@0x7f8a1c
Method: set_size(PizzaSize.LARGE)
Action: Set self._size = PizzaSize.LARGE
Return: self (PizzaBuilder@0x7f8a1c)

Builder state:
  _size = PizzaSize.LARGE (CHANGED)
  _crust = "regular"
  _sauce = "tomato"
  _cheese = "mozzarella"
  _toppings = []
  _extra_cheese = False
  _gluten_free = False

Note: Returning 'self' enables method chaining
```

**Step 3: Call set_crust("thin")**
```
Object: PizzaBuilder@0x7f8a1c (same object)
Method: set_crust("thin")
Action: Set self._crust = "thin"
Return: self (PizzaBuilder@0x7f8a1c)

Builder state:
  _size = PizzaSize.LARGE
  _crust = "thin" (CHANGED)
  _sauce = "tomato"
  _cheese = "mozzarella"
  _toppings = []
  _extra_cheese = False
  _gluten_free = False
```

**Step 4: Call add_topping("pepperoni")**
```
Object: PizzaBuilder@0x7f8a1c
Method: add_topping("pepperoni")
Action: self._toppings.append("pepperoni")
Return: self (PizzaBuilder@0x7f8a1c)

Builder state:
  _size = PizzaSize.LARGE
  _crust = "thin"
  _sauce = "tomato"
  _cheese = "mozzarella"
  _toppings = ["pepperoni"] (CHANGED)
  _extra_cheese = False
  _gluten_free = False
```

**Step 5: Call add_topping("mushrooms")**
```
Object: PizzaBuilder@0x7f8a1c
Method: add_topping("mushrooms")
Action: self._toppings.append("mushrooms")
Return: self (PizzaBuilder@0x7f8a1c)

Builder state:
  _size = PizzaSize.LARGE
  _crust = "thin"
  _sauce = "tomato"
  _cheese = "mozzarella"
  _toppings = ["pepperoni", "mushrooms"] (CHANGED)
  _extra_cheese = False
  _gluten_free = False
```

**Step 6: Call set_extra_cheese(True)**
```
Object: PizzaBuilder@0x7f8a1c
Method: set_extra_cheese(True)
Action: Set self._extra_cheese = True
Return: self (PizzaBuilder@0x7f8a1c)

Builder state:
  _size = PizzaSize.LARGE
  _crust = "thin"
  _sauce = "tomato"
  _cheese = "mozzarella"
  _toppings = ["pepperoni", "mushrooms"]
  _extra_cheese = True (CHANGED)
  _gluten_free = False

Note: Builder accumulates all configuration
```

**Step 7: Call build()**
```
Object: PizzaBuilder@0x7f8a1c
Method: build()
Action: Create Pizza object from builder state

Step 7a: Call Pizza constructor
  Create Pizza@0x7f9c4d
  Pass all builder's accumulated values:
    size = PizzaSize.LARGE
    crust = "thin"
    sauce = "tomato"
    cheese = "mozzarella"
    toppings = ["pepperoni", "mushrooms"].copy()
    extra_cheese = True
    gluten_free = False

Step 7b: Pizza __init__ runs
  Set all instance variables
  Call _validate() to ensure valid configuration

Step 7c: Validation passes
  Check: toppings not empty? True (has 2 toppings)
  Check: gluten_free constraints? N/A (not gluten free)
  Result: Validation successful

Return: Pizza@0x7f9c4d
```

### Final State After Step 7

```
Memory:

PizzaBuilder@0x7f8a1c (still exists):
  _size = PizzaSize.LARGE
  _crust = "thin"
  _sauce = "tomato"
  _cheese = "mozzarella"
  _toppings = ["pepperoni", "mushrooms"]
  _extra_cheese = True
  _gluten_free = False

Pizza@0x7f9c4d (newly created):
  size = PizzaSize.LARGE
  crust = "thin"
  sauce = "tomato"
  cheese = "mozzarella"
  toppings = ["pepperoni", "mushrooms"]
  extra_cheese = True
  gluten_free = False

Variables:
  pizza = Pizza@0x7f9c4d

Note: Builder used to construct Pizza, then can be discarded
```

## Scenario: Query Builder with Multiple Conditions

**Code:**
```python
query = (QueryBuilder()
         .select("id", "name")
         .from_table("users")
         .where("age > 18")
         .where("status = 'active'")
         .order_by("name", "ASC")
         .build())
```

### Execution Trace

**Step 1: Create QueryBuilder()**
```
Initial state:
  _select_fields = []
  _from_table = None
  _joins = []
  _where_conditions = []
  _group_by_fields = []
  _having_conditions = []
  _order_by_fields = []
  _limit_value = None
  _offset_value = None

Returns: QueryBuilder@0x7f1a2b
```

**Step 2: select("id", "name")**
```
Action: self._select_fields.extend(["id", "name"])

State:
  _select_fields = ["id", "name"] (CHANGED)
  _from_table = None
  _where_conditions = []
  _order_by_fields = []
  (other fields remain empty)

Returns: self
```

**Step 3: from_table("users")**
```
Action: self._from_table = "users"

State:
  _select_fields = ["id", "name"]
  _from_table = "users" (CHANGED)
  _where_conditions = []
  _order_by_fields = []

Returns: self
```

**Step 4: where("age > 18")**
```
Action: self._where_conditions.append("age > 18")

State:
  _select_fields = ["id", "name"]
  _from_table = "users"
  _where_conditions = ["age > 18"] (CHANGED)
  _order_by_fields = []

Returns: self
```

**Step 5: where("status = 'active'")**
```
Action: self._where_conditions.append("status = 'active'")

State:
  _select_fields = ["id", "name"]
  _from_table = "users"
  _where_conditions = ["age > 18", "status = 'active'"] (CHANGED)
  _order_by_fields = []

Note: Multiple where() calls accumulate conditions
Returns: self
```

**Step 6: order_by("name", "ASC")**
```
Action: self._order_by_fields.append("name ASC")

State:
  _select_fields = ["id", "name"]
  _from_table = "users"
  _where_conditions = ["age > 18", "status = 'active'"]
  _order_by_fields = ["name ASC"] (CHANGED)

Returns: self
```

**Step 7: build()**
```
Action: Create SQLQuery object

Step 7a: Create SQLQuery with all accumulated values
  SQLQuery@0x7f3c8e created with:
    select_fields = ["id", "name"].copy()
    from_table = "users"
    joins = [].copy()
    where_conditions = ["age > 18", "status = 'active'"].copy()
    group_by_fields = [].copy()
    having_conditions = [].copy()
    order_by_fields = ["name ASC"].copy()
    limit_value = None
    offset_value = None

Step 7b: SQLQuery.__init__ runs
  Store all parameters
  Call _validate()

Step 7c: Validation
  Check: from_table is not empty? True ("users")
  Check: having without group_by? False (no having)
  Result: Validation successful

Returns: SQLQuery@0x7f3c8e
```

**Step 8: Generate SQL string**
```
When query.to_sql() is called:

Processing:
  1. Start with empty parts list
  2. Add "SELECT id, name" (from select_fields)
  3. Add "FROM users" (from from_table)
  4. Skip joins (empty)
  5. Add "WHERE age > 18 AND status = 'active'" (join where_conditions)
  6. Skip group_by, having (empty)
  7. Add "ORDER BY name ASC" (from order_by_fields)
  8. Skip limit, offset (None)
  9. Join all parts with spaces

Result: "SELECT id, name FROM users WHERE age > 18 AND status = 'active' ORDER BY name ASC"
```

### Final State

```
QueryBuilder@0x7f1a2b (can be discarded or reused):
  _select_fields = ["id", "name"]
  _from_table = "users"
  _where_conditions = ["age > 18", "status = 'active'"]
  _order_by_fields = ["name ASC"]
  (other fields empty)

SQLQuery@0x7f3c8e (the product):
  select_fields = ["id", "name"]
  from_table = "users"
  where_conditions = ["age > 18", "status = 'active'"]
  order_by_fields = ["name ASC"]

query = SQLQuery@0x7f3c8e
```

## Key Insights from Dry Runs

**1. Builder Accumulation Pattern:**
```
Each method call:
  1. Modifies builder's internal state
  2. Returns 'self' for chaining
  3. Accumulates configuration step-by-step
  4. Final build() creates product from accumulated state
```

**2. Method Chaining Mechanics:**
```
builder.method1().method2().method3()
  = ((builder.method1()).method2()).method3()
  = Each method returns same builder instance
  = Enables fluent, readable construction
```

**3. Separation of Concerns:**
```
Builder:
  - Accumulates configuration
  - Provides fluent interface
  - Can be reused/reset

Product:
  - Created from builder state
  - Validated during construction
  - Immutable after creation
```

**4. State Independence:**
```
Builder maintains state during construction
Product copies values from builder (defensive copy)
Builder can be modified after build() without affecting product
```

**5. Validation Timing:**
```
Builder methods: Usually no validation (accumulate freely)
build() method: Validates complete configuration
Product __init__: Final validation checkpoint
Fails fast if configuration invalid
```
