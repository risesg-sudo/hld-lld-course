# Dry Run: Template Method Pattern

This document traces execution of the template method pattern, showing how the base class coordinates calls to subclass methods.

## Setup

Create a CSV processor:

```python
processor = CSVProcessor()
```

**Memory State**:
```
0x3001: CSVProcessor instance
  (inherits from DataProcessor)

Class hierarchy:
  CSVProcessor extends DataProcessor
  DataProcessor is ABC
```

## Operation: Process CSV File

```python
processor.process("data.csv")
```

### Step 1: Enter Template Method

**Call**: `CSVProcessor.process("data.csv")`

**Lookup**: CSVProcessor doesn't define `process()`, so walk up hierarchy.

**Found**: `DataProcessor.process()` in base class

**Enter**:
```
self = CSVProcessor at 0x3001
filepath = "data.csv"
```

**Print**:
```
Output: "Processing: data.csv"
```

### Step 2: Load Data (Hook Method)

**Template calls**: `raw_data = self.load_data(filepath)`

**Method Resolution**:
```
Check CSVProcessor.load_data(): Not defined
Check DataProcessor.load_data(): Found (hook method)
```

**Execute**: `DataProcessor.load_data()`
```
self = CSVProcessor at 0x3001
filepath = "data.csv"

Output: "Loading data from data.csv"
Return: "raw_data_content"
```

**State Update**:
```
raw_data = "raw_data_content"
```

### Step 3: Parse Data (Abstract Method)

**Template calls**: `parsed_data = self.parse_data(raw_data)`

**Method Resolution**:
```
Check CSVProcessor.parse_data(): Found (implements abstract)
```

**Execute**: `CSVProcessor.parse_data()`
```
self = CSVProcessor at 0x3001
raw_data = "raw_data_content"

Output: "Parsing CSV format"
```

**Parsing Logic**:
```
csv_data = "name,age,city\nJohn,30,NYC\nJane,25,LA\nBob,35,Chicago"

Split into lines:
  Line 0: "name,age,city"
  Line 1: "John,30,NYC"
  Line 2: "Jane,25,LA"
  Line 3: "Bob,35,Chicago"

Parse headers:
  headers = ["name", "age", "city"]

Parse records:
  Record 1: {"name": "John", "age": "30", "city": "NYC"}
  Record 2: {"name": "Jane", "age": "25", "city": "LA"}
  Record 3: {"name": "Bob", "age": "35", "city": "Chicago"}

Output: "  Parsed 3 CSV records"
Return: [record1, record2, record3]
```

**State Update**:
```
parsed_data = [
  {"name": "John", "age": "30", "city": "NYC"},
  {"name": "Jane", "age": "25", "city": "LA"},
  {"name": "Bob", "age": "35", "city": "Chicago"}
]
```

### Step 4: Validate Data (Hook Method)

**Template calls**: `valid = self.validate_data(parsed_data)`

**Method Resolution**:
```
Check CSVProcessor.validate_data(): Not defined
Check DataProcessor.validate_data(): Found (hook method)
```

**Execute**: `DataProcessor.validate_data()`
```
self = CSVProcessor at 0x3001
data = [3 records]

Output: "Validating 3 records"

Check: len(data) > 0?
  len([3 records]) = 3
  3 > 0 = True

Return: True
```

**State Update**:
```
valid = True
```

### Step 5: Conditional Check

**Template checks**: `if valid:`

```
valid = True → Execute transformation branch
```

### Step 6: Transform Data (Abstract Method)

**Template calls**: `transformed = self.transform_data(parsed_data)`

**Method Resolution**:
```
Check CSVProcessor.transform_data(): Found (implements abstract)
```

**Execute**: `CSVProcessor.transform_data()`
```
self = CSVProcessor at 0x3001
data = [3 records]

Output: "Transforming CSV data"
```

**Transformation Logic**:
```
For each record:

Record 1:
  Original: {"name": "John", "age": "30", "city": "NYC"}
  age_int = int("30") = 30
  year_born = 2024 - 30 = 1994
  Transformed: {"name": "John", "age": 30, "city": "NYC", "year_born": 1994}

Record 2:
  Original: {"name": "Jane", "age": "25", "city": "LA"}
  age_int = int("25") = 25
  year_born = 2024 - 25 = 1999
  Transformed: {"name": "Jane", "age": 25, "city": "LA", "year_born": 1999}

Record 3:
  Original: {"name": "Bob", "age": "35", "city": "Chicago"}
  age_int = int("35") = 35
  year_born = 2024 - 35 = 1989
  Transformed: {"name": "Bob", "age": 35, "city": "Chicago", "year_born": 1989}

Output: "  Added year_born field"
Return: [transformed1, transformed2, transformed3]
```

