# AUTO GEAR — Automotive Accessories E-Commerce & POS System

**Version:** 1.0 (Phase 4 Final)  
**Deadline:** December 3, 2026  
**Academic Project:** Full-stack web-based inventory and point-of-sale system demonstrating Python OOP, Data Structures & Algorithms, MySQL, Flask, and modern HTML/CSS/JS.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| Backend | Python 3.14, Flask 3.1.3 |
| Database | MySQL 8 (via XAMPP) |
| DSA Engine | 9 custom Python algorithm implementations |

---

## Project Structure

```
AUTO_GEAR/
├── backend/
│   ├── app.py                   # Flask application factory and server entry point
│   ├── config.py                # Environment-based configuration (loads .env)
│   ├── database/
│   │   ├── connection.py        # MySQL connection pool and helper functions
│   │   └── schema.sql           # Complete schema + seed data
│   ├── dsa/
│   │   ├── linked_list.py       # Singly Linked List (Node, insert, delete, search, traverse)
│   │   ├── doubly_linked_list.py# Doubly Linked List (bidirectional traversal, cart operations)
│   │   ├── binary_search.py     # Linear Search & Binary Search with comparison metrics
│   │   ├── sorting.py           # Bubble, Selection, Insertion, Merge, Quick Sort + benchmarking
│   │   ├── binary_search_tree.py# BST (insert, search, delete, inorder, preorder, postorder)
│   │   ├── backtracking.py      # Recursive backtracking — budget-constrained bundle builder
│   │   ├── greedy.py            # Greedy algorithm — max-value product selection
│   │   ├── dynamic_programming.py# 0/1 Knapsack DP (tabulation) — optimal budget allocation
│   │   └── graph.py             # Weighted graph + BFS, DFS, Dijkstra's shortest path
│   ├── models/
│   │   ├── product.py           # Product, Category, Inventory, ProductService OOP classes
│   │   ├── customer.py          # Customer OOP class with get_or_create
│   │   └── order.py             # Order, OrderItem, Receipt OOP classes
│   └── routes/
│       ├── product_routes.py    # /api/products, /api/categories CRUD endpoints
│       ├── algorithm_routes.py  # /api/algorithms/* DSA REST endpoints
│       ├── cart_routes.py       # /api/cart/* DoublyLinkedList cart endpoints
│       ├── checkout_routes.py   # /api/checkout ACID transaction endpoint
│       └── admin_routes.py      # /api/admin/* authenticated dashboard endpoints
├── frontend/
│   ├── index.html               # Homepage — featured products + 3 DSA interactive panels
│   ├── products.html            # Catalog — search, sort (5 algorithms), category filter
│   ├── cart.html                # Shopping cart — qty controls, order summary
│   ├── checkout.html            # Checkout form + ASCII receipt modal
│   ├── admin.html               # Admin dashboard — 5 management tabs + DSA visualizer
│   ├── css/
│   │   ├── style.css            # Global dark automotive theme
│   │   ├── products.css         # Catalog grid and card styles
│   │   └── admin.css            # Admin panel, tables, KPI cards, BST visualizer
│   └── js/
│       ├── app.js               # Shared helpers (formatPHP, showToast, updateCartBadge) + homepage
│       ├── products.js          # Catalog: load products, sort via DSA API, search, add to cart
│       ├── cart.js              # Cart + Checkout: manage DLL cart, checkout submit, receipt modal
│       └── admin.js             # Admin: login, all tabs, product CRUD, inventory, orders, DSA tabs
├── .env                         # Environment variables (not committed to git)
├── .env.example                 # Environment variable template
├── .gitignore                   # Git exclusions
└── README.md                    # This file
```

---

## Installation & Setup

### Prerequisites

- **Python 3.14** installed (from python.org)
- **XAMPP** installed with MySQL 8
- **pip** packages: `flask`, `mysql-connector-python`, `python-dotenv`, `werkzeug`

### Step 1 — Install Python Packages

```bash
pip install flask mysql-connector-python python-dotenv werkzeug
```

### Step 2 — Start XAMPP MySQL

Start MySQL from the **XAMPP Control Panel** (or manually):

```powershell
& "C:\xampp\mysql\bin\mysqld.exe" --defaults-file="C:\xampp\mysql\bin\my.ini" --standalone
```

### Step 3 — Create Database & Seed Data

```powershell
Get-Content "C:\Users\Bryan_Dulay\Desktop\AutoGearProject\AUTO_GEAR\backend\database\schema.sql" | & "C:\xampp\mysql\bin\mysql.exe" -u root
```

This creates the `autogear_db` database, all tables, 6 categories, 10 products, and the default admin account.

### Step 4 — Configure Environment

