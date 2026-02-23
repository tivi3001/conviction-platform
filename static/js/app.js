/**
 * Conviction Platform - Main Application Controller
 */

class ConvictionApp {
    constructor() {
        this.currentTier = 1;
        this.allStocks = [];
        this.setupEventListeners();
        this.initializeApp();
    }

    setupEventListeners() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tier = parseInt(e.target.closest('.tab-btn').dataset.tier);
                this.switchTier(tier);
            });
        });

        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshData());
        document.getElementById('searchInput').addEventListener('input', (e) => this.filterStocks(e.target.value));
        document.getElementById('searchClear').addEventListener('click', () => {
            document.getElementById('searchInput').value = '';
            this.filterStocks('');
        });
        document.getElementById('detailModalClose').addEventListener('click', () => this.closeDetailModal());
        document.getElementById('detailModalOverlay').addEventListener('click', () => this.closeDetailModal());
        document.getElementById('loadMoreBtn').addEventListener('click', () => this.loadMore());
    }

    async initializeApp() {
        console.log('🚀 Initializing Conviction Trading Platform...');
        try {
            // Just load tier info first
            const tiersResponse = await api.getTiers();
            if (tiersResponse.status === 'success') {
                document.querySelector('#tab-tier1 .tab-count').textContent = tiersResponse.tiers['1'].count;
                document.querySelector('#tab-tier2 .tab-count').textContent = tiersResponse.tiers['2'].count;
                document.querySelector('#tab-tier3 .tab-count').textContent = tiersResponse.tiers['3'].count;
            }

            // Load first tier
            await this.switchTier(1);
            console.log('✅ Platform initialized');
        } catch (error) {
            console.error('Initialization error:', error);
            this.showError('Backend is initializing... please refresh in a moment');
        }
    }

    async switchTier(tier) {
        this.currentTier = tier;
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.tier) === tier);
        });

        this.showLoading(true);
        try {
            const result = await api.getWatchlist(tier);
            if (result.status === 'success') {
                this.allStocks = result.results;
                this.renderStocks(this.allStocks.slice(0, 50));
                this.updateStats(this.allStocks);
            } else {
                this.showError('Failed to load stocks');
            }
        } catch (error) {
            console.error('Error switching tier:', error);
            this.showError('Error loading stocks - ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }

    renderStocks(stocks) {
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';

        if (stocks.length === 0) {
            document.getElementById('emptyState').style.display = 'block';
            return;
        }

        document.getElementById('emptyState').style.display = 'none';

        stocks.forEach(stock => {
            if (stock.error) return;

            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="col-symbol"><strong>${stock.symbol}</strong></td>
                <td class="col-conviction">${stock.conviction_score?.toFixed(1) || '--'}</td>
                <td class="col-level"><span class="conviction-level">${this.getLevel(stock.conviction_score)}</span></td>
                <td class="col-val">${stock.valuation_score?.toFixed(0) || '--'}</td>
                <td class="col-growth">${stock.growth_score?.toFixed(0) || '--'}</td>
                <td class="col-sent">${stock.sentiment_score?.toFixed(0) || '--'}</td>
                <td class="col-trend">─</td>
                <td class="col-change ${stock.score_change_points > 0 ? 'change-positive' : 'change-negative'}">
                    ${stock.score_change_points > 0 ? '+' : ''}${stock.score_change_points?.toFixed(1) || '--'}
                </td>
            `;

            row.addEventListener('click', () => this.openDetailModal(stock.symbol, stock));
            tbody.appendChild(row);
        });

        this.updateLastUpdated();
    }

    getLevel(score) {
        if (score >= 70) return 'STRONG BUY';
        if (score >= 60) return 'BUY';
        if (score >= 55) return 'HOLD';
        if (score >= 45) return 'AVOID';
        return 'SHORT';
    }

    filterStocks(searchTerm) {
        const filtered = this.allStocks.filter(stock => 
            stock.symbol?.toUpperCase().includes(searchTerm.toUpperCase())
        );
        this.renderStocks(filtered.slice(0, 50));
    }

    updateStats(stocks) {
        const validStocks = stocks.filter(s => s.conviction_score !== undefined);
        const highConviction = validStocks.filter(s => s.conviction_score >= 65).length;
        const avgConviction = validStocks.length > 0
            ? (validStocks.reduce((sum, s) => sum + s.conviction_score, 0) / validStocks.length).toFixed(1)
            : '--';

        document.getElementById('highConvictionCount').textContent = highConviction;
        document.getElementById('avgConvictionScore').textContent = avgConviction;
    }

    async openDetailModal(symbol, stock) {
        console.log(`📊 Opening modal for ${symbol}`);
        const detail = await api.getStockDetail(symbol);

        if (detail.status !== 'success') {
            this.showError(`Failed to load ${symbol}`);
            return;
        }

        document.getElementById('detailSymbol').textContent = symbol;
        document.getElementById('detailPrice').textContent = '$' + (detail.valuation_score || 0).toFixed(2);
        document.getElementById('detailSentiment').textContent = (detail.sentiment_score || 0).toFixed(0);
        document.getElementById('detailValuation').textContent = (detail.valuation_score || 0).toFixed(0);
        document.getElementById('detailGrowth').textContent = (detail.growth_score || 0).toFixed(0);
        document.getElementById('detailThesis').textContent = detail.thesis || 'No thesis';
        document.getElementById('detailRisks').textContent = detail.what_could_break || 'No risks identified';

        document.getElementById('detailModal').classList.add('active');
    }

    closeDetailModal() {
        document.getElementById('detailModal').classList.remove('active');
    }

    async refreshData() {
        console.log('🔄 Refreshing...');
        await api.clearCache();
        await this.switchTier(this.currentTier);
    }

    loadMore() {
        // Not implemented yet
    }

    showLoading(show) {
        document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none';
    }

    showError(message) {
        console.error('❌ ' + message);
        alert(message);
    }

    updateLastUpdated() {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        document.getElementById('lastUpdated').textContent = `Last updated: ${time}`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, initializing...');
    window.app = new ConvictionApp();
});
