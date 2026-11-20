document.addEventListener("DOMContentLoaded", () => {
    updateCartBadge();

    // Determine current page: cart.html or checkout.html
    if (document.getElementById("cart-tbody")) {
        loadCartPage();
        const btnClear = document.getElementById("btn-clear-cart");
        if (btnClear) btnClear.addEventListener("click", clearCart);
    }

    if (document.getElementById("checkout-form")) {
        loadCheckoutPage();
        const form = document.getElementById("checkout-form");
        if (form) form.addEventListener("submit", handleCheckoutSubmit);

        const btnCloseReceipt = document.getElementById("btn-close-receipt");
        if (btnCloseReceipt) {
            btnCloseReceipt.addEventListener("click", () => {
                document.getElementById("receipt-modal").classList.remove("open");
                window.location.href = "products.html";
            });
        }

        const btnPrint = document.getElementById("btn-print-receipt");
        if (btnPrint) {
            btnPrint.addEventListener("click", () => {
                window.print();
            });
        }
    }
});

// ---------------------------------------------------
// Cart Page Operations
// ---------------------------------------------------
async function loadCartPage() {
    const tbody = document.getElementById("cart-tbody");
    const container = document.getElementById("cart-layout-container");
    const emptyState = document.getElementById("empty-cart-state");

    try {
        const res = await fetch("/api/cart");
        const data = await res.json();

        if (data.success) {
            if (data.is_empty || data.items.length === 0) {
                if (container) container.style.display = "none";
                if (emptyState) emptyState.style.display = "block";
                return;
            }

            if (container) container.style.display = "grid";
            if (emptyState) emptyState.style.display = "none";

            tbody.innerHTML = data.items.map(item => `
                <tr>
                    <td>
                        <div style="font-weight: 700; color: #fff;">${item.product_name}</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">${item.category_name}</div>
                    </td>
                    <td>${formatPHP(item.unit_price)}</td>
                    <td>
                        <div class="qty-controls">
                            <button class="qty-btn" onclick="updateItemQuantity(${item.product_id}, ${item.quantity - 1})">-</button>
                            <span class="qty-display">${item.quantity}</span>
                            <button class="qty-btn" onclick="updateItemQuantity(${item.product_id}, ${item.quantity + 1})" ${item.quantity >= item.available_stock ? "disabled style='opacity:0.4;'" : ""}>+</button>
                        </div>
                    </td>
                    <td style="font-weight: 700; color: var(--accent-primary);">${formatPHP(item.subtotal)}</td>
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="removeCartItem(${item.product_id})">Remove</button>
                    </td>
                </tr>
            `).join("");

            document.getElementById("summary-subtotal").textContent = formatPHP(data.total_price);
            document.getElementById("summary-total").textContent = formatPHP(data.total_price);
        }
    } catch (e) {
        showToast("Error loading shopping cart.", "error");
    }
}

async function updateItemQuantity(productId, newQty) {
    try {
        const res = await fetch("/api/cart/update", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_id: productId, quantity: newQty }),
        });
        const data = await res.json();
        if (res.ok && data.success) {
            updateCartBadge();
            loadCartPage();
        } else {
            showToast(data.error || "Cannot update item quantity.", "error");
        }
    } catch (e) {
        showToast("Failed to update cart.", "error");
    }
}

async function removeCartItem(productId) {
    try {
        const res = await fetch(`/api/cart/remove/${productId}`, {
            method: "DELETE",
        });
        const data = await res.json();
        if (data.success) {
            showToast(data.message, "info");
            updateCartBadge();
            loadCartPage();
        }
    } catch (e) {
        showToast("Failed to remove item.", "error");
    }
}

async function clearCart() {
    if (!confirm("Are you sure you want to empty your shopping cart?")) return;
    try {
        const res = await fetch("/api/cart/clear", { method: "DELETE" });
        const data = await res.json();
        if (data.success) {
            showToast("Cart cleared.", "info");
            updateCartBadge();
            loadCartPage();
        }
    } catch (e) {
        showToast("Failed to clear cart.", "error");
    }
}

// ---------------------------------------------------
// Checkout Page Operations
// ---------------------------------------------------
async function loadCheckoutPage() {
    const itemsList = document.getElementById("checkout-items-list");
    const totalDisplay = document.getElementById("checkout-total");
    const container = document.getElementById("checkout-container");
    const emptyNotice = document.getElementById("checkout-empty-notice");

    try {
        const res = await fetch("/api/cart");
        const data = await res.json();

        if (data.success) {
            if (data.is_empty || data.items.length === 0) {
                if (container) container.style.display = "none";
                if (emptyNotice) emptyNotice.style.display = "block";
                return;
            }

            itemsList.innerHTML = data.items.map(item => `
                <div class="review-item">
                    <div>
                        <div style="font-weight: 600; color: #fff;">${item.product_name}</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">${item.quantity} x ${formatPHP(item.unit_price)}</div>
                    </div>
                    <div style="font-weight: 700; color: #fff;">${formatPHP(item.subtotal)}</div>
                </div>
            `).join("");

            totalDisplay.textContent = formatPHP(data.total_price);
        }
    } catch (e) {
        showToast("Error loading order review.", "error");
    }
}

async function handleCheckoutSubmit(e) {
    e.preventDefault();

    const nameInput = document.getElementById("cust-name");
    const emailInput = document.getElementById("cust-email");
    const submitBtn = document.getElementById("btn-submit-order");

    const payload = {
        customer_name: nameInput.value.trim(),
        customer_email: emailInput.value.trim(),
    };

    submitBtn.disabled = true;
    submitBtn.textContent = "Processing Transaction in MySQL...";

    try {
        const res = await fetch("/api/checkout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showToast("Order completed successfully!", "success");
            updateCartBadge();

            // Display Digital Receipt in Modal
            const modal = document.getElementById("receipt-modal");
            const receiptBox = document.getElementById("receipt-ascii-box");
            if (receiptBox && data.receipt) {
                receiptBox.textContent = data.receipt.ascii_format;
            }
            if (modal) modal.classList.add("open");
        } else {
            showToast(data.error || "Checkout transaction failed.", "error");
            submitBtn.disabled = false;
            submitBtn.textContent = "Complete Order & Generate Receipt →";
        }
    } catch (err) {
        showToast("Error during transaction processing.", "error");
        submitBtn.disabled = false;
        submitBtn.textContent = "Complete Order & Generate Receipt →";
    }
}
