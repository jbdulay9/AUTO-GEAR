"""
Flask Blueprint for Product Catalog and Management REST Endpoints.
"""

from flask import Blueprint, jsonify, request
from backend.models.product import ProductService

product_bp = Blueprint("products", __name__)
_product_service = None


def get_service() -> ProductService:
    """Lazy loader for ProductService singleton."""
    global _product_service
    if _product_service is None:
        _product_service = ProductService()
    return _product_service


# ---------------------------------------------------
# Category Endpoints
# ---------------------------------------------------
@product_bp.route("/categories", methods=["GET"])
def get_categories():
    """Returns all available product categories."""
    try:
        service = get_service()
        categories = service.get_all_categories()
        return jsonify({"success": True, "categories": categories}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------
# Product Catalog Endpoints
# ---------------------------------------------------
@product_bp.route("/products", methods=["GET"])
def list_products():
    """
    Returns products in the inventory.
    Supports optional query filter: ?category_id=<int>
    """
    try:
        service = get_service()
        category_id = request.args.get("category_id", type=int)
        products = service.get_all_products(category_id=category_id)
        return jsonify({
            "success": True,
            "count": len(products),
            "products": products
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@product_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id: int):
    """Returns detailed information for a single product."""
    try:
        service = get_service()
        product = service.get_product_by_id(product_id)
        return jsonify({"success": True, "product": product}), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------
# Product Management (CRUD) Endpoints
# ---------------------------------------------------
@product_bp.route("/products", methods=["POST"])
def create_product():
    """Creates a new automotive accessory in the catalog."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400

    try:
        service = get_service()
        new_product = service.create_product(data)
        return jsonify({
            "success": True,
            "message": f"Product '{new_product['product_name']}' created successfully.",
            "product": new_product
        }), 201
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@product_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id: int):
    """Updates an existing product in the catalog."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400

    try:
        service = get_service()
        updated_product = service.update_product(product_id, data)
        return jsonify({
            "success": True,
            "message": f"Product '{updated_product['product_name']}' updated successfully.",
            "product": updated_product
        }), 200
    except ValueError as ve:
        status_code = 404 if "does not exist" in str(ve) else 400
        return jsonify({"success": False, "error": str(ve)}), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@product_bp.route("/products/<int:product_id>/stock", methods=["PATCH"])
def update_stock(product_id: int):
    """Updates stock quantity for a product."""
    data = request.get_json()
    if not data or "stock" not in data:
        return jsonify({"success": False, "error": "Field 'stock' is required."}), 400

    try:
        service = get_service()
        updated_product = service.update_stock(product_id, data["stock"])
        return jsonify({
            "success": True,
            "message": f"Stock for product ID {product_id} updated to {updated_product['stock']}.",
            "product": updated_product
        }), 200
    except ValueError as ve:
        status_code = 404 if "does not exist" in str(ve) else 400
        return jsonify({"success": False, "error": str(ve)}), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@product_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int):
    """Deletes a product from the inventory and database."""
    try:
        service = get_service()
        result = service.delete_product(product_id)
        return jsonify(result), 200
    except ValueError as ve:
        status_code = 404 if "does not exist" in str(ve) else 400
        return jsonify({"success": False, "error": str(ve)}), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
