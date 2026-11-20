import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime
from pathlib import Path


# PRODUCT CLASS
class Product:

    def __init__(self, product_id, name, category, price, stock):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock


# CART ITEM CLASS
class CartItem:

    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

    def subtotal(self):
        return self.product.price * self.quantity


# SHOPPING CART CLASS
class ShoppingCart:

    def __init__(self):
        self.items = []

    def add_item(self, product, quantity):
        for item in self.items:
            if item.product.product_id == product.product_id:
                item.quantity += quantity
                return
        self.items.append(CartItem(product, quantity))

    def remove_item(self, product_id):
        self.items = [item for item in self.items if item.product.product_id != product_id]

    def total_price(self):
        total = 0
        for item in self.items:
            total += item.subtotal()
        return total

    def clear_cart(self):
        self.items.clear()


# RECEIPT CLASS
class Receipt:

    def __init__(self, customer_name, customer_email, cart):
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.cart = cart
        self.total = cart.total_price()

        self.receipts_folder = Path("receipts")

        now = datetime.now()
        self.receipt_id = now.strftime("%Y%m%d%H%M%S")
        self.date = now.strftime("%Y-%m-%d %H:%M:%S")

    def _ensure_folder_exists(self):
        if not self.receipts_folder.exists():
            self.receipts_folder.mkdir(parents=True, exist_ok=True)

    def generate_text(self):
        text = f"""
====================================
           AUTO GEAR RECEIPT
====================================
Receipt ID   : {self.receipt_id}
Date         : {self.date}
Customer     : {self.customer_name}
Email        : {self.customer_email}

----------------------------------------
ITEMS:
"""
        for item in self.cart.items:
            text += f"{item.product.name:<35} x{item.quantity:2}   ₱{item.subtotal():,.2f}\n"

        text += "----------------------------------------\n"
        text += f"TOTAL AMOUNT : ₱{self.total:,.2f}\n"
        text += "\nThank you for shopping with AUTO GEAR!\n"
        return text

    def save(self):
        self._ensure_folder_exists()

        try:
            filename = self.receipts_folder / f"AUTOGEAR_Receipt_{self.receipt_id}.txt"
            filename.write_text(self.generate_text(), encoding="utf-8")
            return str(filename)
        except OSError:
            return None


