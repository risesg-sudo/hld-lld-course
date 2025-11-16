"""
Template Method Pattern - Define algorithm skeleton in base class, defer steps to subclasses.

This module demonstrates various template method implementations:
1. Data mining pipeline (parse, analyze, extract, output)
2. Game development loop (initialize, update, render, input)
3. Report generation (header, content, footer, format)
4. Document processing (load, parse, transform, save)
5. Beverage preparation (different drink types)
6. Task execution with hooks (template with optional steps)

Key Learning Points:
- Template method defines algorithm structure in base class
- Concrete steps implemented in subclasses
- Hook methods provide optional override points
- Inverts control - framework calls your code
- Good for code reuse in inheritance hierarchies
- Provides consistent structure across implementations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# 1. DATA MINING TEMPLATE METHOD
# ============================================================================

class DataMiner(ABC):
    """
    Template method for data mining process.

    Template method defines the algorithm skeleton:
    1. Open data source
    2. Extract raw data
    3. Parse data
    4. Analyze data
    5. Generate report
    6. Save report
    """

    def mine(self, path: str) -> None:
        """
        Template method defining data mining algorithm.

        This is the algorithm skeleton - steps are implemented by subclasses.
        """
        print(f"\n{'='*60}")
        print(f"Mining data from: {path}")
        print(f"{'='*60}")

        raw_data = self.open_file(path)
        data = self.extract_data(raw_data)
        parsed_data = self.parse_data(data)
        analysis = self.analyze_data(parsed_data)
        report = self.generate_report(analysis)
        self.save_report(report)

        print(f"Data mining complete!")

    @abstractmethod
    def open_file(self, path: str) -> str:
        """Open and read data source."""
        pass

    @abstractmethod
    def extract_data(self, raw: str) -> List[str]:
        """Extract relevant data from raw source."""
        pass

    @abstractmethod
    def parse_data(self, data: List[str]) -> List[Dict]:
        """Parse extracted data into structured format."""
        pass

    @abstractmethod
    def analyze_data(self, data: List[Dict]) -> Dict:
        """Analyze structured data."""
        pass

    def generate_report(self, analysis: Dict) -> str:
        """Hook method - default implementation, can be overridden."""
        return f"Analysis Report: {analysis}"

    def save_report(self, report: str) -> None:
        """Hook method - default implementation, can be overridden."""
        print(f"Saving report: {report[:50]}...")


class CSVDataMiner(DataMiner):
    """Data miner for CSV files."""

    def open_file(self, path: str) -> str:
        """Simulate opening CSV file."""
        print(f"Opening CSV file: {path}")
        return "name,age,salary\nJohn,30,50000\nJane,28,55000\nBob,35,60000"

    def extract_data(self, raw: str) -> List[str]:
        """Extract lines from CSV."""
        print(f"Extracting CSV data...")
        lines = raw.split('\n')
        return lines[1:]  # Skip header

    def parse_data(self, data: List[str]) -> List[Dict]:
        """Parse CSV into dictionaries."""
        print(f"Parsing CSV data...")
        parsed = []
        for line in data:
            if line.strip():
                name, age, salary = line.split(',')
                parsed.append({
                    'name': name,
                    'age': int(age),
                    'salary': int(salary)
                })
        return parsed

    def analyze_data(self, data: List[Dict]) -> Dict:
        """Analyze CSV data."""
        print(f"Analyzing {len(data)} records...")
        return {
            'count': len(data),
            'avg_age': sum(d['age'] for d in data) / len(data),
            'avg_salary': sum(d['salary'] for d in data) / len(data),
            'max_salary': max(d['salary'] for d in data)
        }


class JSONDataMiner(DataMiner):
    """Data miner for JSON files."""

    def open_file(self, path: str) -> str:
        """Simulate opening JSON file."""
        print(f"Opening JSON file: {path}")
        return '[{"name":"John","age":30},{"name":"Jane","age":28}]'

    def extract_data(self, raw: str) -> List[str]:
        """Extract JSON objects."""
        print(f"Extracting JSON data...")
        # Simulate JSON parsing
        return raw.replace('[', '').replace(']', '').split('},')

    def parse_data(self, data: List[str]) -> List[Dict]:
        """Parse JSON into dictionaries."""
        print(f"Parsing JSON data...")
        parsed = []
        for item in data:
            # Simulate JSON parsing
            if 'name' in item:
                parsed.append({
                    'name': 'parsed_user',
                    'data': item[:30]
                })
        return parsed

    def analyze_data(self, data: List[Dict]) -> Dict:
        """Analyze JSON data."""
        print(f"Analyzing {len(data)} JSON objects...")
        return {'items': len(data), 'source': 'JSON'}

    def generate_report(self, analysis: Dict) -> str:
        """Override to customize report format."""
        return f"JSON Analysis: {analysis['items']} items processed from JSON"


# ============================================================================
# 2. GAME DEVELOPMENT TEMPLATE METHOD
# ============================================================================

class Game(ABC):
    """
    Template method for game loop.

    Defines game lifecycle:
    1. Initialize game
    2. Game loop:
       - Handle input
       - Update game state
       - Render frame
    3. Cleanup
    """

    def __init__(self, name: str):
        self.name = name
        self.running = False
        self.frame_count = 0

    def run(self, frames: int = 5) -> None:
        """Template method - execute game."""
        print(f"\n{'='*60}")
        print(f"Starting game: {self.name}")
        print(f"{'='*60}")

        self.initialize()
        self.running = True

        for i in range(frames):
            self.handle_input(f"Input {i}")
            self.update(f"Frame {i}")
            self.render()
            self.frame_count += 1

        self.cleanup()

    @abstractmethod
    def initialize(self) -> None:
        """Initialize game resources."""
        pass

    @abstractmethod
    def handle_input(self, input_data: str) -> None:
        """Handle user input."""
        pass

    @abstractmethod
    def update(self, frame_info: str) -> None:
        """Update game state."""
        pass

    def render(self) -> None:
        """Hook method - default rendering."""
        print(f"  Rendering frame {self.frame_count}...")

    def cleanup(self) -> None:
        """Hook method - default cleanup."""
        print(f"Cleaning up game resources...")
        self.running = False


class ArcadeGame(Game):
    """Arcade game implementation."""

    def __init__(self):
        super().__init__("Arcade Game")
        self.score = 0

    def initialize(self) -> None:
        """Initialize arcade game."""
        print(f"Initializing arcade game...")
        print(f"  Loading sprites")
        print(f"  Setting up score system")
        self.score = 0

    def handle_input(self, input_data: str) -> None:
        """Handle arcade input."""
        print(f"  Input: Player moves left/right")

    def update(self, frame_info: str) -> None:
        """Update arcade game state."""
        print(f"  Updating: Enemy position, projectiles")
        self.score += 10

    def render(self) -> None:
        """Render arcade game."""
        print(f"  Rendering: Score={self.score}")


class PuzzleGame(Game):
    """Puzzle game implementation."""

    def __init__(self):
        super().__init__("Puzzle Game")
        self.moves = 0

    def initialize(self) -> None:
        """Initialize puzzle game."""
        print(f"Initializing puzzle game...")
        print(f"  Generating puzzle")
        print(f"  Setting up move counter")

    def handle_input(self, input_data: str) -> None:
        """Handle puzzle input."""
        print(f"  Input: Player selects tile")
        self.moves += 1

    def update(self, frame_info: str) -> None:
        """Update puzzle state."""
        print(f"  Updating: Checking valid moves")

    def render(self) -> None:
        """Render puzzle."""
        print(f"  Rendering: Moves={self.moves}")

    def cleanup(self) -> None:
        """Cleanup puzzle game."""
        super().cleanup()
        print(f"Final moves: {self.moves}")


class RPGGame(Game):
    """RPG game implementation."""

    def __init__(self):
        super().__init__("RPG Game")
        self.health = 100
        self.experience = 0

    def initialize(self) -> None:
        """Initialize RPG."""
        print(f"Initializing RPG...")
        print(f"  Loading world data")
        print(f"  Creating character")
        self.health = 100
        self.experience = 0

    def handle_input(self, input_data: str) -> None:
        """Handle RPG input."""
        print(f"  Input: Movement, attack, use item")

    def update(self, frame_info: str) -> None:
        """Update RPG state."""
        print(f"  Updating: NPC AI, combat system, physics")
        self.experience += 5

    def render(self) -> None:
        """Render RPG."""
        print(f"  Rendering: Health={self.health}, XP={self.experience}")


# ============================================================================
# 3. REPORT GENERATION TEMPLATE METHOD
# ============================================================================

class Report(ABC):
    """
    Template method for report generation.

    Report structure:
    1. Create header
    2. Create title
    3. Create body
    4. Create footer
    5. Format report
    """

    def generate(self) -> str:
        """Template method - generate report."""
        report = ""
        report += self.get_header()
        report += self.get_title()
        report += self.get_body()
        report += self.get_footer()
        return self.format_report(report)

    @abstractmethod
    def get_header(self) -> str:
        """Get report header."""
        pass

    @abstractmethod
    def get_title(self) -> str:
        """Get report title."""
        pass

    @abstractmethod
    def get_body(self) -> str:
        """Get report body."""
        pass

    def get_footer(self) -> str:
        """Hook method - default footer."""
        return f"\nGenerated: {datetime.now()}\n"

    def format_report(self, report: str) -> str:
        """Hook method - default formatting."""
        return report


class SalesReport(Report):
    """Sales report implementation."""

    def get_header(self) -> str:
        return "SALES REPORT\n" + "="*40 + "\n"

    def get_title(self) -> str:
        return "Monthly Sales Report\n\n"

    def get_body(self) -> str:
        return """Q1 Sales: $100,000
