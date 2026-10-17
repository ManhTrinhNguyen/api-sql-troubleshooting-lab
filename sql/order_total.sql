SELECT order_id, SUM(quantity * unit_price_cents) AS total_cents FROM order_items WHERE order_id=1 GROUP BY order_id;
