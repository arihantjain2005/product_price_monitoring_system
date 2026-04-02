/**
 * config.js — Application Configuration
 * Responsibility: Single source of truth for all runtime constants.
 * No other file should hardcode URLs or keys.
 */
const CONFIG = Object.freeze({
    API_BASE_URL: 'http://127.0.0.1:8000',
    API_KEY: 'entrupy-intern-test-key-2026',
    REFRESH_INTERVAL_MS: 10000,   // poll every 10 s for near-real-time updates
    REQUEST_TIMEOUT_MS: 30000     // 30 s — allows synchronous refresh to complete
});
