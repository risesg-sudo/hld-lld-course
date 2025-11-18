# Template Method Pattern

## The Hook

Picture this: you're building data processing pipelines for CSV, JSON, and XML files. All three follow the same steps—open file, extract data, parse it, analyze it, generate a report, save results. The structure never changes. But how you parse CSV differs from how you parse JSON. How you extract XML differs from how you extract CSV.

Do you copy-paste the entire pipeline three times, changing just the parsing logic? That creates maintenance nightmares. Change the analysis step? Update three places. Bug in the report generation? Fix it three times.

Or do you write one pipeline with conditionals for each format? That tangles format-specific logic throughout the pipeline. Adding a new format means touching multiple methods.

There must be a better way to reuse the common structure while allowing format-specific customization.

## The Problem

Why is code reuse difficult when algorithms share structure but differ in details?

**Duplication vs. Coupling**: You face a choice. Copy the algorithm for each variation, duplicating the common parts. Or centralize the algorithm with conditionals for variations, coupling everything together. Neither option is satisfying.

**Algorithm Structure Enforcement**: Suppose all data miners must follow the sequence: open, extract, parse, analyze, report, save. How do you enforce this? If each subclass implements the entire sequence, nothing prevents someone from reordering steps or skipping analysis.

**Protected Common Logic**: Some parts of the algorithm shouldn't be overridden. The reporting step always follows the same pattern. Analysis always happens before reporting. How do you make the structure fixed while allowing specific steps to vary?

**Framework Design**: When building frameworks, you define the control flow, but let users customize specific operations. The framework calls user code, not vice versa. This "inversion of control" is hard to achieve without a pattern.

The fundamental tension: you need the rigidity of a fixed algorithm structure with the flexibility of customizable steps. How do you get both?

## The Solution

Template Method pattern uses inheritance to separate the algorithm skeleton from step implementations.

**Define Algorithm in Base Class**: The base class contains a template method that defines the algorithm structure. This method calls other methods—some abstract, some concrete, some hooks.

:::multilang:::

```python
class DataMiner(ABC):
    def mine(self, path: str) -> None:
        """Template method - defines algorithm skeleton."""
        raw_data = self.open_file(path)
        data = self.extract_data(raw_data)
        parsed = self.parse_data(data)
        analysis = self.analyze_data(parsed)
        report = self.generate_report(analysis)
        self.save_report(report)

    @abstractmethod
    def parse_data(self, data: List[str]) -> List[Dict]:
        """Subclasses must implement."""
        pass

    def generate_report(self, analysis: Dict) -> str:
        """Hook - subclasses can override."""
        return f"Report: {analysis}"
```

```cpp
class DataMiner {
public:
    // Template method - defines algorithm skeleton
    void mine(const std::string& path) {
        auto rawData = openFile(path);
        auto data = extractData(rawData);
        auto parsed = parseData(data);
        auto analysis = analyzeData(parsed);
        auto report = generateReport(analysis);
        saveReport(report);
    }

    // Subclasses must implement
    virtual std::vector<std::map<std::string, std::string>>
    parseData(const std::vector<std::string>& data) = 0;

    // Hook - subclasses can override
    virtual std::string generateReport(
        const std::map<std::string, int>& analysis
    ) {
        return "Report: " + /* format analysis */;
    }

    virtual ~DataMiner() = default;
};
```

```java
abstract class DataMiner {
    // Template method - defines algorithm skeleton
    public final void mine(String path) {
        List<String> rawData = openFile(path);
        List<String> data = extractData(rawData);
        List<Map<String, String>> parsed = parseData(data);
        Map<String, Integer> analysis = analyzeData(parsed);
        String report = generateReport(analysis);
        saveReport(report);
    }

    // Subclasses must implement
    protected abstract List<Map<String, String>>
        parseData(List<String> data);

    // Hook - subclasses can override
    protected String generateReport(Map<String, Integer> analysis) {
        return "Report: " + analysis.toString();
    }
}
```

:::

