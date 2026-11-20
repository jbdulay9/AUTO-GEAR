"""
Flask Blueprint for Checkout and Order Processing REST Endpoints.
Guarantees ACID transactional consistency for order placement and inventory deduction.
"""

from decimal import Decimal
from flask import Blueprint, jsonify, request, session
from backend.database.connection import get_connection
from backend.models.customer import Customer
from backend.models.order import Order, OrderItem, Receipt
from backend.models.product import ProductService
from backend.routes.product_routes import get_service

checkout_bp = Blueprint("checkout", __name__)


@checkout_bp.route("/checkout", methods=["POST"])
def process_checkout():
    """
    Executes customer checkout under a strict MySQL transaction:
    1. Validates customer credentials.
    2. Verifies stock availability for every cart item with row locks.
    3. Creates customer record if new.
    4. Inserts Order and OrderItem records.
    5. Decrements stock in MySQL products table.
    6. Commits transaction and synchronizes in-memory DSA inventory.
    7. Clears shopping cart and returns digital receipt.
    """
    data = request.get_json() or {}
    name = (data.get("customer_name") or data.get("name") or "").strip()
    email = (data.get("customer_email") or data.get("email") or "").strip()

    if not name or not email:
        return jsonify({"success": False, "error": "Customer name and email are required."}), 400

    # Get items from payload or from session cart
    cart_items = data.get("items") or session.get("cart", [])
    if not cart_items:
        return jsonify({"success": False, "error": "Cannot checkout with an empty cart."}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Start ACID transaction
        conn.start_transaction()

        validated_items = []
        grand_total = 0.0

        # 1. Verify stock availability with FOR UPDATE row locks
        for item in cart_items:
            pid = int(item["product_id"])
            qty = int(item["quantity"])

            if qty <= 0:
                conn.rollback()
                return jsonify({"success": False, "error": f"Invalid quantity ({qty}) for product #{pid}."}), 400

            cursor.execute(
                "SELECT product_id, product_name, price, stock FROM products WHERE product_id = %s FOR UPDATE;",
                (pid,)
            )
            prod = cursor.fetchone()

            if not prod:
                conn.rollback()
                return jsonify({"success": False, "error": f"Product #{pid} no longer exists."}), 404

            if prod["stock"] < qty:
                conn.rollback()
                return jsonify({
                    "success": False,
                    "error": f"Insufficient stock for '{prod['product_name']}'. Available: {prod['stock']}, Requested: {qty}.",
                    "product_id": pid,
                    "available_stock": prod["stock"],
                }), 400

            unit_price = float(prod["price"])
            subtotal = round(unit_price * qty, 2)
            grand_total += subtotal

            validated_items.append({
                "product_id": pid,
                "product_name": prod["product_name"],
                "quantity": qty,
                "unit_price": unit_price,
                "subtotal": subtotal,
            })

        grand_total = round(grand_total, 2)

        # 2. Resolve Customer (get existing or insert new)
        cursor.execute(
            "SELECT customer_id, customer_name, customer_email FROM customers WHERE customer_email = %s;",
            (email.lower(),)
        )
        cust_row = cursor.fetchone()
        if cust_row:
            customer_id = cust_row["customer_id"]
            if cust_row["customer_name"] != name:
                cursor.execute(
                    "UPDATE customers SET customer_name = %s WHERE customer_id = %s;",
                    (name, customer_id)
                )
        else:
            cursor.execute(
                "INSERT INTO customers (customer_name, customer_email) VALUES (%s, %s);",
                (name, email.lower())
            )
            customer_id = cursor.lastrowid

        # 3. Insert Order
        cursor.execute(
            "INSERT INTO orders (customer_id, total_amount, order_status) VALUES (%s, %s, %s);",
            (customer_id, grand_total, "Completed")
        )
        order_id = cursor.lastrowid

        # 4. Insert Order Items and Decrement Stock
        order_item_instances = []
        for v in validated_items:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) "
                "VALUES (%s, %s, %s, %s, %s);",
                (order_id, v["product_id"], v["quantity"], v["unit_price"], v["subtotal"])
            )
            item_id = cursor.lastrowid

            cursor.execute(
                "UPDATE products SET stock = stock - %s WHERE product_id = %s;",
                (v["quantity"], v["product_id"])
            )

            order_item_instances.append(
                OrderItem(
                    order_item_id=item_id,
                    order_id=order_id,
                    product_id=v["product_id"],
                    quantity=v["quantity"],
                    unit_price=v["unit_price"],
                    subtotal=v["subtotal"],
                    product_name=v["product_name"],
                )
            )

        # 5. Commit Transaction
        conn.commit()

        # 6. Synchronize in-memory Inventory & DSA structures
        service = get_service()
        service.sync_inventory()

        # 7. Clear Session Cart
        session["cart"] = []
        session.modified = True

        # 8. Create Order and Receipt domain entities
        order_instance = Order(
            order_id=order_id,
            customer_id=customer_id,
            total_amount=grand_total,
            customer_name=name,
            customer_email=email,
            items=order_item_instances,
        )
        receipt = Receipt(order_instance)

        return jsonify({
            "success": True,
            "message": "Order completed successfully and recorded in MySQL.",
            "order": order_instance.to_dict(),
            "receipt": receipt.to_dict(),
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": f"Transaction failed: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
