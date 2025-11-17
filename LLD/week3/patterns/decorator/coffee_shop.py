"""Decorator Pattern - Coffee Shop Example"""

from abc import ABC, abstractmethod


class Beverage(ABC):
    """Base component interface."""

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def get_cost(self) -> float:
        pass


class SimpleCoffee(Beverage):
    """Concrete component."""

    def get_description(self) -> str:
        return "Simple Coffee"

    def get_cost(self) -> float:
        return 2.00


class BeverageDecorator(Beverage):
    """Base decorator."""

    def __init__(self, beverage: Beverage):
        self._beverage = beverage

    @abstractmethod
    def get_description(self) -> str:
        pass

    def get_cost(self) -> float:
        return self._beverage.get_cost()


class MilkDecorator(BeverageDecorator):
    """Adds milk."""

    def get_description(self) -> str:
        return f"{self._beverage.get_description()}, Milk"

    def get_cost(self) -> float:
        return self._beverage.get_cost() + 0.50


class SugarDecorator(BeverageDecorator):
    """Adds sugar."""

    def get_description(self) -> str:
        return f"{self._beverage.get_description()}, Sugar"

    def get_cost(self) -> float:
        return self._beverage.get_cost() + 0.25


class WhippedCreamDecorator(BeverageDecorator):
    """Adds whipped cream."""

    def get_description(self) -> str:
        return f"{self._beverage.get_description()}, Whipped Cream"

    def get_cost(self) -> float:
        return self._beverage.get_cost() + 0.75


if __name__ == "__main__":
    print("DECORATOR PATTERN DEMONSTRATION")
    print("="*60)

    # Simple coffee
    coffee1 = SimpleCoffee()
    print(f"\n{coffee1.get_description()}: ${coffee1.get_cost():.2f}")

    # Coffee with milk
    coffee2 = MilkDecorator(SimpleCoffee())
    print(f"{coffee2.get_description()}: ${coffee2.get_cost():.2f}")

    # Coffee with milk and sugar
    coffee3 = SugarDecorator(MilkDecorator(SimpleCoffee()))
    print(f"{coffee3.get_description()}: ${coffee3.get_cost():.2f}")

    # Coffee with all add-ons
    coffee4 = WhippedCreamDecorator(SugarDecorator(MilkDecorator(SimpleCoffee())))
    print(f"{coffee4.get_description()}: ${coffee4.get_cost():.2f}")

    print("\n" + "="*60)
    print("Key Observations:")
    print("  - 4 classes handle infinite combinations")
    print("  - Build features by wrapping, not subclassing")
    print("  - Add/remove features at runtime")
    print("="*60)
