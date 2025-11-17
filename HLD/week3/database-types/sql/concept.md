# SQL Databases - Core Concepts

## What Problem Do SQL Databases Solve?

Imagine you're building a banking application. You need to ensure that when money moves between accounts, either both the debit and credit happen, or neither does. You also need to enforce rules like "account balance cannot be negative" and maintain relationships between customers, accounts, and transactions. This is where SQL databases excel.

SQL (Structured Query Language) databases are built around the relational model, where data is organized into tables with predefined relationships. They provide strong guarantees about data integrity and consistency.

## How SQL Databases Work

### Relational Model

Data is organized into tables (relations) with rows and columns:

```
Users Table:
+---------+------------------+----------+
| user_id | email            | created  |
+---------+------------------+----------+
| 1       | alice@email.com  | 2024-01-15|
| 2       | bob@email.com    | 2024-01-16|
+---------+------------------+----------+

Orders Table:
+----------+---------+--------+------------+
| order_id | user_id | amount | order_date |
+----------+---------+--------+------------+
| 101      | 1       | 99.99  | 2024-01-20 |
| 102      | 1       | 49.99  | 2024-01-21 |
| 103      | 2       | 149.99 | 2024-01-22 |
+----------+---------+--------+------------+
```

### Schema

The structure is defined upfront with strict types and constraints:

```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created DATE NOT NULL,
    balance DECIMAL(10,2) DEFAULT 0 CHECK (balance >= 0)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    order_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Relationships

Tables are connected through foreign keys:

- One-to-Many: One user has many orders
- Many-to-Many: Many students enroll in many courses (requires junction table)
- One-to-One: One user has one profile

### Querying with SQL

SQL provides powerful declarative queries:

```sql
-- Find all orders for a specific user with total
SELECT u.email, COUNT(o.order_id) as order_count, SUM(o.amount) as total_spent
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE u.email = 'alice@email.com'
GROUP BY u.email;
```

The database optimizer figures out the most efficient way to execute this query.

## ACID Properties

SQL databases guarantee ACID properties for transactions:

### Atomicity
All operations in a transaction succeed or all fail. No partial updates.

```sql
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- If either UPDATE fails, both are rolled back
```

### Consistency
Database moves from one valid state to another. Constraints are always enforced.

```sql
-- This fails if balance would go negative:
UPDATE accounts SET balance = balance - 500 WHERE id = 1;
-- Error: Check constraint violated
```

### Isolation
Concurrent transactions don't interfere with each other.

```sql
-- Transaction 1:
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- Sees 1000
-- Meanwhile, Transaction 2 updates the balance
SELECT balance FROM accounts WHERE id = 1;  -- Still sees 1000 (isolation)
COMMIT;
```

### Durability
Once committed, data survives crashes.

```sql
COMMIT;  -- After this, data is permanently stored
-- Even if server crashes now, the data is safe
```

## Key Characteristics

### 1. Structured Data
Every row in a table has the same columns. Schema must be defined before inserting data.

### 2. Strong Typing
Each column has a specific data type enforced by the database.

```sql
-- This fails:
INSERT INTO users (user_id, email, created)
VALUES (3, 'charlie@email.com', 'not-a-date');
-- Error: Invalid date format
```

### 3. Referential Integrity
Foreign keys ensure relationships are valid.

```sql
-- This fails if user_id 999 doesn't exist:
INSERT INTO orders (order_id, user_id, amount, order_date)
VALUES (104, 999, 100.00, '2024-01-23');
-- Error: Foreign key constraint violated
```

### 4. Complex Queries
JOINs, subqueries, aggregations, and window functions are native.

```sql
-- Find users who haven't ordered in last 30 days
SELECT u.email
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
    AND o.order_date > CURRENT_DATE - INTERVAL '30 days'
WHERE o.order_id IS NULL;
```

### 5. Vertical Scaling
Traditionally scaled by adding more CPU, RAM, and faster disks to a single server.

## Popular SQL Databases

### PostgreSQL
- Open source, feature-rich
- Excellent for complex queries and data integrity
- JSONB support for semi-structured data
- Strong support for concurrency (MVCC)

### MySQL
- Most popular open source database
- Fast for read-heavy workloads
- Used by Facebook, Twitter, YouTube
- InnoDB engine provides ACID compliance

### Oracle Database
- Enterprise-grade, feature-complete
- Excellent performance and scalability
- Advanced features (partitioning, RAC)
- High cost

### Microsoft SQL Server
- Tight integration with Microsoft ecosystem
- Good for Windows-based applications
- Advanced analytics features

## How Data is Stored

### B-Tree Structure
Most SQL databases use B-trees for indexes and primary keys:

```
            [50]
           /    \
       [25]      [75]
      /   \      /   \
   [10] [35]  [60] [90]
```

This allows O(log n) lookups, insertions, and range queries.

### Row-Oriented Storage
Data is stored row by row on disk:

```
Row 1: [1, 'alice@email.com', '2024-01-15']
Row 2: [2, 'bob@email.com', '2024-01-16']
Row 3: [3, 'charlie@email.com', '2024-01-17']
```

This is efficient for transactional workloads (OLTP) where you typically access all columns of a few rows.

## Evolution and Variations

### NewSQL Databases
Combine SQL benefits with horizontal scalability:
- Google Spanner
- CockroachDB
- VoltDB

### Column-Oriented SQL Databases
Store data by column for analytics workloads (OLAP):
- Amazon Redshift
- Google BigQuery
- Apache Druid

## Trade-offs

### What You Gain
- Data integrity and consistency guarantees
- Complex query capabilities with JOINs
- Mature ecosystem and tooling
- Standardized query language
- Transaction support

### What You Sacrifice
- Schema flexibility (changes can be difficult)
- Horizontal scaling complexity
- Performance at massive scale
- Rigid structure for semi-structured data
