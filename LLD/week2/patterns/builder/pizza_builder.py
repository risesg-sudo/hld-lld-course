"""
Pizza Builder Example

Demonstrates the Builder pattern for constructing complex Pizza objects
with many optional parameters in a readable, fluent way.
"""

from enum import Enum
from typing import List


class PizzaSize(Enum):
    """Pizza size options."""
    SMALL = 8
    MEDIUM = 10
    LARGE = 12
    EXTRA_LARGE = 14


class Pizza:
    """
    Complex product being built.

    Has many parameters - perfect candidate for Builder pattern.
    """

    def __init__(
        self,
        size: PizzaSize,
        crust: str,
        sauce: str,
        cheese: str,
        toppings: List[str],
        extra_cheese: bool,
        gluten_free: bool
    ):
        """
        Constructor with all parameters.

        Note: This would be painful to call directly!
        That's why we use a builder.
        """
        self.size = size
        self.crust = crust
        self.sauce = sauce
        self.cheese = cheese
        self.toppings = toppings
        self.extra_cheese = extra_cheese
        self.gluten_free = gluten_free

        # Validate the pizza configuration
        self._validate()

    def _validate(self):
        """Validate pizza configuration."""
        if not self.toppings:
            raise ValueError("Pizza must have at least one topping")

        if self.gluten_free and self.crust not in ["gluten-free", "cauliflower"]:
            raise ValueError("Gluten-free pizza needs gluten-free crust")

    def calculate_price(self) -> float:
        """Calculate pizza price based on configuration."""
        # Base price by size
        base_prices = {
            PizzaSize.SMALL: 8.99,
            PizzaSize.MEDIUM: 10.99,
            PizzaSize.LARGE: 12.99,
            PizzaSize.EXTRA_LARGE: 14.99
        }

        price = base_prices[self.size]

        # Add topping costs
        price += len(self.toppings) * 1.50

        # Add extra cheese cost
        if self.extra_cheese:
            price += 2.00

        # Add gluten-free cost
        if self.gluten_free:
            price += 3.00

        return price

    def __str__(self):
        """String representation of pizza."""
        return (
            f"\nPizza Order:\n"
            f"  Size: {self.size.name} ({self.size.value}\")\n"
            f"  Crust: {self.crust}\n"
            f"  Sauce: {self.sauce}\n"
            f"  Cheese: {self.cheese}{' (Extra)' if self.extra_cheese else ''}\n"
            f"  Toppings: {', '.join(self.toppings)}\n"
            f"  Gluten-Free: {'Yes' if self.gluten_free else 'No'}\n"
            f"  Price: ${self.calculate_price():.2f}"
        )


class PizzaBuilder:
    """
    Builder for constructing Pizza objects step-by-step.

    Provides fluent interface for readable pizza construction.
    """

    def __init__(self):
        """Initialize builder with default values."""
        # Defaults for all parameters
        self._size = PizzaSize.MEDIUM
        self._crust = "regular"
        self._sauce = "tomato"
        self._cheese = "mozzarella"
        self._toppings = []
        self._extra_cheese = False
        self._gluten_free = False

    def set_size(self, size: PizzaSize) -> "PizzaBuilder":
        """Set pizza size."""
        self._size = size
        return self

    def set_crust(self, crust: str) -> "PizzaBuilder":
        """Set crust type."""
        self._crust = crust
        return self

    def set_sauce(self, sauce: str) -> "PizzaBuilder":
        """Set sauce type."""
        self._sauce = sauce
        return self

    def set_cheese(self, cheese: str) -> "PizzaBuilder":
        """Set cheese type."""
        self._cheese = cheese
        return self

    def add_topping(self, topping: str) -> "PizzaBuilder":
        """Add a single topping."""
        self._toppings.append(topping)
        return self

    def add_toppings(self, *toppings: str) -> "PizzaBuilder":
        """Add multiple toppings at once."""
        self._toppings.extend(toppings)
        return self

    def set_extra_cheese(self, extra: bool) -> "PizzaBuilder":
        """Set extra cheese option."""
        self._extra_cheese = extra
        return self

    def set_gluten_free(self, gluten_free: bool) -> "PizzaBuilder":
        """Set gluten-free option."""
        self._gluten_free = gluten_free
        return self

    def build(self) -> Pizza:
        """
        Build and return the final Pizza object.

        Validation happens here during construction.
        """
        return Pizza(
            size=self._size,
            crust=self._crust,
            sauce=self._sauce,
            cheese=self._cheese,
            toppings=self._toppings.copy(),
            extra_cheese=self._extra_cheese,
            gluten_free=self._gluten_free
        )

    def reset(self) -> "PizzaBuilder":
        """Reset builder to default state for reuse."""
        self.__init__()
        return self


