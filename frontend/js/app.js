/**
 * app.js — Application Bootstrap
 * Responsibility: Initialize the app, bind global UI events.
 * This is the only entry point. All modules must be loaded before this runs.
 */
(() => {
    const refreshBtn   = document.getElementById('trigger-refresh-btn');
    const statusDot    = document.querySelector('.status-dot');
    const statusLabel  = document.querySelector('.status-label');

    let _lastHistoryId = 0;
    
    // ── Global Notification Engine ────────────────────────────────────────────
    // Polls /analytics/recent-changes using a cursor (_lastHistoryId).
    // Fires a toast popup for EVERY price change detected, on ANY screen.
    async function checkRecentChanges() {
        if (_lastHistoryId === 0) return; // cursor not seeded yet — skip

        try {
            const { data } = await Api.getRecentChanges(_lastHistoryId);
            if (!data || data.length === 0) return;

            data.forEach(item => {
                // Skip the dummy seeding row (brand is empty)
                if (!item.brand) return;

                const priceStr = `$${Number(item.new_price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                const msg = `🔔 Price updated! [${item.marketplace}] ${item.brand} — ${item.name} is now ${priceStr}`;
                Components.toast(msg, 'info');
                console.log('[PriceMonitor] Popup fired:', msg);

                if (item.history_id > _lastHistoryId) {
                    _lastHistoryId = item.history_id;
                }
            });
        } catch (err) {
            console.error('[PriceMonitor] Failed to check recent changes:', err);
        }
    }

    async function checkApiStatus() {
        try {
            const res = await fetch(`${CONFIG.API_BASE_URL}/health`);
            if (res.ok) {
                statusDot.className     = 'status-dot status-online';
                statusLabel.textContent = 'API Connected';
            } else {
                throw new Error('API returned error');
            }
        } catch {
            statusDot.className     = 'status-dot status-offline';
            statusLabel.textContent = 'API Offline';
        }
    }

    refreshBtn.addEventListener('click', async () => {
        const original = refreshBtn.innerHTML;
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<span class="btn-icon">⌛</span> Syncing...';

        try {
            await Api.triggerRefresh();  // blocks until ingestion is 100% done
            refreshBtn.innerHTML = '<span class="btn-icon">✓</span> Synced!';
            refreshBtn.style.background = 'var(--success)';
            Components.toast('Data refreshed successfully.', 'success');

            // Sync the active view immediately so UI reflects new data
            Router.syncActiveView();

            // Wait 500 ms to ensure the DB transaction is fully committed,
            // then fire the notification popup(s)
            setTimeout(checkRecentChanges, 500);

        } catch (err) {
            refreshBtn.innerHTML = '<span class="btn-icon">✖</span> Failed';
            refreshBtn.style.background = 'var(--danger)';
            Components.toast(`Refresh failed: ${err.message}`, 'error');
        } finally {
            setTimeout(() => {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = original;
                refreshBtn.style.background = '';
            }, 3000);
        }
    });

    async function init() {
        Router.init();
        await checkApiStatus();

        // Seed the cursor: get the latest PriceHistory ID so we only
        // notify about changes that happen AFTER the app loaded.
        try {
            const { data } = await Api.getRecentChanges(0);
            if (data && data.length > 0 && data[0].history_id > 0) {
                _lastHistoryId = data[0].history_id;
            } else {
                _lastHistoryId = 1; // DB is empty — start from beginning
            }
            console.log('[PriceMonitor] Notification cursor seeded at ID:', _lastHistoryId);
        } catch (e) {
            _lastHistoryId = 1;
            console.warn('[PriceMonitor] Could not seed cursor:', e);
        }

        // Background poller — fires on every screen, every 10 s
        setInterval(checkRecentChanges, CONFIG.REFRESH_INTERVAL_MS);

        Router.navigate('dashboard');
    }

    init();
})();
