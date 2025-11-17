# Dry Run: Command Pattern Execution

## Scenario: Insert, Undo, Redo

**Code:**
```python
editor = TextEditor()
editor.execute_command(InsertCommand(editor.document, "Hello", 0))
editor.undo()
editor.redo()
```

### Step 1: Execute Insert Command

```
Command: InsertCommand(document, "Hello", 0)

Execution:
  1. Call command.execute()
  2. Inside execute(): document.insert("Hello", 0)
  3. Document text becomes: "Hello"
  4. Add command to history: history = [InsertCommand@0x7f8a1c]
  5. Set current_pos = 1

State:
  document.text = "Hello"
  history = [InsertCommand@0x7f8a1c]
  current_pos = 1
```

### Step 2: Undo

```
Execution: editor.undo()

Process:
  1. Check: current_pos > 0? Yes (current_pos = 1)
  2. Decrement: current_pos = 0
  3. Get command: history[0] = InsertCommand@0x7f8a1c
  4. Call: command.undo()
  5. Inside undo(): document.delete(0, 5)
  6. Document text becomes: ""

State:
  document.text = ""
  history = [InsertCommand@0x7f8a1c]  (command still in history)
  current_pos = 0  (pointing before last command)
```

### Step 3: Redo

```
Execution: editor.redo()

Process:
  1. Check: current_pos < len(history)? Yes (0 < 1)
  2. Get command: history[0] = InsertCommand@0x7f8a1c
  3. Call: command.execute()
  4. Inside execute(): document.insert("Hello", 0)
  5. Document text becomes: "Hello"
  6. Increment: current_pos = 1

State:
  document.text = "Hello"
  history = [InsertCommand@0x7f8a1c]
  current_pos = 1
```

## Key Insights

1. Commands stored in history enable undo/redo
2. current_pos tracks position in history
3. Undo: move back and call undo()
4. Redo: move forward and call execute() again
5. Commands encapsulate all info needed to undo
