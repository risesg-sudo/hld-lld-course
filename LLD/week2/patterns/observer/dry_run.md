# Dry Run: Observer Pattern Execution

## Scenario: Stock Price Update with Multiple Observers

**Code:**
```python
apple = Stock("AAPL", 150.0)
trader = Trader("Alice", 145.0)
analyst = Analyst("Bob")

apple.attach(trader)
apple.attach(analyst)
apple.set_price(142.0)
```

### Step 1: Create Stock

```
Execution: Stock("AAPL", 150.0)

Memory:
  Stock@0x7f8a1c:
    symbol = "AAPL"
    price = 150.0
    _observers = []  (empty list)

Variables:
  apple = Stock@0x7f8a1c
```

### Step 2: Create Observers

```
Execution: Trader("Alice", 145.0)
Memory:
  Trader@0x7f9b2d:
    name = "Alice"
    buy_threshold = 145.0

Execution: Analyst("Bob")
Memory:
  Analyst@0x7fac3e:
    name = "Bob"

Variables:
  trader = Trader@0x7f9b2d
  analyst = Analyst@0x7fac3e
```

### Step 3: Attach Trader

```
Execution: apple.attach(trader)

Check: Is trader in _observers? No
Action: _observers.append(trader)

Stock@0x7f8a1c state:
  _observers = [Trader@0x7f9b2d]
```

### Step 4: Attach Analyst

```
Execution: apple.attach(analyst)

Stock@0x7f8a1c state:
  _observers = [Trader@0x7f9b2d, Analyst@0x7fac3e]
```

### Step 5: Set Price (Triggers Notification)

```
Execution: apple.set_price(142.0)

Step 5a: Store old price
  old_price = 150.0

Step 5b: Update price
  self.price = 142.0

Step 5c: Calculate change
  change_pct = ((142.0 - 150.0) / 150.0) * 100 = -5.33%

Step 5d: Call _notify_observers(150.0, 142.0)

Step 5e: Iterate through _observers
  
  Iteration 1: observer = Trader@0x7f9b2d
    Call: trader.on_price_changed(apple, 150.0, 142.0)
    
    Inside trader.on_price_changed:
      Check: new_price (142.0) < buy_threshold (145.0)? Yes
      Check: new_price (142.0) < old_price (150.0)? Yes
      Action: Print "BUY signal!"
  
  Iteration 2: observer = Analyst@0x7fac3e
    Call: analyst.on_price_changed(apple, 150.0, 142.0)
    
    Inside analyst.on_price_changed:
      Calculate: change_pct = -5.33%
      Check: abs(-5.33) > 5? Yes
      Action: Print "BEARISH - Significant 5.3% move"

Result: Both observers notified and reacted independently
```

## Key Insights

1. **Subject stores observer list:**
   - Maintains references to all observers
   - Iterates through list when notifying

2. **Notification is push model:**
   - Subject sends data (old_price, new_price) to observers
   - Observers don't need to query subject

3. **Observers react independently:**
   - Each has its own logic
   - Order of notification follows list order

4. **Loose coupling:**
   - Subject only knows observer interface
   - Can add/remove observers at runtime
