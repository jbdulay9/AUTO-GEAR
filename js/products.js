let allProducts = [];
let currentCategory = "";

document.addEventListener("DOMContentLoaded", () => {
    updateCartBadge();
    loadCategories();
    loadProducts();

    // Event Listeners for Controls
    const searchInput = document.getElementById("catalog-search");
    if (searchInput) {
        searchInput.addEventListener("input", debounce(handleSearch, 300));
    }

    const sortAttr = document.getElementById("sort-attribute");
    const sortAlgo = document.getElementById("sort-algorithm");
    const sortOrder = document.getElementById("sort-order");

    if (sortAttr) sortAttr.addEventListener("change", applySorting);
    if (sortAlgo) sortAlgo.addEventListener("change", applySorting);
    if (sortOrder) sortOrder.addEventListener("change", applySorting);

    const dismissMetric = document.getElementById("metric-dismiss");
    if (dismissMetric) {
        dismissMetric.addEventListener("click", () => {
            document.getElementById("algorithm-metric-banner").style.display = "none";
        });
    }
});

// Utility: Debounce Input
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// 1. Load Categories
async function loadCategories() {
    const container = document.getElementById("category-pills-container");
    if (!container) return;

    try {
        const res = await fetch("/api/categories");
        const data = await res.json();
        if (data.success) {
            container.innerHTML = `<button class="pill-btn active" data-category="">All Categories</button>` +
                data.categories.map(c => `
                    <button class="pill-btn" data-category="${c.category_id}">${c.category_name}</button>
                `).join("");

            container.querySelectorAll(".pill-btn").forEach(btn => {
                btn.addEventListener("click", () => {
                    container.querySelectorAll(".pill-btn").forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                    currentCategory = btn.getAttribute("data-category");
                    loadProducts();
                });
            });
        }
    } catch (e) {
        console.error("Failed to load categories:", e);
    }
}

// 2. Load Products Catalog
async function loadProducts() {
    const grid = document.getElementById("products-grid");
    if (!grid) return;

    let url = "/api/products";
    if (currentCategory) {
        url += `?category_id=${currentCategory}`;
    }

    try {
        const res = await fetch(url);
        const data = await res.json();
        if (data.success) {
            allProducts = data.products;
            applySorting();
        }
    } catch (e) {
        grid.innerHTML = `<div class="empty-state"><p>Error connecting to catalog service.</p></div>`;
    }
}

// 3. Sorting using Manual DSA Algorithms
async function applySorting() {
    const attribute = document.getElementById("sort-attribute").value;
    const algorithm = document.getElementById("sort-algorithm").value;
    const isDesc = document.getElementById("sort-order").value === "desc";
    const banner = document.getElementById("algorithm-metric-banner");
    const metricText = document.getElementById("metric-text");

    try {
        const res = await fetch("/api/algorithms/sort", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                attribute: attribute,
                algorithm: algorithm,
                reverse: isDesc,
            }),
        });
        const data = await res.json();

        if (data.success) {
            if (algorithm === "all") {
                // Benchmarked all 5 sorts
                const results = data.data.results;
                const fastest = results.reduce((prev, curr) => (prev.time_ms < curr.time_ms ? prev : curr));
                banner.style.display = "flex";
                metricText.innerHTML = `<strong>Sort Benchmark across 5 Algorithms:</strong> Fastest: <em>${fastest.algorithm}</em> (${fastest.time_ms} ms) | Quick Sort: ${results[4].comparisons} comps | Merge Sort: ${results[3].comparisons} comps | Bubble: ${results[0].comparisons} comps`;
                renderProductGrid(data.data.sorted_items);
            } else {
                const metrics = data.data.metrics;
                banner.style.display = "flex";
                metricText.innerHTML = `<strong>${metrics.algorithm} (${metrics.time_complexity}):</strong> Comparisons: <strong>${metrics.comparisons}</strong> | Swaps/Moves: <strong>${metrics.swaps}</strong> | Execution Time: <strong>${metrics.time_ms} ms</strong> | Sorted by: <em>${attribute}</em>`;
                renderProductGrid(data.data.products);
            }
        }
    } catch (e) {
        console.error("Sorting error:", e);
        renderProductGrid(allProducts);
    }
}

// 4. Searching using Linear and Binary Search Algorithms
async function handleSearch() {
    const query = document.getElementById("catalog-search").value.trim();
    if (!query) {
        loadProducts();
        return;
    }

    const banner = document.getElementById("algorithm-metric-banner");
    const metricText = document.getElementById("metric-text");

    // Detect if numeric ID search or string name search
    const isNumeric = /^\d+$/.test(query);
    const mode = isNumeric ? "id" : "name";

    try {
        const res = await fetch("/api/algorithms/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ target: isNumeric ? parseInt(query) : query, mode: mode }),
        });
        const data = await res.json();

        if (data.success) {
            const comp = data.data;
            const lin = comp.linear_search;
            const bin = comp.binary_search;

            banner.style.display = "flex";
            metricText.innerHTML = `<strong>Search Comparison:</strong> Linear Search: <strong>${lin.comparisons}</strong> comparisons (${lin.time_ms} ms) vs. Binary Search: <strong>${bin.comparisons}</strong> comparisons (${bin.time_ms} ms) | Efficiency Gain: <strong>${comp.efficiency_ratio}x</strong>`;

            if (lin.found && lin.item) {
                renderProductGrid([lin.item]);
            } else {
                renderProductGrid([]);
            }
        }
    } catch (e) {
        console.error("Search error:", e);
    }
}

// 5. Render Product Grid
function renderProductGrid(products) {
    const grid = document.getElementById("products-grid");
    if (!products || products.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">&#128269;</div>
                <h3>No matching automotive accessories found</h3>
                <p style="color: var(--text-secondary); margin-top: 0.5rem;">Try modifying your search query or category filters.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = products.map(p => `
        <div class="product-card">
            <div class="product-category-tag">${p.category_name || "Accessories"}</div>
            <div class="product-title">${p.product_name}</div>
            <div class="product-description">${p.description || "High-quality precision engineered automotive component."}</div>
            <div class="product-footer">
                <div class="price-stock-row">
                    <span class="product-price">${formatPHP(p.price)}</span>
                    <span class="badge ${p.stock > 5 ? "badge-in-stock" : (p.stock > 0 ? "badge-low-stock" : "badge-out-stock")}">
                        ${p.stock > 0 ? p.stock + " in stock" : "Out of stock"}
                    </span>
                </div>
                <div class="cart-action-row">
                    <input type="number" id="qty-${p.product_id}" class="qty-input" value="1" min="1" max="${p.stock}" ${p.stock <= 0 ? "disabled" : ""}>
                    <button class="btn btn-primary btn-add-cart" onclick="addToCart(${p.product_id})" ${p.stock <= 0 ? "disabled style='opacity:0.5; cursor:not-allowed;'" : ""}>
                        ${p.stock > 0 ? "Add to Cart" : "Sold Out"}
                    </button>
                </div>
            </div>
        </div>
    `).join("");
}

// 6. Add to Cart
async function addToCart(productId) {
    const qtyInput = document.getElementById(`qty-${productId}`);
    const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

    try {
        const res = await fetch("/api/cart/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_id: productId, quantity: quantity }),
        });
        const data = await res.json();

        if (res.ok && data.success) {
            showToast(data.message, "success");
            updateCartBadge();
        } else {
            showToast(data.error || "Failed to add product.", "error");
        }
    } catch (e) {
        showToast("Error communicating with cart service.", "error");
    }
}
