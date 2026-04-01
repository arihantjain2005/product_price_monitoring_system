/**
 * views/products.js — Products Catalog View
 * Responsibility: Renders and manages the Products Hub screen only.
 * Uses Api service and Components library. No raw fetch calls.
 */
const ProductsView = (() => {
    let debounceTimer = null;
    let currentPage = 0;
    const PAGE_SIZE = 12;

    async function render(container) {
        container.innerHTML = `
            <div class="filter-bar">
                <input type="text"   id="filter-search"  placeholder="🔍  Search products..." autocomplete="off">
                <select id="filter-category">
                    <option value="">All Categories</option>
                    <option value="Belts">Belts</option>
                    <option value="Jewelry">Jewelry</option>
                    <option value="Apparel">Apparel</option>
                    <option value="General">General</option>
                </select>
                <select id="filter-source">
                    <option value="">All Marketplaces</option>
                    <option value="Grailed">Grailed</option>
                    <option value="Fashionphile">Fashionphile</option>
                    <option value="1stdibs">1stdibs</option>
                </select>
                <input type="number" id="filter-min-price" placeholder="Min $" min="0" step="any">
                <input type="number" id="filter-max-price" placeholder="Max $" min="0" step="any">
            </div>
            <div id="products-grid" class="products-grid"></div>
            <div class="pagination-bar" id="pagination-bar" style="display:none;">
                <button class="btn-page" id="btn-prev">← Prev</button>
                <span   class="page-info" id="page-info">Page 1</span>
                <button class="btn-page" id="btn-next">Next →</button>
            </div>`;

        const debouncedLoad = () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => { currentPage = 0; _load(); }, 350);
        };

        document.getElementById('filter-search').addEventListener('keyup', debouncedLoad);
        document.getElementById('filter-category').addEventListener('change', () => { currentPage = 0; _load(); });
        document.getElementById('filter-source').addEventListener('change', () => { currentPage = 0; _load(); });
        document.getElementById('filter-min-price').addEventListener('change', () => { currentPage = 0; _load(); });
        document.getElementById('filter-max-price').addEventListener('change', () => { currentPage = 0; _load(); });

        document.getElementById('btn-prev').addEventListener('click', () => {
            if (currentPage > 0) { currentPage--; _load(); }
        });
        document.getElementById('btn-next').addEventListener('click', () => {
            currentPage++;
            _load();
        });

        await _load();
    }

    async function _load() {
        const grid = document.getElementById('products-grid');
        if (!grid) return;

        grid.innerHTML = Components.loader();

        const search   = document.getElementById('filter-search')?.value.trim();
        const category = document.getElementById('filter-category')?.value;
        const source   = document.getElementById('filter-source')?.value;
        const minPrice = document.getElementById('filter-min-price')?.value;
        const maxPrice = document.getElementById('filter-max-price')?.value;

        const params = new URLSearchParams();
        if (search)   params.set('search', search);
        if (category) params.set('category', category);
        if (source)   params.set('source', source);
        if (minPrice) params.set('min_price', minPrice);
        if (maxPrice) params.set('max_price', maxPrice);
        params.set('skip',  currentPage * PAGE_SIZE);
        params.set('limit', PAGE_SIZE);

        try {
            const { data } = await Api.getProducts(`?${params.toString()}`);

            const paginationBar = document.getElementById('pagination-bar');
            const pageInfo      = document.getElementById('page-info');
            const btnPrev       = document.getElementById('btn-prev');
            const btnNext       = document.getElementById('btn-next');

            if (!data || data.length === 0) {
                grid.innerHTML = Components.emptyState('No products match your filters. Try a broader search.');
                if (currentPage === 0 && paginationBar) paginationBar.style.display = 'none';
                return;
            }

            grid.innerHTML = data.map(p => Components.productCard(p)).join('');

            if (paginationBar) {
                paginationBar.style.display = 'flex';
                if (pageInfo) pageInfo.textContent = `Page ${currentPage + 1}`;
                if (btnPrev)  btnPrev.disabled = currentPage === 0;
                if (btnNext)  btnNext.disabled = data.length < PAGE_SIZE;
            }

            grid.querySelectorAll('.product-card').forEach(card => {
                card.addEventListener('click', () => {
                    const id = card.dataset.productId;
                    Router.navigateToDetail(id);
                });
            });

        } catch (err) {
            grid.innerHTML = Components.emptyState('Could not load products. Is the API running?');
            Components.toast(`Products load failed: ${err.message}`, 'error');
        }
    }

    return { render };
})();

