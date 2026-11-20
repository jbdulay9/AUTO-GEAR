// Shared Helper: Currency Formatter
function formatPHP(amount) {
    return '₱' + Number(amount || 0).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Shared Helper: Toast Notifications
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Shared Helper: Sync Header Cart Badge
async function updateCartBadge() {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;
    try {
        const res = await fetch('/api/cart');
        const data = await res.json();
        if (data.success) {
            badge.textContent = data.total_items || 0;
        }
    } catch (e) {
        // silent fail
    }
}

// Homepage Specific Execution
document.addEventListener('DOMContentLoaded', () => {
    updateCartBadge();

    // 1. Load Featured Products on Homepage
    const featuredGrid = document.getElementById('featured-products-grid');
    if (featuredGrid) {
        loadFeaturedProducts();
    }

    // 2. Setup DSA Tab Switcher
    const tabBtns = document.querySelectorAll('.dsa-tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-target');
            document.querySelectorAll('.dsa-panel').forEach(p => p.style.display = 'none');
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) targetPanel.style.display = 'block';
        });
    });

    // 3. Setup DSA Interactive Tools
    const btnBundles = document.getElementById('btn-build-bundles');
    if (btnBundles) btnBundles.addEventListener('click', runBundleBuilder);

    const btnRecommend = document.getElementById('btn-run-recommend');
    if (btnRecommend) btnRecommend.addEventListener('click', runBudgetOptimizer);

    const btnNav = document.getElementById('btn-run-nav');
    if (btnNav) btnNav.addEventListener('click', runStoreNavigation);
});