Copy `.env.example` to `.env` (already done). The default `.env` contains:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=autogear_db
DB_USER=root
DB_PASSWORD=
SECRET_KEY=autogear_dev_secret_key_2026
DEBUG=True
```

### Step 5 — Run the Flask Server

```powershell
& "C:\Users\Bryan_Dulay\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\Bryan_Dulay\Desktop\AutoGearProject\AUTO_GEAR\backend\app.py"
```

### Step 6 — Open in Browser

Navigate to: **http://127.0.0.1:5000**

---

## Admin Credentials

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |
| URL | http://127.0.0.1:5000/admin.html |

---

## Features

### Customer Storefront

- **Homepage** — Featured products grid with quick-add to cart; 3 interactive DSA panels
- **Product Catalog** — All 10 products from MySQL; real-time search + sorting
- **Search** — Dual algorithm comparison (Linear Search vs. Binary Search) with metrics
- **Sort** — 5 selectable algorithms (Bubble, Selection, Insertion, Merge, Quick Sort) or benchmark all 5
- **Category Filters** — Pill buttons to filter by Audio, Lighting, Accessories, Security, Exterior, Air Freshener
- **Stock Badges** — Live stock status (In Stock / Low Stock / Out of Stock) from MySQL

### Shopping Cart

- Backed by a custom **Doubly Linked List** (bidirectional traversal)
- Add, increase/decrease quantity, remove, or clear cart
- Live stock validation on every operation
- Order summary with running total (PHP)
- Cart badge on every page updated via `/api/cart`

### Checkout & Receipt

- Customer name + email required
- Full ACID MySQL transaction:
  - Row-level `FOR UPDATE` locks for stock validation
  - Atomic insert of `orders` + `order_items`
  - Atomic `stock` decrement
  - Rollback on any error
- ASCII digital receipt displayed in modal (matches original desktop format)
- Cart cleared automatically after confirmed order

### Admin Dashboard (5 Tabs)

| Tab | Features |
|---|---|
| Overview KPIs | Total products, total orders, gross revenue, low-stock count, recent 5 orders |
| Product Catalog CRUD | Add/Edit/Delete products; assign categories, price, stock, description |
| Stock & Inventory | View all stock levels, color-coded status, inline stock quantity adjustment |
| Customer Orders | Full transaction history, itemized order detail modal, status update |
| DSA & BST Analysis | Live BST traversal (Inorder/Preorder/Postorder), All-5-algorithm sort benchmark |

---

## DSA Implementations

All 9 algorithms are **genuine custom Python implementations** — no built-in sort/search substitutes.

| # | Algorithm | File | Integration |
|---|---|---|---|
| 1 | Singly Linked List | `dsa/linked_list.py` | Inventory product chain in `ProductService` |
| 2 | Doubly Linked List | `dsa/doubly_linked_list.py` | Shopping cart (bidirectional traversal, O(1) node removal) |
| 3 | Linear & Binary Search | `dsa/binary_search.py` | Product name/ID search with comparison metrics |
| 4 | 5 Sorting Algorithms | `dsa/sorting.py` | Catalog sorting with comparisons, swaps, timing metrics |
| 5 | Binary Search Tree | `dsa/binary_search_tree.py` | Product ID index; inorder/preorder/postorder traversal |
| 6 | Backtracking | `dsa/backtracking.py` | Budget-constrained accessory bundle builder |
| 7 | Greedy Algorithm | `dsa/greedy.py` | Max-value product selection under budget |
| 8 | Dynamic Programming | `dsa/dynamic_programming.py` | 0/1 Knapsack (tabulation) — optimal budget allocation |
| 9 | Graph + Dijkstra | `dsa/graph.py` | Store aisle navigation with weighted walkways |

---

## API Reference

### Products & Categories
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/products` | List all products (optional `?category_id=`) |
| GET | `/api/products/<id>` | Single product details |
| POST | `/api/products` | Create product |
| PUT | `/api/products/<id>` | Update product |
| PATCH | `/api/products/<id>/stock` | Update stock quantity |
| DELETE | `/api/products/<id>` | Delete product |
| GET | `/api/categories` | List all categories |

### Cart
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/cart` | View cart (DLL items + live stock) |
| POST | `/api/cart/add` | Add product to DLL cart |
| PUT | `/api/cart/update` | Update item quantity |
| DELETE | `/api/cart/remove/<id>` | Remove specific item |
| DELETE | `/api/cart/clear` | Clear all cart items |

### Checkout
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/checkout` | ACID transaction checkout + receipt |

### Algorithms
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/algorithms/search` | Linear + Binary search comparison |
| POST | `/api/algorithms/sort` | Sort by attribute/algorithm (or benchmark all 5) |
| GET | `/api/algorithms/bst/traverse` | BST inorder/preorder/postorder traversal |
| POST | `/api/algorithms/bundle-builder` | Backtracking budget bundle generator |
| POST | `/api/algorithms/recommendations` | Greedy + DP knapsack comparison |
| GET | `/api/algorithms/store-graph` | Store layout vertices |
| POST | `/api/algorithms/shortest-path` | Dijkstra's shortest store path |

### Admin (Session-Protected)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/admin/login` | Admin authentication |
| GET | `/api/admin/verify` | Check session auth status |
| POST | `/api/admin/logout` | End admin session |
| GET | `/api/admin/dashboard` | KPIs + recent orders |
| GET | `/api/admin/orders` | All customer orders |
| GET | `/api/admin/orders/<id>` | Order detail + items |
| PATCH | `/api/admin/orders/<id>/status` | Update order status |

---

## Development Phases Completed

| Phase | Scope | Status |
|---|---|---|
| Phase 1 | Flask + MySQL Foundation, schema, seed data | ✅ COMPLETE |
| Phase 2 | Python OOP architecture (Product, Inventory, ProductService, Customer, Order, Receipt) | ✅ COMPLETE |
| Phase 3 | All 9 DSA implementations with Flask API endpoints | ✅ COMPLETE |
| Phase 4 | Complete frontend, cart, checkout, admin dashboard, integration testing | ✅ COMPLETE |

---

*AUTO GEAR — Built for academic demonstration. December 2026.*
