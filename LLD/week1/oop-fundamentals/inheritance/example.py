"""
Inheritance Example: Vehicle Hierarchy
Demonstrates code reuse and IS-A relationship
"""

# Base class (Parent)
class Vehicle:
    """
    Base class representing any vehicle.
    Contains common attributes and methods shared by all vehicles.
    """

    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year
        self.is_running = False

    def start(self):
        """Start the vehicle engine."""
        if not self.is_running:
            self.is_running = True
            return f"{self.brand} {self.model} started"
        return "Already running"

    def stop(self):
        """Stop the vehicle engine."""
        if self.is_running:
            self.is_running = False
            return f"{self.brand} {self.model} stopped"
        return "Already stopped"

    def get_info(self):
        """Get vehicle information."""
        return f"{self.year} {self.brand} {self.model}"


# Derived class (Child) - Single Inheritance
class Car(Vehicle):
    """
    Car class inherits from Vehicle.
    Adds car-specific attributes and methods.
    """

    def __init__(self, brand, model, year, num_doors):
        # Call parent constructor to initialize inherited attributes
        super().__init__(brand, model, year)

        # Add car-specific attribute
        self.num_doors = num_doors
        self.trunk_open = False

    def open_trunk(self):
        """Car-specific method."""
        if not self.trunk_open:
            self.trunk_open = True
            return "Trunk opened"
        return "Trunk already open"

    def close_trunk(self):
        """Car-specific method."""
        if self.trunk_open:
            self.trunk_open = False
            return "Trunk closed"
        return "Trunk already closed"

    # Method overriding - customize inherited behavior
    def get_info(self):
        """Override parent method to include car-specific information."""
        base_info = super().get_info()  # Call parent method
        return f"{base_info} - {self.num_doors} doors"


class Motorcycle(Vehicle):
    """
    Motorcycle class inherits from Vehicle.
    Demonstrates different specialization of the same base class.
    """

    def __init__(self, brand, model, year, engine_cc):
        super().__init__(brand, model, year)
        self.engine_cc = engine_cc

    def wheelie(self):
        """Motorcycle-specific method."""
        if self.is_running:
            return "Performing wheelie!"
        return "Start the motorcycle first to do a wheelie"

    def get_info(self):
        """Override with motorcycle-specific information."""
        base_info = super().get_info()
        return f"{base_info} - {self.engine_cc}cc engine"


# Multi-level inheritance - ElectricCar inherits from Car, which inherits from Vehicle
class ElectricCar(Car):
    """
    ElectricCar inherits from Car (which inherits from Vehicle).
    Demonstrates multi-level inheritance.
    """

    def __init__(self, brand, model, year, num_doors, battery_capacity):
        # Initialize Car (which initializes Vehicle)
        super().__init__(brand, model, year, num_doors)

        # Add ElectricCar-specific attributes
        self.battery_capacity = battery_capacity
        self.charge_level = 100  # percentage

    def charge(self, amount):
        """ElectricCar-specific method."""
        old_level = self.charge_level
        self.charge_level = min(100, self.charge_level + amount)
        return f"Charged from {old_level}% to {self.charge_level}%"

    def start(self):
        """Override start method for electric vehicles."""
        if self.charge_level < 10:
            return "Cannot start: battery too low, please charge"

        if not self.is_running:
            self.is_running = True
            return f"{self.brand} {self.model} powered on (silent, battery at {self.charge_level}%)"
        return "Already running"

    def get_info(self):
        """Override to include electric-specific information."""
        base_info = super().get_info()  # Calls Car.get_info()
        return f"{base_info} - {self.battery_capacity}kWh battery at {self.charge_level}%"


# Demonstration
if __name__ == "__main__":
    print("=== Vehicle Inheritance Demo ===\n")

    # Regular Car
    print("--- Creating a Car ---")
    car = Car("Toyota", "Camry", 2023, 4)
    print(car.get_info())
    print(car.start())
    print(car.open_trunk())
    print(car.close_trunk())
    print()

    # Motorcycle
    print("--- Creating a Motorcycle ---")
    motorcycle = Motorcycle("Harley-Davidson", "Sportster", 2022, 1200)
    print(motorcycle.get_info())
    print(motorcycle.wheelie())  # Try before starting
    print(motorcycle.start())
    print(motorcycle.wheelie())  # Try after starting
    print()

    # Electric Car (Multi-level inheritance)
    print("--- Creating an Electric Car ---")
    tesla = ElectricCar("Tesla", "Model 3", 2023, 4, 75)
    print(tesla.get_info())
    print(tesla.start())
    print(tesla.open_trunk())  # Inherited from Car
    print(tesla.charge(10))    # ElectricCar-specific
    print()

    # Polymorphism - treat all as vehicles
    print("--- Polymorphism: Treating Different Types as Vehicle ---")
    vehicles = [car, motorcycle, tesla]

    print("Stopping all vehicles:")
    for vehicle in vehicles:
        print(f"  {vehicle.stop()}")

    print("\nVehicle types:")
    for vehicle in vehicles:
        print(f"  {vehicle.get_info()}")
