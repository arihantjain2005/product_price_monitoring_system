/**
 * router.js — Client-Side View Router
 * Responsibility: Maps navigation events to view renders. Manages active states.
 * No API calls, no component logic — orchestration only.
 */
const Router = (() => {
    const dynamicView  = document.getElementById('dynamic-view');
    const pageTitle    = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');

    const routes = {
        dashboard: {
            title:    'Dashboard Overview',
            subtitle: 'Aggregate statistics across all tracked marketplaces',
            render:   (el) => DashboardView.render(el)
        },
        products: {
            title:    'Products Hub',
            subtitle: 'Browse and filter tracked products from all marketplaces',
            render:   (el) => ProductsView.render(el)
        },
        webhooks: {
            title:    'Webhook Registry',
            subtitle: 'Manage downstream notification endpoints',
            render:   (el) => WebhooksView.render(el)
        }
    };

    function navigate(viewKey) {
        const route = routes[viewKey];
        if (!route) return;

        pageTitle.textContent    = route.title;
        pageSubtitle.textContent = route.subtitle;

        document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
        const navEl = document.getElementById(`nav-${viewKey}`);
        if (navEl) navEl.parentElement.classList.add('active');

        dynamicView.innerHTML = Components.loader();
        route.render(dynamicView);
    }

    function navigateToDetail(productId) {
        pageTitle.textContent    = 'Product Detail';
        pageSubtitle.textContent = 'Price history and marketplace listings for this product';
        dynamicView.innerHTML    = Components.loader();
        DetailView.render(dynamicView, productId);
    }

    function init() {
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = e.currentTarget.dataset.view;
                navigate(view);
            });
        });
    }

    return { init, navigate, navigateToDetail };
})();
