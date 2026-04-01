/**
 * views/webhooks.js — Webhooks View
 * Responsibility: Renders and manages the configurable Webhooks.
 */
const WebhooksView = (() => {
    let containerElement = null;

    async function loadWebhooks() {
        const listContainer = containerElement.querySelector('#webhook-list');
        listContainer.innerHTML = Components.loader();
        
        try {
            const { data } = await Api.getWebhooks();
            if (!data || data.length === 0) {
                listContainer.innerHTML = Components.emptyState('No webhooks registered yet.');
                return;
            }

            const html = data.map(hook => `
                <div class="product-card" style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div class="product-card-name">${hook.target_url}</div>
                        <div class="product-card-category">Added: ${new Date(hook.created_at).toLocaleString()}</div>
                    </div>
                    <button class="btn-primary" style="background-color: var(--danger-color); min-width: auto;" data-id="${hook.id}" onclick="WebhooksView.handleDelete(${hook.id})">Delete</button>
                </div>
            `).join('');
            
            listContainer.innerHTML = html;
        } catch (err) {
            listContainer.innerHTML = Components.emptyState('Failed to load webhooks.');
            Components.toast(`Error: ${err.message}`, 'error');
        }
    }

    async function handleDelete(id) {
        if (!confirm('Are you sure you want to delete this webhook?')) return;
        
        try {
            await Api.deleteWebhook(id);
            Components.toast('Webhook deleted successfully.', 'success');
            await loadWebhooks();
        } catch (err) {
            Components.toast(`Delete failed: ${err.message}`, 'error');
        }
    }

    async function handleAdd(event) {
        event.preventDefault();
        const input = containerElement.querySelector('#webhook-url');
        const url = input.value.trim();
        
        if (!url) {
            Components.toast('URL cannot be empty', 'error');
            return;
        }

        try {
            await Api.registerWebhook(url);
            input.value = '';
            Components.toast('Webhook registered successfully!', 'success');
            await loadWebhooks();
        } catch (err) {
            Components.toast(`Registration failed: ${err.message}`, 'error');
        }
    }

    async function render(container) {
        containerElement = container;
        container.innerHTML = `
            <div class="form-container" style="background: var(--surface-bg); padding: 2rem; border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 2rem;">
                <h2 style="margin-top: 0;">Register New Webhook</h2>
                <p style="color: var(--text-muted); margin-bottom: 1.5rem;">Enter a target URL that will receive HTTP POST payloads when prices change.</p>
                <form id="webhook-form" style="display: flex; gap: 1rem;">
                    <input type="url" id="webhook-url" placeholder="https://example.com/webhook" required style="flex-grow: 1; padding: 0.75rem 1rem; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-color); color: var(--text-color);">
                    <button type="submit" class="btn-primary">Add Webhook</button>
                </form>
            </div>
            <h3>Registered Webhooks</h3>
            <div id="webhook-list" style="display: flex; flex-direction: column; gap: 1rem; margin-top: 1rem;">
            </div>
        `;

        container.querySelector('#webhook-form').addEventListener('submit', handleAdd);
        
        await loadWebhooks();
    }

    return { render, handleDelete };
})();
