"""
SQL Query Builder Example

Demonstrates the Builder pattern for constructing complex SQL queries.
Shows how builder simplifies creating queries with many optional clauses.
"""

from typing import List, Optional


class SQLQuery:
    """
    Represents a complete SQL query.

    This is the "product" being built by QueryBuilder.
    """

    def __init__(
        self,
        select_fields: List[str],
        from_table: str,
        joins: List[str],
        where_conditions: List[str],
        group_by_fields: List[str],
        having_conditions: List[str],
        order_by_fields: List[str],
        limit_value: Optional[int],
        offset_value: Optional[int]
    ):
        """Initialize SQL query with all components."""
        self.select_fields = select_fields
        self.from_table = from_table
        self.joins = joins
        self.where_conditions = where_conditions
        self.group_by_fields = group_by_fields
        self.having_conditions = having_conditions
        self.order_by_fields = order_by_fields
        self.limit_value = limit_value
        self.offset_value = offset_value

        # Validate the query
        self._validate()

    def _validate(self):
        """Validate query structure."""
        if not self.from_table:
            raise ValueError("Query must have a FROM clause")

        if self.having_conditions and not self.group_by_fields:
            raise ValueError("HAVING clause requires GROUP BY")

    def to_sql(self) -> str:
        """Generate SQL string from query components."""
        parts = []

        # SELECT clause
        if self.select_fields:
            fields = ", ".join(self.select_fields)
            parts.append(f"SELECT {fields}")
        else:
            parts.append("SELECT *")

        # FROM clause
        parts.append(f"FROM {self.from_table}")

        # JOIN clauses
        for join in self.joins:
            parts.append(join)

        # WHERE clause
        if self.where_conditions:
            conditions = " AND ".join(self.where_conditions)
            parts.append(f"WHERE {conditions}")

        # GROUP BY clause
        if self.group_by_fields:
            fields = ", ".join(self.group_by_fields)
            parts.append(f"GROUP BY {fields}")

        # HAVING clause
        if self.having_conditions:
            conditions = " AND ".join(self.having_conditions)
            parts.append(f"HAVING {conditions}")

        # ORDER BY clause
        if self.order_by_fields:
            fields = ", ".join(self.order_by_fields)
            parts.append(f"ORDER BY {fields}")

        # LIMIT clause
        if self.limit_value is not None:
            parts.append(f"LIMIT {self.limit_value}")

        # OFFSET clause
        if self.offset_value is not None:
            parts.append(f"OFFSET {self.offset_value}")

        return " ".join(parts)

    def __str__(self):
        """String representation of query."""
        return self.to_sql()


class QueryBuilder:
    """
    Builder for constructing SQL queries fluently.

    Provides a readable, step-by-step way to build complex queries.
    """

    def __init__(self):
        """Initialize builder with empty state."""
        self._select_fields = []
        self._from_table = None
        self._joins = []
        self._where_conditions = []
        self._group_by_fields = []
        self._having_conditions = []
        self._order_by_fields = []
        self._limit_value = None
        self._offset_value = None

    def select(self, *fields: str) -> "QueryBuilder":
        """Add fields to SELECT clause."""
        self._select_fields.extend(fields)
        return self

    def from_table(self, table: str) -> "QueryBuilder":
        """Set FROM table."""
        self._from_table = table
        return self

    def inner_join(self, table: str, condition: str) -> "QueryBuilder":
        """Add INNER JOIN clause."""
        self._joins.append(f"INNER JOIN {table} ON {condition}")
        return self

    def left_join(self, table: str, condition: str) -> "QueryBuilder":
        """Add LEFT JOIN clause."""
        self._joins.append(f"LEFT JOIN {table} ON {condition}")
        return self

    def right_join(self, table: str, condition: str) -> "QueryBuilder":
        """Add RIGHT JOIN clause."""
        self._joins.append(f"RIGHT JOIN {table} ON {condition}")
        return self

    def where(self, condition: str) -> "QueryBuilder":
        """Add WHERE condition (multiple calls are AND-ed)."""
        self._where_conditions.append(condition)
        return self

    def group_by(self, *fields: str) -> "QueryBuilder":
        """Add GROUP BY fields."""
        self._group_by_fields.extend(fields)
        return self

    def having(self, condition: str) -> "QueryBuilder":
        """Add HAVING condition."""
        self._having_conditions.append(condition)
        return self

    def order_by(self, field: str, direction: str = "ASC") -> "QueryBuilder":
        """Add ORDER BY field with direction."""
        self._order_by_fields.append(f"{field} {direction}")
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """Set LIMIT value."""
        self._limit_value = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """Set OFFSET value."""
        self._offset_value = offset
        return self

    def build(self) -> SQLQuery:
        """Build and return the final SQLQuery object."""
        return SQLQuery(
            select_fields=self._select_fields.copy(),
            from_table=self._from_table,
            joins=self._joins.copy(),
            where_conditions=self._where_conditions.copy(),
            group_by_fields=self._group_by_fields.copy(),
            having_conditions=self._having_conditions.copy(),
            order_by_fields=self._order_by_fields.copy(),
            limit_value=self._limit_value,
            offset_value=self._offset_value
        )

    def reset(self) -> "QueryBuilder":
        """Reset builder to empty state."""
        self.__init__()
        return self


