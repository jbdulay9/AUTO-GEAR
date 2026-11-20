/**
 * AUTO GEAR - Administrator Console Client Script
 * Handles Admin Authentication, Product CRUD, Low-Stock Inventory Management, Order Auditing, and DSA Visualizer.
 */

document.addEventListener("DOMContentLoaded", () => {
    checkAdminSession();

    // Setup Login Form
    const loginForm = document.getElementById("admin-login-form");
    if (loginForm) loginForm.addEventListener("submit", handleAdminLogin);

    // Setup Logout Button
    const btnLogout = document.getElementById("btn-admin-logout");
    if (btnLogout) btnLogout.addEventListener("click", handleAdminLogout);

    // Setup Refresh Button
    const btnRefresh = document.getElementById("btn-refresh-admin");
    if (btnRefresh) btnRefresh.addEventListener("click", loadDashboardData);

    // Tab Switching
    const tabBtns = document.querySelectorAll(".admin-tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const tabId = btn.getAttribute("data-tab");
            document.querySelectorAll(".admin-tab-content").forEach(content => {
                content.classList.remove("active");
            });
            const target = document.getElementById(tabId);
            if (target) target.classList.add("active");

            // Lazy-load specific tab content
            if (tabId === "tab-products") loadProductsTable();
            if (tabId === "tab-inventory") loadInventoryTable();
            if (tabId === "tab-orders") loadAllOrdersTable();
            if (tabId === "tab-dsa") loadBSTTraversals("inorder");
        });
    });

    // Product Modal Controls
    const btnAddProd = document.getElementById("btn-open-add-product");
    if (btnAddProd) btnAddProd.addEventListener("click", () => openProductModal());

    const btnCloseProdModal = document.getElementById("btn-close-prod-modal");
    if (btnCloseProdModal) btnCloseProdModal.addEventListener("click", closeProductModal);

    const btnCancelProdModal = document.getElementById("btn-cancel-prod-modal");
    if (btnCancelProdModal) btnCancelProdModal.addEventListener("click", closeProductModal);

    const prodForm = document.getElementById("product-form");
    if (prodForm) prodForm.addEventListener("submit", handleProductFormSubmit);

    // Order Modal Close Controls
    const btnCloseOrderModal = document.getElementById("btn-close-order-modal");
    if (btnCloseOrderModal) btnCloseOrderModal.addEventListener("click", closeOrderModal);

    const btnDismissOrderModal = document.getElementById("btn-dismiss-order-modal");
    if (btnDismissOrderModal) btnDismissOrderModal.addEventListener("click", closeOrderModal);

    // BST Traversal Buttons
    const bstBtns = document.querySelectorAll(".bst-view-btn");
    bstBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            bstBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            loadBSTTraversals(btn.getAttribute("data-traversal"));
        });
    });

    // Sort Benchmark Button
    const btnSortBench = document.getElementById("btn-run-sort-benchmark");
    if (btnSortBench) btnSortBench.addEventListener("click", runSortBenchmark);
});

// ---------------------------------------------------
// Authentication & Session
// ---------------------------------------------------
async function checkAdminSession() {
    try {
        const res = await fetch("/api/admin/verify");
        const data = await res.json();
        if (data.authenticated) {
            showDashboardView(data.username);
        } else {
            showLoginView();
        }
    } catch (e) {
        showLoginView();
    }
}

function showLoginView() {
    document.getElementById("admin-login-view").style.display = "flex";
    document.getElementById("admin-dashboard-view").style.display = "none";
}

function showDashboardView(username) {
    document.getElementById("admin-login-view").style.display = "none";
    document.getElementById("admin-dashboard-view").style.display = "block";
    document.getElementById("admin-current-user").textContent = username || "admin";
    loadDashboardData();
    loadCategoryDropdown();
}

async function handleAdminLogin(e) {
    e.preventDefault();
    const user = document.getElementById("admin-user").value.trim();
    const pass = document.getElementById("admin-pass").value.trim();

    try {
        const res = await fetch("/api/admin/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: user, password: pass }),
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showToast(data.message, "success");
            showDashboardView(data.admin.username);
        } else {
            showToast(data.error || "Login denied.", "error");
        }
    } catch (err) {
        showToast("Error authenticating admin.", "error");
    }
}