Q2 Sales: $120,000
Q3 Sales: $150,000
Q4 Sales: $200,000

Total Annual Sales: $570,000
Growth Rate: 15%
"""

    def get_footer(self) -> str:
        return f"\nReport Period: {datetime.now().year}\n"


class FinancialReport(Report):
    """Financial report implementation."""

    def get_header(self) -> str:
        return "FINANCIAL REPORT\n" + "-"*40 + "\n"

    def get_title(self) -> str:
        return "Annual Financial Statement\n\n"

    def get_body(self) -> str:
        return """Revenue: $1,000,000
Expenses: $600,000
Profit: $400,000
Profit Margin: 40%

Cash Flow: Positive
Debt: Manageable
"""

    def format_report(self, report: str) -> str:
        """Override formatting for financial report."""
        return f"[CONFIDENTIAL]\n{report}\n[END CONFIDENTIAL]"


class EmployeeReport(Report):
    """Employee report implementation."""

    def get_header(self) -> str:
        return "EMPLOYEE REPORT\n" + "*"*40 + "\n"

    def get_title(self) -> str:
        return "Team Performance Report\n\n"

    def get_body(self) -> str:
        return """Total Employees: 50
New Hires: 5
Departures: 2
Promotions: 3

Average Salary: $75,000
Satisfaction Score: 8.5/10
Retention Rate: 95%
"""


# ============================================================================
# 4. BEVERAGE PREPARATION TEMPLATE METHOD
# ============================================================================

class Beverage(ABC):
    """
    Template method for beverage preparation.

    Preparation steps:
    1. Boil water
    2. Brew ingredient
    3. Pour into cup
    4. Add condiments
    """

    def prepare(self) -> None:
        """Template method - prepare beverage."""
        print(f"\nPreparing {self.__class__.__name__}...")
        self.boil_water()
        self.brew()
        self.pour_cup()
        self.add_condiments()
        print(f"{self.__class__.__name__} ready!")

    def boil_water(self) -> None:
        """Default implementation - can be overridden."""
        print(f"  Boiling water...")

    @abstractmethod
    def brew(self) -> None:
        """Brew the beverage."""
        pass

    def pour_cup(self) -> None:
        """Default implementation - can be overridden."""
        print(f"  Pouring into cup...")

    def add_condiments(self) -> None:
        """Hook method - subclasses can override."""
        print(f"  No condiments")


class Coffee(Beverage):
    """Coffee implementation."""

    def brew(self) -> None:
        print(f"  Brewing coffee grounds...")

    def add_condiments(self) -> None:
        print(f"  Adding sugar and cream...")


class Tea(Beverage):
    """Tea implementation."""

    def brew(self) -> None:
        print(f"  Steeping tea bag...")

    def add_condiments(self) -> None:
        print(f"  Adding honey and lemon...")


class HotChocolate(Beverage):
    """Hot chocolate implementation."""

    def brew(self) -> None:
        print(f"  Mixing cocoa powder...")

    def add_condiments(self) -> None:
        print(f"  Adding whipped cream and marshmallows...")


# ============================================================================
# 5. SORTING WITH TEMPLATE METHOD
# ============================================================================

class SortingAlgorithm(ABC):
    """
    Template method for sorting.

    Common steps:
    1. Validate input
    2. Initialize
    3. Sort
    4. Verify result
    """

    def sort(self, arr: List[int]) -> List[int]:
        """Template method - sort array."""
        self.validate(arr)
        self.initialize(arr)
        self.do_sort(arr)
        self.verify(arr)
        return arr

    def validate(self, arr: List[int]) -> None:
        """Validate input."""
        if not isinstance(arr, list):
            raise ValueError("Input must be a list")
        print(f"  Validating input...")

    def initialize(self, arr: List[int]) -> None:
        """Hook method - initialization."""
        print(f"  Initializing with {len(arr)} elements...")

    @abstractmethod
    def do_sort(self, arr: List[int]) -> None:
        """Perform sorting."""
        pass

    def verify(self, arr: List[int]) -> None:
        """Verify sorted result."""
        for i in range(len(arr) - 1):
            if arr[i] > arr[i + 1]:
                raise ValueError("Array not properly sorted")
        print(f"  Verification passed!")


class BubbleSort(SortingAlgorithm):
    """Bubble sort implementation."""

    def do_sort(self, arr: List[int]) -> None:
        print(f"  Bubble sorting...")
        for i in range(len(arr)):
            for j in range(len(arr) - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]


class QuickSort(SortingAlgorithm):
    """Quick sort implementation."""

    def do_sort(self, arr: List[int]) -> None:
        print(f"  Quick sorting...")
        self._quick_sort(arr, 0, len(arr) - 1)

    def _quick_sort(self, arr, low, high):
        if low < high:
            pi = self._partition(arr, low, high)
            self._quick_sort(arr, low, pi - 1)
            self._quick_sort(arr, pi + 1, high)

    def _partition(self, arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] < pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1


# ============================================================================
# 6. DEMONSTRATION
# ============================================================================

def demo_data_mining():
    """Demonstrate data mining template method."""
    print("\n" + "="*60)
    print("TEMPLATE METHOD - DATA MINING EXAMPLE")
    print("="*60)

    # CSV mining
    csv_miner = CSVDataMiner()
    csv_miner.mine("data.csv")

    # JSON mining
    json_miner = JSONDataMiner()
    json_miner.mine("data.json")


def demo_game_loop():
    """Demonstrate game template method."""
    print("\n" + "="*60)
    print("TEMPLATE METHOD - GAME LOOP EXAMPLE")
    print("="*60)

    arcade = ArcadeGame()
    arcade.run(frames=3)

    puzzle = PuzzleGame()
    puzzle.run(frames=3)

    rpg = RPGGame()
    rpg.run(frames=3)


def demo_report_generation():
    """Demonstrate report generation template method."""
    print("\n" + "="*60)
    print("TEMPLATE METHOD - REPORT GENERATION EXAMPLE")
    print("="*60)

    print("\nSales Report:")
    print("-" * 40)
    sales_report = SalesReport()
    print(sales_report.generate())

    print("\nFinancial Report:")
    print("-" * 40)
    financial_report = FinancialReport()
    print(financial_report.generate())

    print("\nEmployee Report:")
    print("-" * 40)
    employee_report = EmployeeReport()
    print(employee_report.generate())


def demo_beverage_preparation():
    """Demonstrate beverage template method."""
    print("\n" + "="*60)
    print("TEMPLATE METHOD - BEVERAGE PREPARATION EXAMPLE")
    print("="*60)

    coffee = Coffee()
    coffee.prepare()

    tea = Tea()
    tea.prepare()

    hot_chocolate = HotChocolate()
    hot_chocolate.prepare()


def demo_sorting_with_template():
    """Demonstrate sorting with template method."""
    print("\n" + "="*60)
    print("TEMPLATE METHOD - SORTING EXAMPLE")
    print("="*60)

    arr = [64, 34, 25, 12, 22, 11, 90]
    print(f"\nOriginal array: {arr}")

    print("\nBubble Sort:")
    bubble = BubbleSort()
    result = bubble.sort(arr.copy())
    print(f"Result: {result}")

    print("\nQuick Sort:")
    quick = QuickSort()
    result = quick.sort(arr.copy())
    print(f"Result: {result}")


def demo_template_method_benefits():
    """Demonstrate template method benefits."""
    print("\n" + "="*60)
    print("TEMPLATE METHOD - BENEFITS")
    print("="*60)

    print("""
