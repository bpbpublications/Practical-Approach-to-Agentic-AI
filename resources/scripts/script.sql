CREATE TABLE customer (
    customer_id      BIGINT PRIMARY KEY,
    name             VARCHAR(255) NOT NULL,
    email            VARCHAR(255) NOT NULL UNIQUE,
    phone            VARCHAR(255) NOT NULL,
    type             VARCHAR(255) NOT NULL,
    last_active      DATE NOT NULL,
    credits_available INT DEFAULT 0
);
INSERT INTO customer (customer_id, name, email, phone, type, last_active, credits_available)
VALUES 
(1, 'Amit Sharma', 'amit.sharma@example.com', '+91-9876543210', 'Retail', '2025-08-10', 500);

INSERT INTO customer (customer_id, name, email, phone, type, last_active, credits_available)
VALUES 
(2, 'Priya Iyer', 'priya.iyer@example.com', '+91-9123456789', 'Wholesale', '2025-08-15', 1200);

INSERT INTO customer (customer_id, name, email, phone, type, last_active, credits_available)
VALUES 
(3, 'Rahul Verma', 'rahul.verma@example.com', '+91-9988776655', 'Retail', '2025-08-18', 300);

INSERT INTO customer (customer_id, name, email, phone, type, last_active, credits_available)
VALUES 
(4, 'Shweta Kamath', 'shweta.kamath@example.com', '+91-9988776650', 'Retail', '2025-08-25', 300);

CREATE TABLE product (
    product_id          BIGINT PRIMARY KEY,
    product_code        VARCHAR(50) NOT NULL UNIQUE,
    product_category    VARCHAR(50) NOT NULL,
    description         VARCHAR(255) NOT NULL,
    price               DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    active              VARCHAR(255) NOT NULL CHECK (active IN ('Y','N')),
    regularly_purchased BOOLEAN DEFAULT FALSE
);
INSERT INTO product (product_id, product_code, product_category, description, price, active, regularly_purchased) VALUES
(1,  'PRD001', 'Groceries', 'Organic Basmati Rice 5kg', 599.00, 'Y', TRUE),
(2,  'PRD002', 'Groceries', 'Premium Whole Wheat Atta 10kg', 450.00, 'Y', TRUE),
(3,  'PRD003', 'Groceries', 'Cold-Pressed Groundnut Oil 1L', 280.00, 'Y', TRUE),
(4,  'PRD004', 'Groceries', 'Organic Tur Dal 2kg', 340.00, 'Y', TRUE),
(5,  'PRD005', 'Groceries', 'Himalayan Rock Salt 1kg', 120.00, 'Y', TRUE),

(6,  'PRD006', 'Personal Care', 'Ayurvedic Herbal Shampoo 500ml', 250.00, 'Y', TRUE),
(7,  'PRD007', 'Personal Care', 'Neem & Aloe Vera Face Wash 100ml', 180.00, 'Y', TRUE),
(8,  'PRD008', 'Personal Care', 'Charcoal Toothpaste 120g', 150.00, 'Y', TRUE),
(9,  'PRD009', 'Personal Care', 'Organic Cotton Face Towel Pack of 3', 300.00, 'Y', FALSE),
(10, 'PRD010', 'Personal Care', 'Coconut Oil Hair Serum 100ml', 220.00, 'Y', TRUE),

(11, 'PRD011', 'Household', 'Eco-Friendly Bamboo Toothbrush Pack of 4', 199.00, 'Y', TRUE),
(12, 'PRD012', 'Household', 'Biodegradable Garbage Bags 30pcs', 150.00, 'Y', TRUE),
(13, 'PRD013', 'Household', 'Reusable Steel Straw Pack with Cleaner', 99.00, 'Y', FALSE),
(14, 'PRD014', 'Household', 'Natural Floor Cleaner with Neem Extract 1L', 210.00, 'Y', TRUE),
(15, 'PRD015', 'Household', 'Organic Laundry Detergent 2kg', 390.00, 'Y', TRUE),

