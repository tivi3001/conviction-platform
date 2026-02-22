/**
 * API Client for Conviction Trading Platform
 */
const api = {
    getWatchlist: async (tier = null) => {
        try {
            const url = tier ? `/api/watchlist?tier=${tier}` : '/api/watchlist';
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching watchlist:', error);
            return { status: 'error', error: error.message, results: [] };
        }
    },

    getStockDetail: async (symbol) => {
        try {
            const response = await fetch(`/api/stock/${symbol}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`Error fetching ${symbol}:`, error);
            return { status: 'error', error: error.message };
        }
    },

    getTiers: async () => {
        try {
            const response = await fetch('/api/tiers');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching tiers:', error);
            return { status: 'error', error: error.message };
        }
    },

    clearCache: async () => {
        try {
            const response = await fetch('/api/cache/clear', { method: 'POST' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error clearing cache:', error);
            return { status: 'error', error: error.message };
        }
    },

    healthCheck: async () => {
        try {
            const response = await fetch('/health');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', error: error.message };
        }
    }
};