def demonstrate_simple_query():
    """Demonstrate simple query construction."""
    print("="*70)
    print("SIMPLE QUERY")
    print("="*70)

    query = (QueryBuilder()
             .select("id", "name", "email")
             .from_table("users")
             .where("age > 18")
             .where("status = 'active'")
             .order_by("name", "ASC")
             .limit(10)
             .build())

    print("\nGenerated SQL:")
    print(query.to_sql())


def demonstrate_complex_query():
    """Demonstrate complex query with joins and aggregations."""
    print("\n" + "="*70)
    print("COMPLEX QUERY WITH JOINS")
    print("="*70)

    query = (QueryBuilder()
             .select("u.id", "u.name", "COUNT(p.id) as post_count")
             .from_table("users u")
             .left_join("posts p", "u.id = p.user_id")
             .where("u.created_at > '2020-01-01'")
             .where("u.status = 'active'")
             .group_by("u.id", "u.name")
             .having("COUNT(p.id) > 5")
             .order_by("post_count", "DESC")
             .limit(20)
             .build())

    print("\nGenerated SQL:")
    print(query.to_sql())


def demonstrate_pagination():
    """Demonstrate pagination using LIMIT and OFFSET."""
    print("\n" + "="*70)
    print("PAGINATION QUERIES")
    print("="*70)

    page_size = 10

    for page in range(1, 4):
        offset = (page - 1) * page_size

        query = (QueryBuilder()
                 .select("id", "title", "created_at")
                 .from_table("articles")
                 .where("published = true")
                 .order_by("created_at", "DESC")
                 .limit(page_size)
                 .offset(offset)
                 .build())

        print(f"\nPage {page}:")
        print(f"  {query.to_sql()}")


def demonstrate_validation():
    """Demonstrate query validation."""
    print("\n" + "="*70)
    print("QUERY VALIDATION")
    print("="*70)

    print("\n1. Invalid: HAVING without GROUP BY")
    try:
        query = (QueryBuilder()
                 .select("name", "COUNT(*)")
                 .from_table("users")
                 .having("COUNT(*) > 5")
                 .build())
    except ValueError as e:
        print(f"   Error (expected): {e}")

    print("\n2. Invalid: Missing FROM clause")
    try:
        query = (QueryBuilder()
                 .select("id", "name")
                 .build())
    except ValueError as e:
        print(f"   Error (expected): {e}")


def compare_approaches():
    """Compare builder with string concatenation."""
    print("\n" + "="*70)
    print("COMPARISON: Builder vs String Concatenation")
    print("="*70)

    print("\n1. String concatenation (error-prone):")
    sql = "SELECT id, name FROM users"
    sql += " WHERE age > 18"
    sql += " AND status = 'active'"
    sql += " ORDER BY name ASC"
    sql += " LIMIT 10"
    print(f"   {sql}")
    print("   (Easy to make syntax errors!)")

    print("\n2. Builder pattern (safe and readable):")
    print("   QueryBuilder()")
    print("       .select('id', 'name')")
    print("       .from_table('users')")
    print("       .where('age > 18')")
    print("       .where('status = \"active\"')")
    print("       .order_by('name', 'ASC')")
    print("       .limit(10)")
    print("       .build()")
    print("   (Self-documenting and validated!)")


if __name__ == "__main__":
    demonstrate_simple_query()
    demonstrate_complex_query()
    demonstrate_pagination()
    demonstrate_validation()
    compare_approaches()

    print("\n" + "="*70)
    print("KEY POINTS")
    print("="*70)
    print("""
1. Builder creates complex queries in readable, step-by-step manner
2. Each method adds one clause - clear and focused
3. Validation happens at build() time
4. Prevents common SQL syntax errors
5. Easy to add/remove clauses without breaking query
6. More maintainable than string concatenation
7. Type-safe and IDE-friendly
    """)
