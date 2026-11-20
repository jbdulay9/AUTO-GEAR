"""
Flask Blueprint for Shopping Cart REST Endpoints.
Integrates custom DoublyLinkedList from Phase 3 for bidirectional in-memory cart operations.
"""

from flask import Blueprint, jsonify, request, session
from backend.dsa.doubly_linked_list import DoublyLinkedList
from backend.database.connection import fetch_one

cart_bp = Blueprint("cart", __name__)


def _load_cart_from_session() -> DoublyLinkedList:
    """Reconstructs a DoublyLinkedList instance from Flask session data."""
    dll = DoublyLinkedList()
    cart_data = session.get("cart", [])
    for item in cart_data:
        dll.append(item)
    return dll


def _save_cart_to_session(dll: DoublyLinkedList):
    """Persists DoublyLinkedList items back to Flask session."""
    session["cart"] = dll.to_list()
    session.modified = True


@cart_bp.route("/cart", methods=["GET"])
def view_cart():
    """
    Returns all items in the shopping cart in forward traversal order.
    Checks live database stock levels for each item.
    """
    dll = _load_cart_from_session()
    items = []
    total_price = 0.0
    total_quantity = 0

    for item in dll.traverse_forward():
        pid = item["product_id"]
        # Fetch live stock & details from MySQL
        db_prod = fetch_one(
            "SELECT p.product_name, p.price, p.stock, c.category_name "
            "FROM products p LEFT JOIN categories c ON p.category_id = c.category_id "
            "WHERE p.product_id = %s;",
            (pid,)
        )
        live_stock = db_prod["stock"] if db_prod else 0
        live_price = float(db_prod["price"]) if db_prod else float(item.get("price", 0))

        subtotal = round(live_price * item["quantity"], 2)
        total_price += subtotal
        total_quantity += item["quantity"]

        items.append({
            "product_id": pid,
            "product_name": db_prod["product_name"] if db_prod else item.get("product_name"),
            "category_name": db_prod["category_name"] if db_prod else item.get("category_name", ""),
            "unit_price": live_price,
            "quantity": item["quantity"],
            "subtotal": subtotal,
            "available_stock": live_stock,
            "in_stock": live_stock >= item["quantity"],
        })

    return jsonify({
        "success": True,
        "items": items,
        "total_items": total_quantity,
        "total_price": round(total_price, 2),
        "is_empty": len(items) == 0,
    }), 200


@cart_bp.route("/cart/add", methods=["POST"])
def add_to_cart():
    """
    Adds a product to the DoublyLinkedList cart.
    Validates live stock availability before addition.
    """
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id:
        return jsonify({"success": False, "error": "Product ID is required."}), 400
    if quantity <= 0:
        return jsonify({"success": False, "error": "Quantity must be greater than zero."}), 400

    # Validate product and stock from MySQL
    db_prod = fetch_one(
        "SELECT p.product_id, p.product_name, p.price, p.stock, c.category_name "
        "FROM products p LEFT JOIN categories c ON p.category_id = c.category_id "
        "WHERE p.product_id = %s;",
        (product_id,)
    )
    if not db_prod:
        return jsonify({"success": False, "error": f"Product #{product_id} not found."}), 404

    available_stock = db_prod["stock"]
    dll = _load_cart_from_session()

    # Search if already in cart
    existing_node = dll.find_node(lambda item: item["product_id"] == product_id)
    if existing_node:
        new_qty = existing_node.data["quantity"] + quantity
        if new_qty > available_stock:
            return jsonify({
                "success": False,
                "error": f"Cannot add {quantity} more. Total in cart ({new_qty}) exceeds stock ({available_stock}).",
                "available_stock": available_stock
            }), 400
        existing_node.data["quantity"] = new_qty
    else:
        if quantity > available_stock:
            return jsonify({
                "success": False,
                "error": f"Requested quantity ({quantity}) exceeds available stock ({available_stock}).",
                "available_stock": available_stock
            }), 400
        dll.append({
            "product_id": db_prod["product_id"],
            "product_name": db_prod["product_name"],
            "category_name": db_prod["category_name"] or "",
            "price": float(db_prod["price"]),
            "quantity": quantity,
        })

    _save_cart_to_session(dll)
    return jsonify({
        "success": True,
        "message": f"Added '{db_prod['product_name']}' to cart.",
        "total_items": len(dll),
    }), 200


@cart_bp.route("/cart/update", methods=["PUT"])
def update_cart_item():
    """
    Updates the quantity of a product in the DoublyLinkedList cart.
    If quantity <= 0, unlinks and removes the node.
    """
    data = request.get_json() or {}
    product_id = data.get("product_id")
    if product_id is None:
        return jsonify({"success": False, "error": "Product ID is required."}), 400

    quantity = int(data.get("quantity", 0))
    dll = _load_cart_from_session()
    target_node = dll.find_node(lambda item: item["product_id"] == product_id)

    if not target_node:
        return jsonify({"success": False, "error": "Item not found in cart."}), 404

    if quantity <= 0:
        dll.remove_node(target_node)
        _save_cart_to_session(dll)
        return jsonify({"success": True, "message": "Item removed from cart."}), 200

    # Validate stock
    db_prod = fetch_one("SELECT stock FROM products WHERE product_id = %s;", (product_id,))
    available_stock = db_prod["stock"] if db_prod else 0
    if quantity > available_stock:
        return jsonify({
            "success": False,
            "error": f"Quantity {quantity} exceeds available stock ({available_stock}).",
            "available_stock": available_stock
        }), 400

    target_node.data["quantity"] = quantity
    _save_cart_to_session(dll)
    return jsonify({"success": True, "message": "Cart updated successfully."}), 200


@cart_bp.route("/cart/remove/<int:product_id>", methods=["DELETE"])
def remove_from_cart(product_id: int):
    """Removes a specific item from the DoublyLinkedList cart."""
    dll = _load_cart_from_session()
    removed = dll.remove(lambda item: item["product_id"] == product_id)
    if removed:
        _save_cart_to_session(dll)
        return jsonify({"success": True, "message": "Item removed from cart."}), 200
    return jsonify({"success": False, "error": "Item not found in cart."}), 404


@cart_bp.route("/cart/clear", methods=["DELETE"])
def clear_cart():
    """Empties the shopping cart."""
    dll = _load_cart_from_session()
    dll.clear()
    _save_cart_to_session(dll)
    return jsonify({"success": True, "message": "Shopping cart cleared."}), 200
