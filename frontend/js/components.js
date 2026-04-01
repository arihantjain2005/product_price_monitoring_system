/**
 * components.js — Shared UI Component Library
 * Responsibility: Reusable DOM builders. Returns HTML strings or elements.
 * No API calls, no routing, pure render functions.
 */
const Components = (() => {

    function loader() {
        return `
            <div class="loader-container">
                <div class="loader-spinner"></div>
                <p>Loading data...</p>
            </div>`;
    }

    function emptyState(message = 'No data found.') {
        return `
            <div class="empty-state">
                <span class="empty-state-icon">📭</span>
                <p>${message}</p>
            </div>`;
    }

    function statCard(label, value, id) {
        return `
            <div class="stat-card">
                <h3>${label}</h3>
                <h2 id="${id}">${value}</h2>
            </div>`;
    }

    function productCard(product) {
        const listingsHtml = (product.listings || []).map(listing => `
            <div class="listing-row">
                <span class="listing-marketplace">${listing.marketplace_name}</span>
                <span class="listing-price">$${listing.current_price?.toLocaleString() ?? 'N/A'}</span>
            </div>
        `).join('');

        return `
            <div class="product-card" data-product-id="${product.id}">
                <div class="product-card-brand">${product.brand}</div>
                <div class="product-card-name">${product.name}</div>
                <span class="product-card-category">${product.category}</span>
                <div class="product-card-listings">
                    ${listingsHtml || '<span style="color:var(--text-muted)">No listings yet</span>'}
                </div>
            </div>`;
    }

    let toastContainer = null;
    function toast(message, type = 'info') {
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        const t = document.createElement('div');
        t.className = `toast toast-${type}`;
        t.textContent = message;
        toastContainer.appendChild(t);
        setTimeout(() => t.remove(), 3500);
    }

    return { loader, emptyState, statCard, productCard, toast };
})();