# AUTOGEAR SYSTEM CLASS
class AutoGearSystem:

    def __init__(self):
        self.products = []
        self.cart = ShoppingCart()
        self.admin_password = "admin123"
        self.load_products()

    def load_products(self):
        try:
            with open("products.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                self.products = []
                for item in data:
                    product = Product(
                        item["product_id"], item["name"], item["category"],
                        item["price"], item["stock"]
                    )
                    self.products.append(product)
        except FileNotFoundError:
            self.products = [
                Product(1, "Speakers", "Audio", 4500, 15),
                Product(2, "Amplifiers", "Audio", 8500, 10),
                Product(3, "LED Lights", "Lighting", 2800, 20),
                Product(4, "LED Bulbs", "Lighting", 1200, 25),
                Product(5, "Car Horns", "Accessories", 1800, 15),
                Product(6, "Car Security Systems (Alarm)", "Security", 6500, 8),
                Product(7, "Rain Visors", "Exterior", 2200, 20),
                Product(8, "Paradise Air - Cherry", "Air Freshener", 350, 30),
                Product(9, "Paradise Air - Vanilla", "Air Freshener", 350, 30),
                Product(10, "Paradise Air - Sandalwood", "Air Freshener", 350, 30),
            ]
            self.save_products()

    def save_products(self):
        data = [vars(p) for p in self.products]
        with open("products.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def get_next_product_id(self):
        # Prevents duplicate IDs after deleting items
        return max((p.product_id for p in self.products), default=0) + 1

    def find_product(self, product_id):
        for product in self.products:
            if product.product_id == product_id:
                return product
        return None

    def add_product(self, product):
        self.products.append(product)
        self.save_products()

    def delete_product(self, product_id):
        self.products = [p for p in self.products if p.product_id != product_id]
        self.save_products()

    def checkout(self, customer_name, customer_email):
        if not self.cart.items:
            return None, "Cart is empty"

        receipt = Receipt(customer_name, customer_email, self.cart)
        filename = receipt.save()

        self.cart.clear_cart()
        return receipt, filename


# GUI
class AutoGearGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("AUTO GEAR SYSTEM")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1e1e1e")

        self.system = AutoGearSystem()

        # Restore reserved cart stock if window is closed before checkout
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_header()
        self.create_cart_section()
        self.create_left_section()

    def on_closing(self):
        if self.system.cart.items:
            self.clear_cart()
        self.root.destroy()

    def create_header(self):
        header = tk.Frame(self.root, bg="#111")
        header.pack(fill="x")
        tk.Label(
            header, text="AUTO GEAR", font=("Arial", 24, "bold"),
            fg="white", bg="#111", pady=15
        ).pack(side="left", padx=20)
        tk.Button(
            header, text="Admin Panel", bg="#d63031", fg="white",
            font=("Arial", 10, "bold"), command=self.admin_login
        ).pack(side="right", padx=20)

    def create_left_section(self):
        # Container for product table, add-to-cart controls, and checkout form
        self.left_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.create_product_section(self.left_frame)
        self.create_checkout_section(self.left_frame)

    def create_product_section(self, parent):
        tk.Label(
            parent, text="Available Products", font=("Arial", 16, "bold"),
            fg="white", bg="#1e1e1e"
        ).pack(anchor="w")

        columns = ("ID", "Name", "Category", "Price", "Stock")
        self.product_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=140)
        self.product_tree.pack(fill="both", expand=True, pady=10)
        self.display_products()

        cf = tk.Frame(parent, bg="#1e1e1e")
        cf.pack(fill="x", pady=(0, 10))
        tk.Label(cf, text="Quantity:", fg="white", bg="#1e1e1e").pack(side="left")
        self.quantity_entry = tk.Entry(cf, width=5)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.pack(side="left", padx=5)
        tk.Button(
            cf, text="Add To Cart", bg="#00b894", fg="white",
            font=("Arial", 10, "bold"), command=self.add_to_cart
        ).pack(side="left", padx=10)

    def create_cart_section(self):
        frame = tk.Frame(self.root, bg="#2d3436", width=350)
        frame.pack(side="right", fill="y", padx=10, pady=10)

        tk.Label(
            frame, text="Shopping Cart", font=("Arial", 16, "bold"),
            fg="white", bg="#2d3436"
        ).pack(pady=10)

        columns = ("Product", "Qty", "Subtotal")
        self.cart_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=110)
        self.cart_tree.pack(padx=10, pady=10)

        self.total_label = tk.Label(
            frame, text="Total: ₱0.00", font=("Arial", 14, "bold"),
            fg="#ffeaa7", bg="#2d3436"
        )
        self.total_label.pack(pady=10)

        tk.Button(frame, text="Remove Selected", bg="#d63031", fg="white", command=self.remove_item).pack(pady=5)
        tk.Button(frame, text="Clear Cart", bg="#636e72", fg="white", command=self.clear_cart).pack(pady=5)

    def create_checkout_section(self, parent):
        # Packed cleanly inside left_frame instead of hardcoded .place() coordinates
        frame = tk.Frame(parent, bg="#1e1e1e")
        frame.pack(fill="x", anchor="w", pady=10)

        tk.Label(frame, text="Customer Name:", fg="white", bg="#1e1e1e").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="Email:", fg="white", bg="#1e1e1e").grid(row=1, column=0, sticky="w")

        self.name_entry = tk.Entry(frame, width=30)
        self.email_entry = tk.Entry(frame, width=30)

        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(
            frame, text="Checkout", bg="#0984e3", fg="white", width=20,
            font=("Arial", 10, "bold"), command=self.checkout
        ).grid(row=2, column=0, columnspan=2, pady=10)

    def display_products(self):
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        for p in self.system.products:
            self.product_tree.insert("", "end", values=(p.product_id, p.name, p.category, f"₱{p.price:,.2f}", p.stock))

    def add_to_cart(self):
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a product.")
            return
        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive quantity.")
            return

        values = self.product_tree.item(selected[0], "values")
        product = self.system.find_product(int(values[0]))

        if product is None:
            messagebox.showerror("Error", "Selected product no longer exists.")
            return

        if product.stock < quantity:
            messagebox.showerror("Error", "Not enough stock available.")
            return

        product.stock -= quantity
        self.system.save_products()
        self.system.cart.add_item(product, quantity)

        self.display_products()
        self.refresh_cart()
        messagebox.showinfo("Success", "Item added to cart.")

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        for item in self.system.cart.items:
            self.cart_tree.insert("", "end", values=(item.product.name, item.quantity, f"₱{item.subtotal():,.2f}"))
        self.total_label.config(text=f"Total: ₱{self.system.cart.total_price():,.2f}")

    def remove_item(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item in the cart to remove.")
            return
        values = self.cart_tree.item(selected[0], "values")
        for item in self.system.cart.items:
            if item.product.name == values[0]:
                item.product.stock += item.quantity
                self.system.cart.remove_item(item.product.product_id)
                break
        self.system.save_products()
        self.display_products()
        self.refresh_cart()

    def clear_cart(self):
        for item in self.system.cart.items:
            item.product.stock += item.quantity
        self.system.cart.clear_cart()
        self.system.save_products()
        self.display_products()
        self.refresh_cart()

    def checkout(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()

        if not name or not email:
            messagebox.showerror("Error", "Please enter customer details.")
            return

        receipt, filename = self.system.checkout(name, email)

        if receipt is None:
            messagebox.showwarning("Empty Cart", "Your cart is empty.")
            return

        if filename:
            messagebox.showinfo("Success", f"Checkout Successful!\n\nReceipt saved:\n{filename}")
        else:
            messagebox.showinfo("Success", "Checkout Successful!\nReceipt could not be saved.")

        self.refresh_cart()
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

    def admin_login(self):
        password = simpledialog.askstring("Admin Login", "Enter Admin Password:", show="*")
        if password is None:
            return
        if password == self.system.admin_password:
            self.open_admin_panel()
        else:
            messagebox.showerror("Access Denied", "Incorrect Password!")

    def open_admin_panel(self):
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Panel")
        admin_window.geometry("400x450")
        admin_window.configure(bg="#2d3436")

        tk.Label(admin_window, text="ADMIN PANEL", font=("Arial", 18, "bold"), fg="white", bg="#2d3436").pack(pady=15)

        tk.Label(admin_window, text="Product Name", fg="white", bg="#2d3436").pack()
        name_entry = tk.Entry(admin_window, width=30)
        name_entry.pack(pady=5)

        tk.Label(admin_window, text="Category", fg="white", bg="#2d3436").pack()
        category_entry = tk.Entry(admin_window, width=30)
        category_entry.pack(pady=5)

        tk.Label(admin_window, text="Price", fg="white", bg="#2d3436").pack()
        price_entry = tk.Entry(admin_window, width=30)
        price_entry.pack(pady=5)

        tk.Label(admin_window, text="Stock", fg="white", bg="#2d3436").pack()
        stock_entry = tk.Entry(admin_window, width=30)
        stock_entry.pack(pady=5)

        def add_product():
            name = name_entry.get().strip()
            category = category_entry.get().strip()

            if not name or not category:
                messagebox.showerror("Error", "Name and category cannot be empty.", parent=admin_window)
                return

            try:
                price = float(price_entry.get())
                stock = int(stock_entry.get())
                if price <= 0 or stock < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Price must be > 0 and stock must be >= 0.", parent=admin_window)
                return

            new_id = self.system.get_next_product_id()
            new_product = Product(new_id, name, category, price, stock)
            self.system.add_product(new_product)
            self.display_products()

            name_entry.delete(0, tk.END)
            category_entry.delete(0, tk.END)
            price_entry.delete(0, tk.END)
            stock_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "Product added successfully.", parent=admin_window)

        def delete_product():
            selected = self.product_tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Select a product.", parent=admin_window)
                return

            pid = int(self.product_tree.item(selected[0], "values")[0])

            # Prevent deleting a product that is currently reserved in the cart
            if any(item.product.product_id == pid for item in self.system.cart.items):
                messagebox.showerror(
                    "Error",
                    "Cannot delete product while it is in the shopping cart.",
                    parent=admin_window
                )
                return

            self.system.delete_product(pid)
            self.display_products()
            messagebox.showinfo("Deleted", "Product deleted.", parent=admin_window)

        tk.Button(
            admin_window, text="Add Product", bg="#00b894", fg="white",
            width=20, command=add_product
        ).pack(pady=10)
        tk.Button(
            admin_window, text="Delete Selected Product", bg="#d63031", fg="white",
            width=20, command=delete_product
        ).pack(pady=5)


# MAIN PROGRAM
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoGearGUI(root)
    root.mainloop()