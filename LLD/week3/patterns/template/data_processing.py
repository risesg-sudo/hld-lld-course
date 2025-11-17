"""
Template Method Pattern Example

Demonstrates how template method enforces algorithm structure
while allowing step-specific customization.
"""

from abc import ABC, abstractmethod
from typing import List, Dict


# ============================================================================
# TEMPLATE CLASS
# ============================================================================

class DataProcessor(ABC):
    """
    Template class defining data processing algorithm.

    Algorithm structure (fixed):
    1. Load data
    2. Parse data
    3. Validate data
    4. Transform data
    5. Save results

    Subclasses customize specific steps.
    """

    def process(self, filepath: str) -> None:
        """
        Template method - defines algorithm skeleton.

        This method is final (not meant to be overridden).
        It calls other methods in a specific order.
        """
        print(f"\n{'='*60}")
        print(f"Processing: {filepath}")
        print(f"{'='*60}")

        # Fixed algorithm structure
        raw_data = self.load_data(filepath)
        parsed_data = self.parse_data(raw_data)
        valid = self.validate_data(parsed_data)

        if valid:
            transformed = self.transform_data(parsed_data)
            self.save_results(transformed)
            print(f"Processing complete!")
        else:
            print(f"Validation failed - aborting")

    def load_data(self, filepath: str) -> str:
        """
        Hook method - default implementation.
        Subclasses can override if needed.
        """
        print(f"Loading data from {filepath}")
        # Simulate loading file
        return "raw_data_content"

    @abstractmethod
    def parse_data(self, raw_data: str) -> List[Dict]:
        """
        Abstract method - subclasses must implement.
        Different parsing logic for each data format.
        """
        pass

    def validate_data(self, data: List[Dict]) -> bool:
        """
        Hook method - default validation.
        Subclasses can override for custom validation.
        """
        print(f"Validating {len(data)} records")
        return len(data) > 0

    @abstractmethod
    def transform_data(self, data: List[Dict]) -> List[Dict]:
        """
        Abstract method - subclasses must implement.
        Different transformation logic for each format.
        """
        pass

    def save_results(self, data: List[Dict]) -> None:
        """
        Hook method - default save implementation.
        Subclasses can override for custom output.
        """
        print(f"Saving {len(data)} records to output")


# ============================================================================
# CONCRETE IMPLEMENTATIONS
# ============================================================================

class CSVProcessor(DataProcessor):
    """Processes CSV data files."""

    def parse_data(self, raw_data: str) -> List[Dict]:
        """Parse CSV format."""
        print("Parsing CSV format")

        # Simulate CSV parsing
        csv_data = "name,age,city\nJohn,30,NYC\nJane,25,LA\nBob,35,Chicago"
        lines = csv_data.split('\n')
        headers = lines[0].split(',')

        parsed = []
        for line in lines[1:]:
            values = line.split(',')
            record = dict(zip(headers, values))
            parsed.append(record)

        print(f"  Parsed {len(parsed)} CSV records")
        return parsed

    def transform_data(self, data: List[Dict]) -> List[Dict]:
        """Transform CSV data."""
        print("Transforming CSV data")

        # Convert age to integer, add year_born field
        transformed = []
        for record in data:
            new_record = record.copy()
            new_record['age'] = int(record['age'])
            new_record['year_born'] = 2024 - int(record['age'])
            transformed.append(new_record)

        print(f"  Added year_born field")
        return transformed


class JSONProcessor(DataProcessor):
    """Processes JSON data files."""

    def parse_data(self, raw_data: str) -> List[Dict]:
        """Parse JSON format."""
        print("Parsing JSON format")

        # Simulate JSON parsing
        json_data = [
            {"id": 1, "name": "Alice", "score": 85},
            {"id": 2, "name": "Bob", "score": 92},
            {"id": 3, "name": "Charlie", "score": 78}
        ]

        print(f"  Parsed {len(json_data)} JSON records")
        return json_data

    def transform_data(self, data: List[Dict]) -> List[Dict]:
        """Transform JSON data."""
        print("Transforming JSON data")

        # Add grade based on score
        transformed = []
        for record in data:
            new_record = record.copy()
            score = record['score']

            if score >= 90:
                grade = 'A'
            elif score >= 80:
                grade = 'B'
            elif score >= 70:
                grade = 'C'
            else:
                grade = 'F'

            new_record['grade'] = grade
            transformed.append(new_record)

        print(f"  Added grade field")
        return transformed

    def validate_data(self, data: List[Dict]) -> bool:
        """Override: Custom validation for JSON."""
        print(f"Validating {len(data)} JSON records")

        # Check all records have required fields
        for record in data:
            if 'id' not in record or 'name' not in record:
                print(f"  Validation error: Missing required fields")
                return False

        print(f"  All records valid")
        return True


# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("TEMPLATE METHOD PATTERN DEMONSTRATION")
    print("="*60)

    # Process CSV file
    csv_processor = CSVProcessor()
    csv_processor.process("data.csv")

    # Process JSON file
    json_processor = JSONProcessor()
    json_processor.process("data.json")

    print("\n" + "="*60)
    print("Key Observations:")
    print("  - Same algorithm structure (load→parse→validate→transform→save)")
    print("  - CSV and JSON differ only in parse/transform steps")
    print("  - Template method enforces the sequence")
    print("  - Subclasses can't change the algorithm flow")
    print("  - Common code (load, save) written once in base class")
    print("="*60)
