/**
 * views/products.js — Products Catalog View
 * Responsibility: Renders and manages the Products Hub screen only.
 * Uses Api service and Components library. No raw fetch calls.
 */
const ProductsView = (() => {
    let debounceTimer = null;
    let currentPage = 0;
    const PAGE_SIZE = 12;
    let _pollTimer = null;
    let _isRendered = false; // true once the grid skeleton is in the DOM

    async function render(container) {
        destroy(); // clear any previous timer before re-rendering
        _isRendered = false;
        currentPage = 0;

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
            debounceTimer = setTimeout(() => { currentPage = 0; _load(false); }, 350);
        };

        document.getElementById('filter-search').addEventListener('keyup', debouncedLoad);
        document.getElementById('filter-category').addEventListener('change', () => { currentPage = 0; _load(false); });
        document.getElementById('filter-source').addEventListener('change', () => { currentPage = 0; _load(false); });
        document.getElementById('filter-min-price').addEventListener('change', () => { currentPage = 0; _load(false); });
        document.getElementById('filter-max-price').addEventListener('change', () => { currentPage = 0; _load(false); });

        document.getElementById('btn-prev').addEventListener('click', () => {
            if (currentPage > 0) { currentPage--; _load(false); }
        });
        document.getElementById('btn-next').addEventListener('click', () => {
            currentPage++;
            _load(false);
        });

        // Initial load — show spinner
        await _load(false);
        _isRendered = true;

        // Poll silently every REFRESH_INTERVAL_MS — NO spinner, patch prices in-place
        _pollTimer = setInterval(() => _load(true), CONFIG.REFRESH_INTERVAL_MS);
    }

    /**
     * _load(silent)
     *   silent=false → shows loader spinner, full re-render (user-initiated)
     *   silent=true  → no spinner, patches card prices in-place (background poll)
     */
    async function _load(silent = false) {
        const grid = document.getElementById('products-grid');
        if (!grid) return;

        // Only show spinner on explicit user-triggered loads
        if (!silent) {
            grid.innerHTML = Components.loader();
        }

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
                if (!silent) {
                    grid.innerHTML = Components.emptyState('No products match your filters. Try a broader search.');
                    if (currentPage === 0 && paginationBar) paginationBar.style.display = 'none';
                }
                return;
            }

            if (silent) {
                // ── Silent poll: patch prices in-place, no full re-render ──
                _patchPricesInPlace(grid, data);
            } else {
                // ── User-triggered: full re-render ──
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
            }

        } catch (err) {
            if (!silent) {
                grid.innerHTML = Components.emptyState('Could not load products. Is the API running?');
                Components.toast(`Products load failed: ${err.message}`, 'error');
            }
        }
    }

    /**
     * Patch only the price values inside existing product cards.
     * Finds each card by data-product-id, then updates each listing's price span.
     * Flashes a highlight animation when a price actually changed.
     */
    function _patchPricesInPlace(grid, products) {
        products.forEach(product => {
            const card = grid.querySelector(`.product-card[data-product-id="${product.id}"]`);
            if (!card) return; // card not in DOM (different page) — skip

            // Get all listing rows in this card
            const listingRows = card.querySelectorAll('.listing-row');

            product.listings.forEach((listing, index) => {
                const row = listingRows[index];
                if (!row) return;

                const priceEl = row.querySelector('.listing-price');
                if (!priceEl) return;

                const newPrice = listing.current_price != null
                    ? `$${listing.current_price.toLocaleString()}`
                    : 'N/A';

                if (priceEl.textContent !== newPrice) {
                    // Price changed — update and flash
                    priceEl.textContent = newPrice;
                    priceEl.classList.remove('price-updated');
                    // Force reflow so animation restarts
                    void priceEl.offsetWidth;
                    priceEl.classList.add('price-updated');
                }
            });
        });
    }

    function destroy() {
        if (_pollTimer !== null) {
            clearInterval(_pollTimer);
            _pollTimer = null;
        }
        _isRendered = false;
    }

    return { render, destroy, sync: () => _load(true) };
})();