**Subclasses Implement Steps**: Subclasses implement abstract methods (required customization) and optionally override hook methods (optional customization).

:::multilang:::

```python
class CSVDataMiner(DataMiner):
    def parse_data(self, data: List[str]) -> List[Dict]:
        """CSV-specific parsing."""
        return [dict(zip(['name', 'age'], line.split(','))) for line in data]

class JSONDataMiner(DataMiner):
    def parse_data(self, data: List[str]) -> List[Dict]:
        """JSON-specific parsing."""
        return json.loads(data[0])
```

```cpp
class CSVDataMiner : public DataMiner {
public:
    std::vector<std::map<std::string, std::string>>
    parseData(const std::vector<std::string>& data) override {
        // CSV-specific parsing
        std::vector<std::map<std::string, std::string>> result;
        for (const auto& line : data) {
            // Parse CSV line
        }
        return result;
    }
};

class JSONDataMiner : public DataMiner {
public:
    std::vector<std::map<std::string, std::string>>
    parseData(const std::vector<std::string>& data) override {
        // JSON-specific parsing
        return parseJSON(data[0]);
    }
};
```

```java
class CSVDataMiner extends DataMiner {
    @Override
    protected List<Map<String, String>> parseData(List<String> data) {
        // CSV-specific parsing
        List<Map<String, String>> result = new ArrayList<>();
        for (String line : data) {
            // Parse CSV line
        }
        return result;
    }
}

class JSONDataMiner extends DataMiner {
    @Override
    protected List<Map<String, String>> parseData(List<String> data) {
        // JSON-specific parsing
        return parseJSON(data.get(0));
    }
}
```

:::

**Three Types of Methods**:

1. **Template Method** (final, not overridden): Defines the algorithm structure. Calls other methods in a specific order.

2. **Abstract Methods** (must override): Steps that subclasses must implement. Different for each concrete class.

3. **Hook Methods** (can override): Steps with default implementation. Subclasses override only if they need custom behavior.

**How It Works**:

Client code calls the template method. The template method executes the algorithm, calling abstract and hook methods at the right points. Subclasses can't change the algorithm structure—that's fixed in the base class. They can only customize specific steps.

:::multilang:::

```python
# Client code
miner = CSVDataMiner()
miner.mine("data.csv")  # Calls template method

# Execution flow:
# 1. mine() calls open_file() - base class implementation
# 2. mine() calls extract_data() - base class implementation
# 3. mine() calls parse_data() - CSVDataMiner implementation
# 4. mine() calls analyze_data() - base class implementation
# 5. mine() calls generate_report() - base class or override
# 6. mine() calls save_report() - base class or override
```

```cpp
// Client code
auto miner = std::make_unique<CSVDataMiner>();
miner->mine("data.csv");  // Calls template method

// Execution flow:
// 1. mine() calls openFile() - base class implementation
// 2. mine() calls extractData() - base class implementation
// 3. mine() calls parseData() - CSVDataMiner implementation (virtual)
// 4. mine() calls analyzeData() - base class implementation
// 5. mine() calls generateReport() - base class or override (virtual)
// 6. mine() calls saveReport() - base class or override
```

```java
// Client code
DataMiner miner = new CSVDataMiner();
miner.mine("data.csv");  // Calls template method

// Execution flow:
// 1. mine() calls openFile() - base class implementation
// 2. mine() calls extractData() - base class implementation
// 3. mine() calls parseData() - CSVDataMiner implementation (abstract)
// 4. mine() calls analyzeData() - base class implementation
// 5. mine() calls generateReport() - base class or override
// 6. mine() calls saveReport() - base class or override
```

:::

**The "Hollywood Principle"**: "Don't call us, we'll call you." The base class (framework) calls subclass methods, not vice versa. This inverts control compared to normal composition.

**Benefits Over Alternatives**:

- **Eliminates Duplication**: Common code lives in base class, written once
- **Enforces Structure**: Template method guarantees algorithm sequence
- **Flexible Customization**: Subclasses control exactly which steps to customize
- **Clear Extension Points**: Abstract and hook methods explicitly show where subclasses can plug in
- **Consistent Behavior**: All implementations follow same algorithm pattern

