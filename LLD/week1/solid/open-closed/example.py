"""
Open/Closed Principle: Discount System
"""
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, amount):
        pass

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent):
        self.percent = percent
        
    def calculate(self, amount):
        return amount * (self.percent / 100)

class FixedDiscount(DiscountStrategy):
    def __init__(self, value):
        self.value = value
        
    def calculate(self, amount):
        return self.value

class BulkDiscount(DiscountStrategy):
    def __init__(self, threshold, discount):
        self.threshold = threshold
        self.discount = discount
        
    def calculate(self, amount):
        return self.discount if amount > self.threshold else 0

class DiscountCalculator:
    """Closed for modification, open for extension"""
    def apply_discount(self, amount, strategy):
        discount = strategy.calculate(amount)
        return amount - discount

if __name__ == "__main__":
    calc = DiscountCalculator()
    
    print(f"$100 with 10%: ${calc.apply_discount(100, PercentageDiscount(10))}")
    print(f"$100 with $5 fixed: ${calc.apply_discount(100, FixedDiscount(5))}")
    print(f"$150 with bulk: ${calc.apply_discount(150, BulkDiscount(100, 10))}")
    print("\nAdding new discount = new class, no modification to calculator!")
