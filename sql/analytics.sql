-- Revenue by country
SELECT country,
       COUNT(*) AS orders,
       ROUND(SUM(quantity * unit_price), 2) AS revenue
FROM orders
WHERE status = 'completed'
GROUP BY country
ORDER BY revenue DESC;

-- Daily order volume
SELECT DATE(order_ts) AS order_date,
       COUNT(*) AS order_count,
       ROUND(SUM(quantity * unit_price), 2) AS gross_value
FROM orders
GROUP BY DATE(order_ts)
ORDER BY order_date;

-- Pipeline health
SELECT run_id, started_at, finished_at, status,
       records_read, records_valid, records_loaded, records_rejected
FROM pipeline_runs
ORDER BY started_at DESC;
