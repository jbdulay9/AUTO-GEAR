"""
Flask Blueprint for Administrator Dashboard and Management REST Endpoints.
Protects administrative operations with server-side authentication and session checks.
"""

from functools import wraps
from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash
from backend.database.connection import fetch_one, fetch_all, execute_query
from backend.models.order import Order, OrderItem
from backend.routes.product_routes import get_service

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    """Decorator ensuring only authenticated administrators can access endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return jsonify({
                "success": False,
                "error": "Authentication required. Please log in as an administrator."
            }), 401
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------
# Admin Authentication Endpoints
# ---------------------------------------------------
@admin_bp.route("/login", methods=["POST"])
def admin_login():
    """Authenticates admin using secure password hash."""
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required."}), 400

    admin_row = fetch_one(
        "SELECT admin_id, username, password_hash FROM admins WHERE username = %s;",
        (username,)
    )

    if not admin_row or not check_password_hash(admin_row["password_hash"], password):
        return jsonify({"success": False, "error": "Invalid username or password."}), 401

    session["admin_logged_in"] = True
    session["admin_id"] = admin_row["admin_id"]
    session["admin_username"] = admin_row["username"]
    session.modified = True

    return jsonify({
        "success": True,
        "message": f"Welcome back, {admin_row['username']}!",
        "admin": {
            "admin_id": admin_row["admin_id"],
            "username": admin_row["username"]
        }
    }), 200


@admin_bp.route("/verify", methods=["GET"])
def verify_session():
    """Checks whether administrator is currently authenticated."""
    is_logged_in = bool(session.get("admin_logged_in"))
    return jsonify({
        "authenticated": is_logged_in,
        "username": session.get("admin_username") if is_logged_in else None
    }), 200


@admin_bp.route("/logout", methods=["POST"])
def admin_logout():
    """Logs out administrator and clears admin session."""
    session.pop("admin_logged_in", None)
    session.pop("admin_id", None)
    session.pop("admin_username", None)
    session.modified = True
    return jsonify({"success": True, "message": "Logged out successfully."}), 200


# ---------------------------------------------------
# Admin Dashboard Statistics
# ---------------------------------------------------
@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def get_dashboard_metrics():
    """Returns business KPIs and inventory health metrics."""
    try:
        # Total products and inventory counts
        counts = fetch_one("""
            SELECT 
                COUNT(*) AS total_products,
                SUM(CASE WHEN stock <= 5 AND stock > 0 THEN 1 ELSE 0 END) AS low_stock_count,
                SUM(CASE WHEN stock = 0 THEN 1 ELSE 0 END) AS out_of_stock_count,
                SUM(stock) AS total_inventory_units
            FROM products;
        """)

        # Total categories
        cat_row = fetch_one("SELECT COUNT(*) AS total_categories FROM categories;")

        # Total orders and revenue
        orders_row = fetch_one("""
            SELECT 
                COUNT(*) AS total_orders,
                COALESCE(SUM(total_amount), 0) AS total_revenue
            FROM orders;
        """)

        # Recent 5 orders
        recent_orders = fetch_all("""
            SELECT 
                o.order_id, 
                o.order_date, 
                o.total_amount, 
                o.order_status,
                c.customer_name, 
                c.customer_email,
                COUNT(oi.order_item_id) AS items_count
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.order_id
            ORDER BY o.order_date DESC
            LIMIT 5;
        """)

        return jsonify({
            "success": True,
            "metrics": {
                "total_products": counts["total_products"] or 0,
                "total_categories": cat_row["total_categories"] or 0,
                "low_stock_count": counts["low_stock_count"] or 0,
                "out_of_stock_count": counts["out_of_stock_count"] or 0,
                "total_inventory_units": int(counts["total_inventory_units"] or 0),
                "total_orders": orders_row["total_orders"] or 0,
                "total_revenue": float(orders_row["total_revenue"] or 0.0),
            },
            "recent_orders": recent_orders,
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------
# Admin Order Management Endpoints
# ---------------------------------------------------
@admin_bp.route("/orders", methods=["GET"])
@admin_required
def list_orders():
    """Retrieves all completed customer transactions with details."""
    try:
        orders = fetch_all("""
            SELECT 
                o.order_id, 
                o.order_date, 
                o.total_amount, 
                o.order_status,
                c.customer_name, 
                c.customer_email,
                COUNT(oi.order_item_id) AS items_count
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.order_id
            ORDER BY o.order_date DESC;
        """)
        return jsonify({"success": True, "orders": orders}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/orders/<int:order_id>", methods=["GET"])
@admin_required
def get_order_details(order_id: int):
    """Retrieves single order with its line items."""
    try:
        order = fetch_one("""
            SELECT 
                o.order_id, 
                o.order_date, 
                o.total_amount, 
                o.order_status,
                c.customer_name, 
                c.customer_email
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = %s;
        """, (order_id,))

        if not order:
            return jsonify({"success": False, "error": f"Order #{order_id} not found."}), 404

        items = fetch_all("""
            SELECT 
                oi.order_item_id, 
                oi.product_id, 
                p.product_name, 
                oi.quantity, 
                oi.unit_price, 
                oi.subtotal
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s;
        """, (order_id,))

        order["items"] = items
        return jsonify({"success": True, "order": order}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route("/orders/<int:order_id>/status", methods=["PATCH"])
@admin_required
def update_order_status(order_id: int):
    """Updates order fulfillment status."""
    data = request.get_json() or {}
    new_status = data.get("order_status") or data.get("status")

    if not new_status:
        return jsonify({"success": False, "error": "New status is required."}), 400

    try:
        execute_query(
            "UPDATE orders SET order_status = %s WHERE order_id = %s;",
            (new_status, order_id),
            commit=True,
        )
        return jsonify({
            "success": True,
            "message": f"Order #{order_id} status updated to '{new_status}'."
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
