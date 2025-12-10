-- Daily revenue for January 2024 using the reporting view
SELECT day::date AS day, total_sales
FROM daily_sales_totals
WHERE day >= DATE '2024-01-01' AND day < DATE '2024-02-01'
ORDER BY day;

-- Top 10 products by gross revenue
SELECT p.id, p.name, SUM(oi.quantity * oi.unit_price) AS product_revenue
FROM order_items oi
JOIN products p ON p.id = oi.product_id
GROUP BY p.id, p.name
ORDER BY product_revenue DESC
LIMIT 10;

-- Highest spending users across all time
SELECT u.id, u.full_name, SUM(oi.quantity * oi.unit_price) AS lifetime_spend
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY u.id, u.full_name
ORDER BY lifetime_spend DESC
LIMIT 10;

-- Sales totals by product category for Q1 2024
SELECT c.id, c.name, DATE_TRUNC('quarter', o.order_date) AS quarter,
       SUM(oi.quantity * oi.unit_price) AS category_sales
FROM categories c
JOIN products p ON p.category_id = c.id
JOIN order_items oi ON oi.product_id = p.id
JOIN orders o ON o.id = oi.order_id
WHERE o.order_date >= DATE '2024-01-01' AND o.order_date < DATE '2024-04-01'
GROUP BY c.id, c.name, quarter
ORDER BY quarter, category_sales DESC;

-- Orders for a specific user within a date range including totals
SELECT o.id AS order_id,
       o.order_date,
       o.status,
       SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.user_id = 42
  AND o.order_date >= DATE '2024-02-01'
  AND o.order_date < DATE '2024-03-01'
GROUP BY o.id, o.order_date, o.status
ORDER BY o.order_date;

-- Explain plans leveraging the supporting indexes
EXPLAIN (ANALYZE, BUFFERS)
SELECT p.id, p.name, SUM(oi.quantity * oi.unit_price) AS product_revenue
FROM order_items oi
JOIN products p ON p.id = oi.product_id
GROUP BY p.id, p.name
ORDER BY product_revenue DESC
LIMIT 10;

EXPLAIN (ANALYZE, BUFFERS)
SELECT u.id, u.full_name, SUM(oi.quantity * oi.unit_price) AS lifetime_spend
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
GROUP BY u.id, u.full_name
ORDER BY lifetime_spend DESC
LIMIT 10;

EXPLAIN (ANALYZE, BUFFERS)
SELECT o.id AS order_id,
       o.order_date,
       o.status,
       SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.user_id = 42
  AND o.order_date >= DATE '2024-02-01'
  AND o.order_date < DATE '2024-03-01'
GROUP BY o.id, o.order_date, o.status
ORDER BY o.order_date;
