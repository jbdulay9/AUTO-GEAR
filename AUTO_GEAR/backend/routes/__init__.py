"""
Flask Routes package for AUTO GEAR.
Exports product_bp, algorithm_bp, cart_bp, checkout_bp, and admin_bp.
"""

from backend.routes.product_routes import product_bp
from backend.routes.algorithm_routes import algorithm_bp
from backend.routes.cart_routes import cart_bp
from backend.routes.checkout_routes import checkout_bp
from backend.routes.admin_routes import admin_bp

__all__ = [
    "product_bp",
    "algorithm_bp",
    "cart_bp",
    "checkout_bp",
    "admin_bp",
]
