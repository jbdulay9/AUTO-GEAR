-- ===================================================
-- AUTO GEAR Database Schema & Initial Seed Script
-- Target Database: MySQL
-- ===================================================

CREATE DATABASE IF NOT EXISTS autogear_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE autogear_db;

-- ---------------------------------------------------
-- 1. Table: categories
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ---------------------------------------------------
-- 2. Table: products
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    description TEXT,
    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------
-- 3. Table: customers
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    customer_email VARCHAR(150) NOT NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------
-- 4. Table: orders
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(50) NOT NULL DEFAULT 'Completed',
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------
-- 5. Table: order_items
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id) REFERENCES products(product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ---------------------------------------------------
-- 6. Table: admins
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

-- ===================================================
-- Initial Seed Data
-- ===================================================

-- Categories
INSERT INTO categories (category_id, category_name) VALUES
    (1, 'Audio'),
    (2, 'Lighting'),
    (3, 'Accessories'),
    (4, 'Security'),
    (5, 'Exterior'),
    (6, 'Air Freshener')
ON DUPLICATE KEY UPDATE category_name = VALUES(category_name);

-- Products (Migrated from original products.json)
INSERT INTO products (product_id, product_name, category_id, price, stock, description) VALUES
    (1, 'Speakers', 1, 4500.00, 15, 'High-fidelity car audio door speakers with clear sound quality.'),
    (2, 'Amplifiers', 1, 8500.00, 10, 'Multi-channel high-output car power amplifier with thermal protection.'),
    (3, 'LED Lights', 2, 2800.00, 20, 'Underglow and interior ambient RGB LED strip kit with wireless controller.'),
    (4, 'LED Bulbs', 2, 1200.00, 25, 'High-lumen energy-efficient LED headlight replacement bulbs.'),
    (5, 'Car Horns', 3, 1800.00, 15, 'Dual snail-tone loud warning electric horns for enhanced safety.'),
    (6, 'Car Security Systems (Alarm)', 4, 6500.00, 8, 'Full-featured anti-theft car security system with keyless remote entry.'),
    (7, 'Rain Visors', 5, 2200.00, 20, 'Durable acrylic side-window rain and wind deflectors.'),
    (8, 'Paradise Air - Cherry', 6, 350.00, 30, 'Long-lasting organic can air freshener - Fresh Cherry scent.'),
    (9, 'Paradise Air - Vanilla', 6, 350.00, 30, 'Long-lasting organic can air freshener - Warm Vanilla scent.'),
    (10, 'Paradise Air - Sandalwood', 6, 350.00, 30, 'Long-lasting organic can air freshener - Exotic Sandalwood scent')
ON DUPLICATE KEY UPDATE
    product_name = VALUES(product_name),
    category_id = VALUES(category_id),
    price = VALUES(price),
    stock = VALUES(stock),
    description = VALUES(description);

-- Default Admin User (username: admin, password: admin123)
INSERT INTO admins (admin_id, username, password_hash) VALUES
    (1, 'admin', 'scrypt:32768:8:1$hZoi0cgYMsdyrutu$ff356109c0cb99cf89951ec979982c00aab1c6c78ac5cf484eb4ed66e50699af96290fb10f7913cf2be5dafc146d2a2a80b66c64fe29a21f15c31033c7462442')
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
    password_hash = VALUES(password_hash);
