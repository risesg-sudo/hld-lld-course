# Dry Run: Open/Closed Principle

## Adding New Discount Type

### Initial: Two discount types
- PercentageDiscount
- FixedDiscount

### Adding BulkDiscount

**Step 1**: Create new class
```python
class BulkDiscount(DiscountStrategy):
    def calculate(self, amount):
        return 10 if amount > 100 else 0
```

**Step 2**: Use immediately
```python
calc.apply_discount(150, BulkDiscount(100, 10))
```

**No modification to**:
- DiscountCalculator
- Existing discount classes
- Any other code

### Benefits

- Calculator never modified
- Existing discounts unchanged
- New functionality added easily
- Open for extension, closed for modification

OCP achieved through abstraction and polymorphism.