async function handleAdminLogout() {
    try {
        await fetch("/api/admin/logout", { method: "POST" });
        showToast("Logged out successfully.", "info");
        showLoginView();
    } catch (e) {
        showLoginView();
    }
}

// ---------------------------------------------------
// Tab 1: Dashboard KPIs
// ---------------------------------------------------
async function loadDashboardData() {
    try {
        const res = await fetch("/api/admin/dashboard");
        const data = await res.json();

        if (data.success) {
            const m = data.metrics;
            document.getElementById("kpi-products").textContent = m.total_products;
            document.getElementById("kpi-orders").textContent = m.total_orders;
            document.getElementById("kpi-revenue").textContent = formatPHP(m.total_revenue);
            document.getElementById("kpi-low-stock").textContent = m.low_stock_count;

            const tbody = document.getElementById("recent-orders-tbody");
            if (data.recent_orders.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">No orders recorded yet.</td></tr>`;
            } else {
                tbody.innerHTML = data.recent_orders.map(o => `
                    <tr>
                        <td><strong>#${o.order_id}</strong></td>
                        <td>${o.order_date}</td>
                        <td>${o.customer_name}</td>
                        <td>${o.items_count} items</td>
                        <td style="font-weight: 700; color: var(--status-success);">${formatPHP(o.total_amount)}</td>
                        <td><span class="badge badge-in-stock">${o.order_status}</span></td>
                    </tr>
                `).join("");
            }
        }
    } catch (e) {
        showToast("Error loading dashboard metrics.", "error");
    }
}

// ---------------------------------------------------
// Tab 2: Product Management (CRUD)
// ---------------------------------------------------
let categoriesCache = [];

async function loadCategoryDropdown() {
    try {
        const res = await fetch("/api/categories");
        const data = await res.json();
        if (data.success) {
            categoriesCache = data.categories;
            const select = document.getElementById("prod-category");
            if (select) {
                select.innerHTML = categoriesCache.map(c => `
                    <option value="${c.category_id}">${c.category_name}</option>
                `).join("");
            }
        }
    } catch (e) {
        console.error("Error loading categories:", e);
    }
}

async function loadProductsTable() {
    const tbody = document.getElementById("admin-products-tbody");
    try {
        const res = await fetch("/api/products");
        const data = await res.json();
        if (data.success) {
            tbody.innerHTML = data.products.map(p => `
                <tr>
                    <td><strong>#${p.product_id}</strong></td>
                    <td><div style="font-weight: 700;">${p.product_name}</div><div style="font-size: 0.8rem; color: var(--text-muted);">${p.description || ""}</div></td>
                    <td><span class="badge" style="background-color: var(--bg-card);">${p.category_name}</span></td>
                    <td style="font-weight: 700;">${formatPHP(p.price)}</td>
                    <td><span class="badge ${p.stock > 5 ? "badge-in-stock" : (p.stock > 0 ? "badge-low-stock" : "badge-out-stock")}">${p.stock} units</span></td>
                    <td>
                        <div class="actions-cell">
                            <button class="btn btn-secondary btn-sm" onclick="openEditProductModal(${p.product_id})">Edit</button>
                            <button class="btn btn-danger btn-sm" onclick="deleteProduct(${p.product_id}, '${p.product_name.replace(/'/g, "\\'")}')">Delete</button>
                        </div>
                    </td>
                </tr>
            `).join("");
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" style="color: var(--status-danger);">Failed to load products.</td></tr>`;
    }
}

function openProductModal(isEdit = false, prod = null) {
    const modal = document.getElementById("product-modal");
    const title = document.getElementById("product-modal-title");
    const hiddenId = document.getElementById("edit-prod-id");

    if (isEdit && prod) {
        title.textContent = `Edit Product #${prod.product_id}`;
        hiddenId.value = prod.product_id;
        document.getElementById("prod-name").value = prod.product_name;
        document.getElementById("prod-category").value = prod.category_id;
        document.getElementById("prod-price").value = prod.price;
        document.getElementById("prod-stock").value = prod.stock;
        document.getElementById("prod-desc").value = prod.description || "";
    } else {
        title.textContent = "Add New Automotive Accessory";
        hiddenId.value = "";
        document.getElementById("product-form").reset();
    }
    modal.classList.add("open");
}

function closeProductModal() {
    document.getElementById("product-modal").classList.remove("open");
}

async function openEditProductModal(productId) {
    try {
        const res = await fetch(`/api/products/${productId}`);
        const data = await res.json();
        if (data.success) {
            openProductModal(true, data.product);
        }
    } catch (e) {
        showToast("Failed to fetch product details.", "error");
    }
}

async function handleProductFormSubmit(e) {
    e.preventDefault();
    const editId = document.getElementById("edit-prod-id").value;
    const isEdit = Boolean(editId);

    const payload = {
        product_name: document.getElementById("prod-name").value.trim(),
        category_id: parseInt(document.getElementById("prod-category").value),
        price: parseFloat(document.getElementById("prod-price").value),
        stock: parseInt(document.getElementById("prod-stock").value),
        description: document.getElementById("prod-desc").value.trim(),
    };

    const url = isEdit ? `/api/products/${editId}` : "/api/products";
    const method = isEdit ? "PUT" : "POST";

    try {
        const res = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showToast(data.message, "success");
            closeProductModal();
            loadProductsTable();
            loadDashboardData();
        } else {
            showToast(data.error || "Failed to save product.", "error");
        }
    } catch (err) {
        showToast("Error saving product to database.", "error");
    }
}