(16, 'PRD016', 'Gourmet', 'Artisanal Dark Chocolate 70% Cocoa 100g', 220.00, 'Y', TRUE),
(17, 'PRD017', 'Gourmet', 'Arabica Coffee Beans 500g', 550.00, 'Y', TRUE),
(18, 'PRD018', 'Gourmet', 'Premium Kashmiri Saffron 1g', 650.00, 'Y', FALSE),
(19, 'PRD019', 'Gourmet', 'Organic Almond Butter 250g', 320.00, 'Y', TRUE),
(20, 'PRD020', 'Gourmet', 'Green Tea Infusion with Tulsi 50 bags', 299.00, 'Y', TRUE);

(21, 'PRD021', 'Groceries', 'Jowar Atta 1kg', 250.00, 'Y', FALSE),
(22, 'PRD022', 'Groceries', 'Toor Dal 250g', 120.00, 'Y', TRUE),
(23, 'PRD023', 'Personal Care', 'Cold Cream', 299.00, 'Y', TRUE);
(24, 'PRD024', 'Gourmet', 'Green Tea Infusion with Tulsi 100 bags', 499.00, 'Y', TRUE);

CREATE TABLE address (
    address_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    address_line_1 VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_cd VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    landmark VARCHAR(255),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES customer(customer_id)
);
-- Address for Amit Sharma
INSERT INTO address (
    address_id, user_id, address_line_1, address_line_2, city, state, postal_cd, country, latitude, longitude, landmark
) VALUES (
    1, 1, 'Flat 502, Gokul Residency', 'Andheri West', 'Mumbai', 'Maharashtra', '400053', 'India',
    19.1197, 72.8468, 'Near Infinity Mall'
);

-- Address for Priya Iyer
INSERT INTO address (
    address_id, user_id, address_line_1, address_line_2, city, state, postal_cd, country, latitude, longitude, landmark
) VALUES (
    2, 2, 'Villa No. 18, Greenwoods Layout', 'Sarjapur Road', 'Bengaluru', 'Karnataka', '560035', 'India',
    12.9063, 77.6790, 'Near Decathlon'
);

-- Address for Rahul Verma
INSERT INTO address (
    address_id, user_id, address_line_1, address_line_2, city, state, postal_cd, country, latitude, longitude, landmark
) VALUES (
    3, 3, 'Plot 24, Defence Colony', 'Sector 18', 'New Delhi', 'Delhi', '110024', 'India',
    28.5672, 77.2345, 'Near Lajpat Nagar Metro Station'
);

INSERT INTO address (
    address_id, user_id, address_line_1, address_line_2, city, state, postal_cd, country, latitude, longitude, landmark
) VALUES (
    4, 4, 'Plot 24, Military Colony', 'Sector 18', 'Vashi', 'Maharashtra', '400615', 'India',
    19.0745, 72.9978, 'Near Vashi station'
);

CREATE TABLE warehouse (
    warehouse_id   BIGINT PRIMARY KEY,
    warehouse_code VARCHAR(50) NOT NULL,
    address        VARCHAR(255) NOT NULL,
    latitude       DECIMAL(10,2) NOT NULL,
    longitude      DECIMAL(10,2) NOT NULL,
    active         VARCHAR(255) NOT NULL
);
INSERT INTO warehouse (warehouse_id, warehouse_code, address, latitude, longitude, active)
VALUES (1, 'MUM-WH-001', 'Andheri East, Mumbai, Maharashtra', 19.1197, 72.8468, 'Y');

INSERT INTO warehouse (warehouse_id, warehouse_code, address, latitude, longitude, active)
VALUES (2, 'DEL-WH-002', 'Okhla Industrial Area, Delhi', 28.5355, 77.3910, 'Y');

INSERT INTO warehouse (warehouse_id, warehouse_code, address, latitude, longitude, active)
VALUES (3, 'BLR-WH-003', 'Whitefield, Bengaluru, Karnataka', 12.9716, 77.5946, 'Y');

