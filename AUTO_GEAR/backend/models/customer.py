from typing import Optional
from backend.database.connection import get_db_manager, DatabaseManager


class Customer:
    """Represents a customer in the AUTO GEAR system."""

    def __init__(self, customer_id: int, customer_name: str, customer_email: str):
        self.customer_id = int(customer_id)
        self.customer_name = str(customer_name).strip()
        self.customer_email = str(customer_email).strip().lower()
        self.validate()

    def validate(self):
        """Ensures customer information satisfies domain rules."""
        if not self.customer_name:
            raise ValueError("Customer name cannot be empty.")
        if len(self.customer_name) > 150:
            raise ValueError("Customer name cannot exceed 150 characters.")
        if not self.customer_email or "@" not in self.customer_email:
            raise ValueError("A valid email address is required.")
        if len(self.customer_email) > 150:
            raise ValueError("Customer email cannot exceed 150 characters.")

    def to_dict(self) -> dict:
        """Serializes Customer instance to a dictionary."""
        return {
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
        }

    @classmethod
    def from_row(cls, row: dict) -> Optional["Customer"]:
        """Constructs a Customer instance from a database dictionary row."""
        if not row:
            return None
        return cls(
            customer_id=row["customer_id"],
            customer_name=row["customer_name"],
            customer_email=row["customer_email"],
        )

    @classmethod
    def get_by_email(cls, email: str, db: DatabaseManager = None) -> Optional["Customer"]:
        """Finds a customer by email address in MySQL."""
        db = db = db or get_db_manager()
        row = db.fetch_one(
            "SELECT customer_id, customer_name, customer_email FROM customers WHERE customer_email = %s;",
            (email.strip().lower(),)
        )
        return cls.from_row(row)

    @classmethod
    def get_or_create(cls, name: str, email: str, db: DatabaseManager = None) -> "Customer":
        """
        Retrieves existing customer by email, or inserts a new record if not found.
        """
        db = db or get_db_manager()
        existing = cls.get_by_email(email, db)
        if existing:
            # Update name if changed
            if existing.customer_name != name.strip():
                db.execute_query(
                    "UPDATE customers SET customer_name = %s WHERE customer_id = %s;",
                    (name.strip(), existing.customer_id),
                    commit=True,
                )
                existing.customer_name = name.strip()
            return existing

        # Validate before insert
        new_customer = cls(0, name, email)
        result = db.execute_query(
            "INSERT INTO customers (customer_name, customer_email) VALUES (%s, %s);",
            (new_customer.customer_name, new_customer.customer_email),
            commit=True,
        )
        new_customer.customer_id = result["lastrowid"]
        return new_customer
