"""
Product and Inventory OOP Domain Models for AUTO GEAR.
Encapsulates Category, Product, Inventory, and ProductService,
seamlessly integrated with custom Data Structures and Algorithms:
- SinglyLinkedList for sequential in-memory storage
- BinarySearchTree for hierarchical indexing and fast ID lookup
- Sorting algorithms for product organization
- Searching algorithms for catalog lookups
- Backtracking for bundle combinations
- Greedy & Dynamic Programming for budget recommendations
- Graph & Dijkstra for simulated store navigation
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from backend.database.connection import get_db_manager, DatabaseManager
from backend.dsa.linked_list import SinglyLinkedList
from backend.dsa.binary_search_tree import BinarySearchTree
from backend.dsa.binary_search import linear_search, binary_search, compare_searches
from backend.dsa.sorting import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    benchmark_all_sorts,
)
from backend.dsa.backtracking import build_accessory_bundles
from backend.dsa.greedy import greedy_budget_recommendations
from backend.dsa.dynamic_programming import (
    knapsack_dp_recommendations,
    compare_greedy_vs_dp,
)
from backend.dsa.graph import Graph, get_default_store_graph


class Category:
    """Encapsulates product category entity and validation."""

    def __init__(self, category_id: int, category_name: str):
        self.category_id = int(category_id)
        self.category_name = str(category_name).strip()
        self.validate()

    def validate(self):
        """Ensures category attributes satisfy domain rules."""
        if not self.category_name:
            raise ValueError("Category name cannot be empty.")
        if len(self.category_name) > 100:
            raise ValueError("Category name cannot exceed 100 characters.")

    def to_dict(self) -> dict:
        """Serializes Category instance to a dictionary."""
        return {
            "category_id": self.category_id,
            "category_name": self.category_name,
        }

    @classmethod
    def from_row(cls, row: dict):
        """Constructs a Category instance from a database dictionary row."""
        if not row:
            return None
        return cls(
            category_id=row["category_id"],
            category_name=row["category_name"],
        )


class Product:
    """
    Domain entity representing an automotive accessory.
    Encapsulates attributes, data validation, and stock adjustments.
    """

    def __init__(
        self,
        product_id: int,
        product_name: str,
        category_id: int,
        price: float,
        stock: int,
        description: str = "",
        category_name: str = None,
    ):
        self.product_id = int(product_id)
        self.product_name = str(product_name).strip()
        self.category_id = int(category_id)
        self.price = float(price)
        self.stock = int(stock)
        self.description = str(description).strip() if description else ""
        self.category_name = str(category_name).strip() if category_name else None

        self.validate()

    def validate(self):
        """Validates domain constraints for a product."""
        if not self.product_name:
            raise ValueError("Product name cannot be empty.")
        if len(self.product_name) > 150:
            raise ValueError("Product name cannot exceed 150 characters.")
        if self.category_id <= 0:
            raise ValueError("Valid category ID is required.")
        if self.price <= 0:
            raise ValueError("Product price must be greater than zero.")
        if self.stock < 0:
            raise ValueError("Product stock quantity cannot be negative.")

    def has_stock(self, quantity: int) -> bool:
        """Checks if available inventory satisfies requested quantity."""
        return quantity > 0 and self.stock >= quantity

    def adjust_stock(self, delta: int):
        """
        Adjusts product stock by delta (positive for replenishment, negative for reduction).
        Raises ValueError if resulting stock would be negative.
        """
        new_stock = self.stock + delta
        if new_stock < 0:
            raise ValueError(f"Insufficient stock for '{self.product_name}'. Available: {self.stock}, Requested: {abs(delta)}")
        self.stock = new_stock

    def to_dict(self) -> dict:
        """Serializes the Product instance to a dictionary for API output."""
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "category_id": self.category_id,
            "category_name": self.category_name,
            "price": round(self.price, 2),
            "stock": self.stock,
            "description": self.description,
        }

    @classmethod
    def from_row(cls, row: dict):
        """Constructs a Product instance from a database dictionary row."""
        if not row:
            return None
        price = float(row["price"]) if isinstance(row["price"], (Decimal, float, int)) else 0.0
        return cls(
            product_id=row["product_id"],
            product_name=row["product_name"],
            category_id=row["category_id"],
            price=price,
            stock=row["stock"],
            description=row.get("description", "") or "",
            category_name=row.get("category_name"),
        )


class Inventory:
    """
    Encapsulates the in-memory product collection using custom DSA:
    - SinglyLinkedList as the primary in-memory sequential container.
    - BinarySearchTree as the hierarchical indexing structure by product_id.
    """

    def __init__(self):
        self._list: SinglyLinkedList = SinglyLinkedList()
        self.bst_index: BinarySearchTree = BinarySearchTree()

    def load_products(self, products: list[Product]):
        """Populates the in-memory linked list and BST index with products."""
        self._list.clear()
        self.bst_index.clear()
        for p in products:
            self._list.insert_tail(p)
            self.bst_index.insert(p.product_id, p)

    def get_all(self) -> list[Product]:
        """Returns all products in linked list traversal order."""
        return self._list.to_list()

    def find_by_id(self, product_id: int) -> Product | None:
        """Searches for a product using the Binary Search Tree index (O(log n))."""
        return self.bst_index.search(product_id)

    def find_by_category(self, category_id: int) -> list[Product]:
        """Filters products by category ID using linked list traversal."""
        return self._list.find_all(lambda p: p.category_id == category_id)

    def add(self, product: Product):
        """Inserts a new product into both the Singly Linked List and BST index."""
        self._list.insert_tail(product)
        self.bst_index.insert(product.product_id, product)

    def update(self, updated_product: Product):
        """Updates product information in both the linked list and BST index."""
        node = self._list.search(lambda p: p.product_id == updated_product.product_id)
        if node:
            # Replaces data in linked list
            current = self._list.head
            while current:
                if current.data.product_id == updated_product.product_id:
                    current.data = updated_product
                    break
                current = current.next
        self.bst_index.insert(updated_product.product_id, updated_product)
        return True

    def remove(self, product_id: int):
        """Removes a product from both the linked list and the BST."""
        self._list.delete(lambda p: p.product_id == product_id)
        self.bst_index.delete(product_id)

    def count(self) -> int:
        """Returns the total number of products in inventory."""
        return len(self._list)


class ProductService:
    """
    Coordinates business logic, validations, database persistence, and DSA operations.
    """

    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or get_db_manager()
        self.inventory = Inventory()
        self.store_graph: Graph = get_default_store_graph()
        self.sync_inventory()

    def sync_inventory(self):
        """Synchronizes the in-memory Inventory collection from the MySQL database."""
        query = """
            SELECT 
                p.product_id, 
                p.product_name, 
                p.category_id, 
                p.price, 
                p.stock, 
                p.description,
                c.category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            ORDER BY p.product_id ASC;
        """
        rows = self.db.fetch_all(query)
        products = [Product.from_row(row) for row in rows]
        self.inventory.load_products(products)
        return self.inventory.count()

    def get_all_categories(self) -> list[dict]:
        """Retrieves all product categories from the database."""
        query = "SELECT category_id, category_name FROM categories ORDER BY category_id ASC;"
        rows = self.db.fetch_all(query)
        categories = [Category.from_row(r) for r in rows]
        return [c.to_dict() for c in categories]

    def get_all_products(self, category_id: int = None) -> list[dict]:
        """Returns all products, optionally filtered by category_id."""
        if category_id:
            products = self.inventory.find_by_category(category_id)
        else:
            products = self.inventory.get_all()
        return [p.to_dict() for p in products]

    def get_product_by_id(self, product_id: int) -> dict:
        """Finds a product by ID via BST index or raises ValueError."""
        product = self.inventory.find_by_id(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} was not found.")
        return product.to_dict()

    def create_product(self, data: dict) -> dict:
        """Validates and persists a new product to MySQL and in-memory structures."""
        name = data.get("product_name") or data.get("name")
        category_id = data.get("category_id")
        price = data.get("price")
        stock = data.get("stock", 0)
        description = data.get("description", "")

        temp_product = Product(
            product_id=0,
            product_name=name,
            category_id=category_id,
            price=price,
            stock=stock,
            description=description,
        )

        cat_check = self.db.fetch_one(
            "SELECT category_id, category_name FROM categories WHERE category_id = %s;",
            (temp_product.category_id,)
        )
        if not cat_check:
            raise ValueError(f"Category ID {temp_product.category_id} does not exist.")

        insert_sql = """
            INSERT INTO products (product_name, category_id, price, stock, description)
            VALUES (%s, %s, %s, %s, %s);
        """
        result = self.db.execute_query(
            insert_sql,
            (
                temp_product.product_name,
                temp_product.category_id,
                temp_product.price,
                temp_product.stock,
                temp_product.description,
            ),
            commit=True,
        )
        new_id = result["lastrowid"]

        persistent_product = Product(
            product_id=new_id,
            product_name=temp_product.product_name,
            category_id=temp_product.category_id,
            price=temp_product.price,
            stock=temp_product.stock,
            description=temp_product.description,
            category_name=cat_check["category_name"],
        )

        self.inventory.add(persistent_product)
        return persistent_product.to_dict()

    def update_product(self, product_id: int, data: dict) -> dict:
        """Updates an existing product in MySQL, linked list, and BST."""
        existing = self.inventory.find_by_id(product_id)
        if not existing:
            raise ValueError(f"Product with ID {product_id} does not exist.")

        name = data.get("product_name", existing.product_name)
        category_id = data.get("category_id", existing.category_id)
        price = data.get("price", existing.price)
        stock = data.get("stock", existing.stock)
        description = data.get("description", existing.description)

        updated_entity = Product(
            product_id=product_id,
            product_name=name,
            category_id=category_id,
            price=price,
            stock=stock,
            description=description,
        )

        cat_check = self.db.fetch_one(
            "SELECT category_id, category_name FROM categories WHERE category_id = %s;",
            (updated_entity.category_id,)
        )
        if not cat_check:
            raise ValueError(f"Category ID {updated_entity.category_id} does not exist.")

        updated_entity.category_name = cat_check["category_name"]

        update_sql = """
            UPDATE products
            SET product_name = %s, category_id = %s, price = %s, stock = %s, description = %s
            WHERE product_id = %s;
        """
        self.db.execute_query(
            update_sql,
            (
                updated_entity.product_name,
                updated_entity.category_id,
                updated_entity.price,
                updated_entity.stock,
                updated_entity.description,
                product_id,
            ),
            commit=True,
        )

        self.inventory.update(updated_entity)
        return updated_entity.to_dict()

    def update_stock(self, product_id: int, new_stock: int) -> dict:
        """Directly updates product stock quantity."""
        if int(new_stock) < 0:
            raise ValueError("Stock quantity cannot be negative.")

        existing = self.inventory.find_by_id(product_id)
        if not existing:
            raise ValueError(f"Product with ID {product_id} does not exist.")

        self.db.execute_query(
            "UPDATE products SET stock = %s WHERE product_id = %s;",
            (int(new_stock), product_id),
            commit=True,
        )

        existing.stock = int(new_stock)
        self.inventory.update(existing)
        return existing.to_dict()

    def delete_product(self, product_id: int) -> dict:
        """Deletes a product from MySQL and in-memory structures."""
        existing = self.inventory.find_by_id(product_id)
        if not existing:
            raise ValueError(f"Product with ID {product_id} does not exist.")

        ref_check = self.db.fetch_one(
            "SELECT COUNT(*) AS ref_count FROM order_items WHERE product_id = %s;",
            (product_id,)
        )
        if ref_check and ref_check["ref_count"] > 0:
            raise ValueError(
                f"Cannot delete product '{existing.product_name}' because it is associated with {ref_check['ref_count']} completed order line items."
            )

        self.db.execute_query(
            "DELETE FROM products WHERE product_id = %s;",
            (product_id,),
            commit=True,
        )

        self.inventory.remove(product_id)
        return {
            "success": True,
            "deleted_product_id": product_id,
            "message": f"Product '{existing.product_name}' was successfully deleted."
        }

    # ---------------------------------------------------
    # DSA Operations Integration
    # ---------------------------------------------------
    def search_catalog(self, target: Any, mode: str = "name") -> dict:
        """
        Executes Linear Search (for name search) or Binary Search (for ID search),
        and compares efficiency between both algorithms.
        """
        products = self.inventory.get_all()
        prod_dicts = [p.to_dict() for p in products]

        if mode == "id":
            target_id = int(target)
            return compare_searches(
                prod_dicts,
                key_func=lambda p: p["product_id"],
                target=target_id
            )
        else:
            return compare_searches(
                prod_dicts,
                key_func=lambda p: p["product_name"],
                target=str(target)
            )

    def sort_catalog(
        self,
        attribute: str = "price",
        algorithm: str = "quick",
        reverse: bool = False
    ) -> dict:
        """
        Sorts the catalog using one of the five custom sorting algorithms:
        bubble, selection, insertion, merge, quick, or 'all' to benchmark all five.
        """
        products = [p.to_dict() for p in self.inventory.get_all()]

        def key_func(p):
            val = p.get(attribute, 0)
            return str(val).lower() if isinstance(val, str) else float(val)

        if algorithm == "all":
            return benchmark_all_sorts(products, key_func=key_func, reverse=reverse)

        algo_map = {
            "bubble": bubble_sort,
            "selection": selection_sort,
            "insertion": insertion_sort,
            "merge": merge_sort,
            "quick": quick_sort,
        }
        sort_fn = algo_map.get(algorithm.lower(), quick_sort)
        sorted_items, metrics = sort_fn(products, key_func=key_func, reverse=reverse)

        return {
            "attribute": attribute,
            "reverse": reverse,
            "metrics": metrics,
            "products": sorted_items,
        }

    def get_bst_traversals(self) -> dict:
        """
        Returns Inorder, Preorder, and Postorder traversals of the BST product index.
        """
        inorder_nodes = [p.to_dict() for p in self.inventory.bst_index.inorder()]
        preorder_nodes = [p.to_dict() for p in self.inventory.bst_index.preorder()]
        postorder_nodes = [p.to_dict() for p in self.inventory.bst_index.postorder()]

        return {
            "bst_size": self.inventory.bst_index.size(),
            "inorder": inorder_nodes,
            "preorder": preorder_nodes,
            "postorder": postorder_nodes,
        }

    def generate_bundles_backtracking(
        self,
        categories: list[str],
        max_budget: float
    ) -> dict:
        """
        Generates bundle packages using recursive backtracking satisfying constraints.
        """
        products = [p.to_dict() for p in self.inventory.get_all()]
        products_by_category: dict[str, list[dict]] = {}
        for p in products:
            cat = p.get("category_name", "General")
            if cat not in products_by_category:
                products_by_category[cat] = []
            products_by_category[cat].append(p)

        bundles = build_accessory_bundles(
            products_by_category=products_by_category,
            category_sequence=categories,
            max_budget=float(max_budget),
        )

        return {
            "categories": categories,
            "budget": float(max_budget),
            "bundles_found": len(bundles),
            "bundles": bundles,
        }

    def recommend_products(self, budget: float, method: str = "compare") -> dict:
        """
        Executes Greedy, Dynamic Programming, or side-by-side comparison for budget recommendations.
        """
        products = [p.to_dict() for p in self.inventory.get_all()]
        budget_val = float(budget)

        if method == "greedy":
            return greedy_budget_recommendations(products, budget_val)
        elif method == "dp":
            return knapsack_dp_recommendations(products, budget_val)
        else:
            return compare_greedy_vs_dp(products, budget_val)

    def navigate_store_layout(
        self,
        start_location: str = "ENTRANCE",
        destination: str = "AISLE_AUDIO"
    ) -> dict:
        """
        Calculates the shortest walking route through store aisles using Dijkstra's algorithm.
        Also provides BFS and DFS exploration orders.
        """
        shortest_path_result = self.store_graph.dijkstra(start_location, destination)
        bfs_order = self.store_graph.bfs(start_location)
        dfs_order = self.store_graph.dfs(start_location)

        return {
            "shortest_path": shortest_path_result,
            "bfs_exploration": bfs_order,
            "dfs_exploration": dfs_order,
            "store_locations": self.store_graph.get_vertices(),
        }
