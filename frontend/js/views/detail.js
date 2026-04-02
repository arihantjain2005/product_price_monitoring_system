/**
 * views/detail.js — Product Detail View
 * Responsibility: Renders a single product's full data and price history chart.
 * Uses Api service and Components library. No raw fetch calls.
 */
const DetailView = (() => {
    let chartInstance = null;

    async function render(container, productId) {
        container.innerHTML = Components.loader();

        try {
            const [{ data: product }, { data: history }] = await Promise.all([
                Api.getProduct(productId),
                Api.getHistory(productId)
            ]);

            container.innerHTML = `
                <button class="btn-back" id="btn-back-to-catalog">← Back to Products</button>

                <div class="detail-header">
                    <div>
                        <div class="detail-brand">${product.brand}</div>
                        <h2 class="detail-name">${product.name}</h2>
                        <span class="product-card-category">${product.category}</span>
                    </div>
                </div>

                <div class="detail-grid">
                    <div class="detail-panel">
                        <h3 class="section-title">Marketplace Listings</h3>
                        <div class="listings-table">
                            ${product.listings.map(l => `
                                <div class="listing-row-detail">
                                    <span class="listing-marketplace-badge">${l.marketplace_name}</span>
                                    <span class="listing-price-large">$${l.current_price?.toLocaleString() ?? 'N/A'}</span>
                                    <a class="listing-link" href="${l.url}" target="_blank" rel="noopener">View ↗</a>
                                </div>
                            `).join('') || '<p style="color:var(--text-muted)">No listings found.</p>'}
                        </div>
                    </div>

                    <div class="detail-panel chart-panel">
                        <h3 class="section-title">Price History Across Marketplaces</h3>
                        <div class="chart-container">
                            <canvas id="price-chart"></canvas>
                        </div>
                        ${history.length === 0
                            ? '<p style="color:var(--text-muted);font-size:0.85rem;margin-top:0.5rem;">No historical data yet.</p>'
                            : ''}
                    </div>
                </div>`;

            document.getElementById('btn-back-to-catalog').addEventListener('click', () => {
                Router.navigate('products');
            });

            if (history.length > 0) {
                _renderChart(history);
            }

        } catch (err) {
            container.innerHTML = Components.emptyState('Could not load product. Is the API running?');
            Components.toast(`Detail load failed: ${err.message}`, 'error');
        }
    }

    function _renderChart(history) {
        const canvas = document.getElementById('price-chart');
        if (!canvas) return;

        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }

        // Helper — format a timestamp as "Apr 2, 5:34 PM" (date + time, no seconds)
        function fmtLabel(ts) {
            return new Date(ts).toLocaleString(undefined, {
                month: 'short', day: 'numeric',
                hour: 'numeric', minute: '2-digit'
            });
        }

        // Group history by marketplace, keep raw timestamp for sorting
        const marketplaces = [...new Set(history.map(h => h.marketplace))];
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

        const datasets = marketplaces.map((market, i) => {
            const points = history
                .filter(h => h.marketplace === market)
                // Sort chronologically so the line draws left → right
                .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
                .map(h => ({
                    x: fmtLabel(h.timestamp),   // "Apr 2, 5:34 PM"
                    y: h.price,
                    rawTs: h.timestamp          // keep for tooltip
                }));
            return {
                label: market,
                data: points,
                borderColor: colors[i % colors.length],
                backgroundColor: colors[i % colors.length] + '22',
                borderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
                tension: 0.3,
                fill: true
            };
        });

        chartInstance = new Chart(canvas, {
            type: 'line',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                parsing: { xAxisKey: 'x', yAxisKey: 'y' },
                plugins: {
                    legend: {
                        labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 } }
                    },
                    tooltip: {
                        callbacks: {
                            // Title row: show the datetime label
                            title: ctx => ctx[0]?.label ?? '',
                            // Value row: show formatted price
                            label: ctx => {
                                const price = `$${ctx.parsed.y.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                                return `  ${ctx.dataset.label}: ${price}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#64748b',
                            maxRotation: 35,
                            autoSkip: true,
                            maxTicksLimit: 10
                        },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    },
                    y: {
                        beginAtZero: false,  // scale to actual data range
                        grace: '10%',        // 10% padding above & below
                        ticks: {
                            color: '#64748b',
                            callback: val => `$${val.toLocaleString()}`
                        },
                        grid: { color: 'rgba(255,255,255,0.04)' }
                    }
                }
            }
        });
    }

    return { render };
})();
