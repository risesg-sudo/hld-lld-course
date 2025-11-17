# Builder Pattern

## The Hook: The Telescoping Constructor Problem

Have you ever seen code like this?

```python
pizza = Pizza("large", "thin", "tomato", ["pepperoni", "mushroom"], "mozzarella", True, False)
```

What does `True` mean? What about `False`? Which parameter is the crust type, and which is the sauce? Now imagine this constructor has 10 parameters, half of them optional. How do you create a pizza with just size and toppings, using default values for everything else?

This is the telescoping constructor problem: as classes gain more parameters, constructors become unwieldy, error-prone, and impossible to remember. The Builder pattern offers an elegant solution.

## The Problem: Complex Object Construction

Complex objects often have:
- Many parameters (5+), some required, most optional
- Validation rules that depend on multiple parameters
- Construction that happens in multiple steps
- Different representations using same construction process

**Traditional Approaches Fall Short:**

**1. Telescoping Constructors:**
```python
Pizza(size)
Pizza(size, crust)
Pizza(size, crust, sauce)
Pizza(size, crust, sauce, toppings)
# ... dozens of combinations
```
Results in: Constructor explosion, confusing parameter order, difficult maintenance.

**2. Setters After Construction:**
```python
pizza = Pizza()
pizza.set_size("large")
pizza.set_crust("thin")
pizza.set_sauce("tomato")
# ... many setter calls
```
Problems: Object partially constructed between calls, not thread-safe, can't create immutable objects.

**3. Parameter Objects:**
```python
pizza = Pizza(PizzaParams(size="large", crust="thin", ...))
```
Better, but: Still need to remember all parameters, no fluent interface, validation awkward.

## The Solution: Separate Construction from Representation

The Builder pattern separates the construction of a complex object from its representation. Instead of forcing all parameters into a constructor, you build the object step-by-step using a dedicated builder class.

**Key Components:**

1. **Product**: The complex object being built (e.g., Pizza)
2. **Builder**: Class that constructs the product step-by-step
3. **Director** (optional): Knows how to use builder to create specific configurations
4. **Fluent Interface**: Method chaining for readable construction

**How It Works:**

```python
pizza = (PizzaBuilder()
         .set_size("large")
         .set_crust("thin")
         .add_topping("pepperoni")
         .add_topping("mushroom")
         .build())
```

Each method:
1. Sets one aspect of the object being built
2. Returns `self` to allow chaining
3. Accumulates configuration in builder's state
4. Final `build()` creates and validates the product

**Why It Works:**

- Self-documenting: Each method name describes what it does
- Flexible: Call only methods you need, skip others
- Safe: Validation happens at build() time
- Readable: Reads like natural language
- Maintainable: Easy to add new optional parameters

## When to Use the Builder Pattern

Consider Builder when:

**Complex Construction Scenarios:**
- Objects with 3+ optional parameters
- Construction requires multiple steps
- Same construction process creates different representations
- Need immutable objects (build once, never change)

**Specific Use Cases:**
- SQL query construction (SELECT, FROM, WHERE, JOIN, ORDER BY)
- HTTP request building (method, URL, headers, body, params)
- UI component configuration (buttons, dialogs, forms)
- Document generation (reports, PDFs, emails)
- Test data creation (complex test fixtures)
- Configuration objects (app settings, database configs)

**Signs You Need Builder:**
- Constructor has 5+ parameters
- You have telescoping constructors
- Parameter order is confusing
- Many parameters have default values
- Object construction requires validation across multiple fields
- You want immutable objects

**When Not to Use Builder:**
- Object has <3 parameters
- Construction is truly simple
- Object is naturally mutable
- Performance is critical and builder overhead matters

## Trade-offs: What You Gain and What You Lose

### What You Gain:

**Readability:**
- Self-documenting code (method names explain purpose)
- Natural language-like construction
- No need to remember parameter order
- Clear what each value represents

**Flexibility:**
- Easy to add new optional parameters
- Call only methods you need
- Different builders can create different representations
- Same construction process, different products

**Immutability:**
- Can build immutable objects step-by-step
- Object created only at build() call
- Safe sharing across threads
- No partial construction states visible