KEY BENEFITS:

1. CODE REUSE
   - Common algorithm steps in base class
   - All subclasses inherit and reuse base implementation
   - DRY principle (Don't Repeat Yourself)

2. CONSISTENT STRUCTURE
   - All subclasses follow same algorithm structure
   - Predictable behavior across implementations
   - Easier to understand codebase

3. INVERSION OF CONTROL
   - Framework defines algorithm structure
   - Your code defines specific steps
   - Similar to "Hollywood Principle" - Don't call us, we'll call you

4. FLEXIBILITY WITH CONSTRAINTS
   - Hook methods allow customization
   - Abstract methods force implementation
   - Control which parts can/must be customized

5. MAINTAINABILITY
   - Change algorithm in one place affects all implementations
   - Easy to understand what subclasses do differently
   - Clear extension points (abstract/hook methods)

6. REDUCE DUPLICATION
   - Eliminate repeated algorithm steps
   - Focus on implementation details, not structure

EXAMPLE STRUCTURE:
- Template method (public, calls helper methods)
- Abstract methods (must be implemented by subclasses)
- Hook methods (default implementation, can be overridden)
- Private methods (implementation details)
    """)


# ============================================================================
# KEY TAKEAWAYS
# ============================================================================

"""
KEY TAKEAWAYS - TEMPLATE METHOD PATTERN:

1. WHEN TO USE:
   - Multiple classes with similar algorithm structure
   - Want to enforce algorithm structure across implementations
   - Common steps can be extracted to base class
   - Different variations of same process

2. DESIGN GUIDELINES:
   - Keep template method simple and readable
   - Use abstract methods for required steps
   - Use hook methods for optional customization
   - Document the algorithm in base class

3. ABSTRACT vs HOOK METHODS:
   - Abstract: Must be implemented (raise NotImplementedError)
   - Hook: Has default implementation, can be overridden

4. COMMON PATTERNS:
   - Top-level public method (template)
   - Protected helper methods (abstract/hooks)
   - Private utility methods
   - Clear separation of concerns

5. COMPARED TO STRATEGY:
   - Template Method: Uses inheritance, algorithm structure defined
   - Strategy: Uses composition, full algorithms encapsulated
   - Choose based on: Is structure same? → Template Method
                     Different algorithms? → Strategy

6. REAL WORLD EXAMPLES:
   - Game loops
   - Data processing pipelines
   - Report generation
   - Testing frameworks
   - Request processing
   - UI rendering
   - Document processing

7. AVOIDING FRAGILE BASE CLASS:
   - Clear interface between base and derived
   - Minimal shared state
   - Well-documented hooks
   - Avoid side effects in hooks

8. MODERN ALTERNATIVES:
   - Composition with strategies
   - Dependency injection
   - Decorator pattern
   - Mix-ins (Python)
"""


if __name__ == "__main__":
    demo_data_mining()
    demo_game_loop()
    demo_report_generation()
    demo_beverage_preparation()
    demo_sorting_with_template()
    demo_template_method_benefits()

    print("\n" + "="*60)
    print("All Template Method examples completed!")
    print("="*60)
