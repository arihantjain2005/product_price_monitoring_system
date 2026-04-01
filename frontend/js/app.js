/**
 * app.js — Application Bootstrap
 * Responsibility: Initialize the app, bind global UI events.
 * This is the only entry point. All modules must be loaded before this runs.
 */
(() => {
    const refreshBtn   = document.getElementById('trigger-refresh-btn');
    const statusDot    = document.querySelector('.status-dot');
    const statusLabel  = document.querySelector('.status-label');

    async function checkApiStatus() {
        try {
            const res = await fetch(`${CONFIG.API_BASE_URL}/health`);
            if (res.ok) {
                statusDot.className  = 'status-dot status-online';
                statusLabel.textContent = 'API Connected';
            } else {
                throw new Error('API returned error');
            }
        } catch {
            statusDot.className  = 'status-dot status-offline';
            statusLabel.textContent = 'API Offline';
        }
    }

    refreshBtn.addEventListener('click', async () => {
        const original = refreshBtn.innerHTML;
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<span class="btn-icon">⌛</span> Syncing...';

        try {
            await Api.triggerRefresh();
            refreshBtn.innerHTML = '<span class="btn-icon">✓</span> Triggered!';
            refreshBtn.style.background = 'var(--success)';
            Components.toast('Data refresh triggered in the background.', 'success');
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

    function init() {
        Router.init();
        checkApiStatus();
        Router.navigate('dashboard');
    }

    init();
})();