**State Update**:
```
transformed = [3 transformed records with year_born field]
```

### Step 7: Save Results (Hook Method)

**Template calls**: `self.save_results(transformed)`

**Method Resolution**:
```
Check CSVProcessor.save_results(): Not defined
Check DataProcessor.save_results(): Found (hook method)
```

**Execute**: `DataProcessor.save_results()`
```
self = CSVProcessor at 0x3001
data = [3 transformed records]

Output: "Saving 3 records to output"
Return: None
```

### Step 8: Template Completion

**Print**:
```
Output: "Processing complete!"
```

**Return**: `None` (template method returns to caller)

## Call Flow Visualization

```
Client
  |
  v
CSVProcessor.process()  (not defined, look up hierarchy)
  |
  v
DataProcessor.process()  (TEMPLATE METHOD - BASE CLASS)
  |
  +---> self.load_data()
  |       |
  |       v
  |     DataProcessor.load_data()  (HOOK - BASE CLASS)
  |
  +---> self.parse_data()
  |       |
  |       v
  |     CSVProcessor.parse_data()  (ABSTRACT - SUBCLASS)
  |
  +---> self.validate_data()
  |       |
  |       v
  |     DataProcessor.validate_data()  (HOOK - BASE CLASS)
  |
  +---> self.transform_data()
  |       |
  |       v
  |     CSVProcessor.transform_data()  (ABSTRACT - SUBCLASS)
  |
  +---> self.save_results()
  |       |
  |       v
  |     DataProcessor.save_results()  (HOOK - BASE CLASS)
  |
  v
Return to Client
```

## Comparison: CSV vs JSON Processing

### CSV Flow:
```
Template (Base) → load_data (Base) → parse_data (CSV) → validate_data (Base) → transform_data (CSV) → save_results (Base)
```

### JSON Flow:
```
Template (Base) → load_data (Base) → parse_data (JSON) → validate_data (JSON) → transform_data (JSON) → save_results (Base)
```

**Differences**:
- `parse_data()`: Different implementation (CSV vs JSON parsing)
- `transform_data()`: Different logic (add year_born vs add grade)
- `validate_data()`: JSON overrides for custom validation; CSV uses default

**Similarities**:
- Same template method orchestrates everything
- Same algorithm structure (load→parse→validate→transform→save)
- Same hook methods for load_data and save_results

## Key Observations

### 1. Fixed Algorithm Structure

Template method in base class defines the sequence:
```python
def process(self, filepath: str):
    raw = self.load_data(filepath)      # Step 1
    parsed = self.parse_data(raw)       # Step 2
    valid = self.validate_data(parsed)  # Step 3
    if valid:
        trans = self.transform_data(parsed)  # Step 4
        self.save_results(trans)            # Step 5
```

Subclasses cannot change this sequence. They can only customize individual steps.

### 2. Method Resolution Through Inheritance

When template calls `self.parse_data()`:
```
1. Check CSVProcessor class: Found → use CSVProcessor.parse_data()
2. If not found, check DataProcessor: Would use base implementation
3. If still not found and abstract: Runtime error
```

The `self` reference ensures correct method gets called based on actual object type.

### 3. Hollywood Principle

"Don't call us, we'll call you"

```
Base class (DataProcessor) calls subclass methods (CSVProcessor.parse_data())
Not the other way around
This inverts normal control flow
```

### 4. Reuse Through Inheritance

Code written once in base class:
- Template method algorithm
- Hook method defaults (load_data, validate_data, save_results)
- Common logic

Code written in each subclass:
- Abstract method implementations (parse_data, transform_data)
- Hook method overrides (optional - JSONProcessor overrides validate_data)

## Summary

Template Method pattern achieves code reuse and algorithm consistency through:

1. **Template method**: Defines fixed algorithm structure in base class
2. **Abstract methods**: Force subclasses to implement format-specific steps
3. **Hook methods**: Provide defaults subclasses can optionally override
4. **Inheritance**: Enables method resolution and code sharing
5. **Inversion of control**: Base class calls subclass code

The cost: inheritance coupling. The benefit: guaranteed algorithm structure with customizable steps.
