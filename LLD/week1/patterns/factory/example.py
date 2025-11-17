"""
Factory Pattern: Vehicle Factory
Centralizes vehicle creation logic
"""
from abc import ABC, abstractmethod

class Vehicle(ABC):
    @abstractmethod
    def start(self): pass
    @abstractmethod
    def drive(self): pass

class Car(Vehicle):
    def start(self): return "Car started"
    def drive(self): return "Driving car"

class Motorcycle(Vehicle):
    def start(self): return "Motorcycle started"
    def drive(self): return "Riding motorcycle"

class Truck(Vehicle):
    def start(self): return "Truck started"
    def drive(self): return "Driving truck"

class VehicleFactory:
    """Centralizes vehicle creation"""
    @staticmethod
    def create(vehicle_type):
        if vehicle_type == "car":
            return Car()
        elif vehicle_type == "motorcycle":
            return Motorcycle()
        elif vehicle_type == "truck":
            return Truck()
        else:
            raise ValueError(f"Unknown type: {vehicle_type}")

if __name__ == "__main__":
    print("=== Factory Pattern Demo ===\n")
    
    types = ["car", "motorcycle", "truck"]
    
    for vtype in types:
        vehicle = VehicleFactory.create(vtype)
        print(f"{vtype.title()}:")
        print(f"  {vehicle.start()}")
        print(f"  {vehicle.drive()}\n")
    
    print("Factory centralizes creation logic!")