**Validation:**
- Centralized validation at build() time
- Can validate cross-field constraints
- Clear error messages ("missing required field")
- Fail fast with specific validation errors

**Maintainability:**
- New parameters added as new methods
- Doesn't break existing code
- Easy to provide default values
- Builder evolves independently of product

### What You Lose:

**Additional Code:**
- Need separate builder class
- More code to write and maintain
- Each new product field needs builder method
- Can feel like boilerplate for simple objects

**Performance Overhead:**
- Builder object creation cost
- Method call overhead for chaining
- Extra object in memory during construction
- Garbage collection of builder after build()

**Complexity:**
- Simple objects become over-engineered
- Additional indirection
- Team needs to understand pattern
- Overkill for 2-parameter objects

**Runtime Validation:**
- Errors caught at build() time, not compile time
- Can create invalid builders (caught only at build)
- Type safety reduced compared to constructor
- Need explicit validation logic

## Fluent Interface: The Builder's Companion

Builder pattern often pairs with fluent interface (method chaining):

```python
def set_size(self, size):
    self.size = size
    return self  # Enable chaining

def add_topping(self, topping):
    self.toppings.append(topping)
    return self  # Enable chaining
```

Benefits:
- Reads left-to-right like English
- Natural grouping of related calls
- Less visual noise (no variable reuse)
- Prettier code formatting

Trade-off:
- Harder to debug (which method failed?)
- Can't easily inspect intermediate state
- All-or-nothing construction

## Director Pattern: Reusable Construction Recipes

Optional enhancement: Director knows how to use builder for specific configurations:

```python
class PizzaDirector:
    def build_margherita(self, builder):
        return (builder
                .set_size("medium")
                .set_crust("thin")
                .add_topping("basil")
                .add_topping("mozzarella")
                .build())
```

Benefits:
- Encapsulates common construction patterns
- Reusable across codebase
- Hides construction complexity from client
- Easy to create variants

## Implementation Patterns

**1. Method Chaining (Most Common):**
```python
builder.set_x().set_y().build()
```

**2. Separate Set Methods:**
```python
builder.set_x()
builder.set_y()
return builder.build()
```

**3. With Context Manager:**
```python
with PizzaBuilder() as builder:
    builder.set_size("large")
    # ... build() called automatically
```

**4. Validation Strategies:**
- **Eager**: Validate each setter call
- **Lazy**: Validate only at build() time (more common)
- **Progressive**: Some validation per method, full validation at build()

## Common Variations

**Step Builder Pattern:**
Forces specific order of construction using type system:
```python
builder.set_size() -> returns CrustBuilder
.set_crust() -> returns ToppingBuilder
.add_toppings() -> returns FinalBuilder
.build() -> returns Pizza
```

**Mutable vs Immutable Builders:**
- Mutable: Reuse builder for multiple products
- Immutable: New builder for each product (functional style)

**Generic Builders:**
```python
GenericBuilder<T>()
    .set("field", value)
    .build()
```
Flexible but loses type safety.

## Real-World Examples

**StringBuilder (Java/C#):**
```java
String result = new StringBuilder()
    .append("Hello")
    .append(" ")
    .append("World")
    .toString();
```

**SQL Query Builders:**
```python
query = (QueryBuilder()
         .select("name", "email")
         .from_table("users")
         .where("age > 18")
         .limit(10)
         .build())
```

**HTTP Request Builders:**
```python
request = (HttpRequestBuilder()
           .url("https://api.example.com")
           .method("POST")
           .header("Auth", "Bearer token")
           .body(json_data)
           .build())
```

## The Verdict

Builder pattern shines for complex object construction. It transforms confusing constructors into readable, self-documenting code. The pattern is especially valuable when:
- Parameters exceed 3-5
- Many parameters are optional
- Construction order matters
- You need immutable objects

However, it's overkill for simple objects. Don't reach for Builder when a simple constructor or dataclass suffices. The additional code and indirection should pay for itself in readability and maintainability.

Modern languages offer alternatives:
- Python: Dataclasses with defaults, keyword arguments
- Kotlin: Named parameters, default values
- But Builder still wins for: complex validation, step-by-step construction, immutable objects

Use Builder thoughtfully. When you do need it, you'll appreciate how it transforms convoluted construction into elegant, readable code.
