"""
Inheritance Example: Vehicle Hierarchy
Demonstrates code reuse and "is-a" relationship
"""

# Base class (Parent)
class Vehicle:
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.is_running = True
            return f"{self.brand} {self.model} started"
        return "Already running"

    def stop(self):
        if self.is_running:
            self.is_running = False
            return f"{self.brand} {self.model} stopped"
        return "Already stopped"

    def get_info(self):
        return f"{self.year} {self.brand} {self.model}"


# Derived class (Child)
class Car(Vehicle):
    def __init__(self, brand, model, year, num_doors):
        # Call parent constructor
        super().__init__(brand, model, year)
        self.num_doors = num_doors
        self.trunk_open = False

    def open_trunk(self):
        self.trunk_open = True
        return "Trunk opened"

    def close_trunk(self):
        self.trunk_open = False
        return "Trunk closed"

    # Method overriding
    def get_info(self):
        base_info = super().get_info()
        return f"{base_info} - {self.num_doors} doors"


class Motorcycle(Vehicle):
    def __init__(self, brand, model, year, engine_cc):
        super().__init__(brand, model, year)
        self.engine_cc = engine_cc
        self.helmet_compartment_open = False

    def wheelie(self):
        if self.is_running:
            return "Performing wheelie! 🏍️"
        return "Start the motorcycle first!"

    def get_info(self):
        base_info = super().get_info()
        return f"{base_info} - {self.engine_cc}cc"


class ElectricCar(Car):
    def __init__(self, brand, model, year, num_doors, battery_capacity):
        super().__init__(brand, model, year, num_doors)
        self.battery_capacity = battery_capacity
        self.charge_level = 100

    def charge(self, amount):
        self.charge_level = min(100, self.charge_level + amount)
        return f"Charged to {self.charge_level}%"

    def get_info(self):
        base_info = super().get_info()
        return f"{base_info} - {self.battery_capacity}kWh battery ({self.charge_level}% charged)"


# Usage Example
if __name__ == "__main__":
    # Create a regular car
    car = Car("Toyota", "Camry", 2023, 4)
    print(car.get_info())  # 2023 Toyota Camry - 4 doors
    print(car.start())     # Toyota Camry started
    print(car.open_trunk()) # Trunk opened

    print("\n" + "="*50 + "\n")

    # Create a motorcycle
    bike = Motorcycle("Harley-Davidson", "Sportster", 2022, 1200)
    print(bike.get_info())  # 2022 Harley-Davidson Sportster - 1200cc
    print(bike.wheelie())   # Start the motorcycle first!
    print(bike.start())     # Harley-Davidson Sportster started
    print(bike.wheelie())   # Performing wheelie! 🏍️

    print("\n" + "="*50 + "\n")

    # Create an electric car
    tesla = ElectricCar("Tesla", "Model 3", 2023, 4, 75)
    print(tesla.get_info())  # 2023 Tesla Model 3 - 4 doors - 75kWh battery (100% charged)
    print(tesla.start())     # Tesla Model 3 started

    # All vehicles can use base class methods
    vehicles = [car, bike, tesla]
    print("\nStopping all vehicles:")
    for vehicle in vehicles:
        print(f"  - {vehicle.stop()}")

    """
    Key Points:
    1. Code reuse - common functionality in Vehicle class
    2. Specialization - each subclass adds unique features
    3. Method overriding - get_info() customized in each class
    4. super() - access parent class methods and constructor
    5. Multi-level inheritance - ElectricCar extends Car which extends Vehicle
    """
