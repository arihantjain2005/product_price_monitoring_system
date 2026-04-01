/**
 * api.js — API Service Layer
 * Responsibility: All backend communication. Returns typed responses.
 * No view code, no DOM manipulation, no routing.
 */
const Api = (() => {
    const headers = {
        'X-API-Key': CONFIG.API_KEY,
        'Content-Type': 'application/json'
    };

    async function request(method, path, body = null) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), CONFIG.REQUEST_TIMEOUT_MS);

        try {
            const res = await fetch(`${CONFIG.API_BASE_URL}${path}`, {
                method,
                headers,
                body: body ? JSON.stringify(body) : null,
                signal: controller.signal
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({ error: res.statusText }));
                throw new Error(err.error || `HTTP ${res.status}`);
            }

            return await res.json();
        } finally {
            clearTimeout(timeout);
        }
    }

    return {
        getAnalytics:    ()           => request('GET',  '/analytics'),
        getProducts:     (params = '') => request('GET',  `/products${params}`),
        getProduct:      (id)         => request('GET',  `/products/${id}`),
        getHistory:      (id)         => request('GET',  `/products/${id}/history`),
        triggerRefresh:  ()           => request('POST', '/refresh'),
        getWebhooks:     ()           => request('GET',  '/webhooks'),
        registerWebhook: (url)        => request('POST', '/webhooks', { target_url: url }),
        deleteWebhook:   (id)         => request('DELETE', `/webhooks/${id}`)
    };
})();
