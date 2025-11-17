# When to Use SQL Databases

## Strong Consistency Requirements

Use SQL when data integrity is critical and you cannot tolerate inconsistencies.

### Financial Applications
Banking systems must ensure accurate account balances and transaction records.

**Example: Money Transfer**
```sql
BEGIN TRANSACTION;
    -- Debit sender
    UPDATE accounts SET balance = balance - 100.00
    WHERE account_id = 'ACC001';

    -- Credit receiver
    UPDATE accounts SET balance = balance + 100.00
    WHERE account_id = 'ACC002';

    -- Record transaction
    INSERT INTO transactions (from_account, to_account, amount, timestamp)
    VALUES ('ACC001', 'ACC002', 100.00, NOW());
COMMIT;
```

If any part fails, the entire transaction rolls back. The money never disappears or gets duplicated.

### E-commerce Order Processing
Order, payment, and inventory must be updated atomically.

**Example: Place Order**
```sql
BEGIN TRANSACTION;
    -- Create order
    INSERT INTO orders (user_id, total_amount)
    VALUES (123, 299.99) RETURNING order_id;

    -- Add order items
    INSERT INTO order_items (order_id, product_id, quantity, price)
    VALUES (456, 789, 2, 149.99);

    -- Reduce inventory
    UPDATE products SET stock_quantity = stock_quantity - 2
    WHERE product_id = 789 AND stock_quantity >= 2;

    -- If stock insufficient, this UPDATE affects 0 rows, transaction fails
COMMIT;
```

## Complex Relationships Between Data

Use SQL when your data has many relationships and you need to query across them.

### Social Network
Users, posts, comments, likes, follows all interconnected.

**Example: Get User Feed**
```sql
-- Get posts from users I follow, with like counts
SELECT p.post_id, p.content, u.username, COUNT(l.like_id) as like_count
FROM posts p
JOIN users u ON p.user_id = u.user_id
JOIN follows f ON p.user_id = f.followed_user_id
LEFT JOIN likes l ON p.post_id = l.post_id
WHERE f.follower_user_id = 123
    AND p.created_at > NOW() - INTERVAL '7 days'
GROUP BY p.post_id, p.content, u.username
ORDER BY p.created_at DESC
LIMIT 20;
```

### Enterprise Resource Planning (ERP)
Customers, orders, invoices, payments, shipping, inventory all related.

**Example: Customer Order History**
```sql
-- Complete customer order information
SELECT
    c.customer_name,
    o.order_id,
    o.order_date,
    oi.product_name,
    oi.quantity,
    p.payment_status,
    s.shipping_status
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN payments p ON o.order_id = p.order_id
LEFT JOIN shipments s ON o.order_id = s.order_id
WHERE c.customer_id = 456
ORDER BY o.order_date DESC;
```

## Structured Data with Defined Schema

Use SQL when your data structure is well-defined and unlikely to change frequently.

### HR Management System
Employee records with consistent fields.

```sql
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department_id INT NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    manager_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);
```

All employees have the same attributes. Schema is stable.

### Inventory Management
Products, categories, suppliers with well-defined attributes.

```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category_id INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
    reorder_level INT NOT NULL,
    supplier_id INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);
```

## ACID Compliance is Required

Use SQL when you need all four ACID properties.

### Booking Systems
Hotel rooms, airplane seats, event tickets must not be double-booked.

**Example: Reserve Hotel Room**
```sql
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
    -- Check availability
    SELECT room_id FROM rooms
    WHERE hotel_id = 5
        AND room_type = 'deluxe'
        AND room_id NOT IN (
            SELECT room_id FROM reservations
            WHERE check_in_date < '2024-02-15'
                AND check_out_date > '2024-02-10'
        )
    LIMIT 1
    FOR UPDATE;  -- Lock the room

    -- Create reservation
    INSERT INTO reservations (room_id, guest_id, check_in_date, check_out_date)
    VALUES (101, 789, '2024-02-10', '2024-02-15');
COMMIT;
```

Serializable isolation ensures no other transaction can book the same room.

### Healthcare Records
Patient data, prescriptions, and medical history must be accurate and consistent.

## Reporting and Analytics on Structured Data

Use SQL when you need complex aggregations and reports.

### Sales Analytics
```sql
-- Monthly sales by region and product category
SELECT
    DATE_TRUNC('month', o.order_date) as month,
    r.region_name,
    pc.category_name,
    COUNT(DISTINCT o.order_id) as order_count,
    SUM(oi.quantity * oi.unit_price) as revenue,
    AVG(oi.quantity * oi.unit_price) as avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN product_categories pc ON p.category_id = pc.category_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN regions r ON c.region_id = r.region_id
WHERE o.order_date >= '2024-01-01'
GROUP BY 1, 2, 3
ORDER BY 1 DESC, 5 DESC;
```

### Business Intelligence
Dashboard queries with multiple JOINs and aggregations.

## When NOT to Use SQL

### Avoid SQL When:

**1. Schema Changes Frequently**
If your data model evolves rapidly, rigid schemas become a bottleneck.

**2. Massive Scale (Billions of Records)**
Horizontal sharding becomes complex. Consider NoSQL alternatives.

**3. Semi-Structured or Unstructured Data**
Storing JSON documents with varying fields is awkward in SQL.

**4. High Write Throughput**
ACID overhead can limit write performance. NoSQL may be faster.

**5. Eventual Consistency is Acceptable**
If you don't need immediate consistency, NoSQL offers better availability.

## Decision Framework

Use SQL if you answer "yes" to most of these:

- [ ] Do you need ACID transactions?
- [ ] Is your data highly relational?
- [ ] Do you need complex JOINs and aggregations?
- [ ] Is your schema relatively stable?
- [ ] Do you need strong consistency guarantees?
- [ ] Is your data structured and fits into tables?
- [ ] Do you prioritize correctness over availability?

## Real-World Examples

### Companies Using SQL as Primary Database

**Stripe (PostgreSQL)**
- Payment processing requires ACID guarantees
- Complex financial transactions and reporting
- Strong consistency for account balances

**Airbnb (MySQL)**
- Booking system needs transaction support
- Complex relationships (users, listings, reservations)
- Moved from MongoDB to MySQL for consistency

**Stack Overflow (SQL Server)**
- Structured data (questions, answers, comments)
- Complex queries for searching and ranking
- Excellent read performance with proper indexing

**GitHub (MySQL)**
- Repositories, users, commits all highly related
- ACID for critical operations
- Later added other databases for specific use cases

## Migration Considerations

### Moving to SQL From NoSQL

Consider migration when:
- You need stronger consistency guarantees
- Your queries have become too complex without JOINs
- Data integrity issues are occurring
- You need better transaction support

### Adding SQL Alongside NoSQL (Polyglot Persistence)

Use both:
- SQL for transactional data (orders, payments)
- NoSQL for session data, caching, real-time analytics
- Each database for its strengths

Example:
- PostgreSQL for user accounts and orders
- Redis for session storage
- Elasticsearch for product search
- Cassandra for activity logs
