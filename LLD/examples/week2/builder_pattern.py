"""
Builder Pattern - Separate object construction from representation.

This module demonstrates various builder implementations:
1. Simple builder for pizza construction
2. Fluent builder with method chaining
3. Complex query builder
4. Director pattern with builders
5. Immutable object construction
6. Parameter validation

Key Learning Points:
- Builder separates complex construction from representation
- Avoids telescoping constructors (multiple overloaded constructors)
- Enables fluent interfaces for readable code
- Supports immutable object creation
- Validates parameters at build time
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


# ============================================================================
# 1. SIMPLE PIZZA BUILDER
# ============================================================================

class Pizza:
    """
    Complex object that benefits from builder pattern.
    """

    class Size(Enum):
        SMALL = 8
        MEDIUM = 10
        LARGE = 12
        EXTRA_LARGE = 14

    def __init__(
        self,
        size: Size,
        crust: str,
        sauce: str,
        toppings: List[str],
        cheese: str,
        extra_cheese: bool,
        gluten_free: bool
    ):
        self.size = size
        self.crust = crust
        self.sauce = sauce
        self.toppings = toppings
        self.cheese = cheese
        self.extra_cheese = extra_cheese
        self.gluten_free = gluten_free
        self._validate()

    def _validate(self):
        """Validate pizza configuration."""
        if not self.toppings:
            raise ValueError("Pizza must have at least one topping")
        if self.size not in Pizza.Size:
            raise ValueError(f"Invalid pizza size: {self.size}")

    def __str__(self):
        return (
            f"Pizza:\n"
            f"  Size: {self.size.name} ({self.size.value} inches)\n"
            f"  Crust: {self.crust}\n"
            f"  Sauce: {self.sauce}\n"
            f"  Cheese: {self.cheese}{' (Extra)' if self.extra_cheese else ''}\n"
            f"  Toppings: {', '.join(self.toppings)}\n"
            f"  Gluten Free: {'Yes' if self.gluten_free else 'No'}"
        )


class PizzaBuilder:
    """
    Builder for constructing Pizza objects.

    Instead of:
        Pizza(Size.LARGE, "thin", "tomato", ["pepperoni"], "mozzarella", True, False)

    You can do:
        Pizza = (PizzaBuilder()
                 .set_size(Pizza.Size.LARGE)
                 .set_crust("thin")
                 .set_sauce("tomato")
                 .add_topping("pepperoni")
                 .add_topping("mushroom")
                 .set_cheese("mozzarella")
                 .set_extra_cheese(True)
                 .build())

    Benefits:
    - Much more readable
    - Self-documenting
    - Easy to add/remove toppings
    - Safe defaults
    """

    def __init__(self):
        self.size = Pizza.Size.MEDIUM
        self.crust = "regular"
        self.sauce = "tomato"
        self.toppings = []
        self.cheese = "mozzarella"
        self.extra_cheese = False
        self.gluten_free = False

    def set_size(self, size: Pizza.Size) -> "PizzaBuilder":
        """Set pizza size."""
        self.size = size
        return self

    def set_crust(self, crust: str) -> "PizzaBuilder":
        """Set crust type."""
        self.crust = crust
        return self

    def set_sauce(self, sauce: str) -> "PizzaBuilder":
        """Set sauce type."""
        self.sauce = sauce
        return self

    def add_topping(self, topping: str) -> "PizzaBuilder":
        """Add a topping."""
        self.toppings.append(topping)
        return self

    def add_toppings(self, *toppings: str) -> "PizzaBuilder":
        """Add multiple toppings."""
        self.toppings.extend(toppings)
        return self

    def set_cheese(self, cheese: str) -> "PizzaBuilder":
        """Set cheese type."""
        self.cheese = cheese
        return self

    def set_extra_cheese(self, extra: bool) -> "PizzaBuilder":
        """Set extra cheese."""
        self.extra_cheese = extra
        return self

    def set_gluten_free(self, gluten_free: bool) -> "PizzaBuilder":
        """Set gluten-free."""
        self.gluten_free = gluten_free
        return self

    def build(self) -> Pizza:
        """Build and return Pizza object."""
        return Pizza(
            size=self.size,
            crust=self.crust,
            sauce=self.sauce,
            toppings=self.toppings.copy(),
            cheese=self.cheese,
            extra_cheese=self.extra_cheese,
            gluten_free=self.gluten_free
        )

    def reset(self) -> "PizzaBuilder":
        """Reset builder to defaults."""
        self.__init__()
        return self


# ============================================================================
# 2. COMPLEX QUERY BUILDER
# ============================================================================

class SQLQuery:
    """Represents a SQL query."""

    def __init__(
        self,
        select: List[str],
        from_table: str,
        where: List[str],
        joins: List[str],
        order_by: List[str],
        limit_value: Optional[int],
        offset_value: Optional[int]
    ):
        self.select = select
        self.from_table = from_table
        self.where = where
        self.joins = joins
        self.order_by = order_by
        self.limit_value = limit_value
        self.offset_value = offset_value

    def __str__(self):
        """Generate SQL string."""
        parts = []

        # SELECT clause
        select_str = ", ".join(self.select) if self.select else "*"
        parts.append(f"SELECT {select_str}")

        # FROM clause
        parts.append(f"FROM {self.from_table}")

        # JOIN clauses
        for join in self.joins:
            parts.append(join)

        # WHERE clause
        if self.where:
            where_str = " AND ".join(self.where)
            parts.append(f"WHERE {where_str}")

        # ORDER BY clause
        if self.order_by:
            order_str = ", ".join(self.order_by)
            parts.append(f"ORDER BY {order_str}")

        # LIMIT and OFFSET
        if self.limit_value is not None:
            parts.append(f"LIMIT {self.limit_value}")
        if self.offset_value is not None:
            parts.append(f"OFFSET {self.offset_value}")

        return " ".join(parts)


class QueryBuilder:
    """
    Builder for constructing complex SQL queries.

    Example:
        query = (QueryBuilder()
                 .select("id", "name", "email")
                 .from_table("users")
                 .where("age > 18")
                 .where("status = 'active'")
                 .left_join("posts ON users.id = posts.user_id")
                 .order_by("name ASC")
                 .limit(10)
                 .build())
    """

    def __init__(self):
        self.select_fields = []
        self.from_table_name = None
        self.where_conditions = []
        self.join_clauses = []
        self.order_by_fields = []
        self.limit_value = None
        self.offset_value = None

    def select(self, *fields: str) -> "QueryBuilder":
        """Add SELECT fields."""
        self.select_fields.extend(fields)
        return self

    def from_table(self, table: str) -> "QueryBuilder":
        """Set FROM table."""
        self.from_table_name = table
        return self

    def where(self, condition: str) -> "QueryBuilder":
        """Add WHERE condition."""
        self.where_conditions.append(condition)
        return self

    def inner_join(self, join_clause: str) -> "QueryBuilder":
        """Add INNER JOIN."""
        self.join_clauses.append(f"INNER JOIN {join_clause}")
        return self

    def left_join(self, join_clause: str) -> "QueryBuilder":
        """Add LEFT JOIN."""
        self.join_clauses.append(f"LEFT JOIN {join_clause}")
        return self

    def right_join(self, join_clause: str) -> "QueryBuilder":
        """Add RIGHT JOIN."""
        self.join_clauses.append(f"RIGHT JOIN {join_clause}")
        return self

    def order_by(self, field: str) -> "QueryBuilder":
        """Add ORDER BY field."""
        self.order_by_fields.append(field)
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """Set LIMIT."""
        self.limit_value = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """Set OFFSET."""
        self.offset_value = offset
        return self

    def build(self) -> SQLQuery:
        """Build and return SQLQuery object."""
        if not self.from_table_name:
            raise ValueError("FROM table is required")

        return SQLQuery(
            select=self.select_fields,
            from_table=self.from_table_name,
            where=self.where_conditions,
            joins=self.join_clauses,
            order_by=self.order_by_fields,
            limit_value=self.limit_value,
            offset_value=self.offset_value
        )

    def reset(self) -> "QueryBuilder":
        """Reset builder."""
        self.__init__()
        return self


# ============================================================================
# 3. HTTP REQUEST BUILDER
# ============================================================================

@dataclass
class HTTPRequest:
    """Represents an HTTP request."""
    method: str
    url: str
    headers: dict
    body: Optional[str] = None
    params: dict = None
    timeout: int = 30

    def __post_init__(self):
        if self.params is None:
            self.params = {}

    def __str__(self):
        result = f"{self.method} {self.url}\n"
        if self.params:
            result += f"Params: {self.params}\n"
        result += "Headers:\n"
        for k, v in self.headers.items():
            result += f"  {k}: {v}\n"
        if self.body:
            result += f"Body: {self.body}\n"
        result += f"Timeout: {self.timeout}s"
        return result


class HTTPRequestBuilder:
    """
    Builder for constructing HTTP requests.

    Example:
        request = (HTTPRequestBuilder()
                   .method("POST")
                   .url("https://api.example.com/users")
                   .add_header("Content-Type", "application/json")
                   .add_header("Authorization", "Bearer token")
                   .body('{"name": "John"}')
                   .timeout(60)
                   .build())
    """

    def __init__(self):
        self.method_val = "GET"
        self.url_val = None
        self.headers_dict = {
            "User-Agent": "HTTPRequestBuilder/1.0",
            "Accept": "application/json"
        }
        self.body_val = None
        self.params_dict = {}
        self.timeout_val = 30

    def method(self, method: str) -> "HTTPRequestBuilder":
        """Set HTTP method."""
        self.method_val = method.upper()
        return self

    def url(self, url: str) -> "HTTPRequestBuilder":
        """Set request URL."""
        self.url_val = url
        return self

    def add_header(self, key: str, value: str) -> "HTTPRequestBuilder":
        """Add a header."""
        self.headers_dict[key] = value
        return self

    def add_param(self, key: str, value: str) -> "HTTPRequestBuilder":
        """Add query parameter."""
        self.params_dict[key] = value
        return self

    def body(self, body: str) -> "HTTPRequestBuilder":
        """Set request body."""
        self.body_val = body
        return self

    def timeout(self, seconds: int) -> "HTTPRequestBuilder":
        """Set request timeout."""
        self.timeout_val = seconds
        return self

    def build(self) -> HTTPRequest:
        """Build and return HTTPRequest object."""
        if not self.url_val:
            raise ValueError("URL is required")

        return HTTPRequest(
            method=self.method_val,
            url=self.url_val,
            headers=self.headers_dict.copy(),
            body=self.body_val,
            params=self.params_dict.copy(),
            timeout=self.timeout_val
        )

    def reset(self) -> "HTTPRequestBuilder":
        """Reset builder."""
        self.__init__()
        return self


# ============================================================================
# 4. DIRECTOR PATTERN WITH BUILDER
# ============================================================================

class PizzaDirector:
    """
    Director class that uses PizzaBuilder to create specific pizza types.

    This separates the construction steps (in director) from the construction
    process (in builder).
    """

    def __init__(self, builder: PizzaBuilder):
        self.builder = builder

    def build_pepperoni(self) -> Pizza:
        """Build a pepperoni pizza."""
        return (self.builder
                .reset()
                .set_size(Pizza.Size.LARGE)
                .set_crust("thin")
                .add_toppings("pepperoni", "mozzarella")
                .set_extra_cheese(True)
                .build())

    def build_vegetarian(self) -> Pizza:
        """Build a vegetarian pizza."""
        return (self.builder
                .reset()
                .set_size(Pizza.Size.MEDIUM)
                .set_crust("thick")
                .add_toppings("mushroom", "bell pepper", "onion", "spinach")
                .set_extra_cheese(True)
                .build())

    def build_hawaiian(self) -> Pizza:
        """Build a hawaiian pizza."""
        return (self.builder
                .reset()
                .set_size(Pizza.Size.LARGE)
                .set_crust("regular")
                .add_toppings("ham", "pineapple", "mozzarella")
                .build())

    def build_vegan(self) -> Pizza:
        """Build a vegan pizza."""
        return (self.builder
                .reset()
                .set_size(Pizza.Size.MEDIUM)
                .set_crust("gluten free")
                .set_cheese("vegan cheese")
                .add_toppings("mushroom", "spinach", "tomato", "olives")
                .set_gluten_free(True)
                .build())


# ============================================================================
# DEMONSTRATION AND TESTING
# ============================================================================

def test_simple_pizza_builder():
    """Test simple pizza builder."""
    print("\n" + "="*70)
    print("TEST 1: SIMPLE PIZZA BUILDER")
    print("="*70)

    # Build a custom pizza
    pizza = (PizzaBuilder()
             .set_size(Pizza.Size.LARGE)
             .set_crust("thin")
             .set_sauce("white")
             .add_topping("chicken")
             .add_topping("mushroom")
             .add_topping("garlic")
             .set_extra_cheese(True)
             .build())

    print(pizza)
    print(f"\nPizza created successfully with {len(pizza.toppings)} toppings")


def test_pizza_with_defaults():
    """Test pizza with default values."""
    print("\n" + "="*70)
    print("TEST 2: PIZZA WITH DEFAULTS")
    print("="*70)

    # Only specify what you need
    pizza = (PizzaBuilder()
             .add_toppings("pepperoni", "olives")
             .build())

    print(pizza)


def test_query_builder():
    """Test SQL query builder."""
    print("\n" + "="*70)
    print("TEST 3: COMPLEX SQL QUERY BUILDER")
    print("="*70)

    query = (QueryBuilder()
             .select("users.id", "users.name", "users.email")
             .select("COUNT(posts.id) as post_count")
             .from_table("users")
             .left_join("posts ON users.id = posts.user_id")
             .where("users.created_at > '2020-01-01'")
             .where("users.status = 'active'")
             .order_by("post_count DESC")
             .order_by("users.name ASC")
             .limit(20)
             .offset(0)
             .build())

    print("Generated SQL Query:")
    print(query)


def test_http_request_builder():
    """Test HTTP request builder."""
    print("\n" + "="*70)
    print("TEST 4: HTTP REQUEST BUILDER")
    print("="*70)

    request = (HTTPRequestBuilder()
               .method("POST")
               .url("https://api.example.com/users")
               .add_header("Content-Type", "application/json")
               .add_header("Authorization", "Bearer token123")
               .add_param("debug", "true")
               .body('{"name": "John", "email": "john@example.com"}')
               .timeout(60)
               .build())

    print("HTTP Request:")
    print(request)


def test_director_pattern():
    """Test director pattern with builders."""
    print("\n" + "="*70)
    print("TEST 5: DIRECTOR PATTERN")
    print("="*70)

    builder = PizzaBuilder()
    director = PizzaDirector(builder)

    print("\n--- PEPPERONI PIZZA ---")
    pepperoni = director.build_pepperoni()
    print(pepperoni)

    print("\n--- VEGETARIAN PIZZA ---")
    vegetarian = director.build_vegetarian()
    print(vegetarian)

    print("\n--- HAWAIIAN PIZZA ---")
    hawaiian = director.build_hawaiian()
    print(hawaiian)

    print("\n--- VEGAN PIZZA ---")
    vegan = director.build_vegan()
    print(vegan)


def test_builder_reuse():
    """Test reusing builder for multiple objects."""
    print("\n" + "="*70)
    print("TEST 6: BUILDER REUSE")
    print("="*70)

    builder = PizzaBuilder()

    # Build first pizza
    pizza1 = (builder
              .set_size(Pizza.Size.LARGE)
              .add_toppings("pepperoni", "mushroom")
              .build())

    # Reuse builder for second pizza
    pizza2 = (builder
              .reset()
              .set_size(Pizza.Size.SMALL)
              .add_topping("cheese")
              .build())

    print(f"Pizza 1 size: {pizza1.size.name}, toppings: {pizza1.toppings}")
    print(f"Pizza 2 size: {pizza2.size.name}, toppings: {pizza2.toppings}")


def test_error_handling():
    """Test error handling in builders."""
    print("\n" + "="*70)
    print("TEST 7: ERROR HANDLING")
    print("="*70)

    # Try to build pizza without toppings
    try:
        pizza = PizzaBuilder().build()
    except ValueError as e:
        print(f"Error (expected): {e}")

    # Try to build query without table
    try:
        query = QueryBuilder().build()
    except ValueError as e:
        print(f"Error (expected): {e}")

    # Try to build request without URL
    try:
        request = HTTPRequestBuilder().build()
    except ValueError as e:
        print(f"Error (expected): {e}")


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

def print_key_takeaways():
    """Print key learning points."""
    print("\n" + "="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print("""
