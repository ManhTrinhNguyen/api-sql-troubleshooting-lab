SELECT customers.name, orders.id AS order_id, orders.status,
       SUM(order_items.quantity * order_items.unit_price_cents) AS total_cents
FROM customers
JOIN orders ON orders.customer_id = customers.id
JOIN order_items ON order_items.order_id = orders.id
WHERE customers.id = 1
GROUP BY customers.id, customers.name, orders.id, orders.status
ORDER BY orders.id;
