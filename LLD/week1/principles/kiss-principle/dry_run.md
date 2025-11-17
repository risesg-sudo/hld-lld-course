# Dry Run: KISS Principle

## Complex vs Simple Inventory

### Complex Inventory Operation

```python
complex_inv.add_item("laptop", 10)
```

**Execution Steps**:
1. Create backup_operation function
2. Add to backup_queue
3. Process entire queue
4. Notify all observers
5. Actually add item to dict
6. Print message

**Result**: Item added after 6 steps

**Code**: 40 lines

### Simple Inventory Operation

```python
simple_inv.add_item("laptop", 10)
```

**Execution Steps**:
1. Add item to dict
2. Print message

**Result**: Item added after 2 steps

**Code**: 10 lines

## Comparison

| Aspect | Complex | Simple |
|--------|---------|--------|
| Steps | 6 | 2 |
| Code Lines | 40 | 10 |
| Understandability | Low | High |
| Maintainability | Low | High |
| Bug Risk | High | Low |

## Key Insight

Both achieve same result. Simple version is:
- Faster to write
- Easier to understand
- Easier to maintain
- Less bug-prone

KISS: Start simple. Add complexity only when proven necessary.
