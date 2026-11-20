import os
import sys
from pathlib import Path
from flask import Flask, jsonify, send_from_directory

# Ensure project root is in the Python search path
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config
from backend.database.connection import test_connection, fetch_all
from backend.routes.product_routes import product_bp
from backend.routes.algorithm_routes import algorithm_bp
from backend.routes.cart_routes import cart_bp
from backend.routes.checkout_routes import checkout_bp
from backend.routes.admin_routes import admin_bp


def create_app():
    """Application factory for the AUTO GEAR Flask backend."""
    app = Flask(
        __name__,
        static_folder=str(PROJECT_ROOT / "frontend"),
        template_folder=str(PROJECT_ROOT / "frontend"),
        static_url_path="",
    )
    app.config.from_object(Config)

    # ---------------------------------------------------
    # Register REST API Blueprints
    # ---------------------------------------------------
    app.register_blueprint(product_bp, url_prefix="/api")
    app.register_blueprint(algorithm_bp, url_prefix="/api/algorithms")
    app.register_blueprint(cart_bp, url_prefix="/api")
    app.register_blueprint(checkout_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # ---------------------------------------------------
    # Health and Diagnostic Endpoints
    # ---------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint to verify Flask is running."""
        return jsonify({
            "status": "online",
            "framework": "Flask",
            "environment": "development" if Config.DEBUG else "production",
            "message": "AUTO GEAR backend service is running successfully"
        }), 200

    @app.route("/api/db-check", methods=["GET"])
    def db_check():
        """Database connectivity diagnostic endpoint."""
        db_status = test_connection()
        if db_status.get("success"):
            try:
                products = fetch_all("SELECT COUNT(*) AS total_products FROM products;")
                total = products[0]["total_products"] if products else 0
                return jsonify({
                    "status": "connected",
                    "database": Config.DB_NAME,
                    "host": Config.DB_HOST,
                    "port": Config.DB_PORT,
                    "total_seeded_products": total,
                    "message": "MySQL database connection established and verified"
                }), 200
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "database": Config.DB_NAME,
                    "error": str(e)
                }), 500
        else:
            return jsonify({
                "status": "disconnected",
                "database": Config.DB_NAME,
                "error": db_status.get("error")
            }), 500

    # ---------------------------------------------------
    # Frontend Page Serving
    # ---------------------------------------------------
    @app.route("/", methods=["GET"])
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/products.html", methods=["GET"])
    def products_page():
        return send_from_directory(app.static_folder, "products.html")

    @app.route("/cart.html", methods=["GET"])
    def cart_page():
        return send_from_directory(app.static_folder, "cart.html")

    @app.route("/checkout.html", methods=["GET"])
    def checkout_page():
        return send_from_directory(app.static_folder, "checkout.html")

    @app.route("/admin.html", methods=["GET"])
    def admin_page():
        return send_from_directory(app.static_folder, "admin.html")

    return app


if __name__ == "__main__":
    app = create_app()
    print(f"Starting AUTO GEAR server on http://127.0.0.1:5000 (Debug: {Config.DEBUG})")
    app.run(host="127.0.0.1", port=5000, debug=Config.DEBUG)
