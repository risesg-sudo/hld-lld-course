# Dry Run: Bank Account Encapsulation

This document traces the step-by-step execution of the bank account example, showing how encapsulation protects data and enforces business rules.

## Initial Setup

```python
account1 = BankAccount("ACC001", "Alice Johnson", 1000)
account2 = BankAccount("ACC002", "Bob Smith", 500)
```

### Memory State After Initialization

**Account 1:**
```
__account_number: "ACC001"
__owner_name: "Alice Johnson"
__balance: 1000
__transaction_history: []
```

**Account 2:**
```
__account_number: "ACC002"
__owner_name: "Bob Smith"
__balance: 500
__transaction_history: []
```

---

## Operation 1: Valid Deposit

```python
account1.deposit(500)
```

### Step-by-Step Execution

**Step 1**: Method `deposit(500)` is called on account1

**Step 2**: Validate amount
- Check: `amount <= 0`
- Result: `500 <= 0` is False, validation passes

**Step 3**: Update balance
- Old balance: 1000
- Operation: `self.__balance += amount` → `1000 + 500`
- New balance: 1500

**Step 4**: Record transaction
- Append to history: `"Deposited: $500"`

**Step 5**: Print success message
- Output: "Successfully deposited $500"

**Step 6**: Return True

### Memory State After Operation

**Account 1:**
```
__account_number: "ACC001"
__owner_name: "Alice Johnson"
__balance: 1500  ← Changed
__transaction_history: ["Deposited: $500"]  ← Updated
```

---

## Operation 2: Invalid Deposit (Negative Amount)

```python
account1.deposit(-100)
```

### Step-by-Step Execution

**Step 1**: Method `deposit(-100)` is called

**Step 2**: Validate amount
- Check: `amount <= 0`
- Result: `-100 <= 0` is True, validation fails

**Step 3**: Print error message
- Output: "Error: Deposit amount must be positive (got $-100)"

**Step 4**: Return False

**Step 5**: Balance remains unchanged due to validation

### Memory State After Operation

**Account 1:** (No changes)
```
__account_number: "ACC001"
__owner_name: "Alice Johnson"
__balance: 1500  ← Unchanged
__transaction_history: ["Deposited: $500"]  ← Unchanged
```

This demonstrates encapsulation protecting data integrity.

---

## Operation 3: Valid Withdrawal

```python
account1.withdraw(200)
```

### Step-by-Step Execution

**Step 1**: Method `withdraw(200)` is called

**Step 2**: Validate amount is positive
- Check: `amount <= 0`
- Result: `200 <= 0` is False, passes

**Step 3**: Validate sufficient balance
- Check: `amount > self.__balance`
- Result: `200 > 1500` is False, passes

**Step 4**: Update balance
- Old balance: 1500
- Operation: `self.__balance -= amount` → `1500 - 200`
- New balance: 1300

**Step 5**: Record transaction
- Append: `"Withdrawn: $200"`

**Step 6**: Print success and return True

### Memory State After Operation

**Account 1:**
```
__account_number: "ACC001"
__owner_name: "Alice Johnson"
__balance: 1300  ← Changed
__transaction_history: [
    "Deposited: $500",
    "Withdrawn: $200"  ← Added
]
```

---

## Operation 4: Invalid Withdrawal (Insufficient Funds)

```python
account1.withdraw(2000)
```

### Step-by-Step Execution

**Step 1**: Method `withdraw(2000)` is called

**Step 2**: Validate amount is positive
- Check: `amount <= 0`
- Result: `2000 <= 0` is False, passes

**Step 3**: Validate sufficient balance
- Check: `amount > self.__balance`
- Result: `2000 > 1300` is True, validation fails

**Step 4**: Print error message
- Output: "Error: Insufficient funds (balance: $1300, requested: $2000)"

**Step 5**: Return False

### Memory State After Operation

**Account 1:** (No changes - protected by encapsulation)
```
__account_number: "ACC001"
__owner_name: "Alice Johnson"
__balance: 1300  ← Unchanged
__transaction_history: [
    "Deposited: $500",
    "Withdrawn: $200"
]  ← Unchanged
```

---

## Operation 5: Transfer Between Accounts

```python
account1.transfer(account2, 300)
```

### Step-by-Step Execution

**Step 1**: Method `transfer(account2, 300)` is called on account1

**Step 2**: Validate amount
- Check: `amount <= 0` → False
- Check: `amount > self.__balance` → `300 > 1300` → False

**Step 3**: Deduct from source account (account1)
- Old balance: 1300
- Operation: `self.__balance -= 300`
- New balance: 1000

**Step 4**: Record transaction in source
- Append: `"Transfer out to ACC002: $300"`

**Step 5**: Deposit to target account (account2)
- Calls `account2.deposit(300)`
- account2's balance: `500 + 300 = 800`
- account2's history: adds `"Deposited: $300"`

**Step 6**: Print success and return True

### Memory State After Operation

**Account 1:**
```
__account_number: "ACC001"
__owner_name: "Alice Johnson"
__balance: 1000  ← Changed
__transaction_history: [
    "Deposited: $500",
    "Withdrawn: $200",
    "Transfer out to ACC002: $300"  ← Added
]
```

**Account 2:**
```
__account_number: "ACC002"
__owner_name: "Bob Smith"
__balance: 800  ← Changed
__transaction_history: [
    "Deposited: $300"  ← Added
]
```

---

## Operation 6: Attempting Direct Access

```python
print(account1.__balance)
```

### Step-by-Step Execution

**Step 1**: Python attempts to access `__balance` attribute

**Step 2**: Name mangling converts `__balance` to `_BankAccount__balance`

**Step 3**: External code uses `__balance`, which doesn't exist as a public attribute

**Step 4**: Python raises `AttributeError`

**Step 5**: Exception is caught and error message printed

### Result

Access denied. Encapsulation prevents direct manipulation of internal state.

**Correct approach:**
```python
balance = account1.get_balance()  # Returns 1000
```

---

## Final Memory State Summary

**Account 1 (Alice Johnson):**
```
Balance: $1000
Transactions:
  1. Deposited: $500
  2. Withdrawn: $200
  3. Transfer out to ACC002: $300
```

**Account 2 (Bob Smith):**
```
Balance: $800
Transactions:
  1. Deposited: $300
```

---

## Key Observations

1. **Data Protection**: Private attributes (`__balance`) cannot be accessed directly
2. **Validation**: All modifications go through methods that enforce rules
3. **Business Logic**: Insufficient funds check prevents invalid state
4. **Audit Trail**: Transaction history tracks all changes
5. **Controlled Access**: Getters provide read-only access
6. **Error Handling**: Invalid operations are rejected without corrupting data

This demonstrates how encapsulation creates a robust, reliable class that maintains its invariants and protects against misuse.