INSERT INTO warehouse (warehouse_id, warehouse_code, address, latitude, longitude, active)
VALUES (4, 'HYD-WH-004', 'Gachibowli, Hyderabad, Telangana', 17.3850, 78.4867, 'Y');

INSERT INTO warehouse (warehouse_id, warehouse_code, address, latitude, longitude, active)
VALUES (5, 'PUN-WH-005', 'Hinjewadi, Pune, Maharashtra', 18.5204, 73.8567, 'Y');

CREATE TABLE warehouse_product (
    warehouse_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    product_quantity INT NOT NULL,
    PRIMARY KEY (warehouse_id, product_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouse(warehouse_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);
-- Mumbai Warehouse (MUM-WH-001)
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (1, 1, 120); -- Organic Basmati Rice
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (1, 2, 150); -- Premium Atta
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (1, 6, 200); -- Herbal Shampoo
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (1, 11, 300); -- Bamboo Toothbrush
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (1, 16, 80);  -- Dark Chocolate

-- Delhi Warehouse (DEL-WH-002)
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (2, 3, 180); -- Groundnut Oil
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (2, 4, 160); -- Tur Dal
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (2, 7, 220); -- Face Wash
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (2, 12, 250); -- Garbage Bags
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (2, 17, 90);  -- Arabica Coffee

-- Bengaluru Warehouse (BLR-WH-003)
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (3, 5, 140); -- Rock Salt
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (3, 8, 190); -- Charcoal Toothpaste
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (3, 13, 100); -- Steel Straw
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (3, 14, 210); -- Floor Cleaner
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (3, 18, 40);  -- Kashmiri Saffron

-- Hyderabad Warehouse (HYD-WH-004)
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (4, 9, 130); -- Cotton Towels
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (4, 10, 160); -- Hair Serum
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (4, 15, 175); -- Laundry Detergent
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (4, 19, 110); -- Almond Butter
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (4, 20, 140); -- Green Tea

-- Pune Warehouse (PUN-WH-005)
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (5, 1, 100); -- Organic Rice
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (5, 3, 120); -- Groundnut Oil
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (5, 6, 150); -- Herbal Shampoo
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (5, 12, 200); -- Garbage Bags
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (5, 16, 70);  -- Dark Chocolate

INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (1, 21, 120); -- Jowar Atta 1kg
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (1, 22, 150); -- Toor Dal 250g
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (1, 23, 200); -- Cold Cream
INSERT INTO warehouse_product (warehouse_id, product_id, product_quantity) VALUES (1, 24, 200); -- Cold Cream

CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    order_date TIMESTAMP NOT NULL,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(255) NOT NULL,
    expected_delivery_date TIMESTAMP NOT NULL,
    actual_delivery_date TIMESTAMP NULL,
    delay_handling_preference BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);
INSERT INTO orders (order_id, order_date, customer_id, total_amount, status, expected_delivery_date, actual_delivery_date, delay_handling_preference)
VALUES
(101, '2025-08-01 10:15:00', 1, 1250.50, 'Delivered', '2025-08-03 18:00:00', '2025-08-03 17:45:00', FALSE),

(102, '2025-08-02 12:20:00', 2, 890.00, 'Shipped', '2025-08-05 18:00:00', NULL, TRUE),

(103, '2025-08-03 09:45:00', 3, 1520.75, 'Processing', '2025-08-06 18:00:00', NULL, FALSE),

(104, '2025-08-04 15:30:00', 1, 450.00, 'Delivered', '2025-08-06 12:00:00', '2025-08-06 11:50:00', TRUE),

(105, '2025-08-05 11:10:00', 2, 2350.40, 'Cancelled', '2025-08-08 20:00:00', NULL, FALSE),

(106, '2025-08-06 14:25:00', 3, 975.00, 'Shipped', '2025-08-09 18:00:00', NULL, TRUE),

(107, '2025-08-07 17:00:00', 1, 1200.00, 'Processing', '2025-08-10 12:00:00', NULL, FALSE),

(108, '2025-08-08 08:40:00', 2, 3200.90, 'Delivered', '2025-08-10 20:00:00', '2025-08-10 19:45:00', TRUE),

(109, '2025-08-09 19:15:00', 3, 780.25, 'Delivered', '2025-08-12 12:00:00', '2025-08-12 12:05:00', FALSE),

(110, '2025-08-10 13:30:00', 1, 1980.60, 'Shipped', '2025-08-13 18:00:00', NULL, TRUE);
INSERT INTO orders (order_id, order_date, customer_id, total_amount, status, expected_delivery_date, actual_delivery_date, delay_handling_preference)
VALUES
-- Received
(111, '2025-08-11 09:10:00', 1, 560.00, 'Received', '2025-08-14 18:00:00', NULL, FALSE),

-- Confirmed
(112, '2025-08-11 11:25:00', 2, 1320.75, 'Confirmed', '2025-08-15 12:00:00', NULL, TRUE),

-- Being processed
(113, '2025-08-12 15:40:00', 3, 890.50, 'Being processed', '2025-08-16 20:00:00', NULL, FALSE),

-- Ready to dispatch
(114, '2025-08-13 14:05:00', 1, 2250.00, 'Ready to dispatch', '2025-08-17 18:00:00', NULL, TRUE),

-- Dispatched
(115, '2025-08-13 19:20:00', 2, 765.90, 'Dispatched', '2025-08-17 12:00:00', NULL, FALSE),

-- Out for delivery
(116, '2025-08-14 08:50:00', 3, 1580.60, 'Out for delivery', '2025-08-18 20:00:00', NULL, TRUE),

-- Delivered
(117, '2025-08-14 17:15:00', 1, 640.40, 'Delivered', '2025-08-18 12:00:00', '2025-08-18 11:45:00', FALSE),

-- Cancelled
(118, '2025-08-15 10:00:00', 2, 1920.25, 'Cancelled', '2025-08-19 18:00:00', NULL, TRUE),

-- Returned
(119, '2025-08-15 13:30:00', 3, 850.75, 'Returned', '2025-08-19 12:00:00', '2025-08-19 11:30:00', FALSE),

-- Another Delivered (to balance distribution)
(120, '2025-08-16 16:20:00', 1, 2890.00, 'Delivered', '2025-08-20 18:00:00', '2025-08-20 17:55:00', TRUE);

INSERT INTO orders (order_id, order_date, customer_id, total_amount, status, expected_delivery_date, actual_delivery_date, delay_handling_preference)
VALUES
-- Received
(121, '2025-08-11 09:10:00', 1, 560.00, 'Dispatched', '2025-08-14 18:00:00', NULL, FALSE);

INSERT INTO orders (order_id, order_date, customer_id, total_amount, status, expected_delivery_date, actual_delivery_date, delay_handling_preference)
VALUES
-- Received
(122, '2025-08-20 09:10:00', 4, 370.00, 'Dispatched', '2025-08-26 18:00:00', NULL, FALSE);

INSERT INTO orders (order_id, order_date, customer_id, total_amount, status, expected_delivery_date, actual_delivery_date, delay_handling_preference)
VALUES
-- Received
(123, '2025-08-20 11:10:00', 4, 370.00, 'Ready to dispatch', '2025-08-26 18:00:00', NULL, FALSE);

UPDATE orders
SET order_date = '2025-08-22 11:10:00',
    total_amount = 598
WHERE order_id = 123;

CREATE TABLE order_item (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(255) NOT NULL,
    CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES product(product_id)
);

INSERT INTO order_item (order_item_id, order_id, product_id, quantity, amount, status) VALUES
-- Status: Received
(1, 101, 1, 2, 1198.00, 'Received'),

-- Status: Confirmed
(2, 102, 6, 1, 250.00, 'Confirmed'),

-- Status: Being processed
(3, 103, 12, 3, 450.00, 'Being processed'),

-- Status: Ready to dispatch
(4, 104, 16, 2, 440.00, 'Ready to dispatch'),

-- Status: Dispatched
(5, 105, 4, 4, 1360.00, 'Dispatched'),

-- Status: Out for delivery
(6, 106, 9, 1, 300.00, 'Out for delivery'),

-- Status: Delivered
(7, 107, 19, 2, 640.00, 'Delivered'),

-- Status: Cancelled
(8, 108, 7, 5, 900.00, 'Cancelled'),

-- Status: Returned
(9, 109, 18, 1, 650.00, 'Returned'),

-- Another Delivered record
(10, 110, 20, 2, 598.00, 'Delivered');

(11, 122, 21, 1, 250.00, 'Dispatched');

(12, 122, 22, 1, 120.00, 'Dispatched');

(13, 123, 20, 1, 250.00, 'Ready to dispatch');

(14, 123, 23, 1, 120.00, 'Ready to dispatch');

CREATE TABLE payment (
    payment_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    transaction_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_mode VARCHAR(50) NOT NULL, -- e.g. UPI, Credit Card, Debit Card, Net Banking, COD
    status VARCHAR(50) NOT NULL,       -- e.g. Pending, Successful, Failed, Refunded
    payment_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    CONSTRAINT fk_payment_order FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

INSERT INTO payment (payment_id, order_id, transaction_id, amount, payment_mode, status, payment_time) VALUES
(1001, 101, 50250001, 1250.50, 'UPI', 'Successful', '2025-08-01 10:20:00'),
(1002, 102, 50250002, 890.00, 'Credit Card', 'Successful', '2025-08-02 12:25:00'),
(1003, 103, 50250003, 1520.75, 'Debit Card', 'Pending', '2025-08-03 09:50:00'),
(1004, 104, 50250004, 450.00, 'Net Banking', 'Successful', '2025-08-04 15:35:00'),
(1005, 105, 50250005, 2350.40, 'Credit Card', 'Failed', '2025-08-05 11:15:00'),
(1006, 106, 50250006, 975.00, 'UPI', 'Successful', '2025-08-06 14:30:00'),
(1007, 107, 50250007, 1200.00, 'Debit Card', 'Pending', '2025-08-07 17:05:00'),
(1008, 108, 50250008, 3200.90, 'UPI', 'Successful', '2025-08-08 08:45:00'),
(1009, 109, 50250009, 780.25, 'Credit Card', 'Refunded', '2025-08-09 19:20:00'),
(1010, 110, 50250010, 1980.60, 'Net Banking', 'Successful', '2025-08-10 13:35:00');
(1011, 122, 50350010, 370.00, 'Net Banking', 'Successful', '2025-08-20 09:10:00');
(1012, 123, 50850010, 598.00, 'Net Banking', 'Successful', '2025-08-20 11:10:00');
update payment set payment_time='2025-08-22 11:10:00' where payment_id=1012;

CREATE TABLE refund (
    refund_id BIGINT PRIMARY KEY,
    payment_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- e.g. Pending, Approved, Processed, Failed
    refund_time TIMESTAMP NOT NULL,
    CONSTRAINT fk_refund_payment FOREIGN KEY (payment_id) REFERENCES payment(payment_id),
    CONSTRAINT fk_refund_order FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE SEQUENCE IF NOT EXISTS refund_redund_id_seq OWNED BY refund.refund_id;
ALTER TABLE refund ALTER COLUMN refund_id SET DEFAULT nextval('refund_redund_id_seq'::regclass);
ALTER TABLE refund ALTER COLUMN refund_id SET NOT NULL;


INSERT INTO refund (refund_id, payment_id, order_id, reason, status, refund_time) VALUES
(2001, 1005, 105, 'Order cancelled by customer before shipping', 'Processed', '2025-08-06 16:00:00'),
(2002, 1009, 109, 'Product returned by customer after delivery', 'Processed', '2025-08-12 15:30:00'),
(2003, 1003, 103, 'Order not processed, refund issued', 'Processed', '2025-08-04 14:20:00'),
(2004, 1007, 107, 'Delayed shipping, partial refund granted', 'Approved', '2025-08-09 10:15:00'),
(2005, 1010, 110, 'Damaged item reported, refund initiated', 'Pending', '2025-08-11 09:10:00'),
(2006, 1002, 102, 'Customer cancelled order, full refund issued', 'Processed', '2025-08-06 18:45:00'),
(2007, 1006, 106, 'Duplicate payment detected, refund issued', 'Processed', '2025-08-07 16:40:00'),
(2008, 1004, 104, 'Product returned after delivery', 'Approved', '2025-08-07 12:05:00'),
(2009, 1001, 101, 'Refund issued due to defective product complaint', 'Processed', '2025-08-04 11:30:00'),
(2010, 1008, 108, 'Refund requested due to incorrect item delivered', 'Pending', '2025-08-10 19:00:00');

CREATE TABLE shopping_cart (
    item_id SERIAL NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    customer_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    PRIMARY KEY (item_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);

-- add a unique constraint to prevent duplicate entries for the same customer and product
ALTER TABLE shopping_cart
ADD CONSTRAINT unique_customer_product UNIQUE (customer_id, product_id);

INSERT INTO shopping_cart (quantity, unit_price, customer_id, product_id) VALUES
(2, 599.00, 1, 1),  -- Amit Sharma added 2 units of Organic Basmati Rice
(1, 250.00, 2, 6),  -- Priya Iyer added 1 unit of Herbal Shampoo
(3, 150.00, 3, 12), -- Rahul Verma added 3 units of Garbage Bags
(1, 220.00, 1, 10), -- Amit Sharma added 1 unit of Coconut Oil Hair Serum
(4, 340.00, 2, 4),  -- Priya Iyer added 4 units of Tur Dal
(2, 300.00, 3, 9);  -- Rahul Verma added 2 units of Organic Cotton Face Towel Pack


CREATE TABLE customer_regular_items (
    item_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    
    PRIMARY KEY (item_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);



INSERT INTO customer_regular_items (item_id, customer_id, product_id, quantity) VALUES
(1, 1, 1, 2), -- Amit Sharma's regular item: Organic Basmati Rice
(2, 2, 6, 1), -- Priya Iyer's regular item: Herbal Shampoo
(3, 3, 12, 3), -- Rahul Verma's regular item: Garbage Bags
(4, 1, 16, 2), -- Amit Sharma's regular item: Dark Chocolate
(5, 2, 4, 4), -- Priya Iyer's regular item: Tur Dal
(6, 3, 9, 1), -- Rahul Verma's regular item     : Cotton Towels
(7, 1, 19, 2), -- Amit Sharma's regular item: Almond Butter
(8, 2, 7, 5), -- Priya Iyer's regular item: Face Wash
(9, 3, 18, 1), -- Rahul Verma's regular item: Kashmiri Saffron
(10, 1, 20, 2); -- Amit Sharma's regular item: Green Tea Infusion

-- data set up for Chapter 10 
update orders set actual_delivery_date = actual_delivery_date + INTERVAL '2 days'
where order_id = 117;

update order_item set order_id = 117 where order_item.order_item_id = 7;

INSERT INTO payment (payment_id, order_id, amount, payment_mode, status, payment_time,transaction_id) VALUES
(1013, 117, 640.40, 'UPI', 'Successful', '"2025-08-14 12:00:00"',1012);

INSERT INTO refund (payment_id, order_id, reason, status, refund_time) VALUES
(1011, 117, 'Delayed delivery', 'Pending', CURRENT_TIMESTAMP);


--------

update order_item set amount = 1250.50 where order_item.order_id = 101 

INSERT INTO payment (payment_id, order_id, amount, payment_mode, status, payment_time,transaction_id) VALUES
(1014, 101, 1250.50, 'UPI', 'Successful', '"2025-08-14 12:00:00"',1012);

INSERT INTO refund (payment_id, order_id, reason, status, refund_time) VALUES
(1012, 101, 'Damaged product', 'Pending', CURRENT_TIMESTAMP);