1. BUILDER PATTERN SOLVES TELESCOPING CONSTRUCTORS
   Problem:
     Pizza(size, crust, sauce, toppings, cheese, extraCheese, glutenFree)
     vs many overloaded constructors
   Solution:
     PizzaBuilder().set_size().set_crust()...build()

2. FLUENT INTERFACE IMPROVES READABILITY
   - Method chaining makes code read like natural language
   - Self-documenting code
   - Easy to understand construction logic

3. FLEXIBILITY WITH OPTIONAL PARAMETERS
   - Add/remove parameters without changing signature
   - Safe defaults for parameters
   - Easy to extend with new options

4. DIRECTOR PATTERN FOR COMMON CONFIGURATIONS
   - Encapsulate specific construction patterns
   - Reusable construction recipes
   - Separates construction logic from product

5. VALIDATION CAN HAPPEN AT BUILD TIME
   - Ensure valid objects are created
   - Fail fast if required parameters missing
   - Can also validate individual steps

6. ALTERNATIVES TO CONSIDER
   - Dataclasses (Python) - simpler for simple objects
   - Named tuples - lightweight immutable objects
   - Keyword arguments - Python's approach
   - But Builder is better for:
     * Complex validation logic
     * Step-by-step construction
     * Fluent/readable interfaces
     * Immutable objects

7. WHEN TO USE BUILDER
   - Complex objects with many parameters
   - Many optional parameters
   - Want immutable objects
   - Want fluent, readable API
   - Step-by-step construction logic

8. IMPLEMENTATION CONSIDERATIONS
   - Return 'self' for method chaining
   - Implement reset() for builder reuse
   - Validate at build() time
   - Consider making Product immutable
   - Use copy() for mutable attributes
    """)


if __name__ == "__main__":
    test_simple_pizza_builder()
    test_pizza_with_defaults()
    test_query_builder()
    test_http_request_builder()
    test_director_pattern()
    test_builder_reuse()
    test_error_handling()
    print_key_takeaways()
