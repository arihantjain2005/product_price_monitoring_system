/**
 * views/products.js — Products Catalog View
 * Responsibility: Renders and manages the Products Hub screen only.
 * Uses Api service and Components library. No raw fetch calls.
 */
const ProductsView = (() => {

    async function render(container) {
        container.innerHTML = `
            <div class="filter-bar">
                <input type="text"   id="filter-category"  placeholder="Filter by category...">
                <input type="number" id="filter-min-price" placeholder="Min price ($)">
                <input type="number" id="filter-max-price" placeholder="Max price ($)">
            </div>
            <div id="products-grid" class="products-grid">
                ${Components.loader()}
            </div>`;

        document.getElementById('filter-category').addEventListener('keyup',  loadProducts);
        document.getElementById('filter-min-price').addEventListener('change', loadProducts);
        document.getElementById('filter-max-price').addEventListener('change', loadProducts);

        await loadProducts();

        container.querySelectorAll('.product-card').forEach(card => {
            card.addEventListener('click', () => {
                Components.toast(`Product detail view coming in Step 18!`, 'info');
            });
        });
    }

    async function loadProducts() {
        const grid = document.getElementById('products-grid');
        if (!grid) return;

        const category = document.getElementById('filter-category')?.value.trim();
        const minPrice = document.getElementById('filter-min-price')?.value;
        const maxPrice = document.getElementById('filter-max-price')?.value;

        const params = new URLSearchParams();
        if (category) params.set('category', category);
        if (minPrice)  params.set('min_price', minPrice);
        if (maxPrice)  params.set('max_price', maxPrice);
        const qs = params.toString() ? `?${params.toString()}` : '';

        grid.innerHTML = Components.loader();

        try {
            const { data } = await Api.getProducts(qs);
            if (!data || data.length === 0) {
                grid.innerHTML = Components.emptyState('No products match your filters.');
                return;
            }
            grid.innerHTML = data.map(p => Components.productCard(p)).join('');
        } catch (err) {
            grid.innerHTML = Components.emptyState('Could not load products. Is the API running?');
            Components.toast(`Products load failed: ${err.message}`, 'error');
        }
    }

    return { render };
})();