async function deleteProduct(productId, productName) {
    if (!confirm(`Are you sure you want to permanently delete '${productName}' from inventory?`)) return;

    try {
        const res = await fetch(`/api/products/${productId}`, { method: "DELETE" });
        const data = await res.json();
        if (res.ok && data.success) {
            showToast(data.message, "success");
            loadProductsTable();
            loadDashboardData();
        } else {
            showToast(data.error || "Failed to delete product.", "error");
        }
    } catch (e) {
        showToast("Error executing product deletion.", "error");
    }
}

// ---------------------------------------------------
// Tab 3: Inventory Stock Adjustment
// ---------------------------------------------------
async function loadInventoryTable() {
    const tbody = document.getElementById("admin-inventory-tbody");
    try {
        const res = await fetch("/api/products");
        const data = await res.json();
        if (data.success) {
            tbody.innerHTML = data.products.map(p => `
                <tr>
                    <td><strong>#${p.product_id}</strong></td>
                    <td>${p.product_name}</td>
                    <td style="font-weight: 700;">${p.stock} units</td>
                    <td>
                        <span class="badge ${p.stock > 5 ? "badge-in-stock" : (p.stock > 0 ? "badge-low-stock" : "badge-out-stock")}">
                            ${p.stock > 5 ? "HEALTHY" : (p.stock > 0 ? "LOW STOCK" : "OUT OF STOCK")}
                        </span>
                    </td>
                    <td>
                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                            <input type="number" id="stock-val-${p.product_id}" class="qty-input" value="${p.stock}" min="0" style="width: 75px;">
                            <button class="btn btn-secondary btn-sm" onclick="saveStockLevel(${p.product_id})">Update Stock</button>
                        </div>
                    </td>
                </tr>
            `).join("");
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="color: var(--status-danger);">Error loading inventory records.</td></tr>`;
    }
}

async function saveStockLevel(productId) {
    const input = document.getElementById(`stock-val-${productId}`);
    const newStock = parseInt(input.value);

    try {
        const res = await fetch(`/api/products/${productId}/stock`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ stock: newStock }),
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showToast(data.message, "success");
            loadInventoryTable();
            loadDashboardData();
        } else {
            showToast(data.error || "Failed to update stock.", "error");
        }
    } catch (e) {
        showToast("Error updating stock quantity.", "error");
    }
}

// ---------------------------------------------------
// Tab 4: Customer Order History
// ---------------------------------------------------
async function loadAllOrdersTable() {
    const tbody = document.getElementById("all-orders-tbody");
    try {
        const res = await fetch("/api/admin/orders");
        const data = await res.json();

        if (data.success) {
            if (data.orders.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No completed orders in database.</td></tr>`;
                return;
            }

            tbody.innerHTML = data.orders.map(o => `
                <tr>
                    <td><strong>#${o.order_id}</strong></td>
                    <td>${o.order_date}</td>
                    <td>${o.customer_name}</td>
                    <td>${o.customer_email}</td>
                    <td>${o.items_count} items</td>
                    <td style="font-weight: 700; color: var(--status-success);">${formatPHP(o.total_amount)}</td>
                    <td><span class="badge badge-in-stock">${o.order_status}</span></td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick="viewOrderDetails(${o.order_id})">View Items</button>
                    </td>
                </tr>
            `).join("");
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="8" style="color: var(--status-danger);">Failed to load order history.</td></tr>`;
    }
}

async function viewOrderDetails(orderId) {
    const modal = document.getElementById("order-detail-modal");
    const modalTitle = document.getElementById("order-modal-title");
    const modalBody = document.getElementById("order-modal-body");

    modalTitle.textContent = `Order #${orderId} Details`;
    modalBody.innerHTML = "<p>Loading order line items...</p>";
    modal.classList.add("open");

    try {
        const res = await fetch(`/api/admin/orders/${orderId}`);
        const data = await res.json();

        if (data.success) {
            const o = data.order;
            modalBody.innerHTML = `
                <div style="margin-bottom: 1rem; font-size: 0.9rem; color: var(--text-secondary);">
                    <div>Customer: <strong>${o.customer_name}</strong> (${o.customer_email})</div>
                    <div>Transaction Date: <strong>${o.order_date}</strong></div>
                    <div>Status: <span class="badge badge-in-stock">${o.order_status}</span></div>
                </div>
                <table class="data-table" style="margin-bottom: 1rem;">
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Unit Price</th>
                            <th>Qty</th>
                            <th>Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${o.items.map(i => `
                            <tr>
                                <td>${i.product_name}</td>
                                <td>${formatPHP(i.unit_price)}</td>
                                <td>${i.quantity}</td>
                                <td style="font-weight: 700;">${formatPHP(i.subtotal)}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
                <div style="text-align: right; font-size: 1.25rem; font-weight: 800; color: var(--accent-primary);">
                    Total Paid: ${formatPHP(o.total_amount)}
                </div>
            `;
        }
    } catch (e) {
        modalBody.innerHTML = "<p style='color: var(--status-danger);'>Failed to load order line items.</p>";
    }
}

function closeOrderModal() {
    document.getElementById("order-detail-modal").classList.remove("open");
}

// ---------------------------------------------------
// Tab 5: DSA Visualizer & Analysis
// ---------------------------------------------------
async function loadBSTTraversals(type = "inorder") {
    const output = document.getElementById("bst-traversal-output");
    output.textContent = "Loading BST index from server...";

    try {
        const res = await fetch("/api/algorithms/bst/traverse");
        const data = await res.json();
        if (data.success) {
            const list = data.data[type];
            output.textContent = `Traversal Mode: ${type.toUpperCase()} (Total Indexed Nodes: ${data.data.bst_size})\n\n` +
                list.map((p, idx) => `[Node #${idx + 1}] ID: ${p.product_id} | ${p.product_name} | ${p.category_name} | ${formatPHP(p.price)} | Stock: ${p.stock}`).join("\n");
        }
    } catch (e) {
        output.textContent = "Failed to load BST traversals.";
    }
}

async function runSortBenchmark() {
    const tbody = document.getElementById("sort-benchmark-tbody");
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-secondary);">Executing Bubble, Selection, Insertion, Merge, and Quick Sort concurrently...</td></tr>`;

    try {
        const res = await fetch("/api/algorithms/sort", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ attribute: "price", algorithm: "all" }),
        });
        const data = await res.json();

        if (data.success) {
            tbody.innerHTML = data.data.results.map(r => `
                <tr>
                    <td><strong>${r.algorithm}</strong></td>
                    <td>${r.classification}</td>
                    <td><code>${r.time_complexity}</code></td>
                    <td><strong>${r.comparisons}</strong></td>
                    <td><strong>${r.swaps}</strong></td>
                    <td style="color: var(--status-success); font-weight: 700;">${r.time_ms} ms</td>
                </tr>
            `).join("");
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" style="color: var(--status-danger);">Benchmark execution failed.</td></tr>`;
    }
}
