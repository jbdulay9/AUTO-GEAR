from flask import Blueprint, jsonify, request
from backend.models.product import ProductService

algorithm_bp = Blueprint("algorithms", __name__)
_product_service = None


def get_service() -> ProductService:
    global _product_service
    if _product_service is None:
        _product_service = ProductService()
    return _product_service


# ---------------------------------------------------
# 1. Searching Algorithms (Linear vs Binary)
# ---------------------------------------------------
@algorithm_bp.route("/search", methods=["POST"])
def search_comparison():
    """Compares Linear Search and Binary Search on the catalog."""
    data = request.get_json() or {}
    target = data.get("target")
    mode = data.get("mode", "name")  # "name" or "id"

    if target is None:
        return jsonify({"success": False, "error": "Target search value is required."}), 400

    try:
        service = get_service()
        result = service.search_catalog(target=target, mode=mode)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------
# 2. Sorting Algorithms (Bubble, Selection, Insertion, Merge, Quick)
# ---------------------------------------------------
@algorithm_bp.route("/sort", methods=["POST"])
def sort_catalog():
    """Sorts catalog products by selected attribute and algorithm."""
    data = request.get_json() or {}
    attribute = data.get("attribute", "price")
    algorithm = data.get("algorithm", "quick")
    reverse = bool(data.get("reverse", False))

    try:
        service = get_service()
        result = service.sort_catalog(attribute=attribute, algorithm=algorithm, reverse=reverse)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------
# 3. Binary Search Tree (BST) Index & Traversals
# ---------------------------------------------------
@algorithm_bp.route("/bst/traverse", methods=["GET"])
def bst_traversals():
    """Returns Inorder, Preorder, and Postorder traversals of the BST product index."""
    try:
        service = get_service()
        result = service.get_bst_traversals()
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------
# 4. Backtracking: Accessory Bundle Builder
# ---------------------------------------------------
@algorithm_bp.route("/bundle-builder", methods=["POST"])
def bundle_builder():
    """Generates valid product bundles via recursive backtracking under budget."""
    data = request.get_json() or {}
    categories = data.get("categories", ["Audio", "Lighting", "Security"])
    max_budget = data.get("max_budget", 15000.0)

    try:
        service = get_service()
        result = service.generate_bundles_backtracking(categories=categories, max_budget=max_budget)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------
# 5. Greedy & Dynamic Programming Recommendations
# ---------------------------------------------------
@algorithm_bp.route("/recommendations", methods=["POST"])
def budget_recommendations():
    """Calculates budget recommendations using Greedy, DP (Knapsack), or comparison."""
    data = request.get_json() or {}
    budget = data.get("budget", 10000.0)
    method = data.get("method", "compare")  # "compare", "greedy", or "dp"

    try:
        service = get_service()
        result = service.recommend_products(budget=budget, method=method)
        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------
# 6. Graph & Dijkstra's Shortest Path Navigation
# ---------------------------------------------------
@algorithm_bp.route("/store-graph", methods=["GET"])
def store_graph_info():
    """Returns store layout vertices and walkway connections."""
    try:
        service = get_service()
        locations = service.store_graph.get_vertices()
        return jsonify({"success": True, "locations": locations}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@algorithm_bp.route("/shortest-path", methods=["POST"])
def shortest_path():
    """Calculates shortest store walking path between aisles via Dijkstra's algorithm."""
    data = request.get_json() or {}
    start = data.get("start", "ENTRANCE")
    destination = data.get("destination", "CASHIER")

    try:
        service = get_service()
        result = service.navigate_store_layout(start_location=start, destination=destination)
        return jsonify({"success": True, "data": result}), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
