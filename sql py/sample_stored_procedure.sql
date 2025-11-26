CREATE SCHEMA IF NOT EXISTS sales;

-- Table: customers
CREATE TABLE IF NOT EXISTS sales.customers
(
  id SERIAL PRIMARY KEY,
  customer_name TEXT NOT NULL,
  email TEXT UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  last_accessed TIMESTAMP WITH TIME ZONE
);

-- Table: orders
CREATE TABLE IF NOT EXISTS sales.orders
(
  order_id SERIAL PRIMARY KEY,
  customer_id INT NOT NULL REFERENCES sales.customers(id) ON DELETE CASCADE,
  order_date TIMESTAMP WITH TIME ZONE DEFAULT now(),
  amount NUMERIC(12,2) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
  notes TEXT
);

-- Sample data for customers
INSERT INTO sales.customers (customer_name, email, created_at, last_accessed)
VALUES
  ('Alice Johnson', 'alice@example.com', now() - INTERVAL '40 days', now() - INTERVAL '2 days'),
  ('Bob Singh', 'bob@example.com', now() - INTERVAL '20 days', now() - INTERVAL '10 hours'),
  ('Carol Patel', 'carol@example.com', now() - INTERVAL '5 days', NULL)
ON CONFLICT (email) DO NOTHING;

-- Sample data for orders
INSERT INTO sales.orders (customer_id, order_date, amount, status, notes)
VALUES
  (1, now() - INTERVAL '30 days', 199.99, 'ACTIVE', 'First order - priority shipping'),
  (1, now() - INTERVAL '10 days', 49.50, 'ACTIVE', NULL),
  (1, now() - INTERVAL '5 days', 15.00, 'CANCELLED', 'Customer cancelled'),
  (2, now() - INTERVAL '15 days', 250.00, 'ACTIVE', 'Bulk purchase'),
  (2, now() - INTERVAL '1 days', 75.25, 'ACTIVE', NULL),
  (3, now() - INTERVAL '2 days', 12.00, 'ACTIVE', 'Sample order')
;



CREATE OR REPLACE FUNCTION sales.get_customer_orders(
  p_customer_id INT,
  p_status VARCHAR DEFAULT 'ACTIVE'
)
RETURNS TABLE (
  order_id INT,
  order_date TIMESTAMP WITH TIME ZONE,
  amount NUMERIC,
  customer_name TEXT
)
LANGUAGE sql
AS $$
  SELECT o.order_id,
         o.order_date,
         o.amount,
         c.customer_name
  FROM sales.orders o
  JOIN sales.customers c ON o.customer_id = c.id
  WHERE o.customer_id = p_customer_id
    AND o.status = COALESCE(p_status, 'ACTIVE')
  ORDER BY o.order_date DESC;
$$;

-- Create a procedure that updates last_accessed for a customer
CREATE OR REPLACE PROCEDURE sales.update_customer_last_access(p_customer_id INT)
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE sales.customers
  SET last_accessed = now()
  WHERE id = p_customer_id;
END;
$$;