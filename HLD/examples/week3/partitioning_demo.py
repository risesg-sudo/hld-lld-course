"""
Database Partitioning Demonstration

This module demonstrates different partitioning strategies used to improve
query performance and manageability of large tables.

Partitioning vs Sharding:
- Partitioning: Splitting a table within a single database
- Sharding: Splitting data across multiple databases

Partitioning Types:
1. Range Partitioning: Partition by value ranges (dates, IDs)
2. Hash Partitioning: Partition by hash function (even distribution)
3. List Partitioning: Partition by discrete values (countries, categories)

Real-World Usage:
- PostgreSQL: Native partitioning (declarative)
- MySQL: Native partitioning (declarative)
- Oracle: Advanced partitioning features
- Time-series databases: Often partition by time

Benefits:
- Query performance (partition pruning)
- Maintenance (drop old partitions)
- Parallel operations
- Better I/O distribution
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib
import random


@dataclass
class SalesRecord:
    """Sample sales record for demonstrations"""

    id: int
    sale_date: datetime
    country: str
    category: str
    amount: float
    customer_id: int


class RangePartitioning:
    """
    Range Partitioning: Divide data based on value ranges

    Use Cases:
    - Time-series data (logs, events, sales)
    - Sequential IDs
    - Numeric ranges (age groups, price ranges)

    Example: Sales table partitioned by month
    - sales_2024_01: Jan 2024 sales
    - sales_2024_02: Feb 2024 sales
    - sales_2024_03: Mar 2024 sales
    """

    def __init__(self):
        self.partitions: Dict[str, List[SalesRecord]] = {}

    def create_partition(self, start_date: datetime, end_date: datetime) -> str:
        """Create a partition for a date range"""
        partition_name = f"sales_{start_date.strftime('%Y_%m')}"
        if partition_name not in self.partitions:
            self.partitions[partition_name] = []
            print(f"Created partition: {partition_name} ({start_date.date()} to {end_date.date()})")
        return partition_name

    def get_partition(self, sale_date: datetime) -> str:
        """Determine which partition a record belongs to"""
        # Partition by month
        return f"sales_{sale_date.strftime('%Y_%m')}"

    def insert(self, record: SalesRecord):
        """Insert record into appropriate partition"""
        partition_name = self.get_partition(record.sale_date)

        # Create partition if doesn't exist
        if partition_name not in self.partitions:
            start_date = record.sale_date.replace(day=1)
            # Last day of month
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
            self.create_partition(start_date, end_date)

        self.partitions[partition_name].append(record)

    def query_range(self, start_date: datetime, end_date: datetime) -> List[SalesRecord]:
        """
        Query with partition pruning

        Only scans relevant partitions instead of entire table
        """
        results = []

        # Determine which partitions to scan (partition pruning)
        current = start_date.replace(day=1)
        partitions_to_scan = set()

        while current <= end_date:
            partition_name = f"sales_{current.strftime('%Y_%m')}"
            partitions_to_scan.add(partition_name)
            # Move to next month
            current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)

        print(f"Partition pruning: Scanning {len(partitions_to_scan)} partitions: {partitions_to_scan}")

        # Scan only relevant partitions
        for partition_name in partitions_to_scan:
            if partition_name in self.partitions:
                for record in self.partitions[partition_name]:
                    if start_date <= record.sale_date <= end_date:
                        results.append(record)

        return results

    def drop_old_partitions(self, before_date: datetime):
        """
        Maintenance: Drop old partitions (much faster than DELETE)

        Example: Drop partitions older than 1 year
        """
        dropped = []
        for partition_name in list(self.partitions.keys()):
            # Extract date from partition name
            year, month = partition_name.split("_")[1:3]
            partition_date = datetime(int(year), int(month), 1)

            if partition_date < before_date:
                del self.partitions[partition_name]
                dropped.append(partition_name)

        return dropped

    def get_partition_stats(self) -> Dict[str, int]:
        """Get row count per partition"""
        return {name: len(records) for name, records in self.partitions.items()}


class HashPartitioning:
    """
    Hash Partitioning: Distribute data evenly using hash function

    Use Cases:
    - Even distribution (no hotspots)
    - No natural partitioning key
    - Load balancing

    Example: Users table partitioned by user_id hash
    - users_p0: hash(user_id) % 4 == 0
    - users_p1: hash(user_id) % 4 == 1
    - users_p2: hash(user_id) % 4 == 2
    - users_p3: hash(user_id) % 4 == 3
    """

    def __init__(self, num_partitions: int = 4):
        self.num_partitions = num_partitions
        self.partitions: Dict[int, List[SalesRecord]] = {i: [] for i in range(num_partitions)}

    def _hash(self, key: int) -> int:
        """Hash function to determine partition"""
        return key % self.num_partitions

    def get_partition(self, customer_id: int) -> int:
        """Determine which partition a record belongs to"""
        return self._hash(customer_id)

    def insert(self, record: SalesRecord):
        """Insert record into appropriate partition"""
        partition_id = self.get_partition(record.customer_id)
        self.partitions[partition_id].append(record)

    def query_by_customer(self, customer_id: int) -> List[SalesRecord]:
        """
        Query by partition key (customer_id)

        Only scans 1 partition (very efficient)
        """
        partition_id = self.get_partition(customer_id)
        print(f"Partition pruning: Scanning partition {partition_id} only")

        return [record for record in self.partitions[partition_id] if record.customer_id == customer_id]

    def query_all(self) -> List[SalesRecord]:
        """
        Query without partition key

        Must scan ALL partitions (no pruning possible)
        """
        print(f"Full table scan: Must scan all {self.num_partitions} partitions")

        results = []
        for partition_records in self.partitions.values():
            results.extend(partition_records)
        return results

    def get_partition_stats(self) -> Dict[int, int]:
        """Get row count per partition (should be roughly even)"""
        return {pid: len(records) for pid, records in self.partitions.items()}


class ListPartitioning:
    """
    List Partitioning: Partition by discrete list of values

    Use Cases:
    - Geographic partitioning (countries, regions)
    - Category partitioning (product types, departments)
    - Status partitioning (active, inactive, deleted)

    Example: Sales table partitioned by country
    - sales_us: country IN ('US', 'CA', 'MX')
    - sales_eu: country IN ('GB', 'FR', 'DE', 'IT', 'ES')
    - sales_asia: country IN ('JP', 'CN', 'IN', 'SG')
    """

    def __init__(self):
        self.partitions: Dict[str, List[SalesRecord]] = {}
        self.partition_mapping: Dict[str, str] = {}

    def create_partition(self, partition_name: str, countries: List[str]):
        """Create a partition for specific countries"""
        self.partitions[partition_name] = []

        for country in countries:
            self.partition_mapping[country] = partition_name

        print(f"Created partition: {partition_name} for countries: {countries}")

    def get_partition(self, country: str) -> Optional[str]:
        """Determine which partition a record belongs to"""
        return self.partition_mapping.get(country, "sales_other")

    def insert(self, record: SalesRecord):
        """Insert record into appropriate partition"""
        partition_name = self.get_partition(record.country)

        # Create 'other' partition if needed
        if partition_name not in self.partitions:
            self.partitions[partition_name] = []

        self.partitions[partition_name].append(record)

    def query_by_country(self, country: str) -> List[SalesRecord]:
        """
        Query by partition key (country)

        Only scans 1 partition
        """
        partition_name = self.get_partition(country)
        print(f"Partition pruning: Scanning partition '{partition_name}' only")

        if partition_name not in self.partitions:
            return []

        return [record for record in self.partitions[partition_name] if record.country == country]

    def query_by_region(self, partition_name: str) -> List[SalesRecord]:
        """Query entire region partition"""
        print(f"Partition pruning: Scanning partition '{partition_name}' only")

        return self.partitions.get(partition_name, [])

    def get_partition_stats(self) -> Dict[str, int]:
        """Get row count per partition"""
        return {name: len(records) for name, records in self.partitions.items()}


class CompositePartitioning:
    """
    Composite (Multi-Level) Partitioning

    Combine multiple partitioning strategies
    Example: Range partitioning by date, then hash partitioning by customer_id

    Structure:
    sales_2024_01_p0
    sales_2024_01_p1
    sales_2024_01_p2
    sales_2024_02_p0
    sales_2024_02_p1
    sales_2024_02_p2
    """

    def __init__(self, num_hash_partitions: int = 4):
        self.num_hash_partitions = num_hash_partitions
        self.partitions: Dict[str, List[SalesRecord]] = {}

    def get_partition(self, record: SalesRecord) -> str:
        """Determine partition using both date and customer_id"""
        # First level: Range partition by month
        month_partition = record.sale_date.strftime("%Y_%m")

        # Second level: Hash partition by customer_id
        hash_partition = record.customer_id % self.num_hash_partitions

        return f"sales_{month_partition}_p{hash_partition}"

    def insert(self, record: SalesRecord):
        """Insert into composite partition"""
        partition_name = self.get_partition(record)

        if partition_name not in self.partitions:
            self.partitions[partition_name] = []

        self.partitions[partition_name].append(record)

    def query_by_date_and_customer(self, date: datetime, customer_id: int) -> List[SalesRecord]:
        """
        Query with both partition keys

        Very efficient: Only scans 1 specific partition
        """
        month_partition = date.strftime("%Y_%m")
        hash_partition = customer_id % self.num_hash_partitions
        partition_name = f"sales_{month_partition}_p{hash_partition}"

        print(f"Partition pruning: Scanning partition '{partition_name}' only (1 of {len(self.partitions)})")

        return [
            record
            for record in self.partitions.get(partition_name, [])
            if record.customer_id == customer_id and record.sale_date.month == date.month
        ]

    def get_partition_stats(self) -> Dict[str, int]:
        """Get row count per partition"""
        return {name: len(records) for name, records in self.partitions.items()}


# ==================== DEMONSTRATION FUNCTIONS ====================


def generate_sample_data(num_records: int = 10000) -> List[SalesRecord]:
    """Generate sample sales data"""
    countries = ["US", "GB", "FR", "DE", "JP", "CN", "IN", "BR", "CA", "AU"]
    categories = ["Electronics", "Clothing", "Food", "Books", "Toys"]

    records = []
    start_date = datetime(2024, 1, 1)

    for i in range(num_records):
        record = SalesRecord(
            id=i,
            sale_date=start_date + timedelta(days=random.randint(0, 364)),  # 1 year of data
            country=random.choice(countries),
            category=random.choice(categories),
            amount=random.uniform(10, 1000),
            customer_id=random.randint(1, 10000),
        )
        records.append(record)

    return records


def demo_range_partitioning():
    """Demonstrate range partitioning by date"""
    print("=" * 80)
    print("DEMO: Range Partitioning (by Date)")
    print("=" * 80)

    # Create partitioned table
    sales_table = RangePartitioning()

    # Insert sample data
    print("\n--- Inserting Data ---")
    records = generate_sample_data(10000)
    for record in records:
        sales_table.insert(record)

    # Show partition distribution
    print("\n--- Partition Statistics ---")
    stats = sales_table.get_partition_stats()
    for partition_name, count in sorted(stats.items()):
        print(f"{partition_name}: {count:5d} records")

    # Query with partition pruning
    print("\n--- Query: Sales in January 2024 ---")
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 31)
    results = sales_table.query_range(start, end)
    print(f"Found {len(results)} records")

    # Query spanning multiple partitions
    print("\n--- Query: Sales in Q1 2024 (Jan-Mar) ---")
    start = datetime(2024, 1, 1)
    end = datetime(2024, 3, 31)
    results = sales_table.query_range(start, end)
    print(f"Found {len(results)} records")

    # Maintenance: Drop old partitions
    print("\n--- Maintenance: Drop partitions older than Oct 2024 ---")
    dropped = sales_table.drop_old_partitions(datetime(2024, 10, 1))
    print(f"Dropped partitions: {dropped}")

    print("\nBenefits:")
    print("  ✓ Fast queries on recent data (partition pruning)")
    print("  ✓ Easy to archive/delete old data (drop partition)")
    print("  ✓ Natural for time-series data")


def demo_hash_partitioning():
    """Demonstrate hash partitioning for even distribution"""
    print("\n" + "=" * 80)
    print("DEMO: Hash Partitioning (by Customer ID)")
    print("=" * 80)

    # Create hash-partitioned table
    sales_table = HashPartitioning(num_partitions=4)

    # Insert sample data
    print("\n--- Inserting Data ---")
    records = generate_sample_data(10000)
    for record in records:
        sales_table.insert(record)

    # Show even distribution
    print("\n--- Partition Statistics (Should be Even) ---")
    stats = sales_table.get_partition_stats()
    for partition_id, count in sorted(stats.items()):
        bar = "█" * (count // 50)
        print(f"Partition {partition_id}: {count:5d} records {bar}")

    avg = sum(stats.values()) / len(stats)
    print(f"\nAverage: {avg:.0f} records per partition")
    print(f"Standard Deviation: {calculate_std_dev(list(stats.values())):.1f}")

    # Query with partition pruning
    print("\n--- Query: Sales for customer_id=123 ---")
    results = sales_table.query_by_customer(123)
    print(f"Found {len(results)} records")

    # Query without partition key (inefficient)
    print("\n--- Query: All sales (no partition key) ---")
    results = sales_table.query_all()
    print(f"Found {len(results)} records")

    print("\nBenefits:")
    print("  ✓ Even distribution (no hotspots)")
    print("  ✓ Good for high-cardinality keys")
    print("  ✓ Efficient queries with partition key")

    print("\nDrawbacks:")
    print("  ✗ Queries without partition key must scan all partitions")
    print("  ✗ Range queries are inefficient")


def demo_list_partitioning():
    """Demonstrate list partitioning by country"""
    print("\n" + "=" * 80)
    print("DEMO: List Partitioning (by Country/Region)")
    print("=" * 80)

    # Create list-partitioned table
    sales_table = ListPartitioning()

    # Define partitions
    sales_table.create_partition("sales_americas", ["US", "CA", "MX", "BR"])
    sales_table.create_partition("sales_europe", ["GB", "FR", "DE", "IT", "ES"])
    sales_table.create_partition("sales_asia", ["JP", "CN", "IN", "SG", "AU"])

    # Insert sample data
    print("\n--- Inserting Data ---")
    records = generate_sample_data(10000)
    for record in records:
        sales_table.insert(record)

    # Show partition distribution
    print("\n--- Partition Statistics ---")
    stats = sales_table.get_partition_stats()
    for partition_name, count in sorted(stats.items()):
        print(f"{partition_name}: {count:5d} records")

    # Query specific country
    print("\n--- Query: Sales in US ---")
    results = sales_table.query_by_country("US")
    print(f"Found {len(results)} records")

    # Query entire region
    print("\n--- Query: All Europe Sales ---")
    results = sales_table.query_by_region("sales_europe")
    print(f"Found {len(results)} records")

    print("\nBenefits:")
    print("  ✓ Logical grouping (by region, category, etc.)")
    print("  ✓ Easy to manage region-specific data")
    print("  ✓ Data locality (co-locate related data)")
    print("  ✓ Compliance (GDPR: EU data stays in EU partition)")


def demo_composite_partitioning():
    """Demonstrate composite partitioning (range + hash)"""
    print("\n" + "=" * 80)
    print("DEMO: Composite Partitioning (Date + Hash)")
    print("=" * 80)

    # Create composite-partitioned table
    sales_table = CompositePartitioning(num_hash_partitions=3)

    # Insert sample data
    print("\n--- Inserting Data ---")
    records = generate_sample_data(10000)
    for record in records:
        sales_table.insert(record)

    # Show partition structure
    print("\n--- Partition Statistics ---")
    stats = sales_table.get_partition_stats()

    # Group by month
    monthly_totals = {}
    for partition_name, count in stats.items():
        month = "_".join(partition_name.split("_")[1:3])  # Extract YYYY_MM
        monthly_totals[month] = monthly_totals.get(month, 0) + count

    print("\nRecords per Month:")
    for month, count in sorted(monthly_totals.items()):
        print(f"{month}: {count:5d} records")

    print(f"\nTotal Partitions: {len(stats)}")

    # Query with both partition keys (very efficient)
    print("\n--- Query: Sales on Jan 15, 2024 for customer_id=500 ---")
    results = sales_table.query_by_date_and_customer(datetime(2024, 1, 15), 500)
    print(f"Found {len(results)} records")

    print("\nBenefits:")
    print("  ✓ Best of both worlds (time-based + even distribution)")
    print("  ✓ Very efficient for queries with both keys")
    print("  ✓ Scalable (can add more hash partitions)")


def demo_partition_pruning_performance():
    """Demonstrate performance benefit of partition pruning"""
    print("\n" + "=" * 80)
    print("DEMO: Partition Pruning Performance Benefit")
    print("=" * 80)

    # Create partitioned table (12 months)
    partitioned_table = RangePartitioning()

    # Create non-partitioned table (all data in one partition)
    non_partitioned = {"all_data": []}

    # Insert 100k records
    print("\n--- Inserting 100,000 Records ---")
    records = generate_sample_data(100000)

    for record in records:
        partitioned_table.insert(record)
        non_partitioned["all_data"].append(record)

    # Query January data
    print("\n--- Query: January 2024 Sales ---")

    # Partitioned: Only scans 1 partition
    print("\nPartitioned Table:")
    partitioned_stats = partitioned_table.get_partition_stats()
    january_partition_size = partitioned_stats.get("sales_2024_01", 0)
    print(f"  Rows to scan: ~{january_partition_size:,} (1 partition)")

    # Non-partitioned: Scans entire table
    print("\nNon-Partitioned Table:")
    print(f"  Rows to scan: {len(non_partitioned['all_data']):,} (entire table)")

    # Calculate performance difference
    reduction = (1 - january_partition_size / len(non_partitioned["all_data"])) * 100
    print(f"\nPartition pruning reduces scanned data by ~{reduction:.0f}%")

    print("\nKey Insight:")
    print("  Partitioning allows the database to skip irrelevant partitions,")
    print("  drastically reducing the amount of data scanned for queries.")


def calculate_std_dev(values: List[int]) -> float:
    """Calculate standard deviation"""
    avg = sum(values) / len(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    return variance**0.5


if __name__ == "__main__":
    # Run all demos
    demo_range_partitioning()
    demo_hash_partitioning()
    demo_list_partitioning()
    demo_composite_partitioning()
    demo_partition_pruning_performance()

    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. Partitioning Strategies:
   - Range: Time-series, sequential data (dates, IDs)
   - Hash: Even distribution, no hotspots
   - List: Discrete values (countries, categories, statuses)
   - Composite: Combine strategies for optimal performance

2. Benefits:
   - Query Performance: Partition pruning (skip irrelevant partitions)
   - Maintenance: Drop old partitions (much faster than DELETE)
   - Parallel Operations: Query multiple partitions in parallel
   - Scalability: Manage large tables more easily

3. Partition Pruning:
   - Database automatically skips irrelevant partitions
   - Can reduce scanned data by 90%+ for targeted queries
   - Requires queries to include partition key

4. When to Partition:
   - Table > 100GB (general guideline)
   - Clear partitioning key exists
   - Queries often filter on partition key
   - Need to archive/delete old data regularly

5. Best Practices:
   - Choose partition key based on query patterns
   - Not too many partitions (overhead)
   - Not too few partitions (defeats purpose)
   - Document partition strategy
   - Monitor partition sizes

Real-World Examples:
- Logs/Events: Range partition by timestamp (daily/monthly)
- Users: Hash partition by user_id (even distribution)
- Sales: List partition by region + Range by date (composite)
- IoT Data: Range partition by device_id and timestamp

Database Support:
- PostgreSQL: Declarative partitioning (v10+)
- MySQL: Native partitioning (InnoDB, NDB)
- Oracle: Advanced partitioning (range, hash, list, composite)
- SQL Server: Partitioning via filegroups
    """)
