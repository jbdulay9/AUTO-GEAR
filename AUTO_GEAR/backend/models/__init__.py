"""
OOP Domain Models package for AUTO GEAR.
Exports Category, Product, Inventory, ProductService, Customer, Order, OrderItem, and Receipt.
"""

from backend.models.product import Category, Product, Inventory, ProductService
from backend.models.customer import Customer
from backend.models.order import Order, OrderItem, Receipt

__all__ = [
    "Category",
    "Product",
    "Inventory",
    "ProductService",
    "Customer",
    "Order",
    "OrderItem",
    "Receipt",
]
