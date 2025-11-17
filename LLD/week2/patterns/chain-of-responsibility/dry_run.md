# Dry Run: Chain of Responsibility Execution

## Scenario: Ticket Routing Through Chain

**Code:**
```python
basic = BasicSupport("Basic", 1)
technical = TechnicalSupport("Technical", 2)
manager = ManagerSupport("Manager", 3)

basic.set_next(technical).set_next(manager)
basic.handle(SupportTicket("T002", "Software crash", 2))
```

### Step 1: Build Chain

```
Create handlers:
  BasicSupport@0x7f8a1c:
    name = "Basic"
    max_priority = 1
    next_handler = None
  
  TechnicalSupport@0x7f9b2d:
    name = "Technical"
    max_priority = 2
    next_handler = None
  
  ManagerSupport@0x7fac3e:
    name = "Manager"
    max_priority = 3
    next_handler = None
```

### Step 2: Link Handlers

```
Execution: basic.set_next(technical)
  basic.next_handler = TechnicalSupport@0x7f9b2d
  Returns: TechnicalSupport@0x7f9b2d

Execution: .set_next(manager) on returned object
  technical.next_handler = ManagerSupport@0x7fac3e
  Returns: ManagerSupport@0x7fac3e

Chain structure:
  BasicSupport@0x7f8a1c -> TechnicalSupport@0x7f9b2d -> ManagerSupport@0x7fac3e -> None
```

### Step 3: Handle Ticket (Priority 2)

```
Ticket: SupportTicket("T002", "Software crash", 2)

Call: basic.handle(ticket)

Handler 1: BasicSupport
  Check: ticket.priority (2) <= max_priority (1)? No
  Check: next_handler exists? Yes
  Action: Pass to next_handler (TechnicalSupport)

Handler 2: TechnicalSupport
  Check: ticket.priority (2) <= max_priority (2)? Yes
  Action: Call self.process(ticket)
  Inside process():
    Print: "Technical Support: Handling..."
    Set: ticket.assigned_to = "Technical Support"
    Print: "Investigating technical issue..."
  Result: Ticket handled, chain stops

Final state:
  ticket.assigned_to = "Technical Support"
  Handlers traversed: Basic (passed) -> Technical (handled)
```

## Key Insights

1. Request enters at chain start
2. Each handler checks if it can handle
3. If yes: process and stop
4. If no: pass to next handler
5. Chain ends when handled or no more handlers
