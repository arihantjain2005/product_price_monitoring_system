/**
 * views/dashboard.js — Dashboard View
 * Responsibility: Renders and manages the Dashboard screen only.
 * Uses Api service and Components library. No raw fetch calls.
 */
const DashboardView = (() => {

    async function render(container) {
        container.innerHTML = `
            <div class="stats-grid">
                ${Components.statCard('Canonical Products',    '--', 'stat-products')}
                ${Components.statCard('Tracked Listings',     '--', 'stat-listings')}
                ${Components.statCard('Price Fluctuations',   '--', 'stat-changes')}
            </div>`;

        try {
            const { data } = await Api.getAnalytics();
            document.getElementById('stat-products').textContent = data.summary.total_canonical_products;
            document.getElementById('stat-listings').textContent = data.summary.total_tracked_listings;
            document.getElementById('stat-changes').textContent  = data.summary.total_recorded_price_fluctuations;
        } catch (err) {
            Components.toast(`Analytics failed: ${err.message}`, 'error');
        }
    }

    return { render };
})();