def demonstrate_basic_builder():
    """Demonstrate basic builder usage."""
    print("="*70)
    print("BASIC BUILDER USAGE")
    print("="*70)

    print("\n1. Building a custom pizza with fluent interface:")
    pizza = (PizzaBuilder()
             .set_size(PizzaSize.LARGE)
             .set_crust("thin")
             .set_sauce("white garlic")
             .add_topping("chicken")
             .add_topping("mushrooms")
             .add_topping("spinach")
             .set_extra_cheese(True)
             .build())

    print(pizza)


def demonstrate_defaults():
    """Demonstrate using default values."""
    print("\n" + "="*70)
    print("USING DEFAULT VALUES")
    print("="*70)

    print("\n1. Building pizza with minimal configuration:")
    print("   (Using defaults for size, crust, sauce, cheese)")

    pizza = (PizzaBuilder()
             .add_toppings("pepperoni", "olives")
             .build())

    print(pizza)


def demonstrate_gluten_free():
    """Demonstrate gluten-free pizza with validation."""
    print("\n" + "="*70)
    print("GLUTEN-FREE PIZZA (with validation)")
    print("="*70)

    print("\n1. Correct gluten-free pizza:")
    pizza = (PizzaBuilder()
             .set_size(PizzaSize.MEDIUM)
             .set_crust("gluten-free")
             .add_topping("vegetables")
             .set_gluten_free(True)
             .build())

    print(pizza)

    print("\n2. Attempting invalid gluten-free pizza:")
    try:
        invalid_pizza = (PizzaBuilder()
                         .set_crust("regular")  # Regular crust
                         .add_topping("cheese")
                         .set_gluten_free(True)  # But marked gluten-free
                         .build())
    except ValueError as e:
        print(f"   Error (expected): {e}")


def demonstrate_builder_reuse():
    """Demonstrate reusing a builder."""
    print("\n" + "="*70)
    print("BUILDER REUSE")
    print("="*70)

    builder = PizzaBuilder()

    print("\n1. First pizza:")
    pizza1 = (builder
              .set_size(PizzaSize.LARGE)
              .add_toppings("pepperoni", "mushrooms")
              .build())
    print(f"   Toppings: {pizza1.toppings}")

    print("\n2. Second pizza (without reset - accumulates toppings!):")
    pizza2 = (builder
              .add_topping("olives")
              .build())
    print(f"   Toppings: {pizza2.toppings}")
    print("   (Notice: olives + previous toppings!)")

    print("\n3. Third pizza (with reset):")
    pizza3 = (builder
              .reset()
              .add_topping("cheese")
              .build())
    print(f"   Toppings: {pizza3.toppings}")
    print("   (Clean slate after reset)")


def compare_with_direct_construction():
    """Compare builder vs direct constructor."""
    print("\n" + "="*70)
    print("COMPARISON: Builder vs Direct Construction")
    print("="*70)

    print("\n1. Direct constructor (hard to read):")
    print("   Pizza(PizzaSize.LARGE, 'thin', 'tomato',")
    print("         'mozzarella', ['pepperoni'], True, False)")

    print("\n2. Builder pattern (self-documenting):")
    print("   PizzaBuilder()")
    print("       .set_size(PizzaSize.LARGE)")
    print("       .set_crust('thin')")
    print("       .add_topping('pepperoni')")
    print("       .set_extra_cheese(True)")
    print("       .build()")

    print("\n   Which is easier to understand?")


if __name__ == "__main__":
    demonstrate_basic_builder()
    demonstrate_defaults()
    demonstrate_gluten_free()
    demonstrate_builder_reuse()
    compare_with_direct_construction()

    print("\n" + "="*70)
    print("KEY POINTS")
    print("="*70)
    print("""
1. Builder provides fluent, readable object construction
2. Method chaining creates natural, self-documenting code
3. Default values eliminate need to specify every parameter
4. Validation happens at build() time
5. Builder can be reused (with reset) for multiple objects
6. Much clearer than constructor with many parameters
    """)