// Load 4 Featured Products
async function loadFeaturedProducts() {
    const grid = document.getElementById('featured-products-grid');
    try {
        const res = await fetch('/api/products');
        const data = await res.json();
        if (data.success && data.products.length > 0) {
            const topProducts = data.products.slice(0, 4);
            grid.innerHTML = topProducts.map(p => `
                <div class="product-card">
                    <div class="product-category-tag">${p.category_name || 'Accessories'}</div>
                    <div class="product-title">${p.product_name}</div>
                    <div class="product-description">${p.description || 'High performance automotive accessory.'}</div>
                    <div class="product-footer">
                        <div class="price-stock-row">
                            <span class="product-price">${formatPHP(p.price)}</span>
                            <span class="badge ${p.stock > 5 ? 'badge-in-stock' : (p.stock > 0 ? 'badge-low-stock' : 'badge-out-stock')}">
                                ${p.stock > 0 ? p.stock + ' in stock' : 'Out of stock'}
                            </span>
                        </div>
                        <div class="cart-action-row">
                            <input type="number" id="qty-${p.product_id}" class="qty-input" value="1" min="1" max="${p.stock}">
                            <button class="btn btn-primary btn-add-cart" onclick="quickAddToCart(${p.product_id})">Add to Cart</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        grid.innerHTML = `<div class="empty-state"><p>Could not load featured products.</p></div>`;
    }
}

// Quick Add To Cart from Home
async function quickAddToCart(productId) {
    const qtyInput = document.getElementById(`qty-${productId}`);
    const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

    try {
        const res = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: quantity })
        });
        const data = await res.json();
        if (res.ok && data.success) {
            showToast(data.message, 'success');
            updateCartBadge();
        } else {
            showToast(data.error || 'Failed to add item.', 'error');
        }
    } catch (e) {
        showToast('Server communication error.', 'error');
    }
}

// 1. Backtracking Bundle Builder Handler
async function runBundleBuilder() {
    const budget = parseFloat(document.getElementById('bundle-budget').value);
    const checkedCats = Array.from(document.querySelectorAll('.bundle-cat:checked')).map(cb => cb.value);
    const resultsContainer = document.getElementById('bundle-results');

    if (checkedCats.length === 0) {
        showToast('Please select at least one category for the bundle.', 'error');
        return;
    }

    resultsContainer.innerHTML = '<p style="color: var(--text-secondary);">Exploring valid combination branches (Backtracking)...</p>';

    try {
        const res = await fetch('/api/algorithms/bundle-builder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ categories: checkedCats, max_budget: budget })
        });
        const data = await res.json();
        if (data.success) {
            const bundles = data.data.bundles;
            if (bundles.length === 0) {
                resultsContainer.innerHTML = `<div class="empty-state" style="padding: 2rem;"><p>No combinations found under ${formatPHP(budget)} for the selected categories. Try raising your budget limit.</p></div>`;
                return;
            }
            resultsContainer.innerHTML = bundles.map(b => `
                <div class="card" style="padding: 1.25rem; background-color: var(--bg-card); border-left: 4px solid var(--accent-primary);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <strong>Bundle #${b.bundle_id}</strong>
                        <span style="color: var(--status-success); font-weight: 700;">${formatPHP(b.total_cost)}</span>
                    </div>
                    <ul style="padding-left: 1.25rem; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
                        ${b.items.map(item => `<li>${item.product_name} (${formatPHP(item.price)})</li>`).join('')}
                    </ul>
                    <div style="font-size: 0.8rem; color: var(--text-muted); display: flex; justify-content: space-between;">
                        <span>Budget: ${formatPHP(b.budget)}</span>
                        <span>Savings: ${formatPHP(b.savings)}</span>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        resultsContainer.innerHTML = '<p style="color: var(--status-danger);">Failed to execute bundle builder algorithm.</p>';
    }
}

// 2. Budget Optimizer (Greedy vs DP) Handler
async function runBudgetOptimizer() {
    const budget = parseFloat(document.getElementById('recommend-budget').value);
    const container = document.getElementById('recommend-results');
    container.innerHTML = '<p style="color: var(--text-secondary); grid-column: 1 / -1;">Computing Greedy heuristic and 0/1 Knapsack DP table...</p>';

    try {
        const res = await fetch('/api/algorithms/recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ budget: budget, method: 'compare' })
        });
        const data = await res.json();
        if (data.success) {
            const comp = data.data;
            const greedy = comp.greedy;
            const dp = comp.dynamic_programming;
            const analysis = comp.comparison.analysis;

            container.innerHTML = `
                <!-- Greedy Results -->
                <div class="card" style="padding: 1.25rem; background-color: var(--bg-card);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4>Greedy Heuristic</h4>
                        <span class="badge" style="background-color: rgba(9, 132, 227, 0.2); color: #74b9ff;">O(n log n)</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
                        Rule: ${greedy.decision_rule}
                    </div>
                    <ul style="padding-left: 1.25rem; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
                        ${greedy.selected_items.map(i => `<li>${i.product_name} (${formatPHP(i.price)}) - Score: ${i.score}</li>`).join('')}
                    </ul>
                    <div style="border-top: 1px solid var(--border-color); padding-top: 0.5rem; font-size: 0.85rem;">
                        <div>Total Spent: <strong>${formatPHP(greedy.total_spent)}</strong></div>
                        <div>Total Utility Score: <strong style="color: var(--accent-primary);">${greedy.total_value}</strong></div>
                    </div>
                </div>

                <!-- 0/1 Knapsack DP Results -->
                <div class="card" style="padding: 1.25rem; background-color: var(--bg-card); border-color: var(--status-success);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="color: var(--status-success);">0/1 Knapsack (Optimal DP)</h4>
                        <span class="badge" style="background-color: rgba(0, 184, 148, 0.2); color: var(--status-success);">O(n · W)</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
                        Technique: Tabulation (Global Optimum Guaranteed)
                    </div>
                    <ul style="padding-left: 1.25rem; font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
                        ${dp.selected_items.map(i => `<li>${i.product_name} (${formatPHP(i.price)}) - Score: ${i.score}</li>`).join('')}
                    </ul>
                    <div style="border-top: 1px solid var(--border-color); padding-top: 0.5rem; font-size: 0.85rem;">
                        <div>Total Spent: <strong>${formatPHP(dp.total_spent)}</strong></div>
                        <div>Total Utility Score: <strong style="color: var(--status-success);">${dp.total_value}</strong></div>
                    </div>
                </div>

                <!-- Analytical Summary Banner -->
                <div style="grid-column: 1 / -1; background-color: #0b1a2c; padding: 0.9rem 1.25rem; border-radius: 6px; border: 1px solid #1b4965; font-size: 0.85rem; color: #a2d2ff;">
                    <strong>Algorithmic Comparison:</strong> ${analysis}
                </div>
            `;
        }
    } catch (e) {
        container.innerHTML = '<p style="color: var(--status-danger);">Failed to calculate budget recommendations.</p>';
    }
}

// 3. Dijkstra Store Navigation Handler
async function runStoreNavigation() {
    const start = document.getElementById('nav-start').value;
    const dest = document.getElementById('nav-dest').value;
    const container = document.getElementById('nav-results');

    container.innerHTML = '<p style="color: var(--text-secondary);">Calculating shortest path via Dijkstra min-heap...</p>';

    try {
        const res = await fetch('/api/algorithms/shortest-path', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start: start, destination: dest })
        });
        const data = await res.json();
        if (data.success) {
            const sp = data.data.shortest_path;
            const pathFormatted = sp.path_details.map(node => `<strong>${node.label}</strong>`).join(' &rarr; ');

            container.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <h4 style="color: var(--accent-primary);">Optimal Walking Route</h4>
                    <span class="badge" style="background-color: rgba(230, 126, 34, 0.2); color: var(--accent-primary); font-size: 0.85rem;">
                        Total Distance: ${sp.total_distance_meters} meters
                    </span>
                </div>
                <div style="font-size: 1rem; color: #fff; margin-bottom: 1rem; padding: 0.75rem; background-color: var(--bg-input); border-radius: 5px;">
                    ${pathFormatted}
                </div>
                <div style="display: flex; gap: 1.5rem; font-size: 0.8rem; color: var(--text-muted);">
                    <div>Algorithm: <strong>Dijkstra's Shortest Path</strong></div>
                    <div>Explored Nodes: <strong>${sp.visited_nodes.length}</strong></div>
                    <div>Graph Model: <strong>Weighted Store Walkways</strong></div>
                </div>
            `;
        }
    } catch (e) {
        container.innerHTML = '<p style="color: var(--status-danger);">Failed to calculate store navigation route.</p>';
    }
}
