/**
 * CONVICTION PLATFORM - MAIN APPLICATION CONTROLLER
 */

class App {
    constructor() {
        this.currentTier = 'tier1';
        this.currentPage = 1;
        this.detailModal = new DetailModal();
        this.setupEventListeners();
        this.initializeApp();
    }

    setupEventListeners() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => 
                this.switchTier(e.target.closest('.tab-btn').dataset.tier)
            );
        });

        document.getElementById('loadMoreBtn')?.addEventListener('click', () => this.loadMore());
        document.getElementById('refreshBtn')?.addEventListener('click', () => this.refreshData());
    }

    async initializeApp() {
        try {
            await this.switchTier('tier1');
        } catch (error) {
            console.error('Failed to initialize:', error);
        }
    }

    async switchTier(tier) {
        this.currentTier = tier;
        this.currentPage = 1;

        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tier === tier);
        });

        if (tier === 'activity') {
            document.getElementById('activityFeed').style.display = 'block';
            document.getElementById('tableContainer').style.display = 'none';
        } else {
            document.getElementById('tableContainer').style.display = 'block';
            document.getElementById('activityFeed').style.display = 'none';
            await this.loadStocksForTier(tier);
        }
    }

    async loadStocksForTier(tier) {
        try {
            const result = await api.getWatchlistPaginated(this.currentPage, 50, tier);
            this.renderStocks(result.results);
        } catch (error) {
            console.error('Failed to load stocks:', error);
        }
    }

    renderStocks(stocks) {
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';

        stocks.forEach(stock => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="col-symbol"><strong>${stock.symbol}</strong></td>
                <td class="col-conviction">${stock.conviction_score.toFixed(1)}</td>
                <td class="col-level"><span class="conviction-level">${this.getLevel(stock.conviction_score)}</span></td>
                <td class="col-val">${stock.valuation_score.toFixed(0)}</td>
                <td class="col-growth">${stock.growth_score.toFixed(0)}</td>
                <td class="col-sent">${stock.sentiment_score.toFixed(0)}</td>
                <td class="col-trend">${this.getTrend(stock)}</td>
                <td class="col-change ${stock.score_change_points > 0 ? 'change-positive' : 'change-negative'}">
                    ${stock.score_change_points > 0 ? '+' : ''}${stock.score_change_points?.toFixed(1) || '--'}
                </td>
            `;

            // ADD CLICK HANDLER TO OPEN DETAIL MODAL
            row.addEventListener('click', () => {
                this.detailModal.open(stock.symbol, stock);
            });

            tbody.appendChild(row);
        });
    }

    getLevel(score) {
        if (score >= 70) return 'STRONG BUY';
        if (score >= 60) return 'BUY';
        if (score >= 55) return 'HOLD';
        if (score >= 45) return 'AVOID';
        return 'SHORT';
    }

    getTrend(stock) {
        if (!stock.conviction_7d_sparkline || stock.conviction_7d_sparkline.length < 2) {
            return '─';
        }
        const first = stock.conviction_7d_sparkline[0];
        const last = stock.conviction_7d_sparkline[stock.conviction_7d_sparkline.length - 1];
        const change = last - first;
        
        if (change > 2) return '📈';
        if (change < -2) return '📉';
        return '─';
    }

    async loadMore() {
        this.currentPage++;
        await this.loadStocksForTier(this.currentTier);
    }

    async refreshData() {
        api.clearCache();
        await this.switchTier(this.currentTier);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