## Code Example

See the complete implementation in `/home/user/hld-lld-course/LLD/week3/patterns/template/data_processing.py`.

The example demonstrates:
- Data processing pipeline with fixed structure
- CSV and JSON implementations with format-specific parsing
- Abstract methods that must be implemented
- Hook methods that can optionally be overridden
- How the template method coordinates everything

Run the example to see how different data formats flow through the same pipeline structure.

## When to Use

**Common Algorithm Structure**: Multiple classes need to implement the same algorithm, differing only in specific steps. The overall flow is the same; details vary.

**Framework Development**: You're building a framework where users customize specific operations. You want to define the control flow while letting users inject custom behavior.

**Enforcing Protocols**: You need to guarantee that certain steps happen in a specific order. Template method makes the sequence explicit and unchangeable.

**Reducing Duplication**: Similar classes duplicate code for common operations. You want to extract the common parts to a base class.

**Testing Frameworks**: Test runners follow a pattern: setup, run test, teardown. Setup and teardown have defaults; subclasses implement run test.

## Trade-offs

**What You Gain**:

- **Code Reuse**: Common algorithm steps written once in base class
- **Consistency**: All subclasses follow same algorithm structure
- **Maintainability**: Change common behavior in one place
- **Inversion of Control**: Framework calls your code, enabling plugin architecture
- **Clear Contracts**: Abstract methods make requirements explicit

**What You Lose**:

- **Flexibility**: Can't change algorithm structure in subclasses; only step implementations
- **Inheritance Coupling**: Tight coupling between base class and subclasses
- **Fragile Base Class**: Changes to base class can break subclasses
- **Debugging Difficulty**: Method calls bounce between base and subclass
- **Limited to Inheritance**: Can't use this pattern without inheritance hierarchy

**When Not to Use**:

- Algorithm structure needs to vary, not just step implementations
- You prefer composition over inheritance
- Only one or two variations exist (inheritance overhead not justified)
- Steps need to be dynamically combined in different orders

**Fragile Base Class Problem**:

Changing the base class template method or its contract can break all subclasses. Mitigate by:
- Keeping base class stable and well-documented
- Using hook methods with sensible defaults instead of abstract methods where possible
- Avoiding shared mutable state between base and subclasses
- Clearly documenting which methods subclasses should override

## Related Patterns

**Template Method vs. Strategy**: Template Method uses inheritance; Strategy uses composition. Template Method fixes algorithm structure, varies steps. Strategy varies entire algorithms. Prefer Strategy for more flexibility, Template Method for enforcing structure.

**Template Method + Strategy**: Can use strategies within template method steps. Template defines structure; strategies vary algorithms at specific steps.

**Factory Method**: Special case of Template Method. Factory Method is a template method that returns objects. The creation algorithm is fixed; the class to instantiate varies.

## Implementation Considerations

**Method Visibility**: Should abstract and hook methods be protected or public? Generally protected—only base class and subclasses need them. Template method is public.

**Default Hook Implementations**: Should hooks do nothing, or provide sensible defaults? Depends on context. Empty implementations for optional behavior; sensible defaults for common cases.

**How Many Abstract Methods**: Too many abstract methods burden subclass implementers. Too few limit customization. Find the right balance for your use case.

**Template Granularity**: Should template method be coarse (few large steps) or fine (many small steps)? Coarser templates are simpler; finer templates allow more customization points.

## Key Takeaways

1. Template Method defines algorithm skeleton in base class, delegates steps to subclasses
2. Uses inheritance to share code and enforce algorithm structure
3. Three method types: template (fixed), abstract (must override), hook (can override)
4. Inverts control: framework calls subclass code, not vice versa
5. Trade-off: Reduced flexibility for increased code reuse and consistency
6. Best for algorithms with fixed structure but variable step implementations
7. Alternative to Strategy when structure matters more than algorithm flexibility
8. Watch for fragile base class problem; keep base class stable
