"""
Conviction Trading Platform - Flask Web Application
"""
from flask import Flask, render_template, jsonify, request
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TARGET_STOCKS, TIER_MAPPING, TIER_LABELS, TIER_1_STOCKS, TIER_2_STOCKS, TIER_3_STOCKS
from engines.valuation_engine import ValuationEngine
from engines.growth_engine import GrowthEngine
from engines.sentiment_engine import SentimentEngine
from engines.confluence_engine import ConfluenceEngine

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

valuation_engine = ValuationEngine()
growth_engine = GrowthEngine()
sentiment_engine = SentimentEngine()
confluence_engine = ConfluenceEngine()

_conviction_cache = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    tier = request.args.get('tier', None)
    stocks_to_analyze = TARGET_STOCKS
    if tier:
        tier_num = int(tier)
        stocks_to_analyze = [s for s in TARGET_STOCKS if TIER_MAPPING.get(s) == tier_num]

    results = []
    for symbol in stocks_to_analyze:
        try:
            if symbol in _conviction_cache:
                results.append(_conviction_cache[symbol])
                continue

            valuation = valuation_engine.analyze_stock(symbol)
            growth = growth_engine.analyze_stock(symbol)
            sentiment = sentiment_engine.analyze_stock(symbol)
            conviction = confluence_engine.calculate_conviction(valuation, growth, sentiment)

            stock_result = {
                'symbol': symbol,
                'conviction_score': round(conviction.conviction_score, 1),
                'conviction_level': conviction.conviction_level.value,
                'valuation_score': round(conviction.valuation_score, 1),
                'growth_score': round(conviction.growth_score, 1),
                'sentiment_score': round(conviction.sentiment_score, 1),
                'pillar_agreement': round(conviction.pillar_agreement, 1),
                'thesis': conviction.thesis,
                'what_could_break': conviction.what_could_break,
                'key_catalysts': conviction.key_catalysts,
                'tier': TIER_MAPPING.get(symbol, 'unknown'),
            }
            _conviction_cache[symbol] = stock_result
            results.append(stock_result)
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")

    results = sorted(results, key=lambda x: x.get('conviction_score', -999), reverse=True)
    return jsonify({'status': 'success', 'results': results, 'count': len(results), 'tier': tier if tier else 'all'})

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_detail(symbol):
    try:
        if symbol in _conviction_cache:
            return jsonify({'status': 'success', **_conviction_cache[symbol]})

        valuation = valuation_engine.analyze_stock(symbol)
        growth = growth_engine.analyze_stock(symbol)
        sentiment = sentiment_engine.analyze_stock(symbol)
        conviction = confluence_engine.calculate_conviction(valuation, growth, sentiment)

        result = {
            'status': 'success',
            'symbol': symbol,
            'conviction_score': round(conviction.conviction_score, 1),
            'conviction_level': conviction.conviction_level.value,
            'valuation_score': round(conviction.valuation_score, 1),
            'growth_score': round(conviction.growth_score, 1),
            'sentiment_score': round(conviction.sentiment_score, 1),
            'pillar_agreement': round(conviction.pillar_agreement, 1),
            'thesis': conviction.thesis,
            'what_could_break': conviction.what_could_break,
            'key_catalysts': conviction.key_catalysts,
            'tier': TIER_MAPPING.get(symbol, 'unknown'),
        }
        _conviction_cache[symbol] = result
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'symbol': symbol, 'error': str(e)}), 400

@app.route('/api/tiers', methods=['GET'])
def get_tiers():
    return jsonify({'status': 'success', 'tiers': {'1': {'name': TIER_LABELS[1], 'count': len(TIER_1_STOCKS)}, '2': {'name': TIER_LABELS[2], 'count': len(TIER_2_STOCKS)}, '3': {'name': TIER_LABELS[3], 'count': len(TIER_3_STOCKS)}}, 'total': len(TARGET_STOCKS)})

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    global _conviction_cache
    _conviction_cache = {}
    return jsonify({'status': 'success', 'message': 'Cache cleared'})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'app': 'Conviction Trading Platform'})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 CONVICTION TRADING PLATFORM - FLASK WEB APPLICATION")
    print("="*70)
    print(f"📊 Analyzing {len(TARGET_STOCKS)} stocks across 3 tiers")
    print(f"   Tier 1: {len(TIER_1_STOCKS)} | Tier 2: {len(TIER_2_STOCKS)} | Tier 3: {len(TIER_3_STOCKS)}")
    print("\n🌐 Starting Flask server...")
    print("   URL: http://localhost:5000")
    print("   Press Ctrl+C to stop")
    print("="*70 + "\n")
    app.run(debug=True, port=5000, host='127.0.0.1')
