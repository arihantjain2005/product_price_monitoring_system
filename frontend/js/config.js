/**
 * config.js — Application Configuration
 * Responsibility: Single source of truth for all runtime constants.
 * No other file should hardcode URLs or keys.
 */
const CONFIG = Object.freeze({
    API_BASE_URL: 'http://localhost:8000',
    API_KEY: 'entrupy-intern-test-key-2026',
    REFRESH_INTERVAL_MS: 30000,
    REQUEST_TIMEOUT_MS: 10000
});
