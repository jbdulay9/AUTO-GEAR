from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from backend.database.connection import get_db_manager, DatabaseManager


class OrderItem:
    """Represents a single purchased line item within an Order."""

    def __init__(
        self,
        order_item_id: int,
        order_id: int,
        product_id: int,
        quantity: int,
        unit_price: float,
        subtotal: float = None,
        product_name: str = None,
    ):
        self.order_item_id = int(order_item_id)
        self.order_id = int(order_id)
        self.product_id = int(product_id)
        self.quantity = int(quantity)
        self.unit_price = float(unit_price)
        self.subtotal = float(subtotal) if subtotal is not None else round(self.quantity * self.unit_price, 2)
        self.product_name = str(product_name).strip() if product_name else f"Product #{self.product_id}"

        self.validate()

    def validate(self):
        """Validates line item rules."""
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if self.unit_price <= 0:
            raise ValueError("Unit price must be positive.")

    def to_dict(self) -> dict:
        """Serializes OrderItem instance to a dictionary."""
        return {
            "order_item_id": self.order_item_id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit_price": round(self.unit_price, 2),
            "subtotal": round(self.subtotal, 2),
        }

    @classmethod
    def from_row(cls, row: dict) -> Optional["OrderItem"]:
        """Constructs an OrderItem instance from a database dictionary row."""
        if not row:
            return None
        unit_price = float(row["unit_price"]) if isinstance(row["unit_price"], (Decimal, float, int)) else 0.0
        subtotal = float(row["subtotal"]) if isinstance(row["subtotal"], (Decimal, float, int)) else 0.0
        return cls(
            order_item_id=row.get("order_item_id", 0),
            order_id=row.get("order_id", 0),
            product_id=row["product_id"],
            quantity=row["quantity"],
            unit_price=unit_price,
            subtotal=subtotal,
            product_name=row.get("product_name"),
        )


class Order:
    """Represents a completed customer transaction in the system."""

    def __init__(
        self,
        order_id: int,
        customer_id: int,
        total_amount: float,
        order_date: Any = None,
        order_status: str = "Completed",
        customer_name: str = None,
        customer_email: str = None,
        items: List[OrderItem] = None,
    ):
        self.order_id = int(order_id)
        self.customer_id = int(customer_id)
        self.total_amount = float(total_amount)
        if isinstance(order_date, datetime):
            self.order_date = order_date.strftime("%Y-%m-%d %H:%M:%S")
        elif order_date:
            self.order_date = str(order_date)
        else:
            self.order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.order_status = str(order_status).strip()
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.items: List[OrderItem] = items or []

    def calculate_total(self) -> float:
        """Calculates total purchase amount from item subtotals."""
        self.total_amount = sum(item.subtotal for item in self.items)
        return round(self.total_amount, 2)

    def to_dict(self) -> dict:
        """Serializes Order instance to a dictionary."""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "order_date": self.order_date,
            "order_status": self.order_status,
            "total_amount": round(self.total_amount, 2),
            "items_count": len(self.items),
            "items": [item.to_dict() for item in self.items],
        }

    @classmethod
    def from_row(cls, row: dict, items: List[OrderItem] = None) -> Optional["Order"]:
        """Constructs an Order instance from a database row."""
        if not row:
            return None
        total = float(row["total_amount"]) if isinstance(row["total_amount"], (Decimal, float, int)) else 0.0
        return cls(
            order_id=row["order_id"],
            customer_id=row["customer_id"],
            total_amount=total,
            order_date=row.get("order_date"),
            order_status=row.get("order_status", "Completed"),
            customer_name=row.get("customer_name"),
            customer_email=row.get("customer_email"),
            items=items or [],
        )


class Receipt:
    """
    Generates structured digital receipts and printable ASCII text for customer purchases.
    Preserves and modernizes the original AUTO GEAR receipt layout.
    """

    def __init__(self, order: Order):
        self.order = order
        self.receipt_id = f"AG-{order.order_id:06d}"
        self.timestamp = order.order_date
        self.customer_name = order.customer_name or "Valued Customer"
        self.customer_email = order.customer_email or "N/A"
        self.items = order.items
        self.total = order.total_amount

    def generate_ascii(self) -> str:
        """Generates formatted ASCII text receipt matching the original desktop design."""
        text = f"""========================================
           AUTO GEAR RECEIPT
========================================
Receipt ID   : {self.receipt_id}
Date         : {self.timestamp}
Customer     : {self.customer_name}
Email        : {self.customer_email}
Status       : {self.order.order_status}

----------------------------------------
ITEMS:
"""
        for item in self.items:
            name_cut = item.product_name[:28]
            text += f"{name_cut:<28} x{item.quantity:2}   ₱{item.subtotal:>10,.2f}\n"

        text += "----------------------------------------\n"
        text += f"TOTAL AMOUNT : ₱{self.total:,.2f}\n"
        text += "========================================\n"
        text += "Thank you for shopping with AUTO GEAR!\n"
        return text

    def to_dict(self) -> dict:
        """Returns structured dictionary representation for web rendering."""
        return {
            "receipt_id": self.receipt_id,
            "order_id": self.order.order_id,
            "date": self.timestamp,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "items": [item.to_dict() for item in self.items],
            "total_amount": round(self.total, 2),
            "ascii_format": self.generate_ascii(),
        }
