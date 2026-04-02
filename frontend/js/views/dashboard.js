/**
 * views/dashboard.js — Dashboard View
 * Responsibility: Renders and manages the Dashboard screen only.
 * Uses Api service and Components library. No raw fetch calls.
 */
const DashboardView = (() => {
    let _pollTimer = null;
    let _lastFluctuations = null;

    async function _fetchStats() {
        try {
            const { data } = await Api.getAnalytics();
            const elP = document.getElementById('stat-products');
            const elL = document.getElementById('stat-listings');
            const elC = document.getElementById('stat-changes');
            // Elements may not exist if user already navigated away
            if (!elP) return;

            _updateStat(elP, data.summary.total_canonical_products);
            _updateStat(elL, data.summary.total_tracked_listings);
            _updateStat(elC, data.summary.total_recorded_price_fluctuations);

            // Trigger popup if fluctuations increased during a silent poll
            const currentFluctuations = data.summary.total_recorded_price_fluctuations;
            _lastFluctuations = currentFluctuations;

        } catch (err) {
            // Silently skip polling errors — avoid toast spam
        }
    }

    /** Update a stat element and flash it if the value changed */
    function _updateStat(el, newValue) {
        const val = String(newValue);
        if (el.textContent === val) return;   // unchanged — do nothing
        el.textContent = val;
        el.classList.remove('stat-updated');
        void el.offsetWidth;                  // force reflow so animation restarts
        el.classList.add('stat-updated');
    }

    async function render(container) {
        destroy(); // clear any previous timer before re-rendering
        _lastFluctuations = null; // reset state on fresh render

        container.innerHTML = `
            <div class="stats-grid">
                ${Components.statCard('Canonical Products',    '--', 'stat-products')}
                ${Components.statCard('Tracked Listings',     '--', 'stat-listings')}
                ${Components.statCard('Price Fluctuations',   '--', 'stat-changes')}
            </div>`;

        // Initial fetch
        await _fetchStats();

        // Poll every REFRESH_INTERVAL_MS for real-time updates
        _pollTimer = setInterval(_fetchStats, CONFIG.REFRESH_INTERVAL_MS);
    }

    function destroy() {
        if (_pollTimer !== null) {
            clearInterval(_pollTimer);
            _pollTimer = null;
        }
    }

    return { render, destroy, sync: _fetchStats };
})();
