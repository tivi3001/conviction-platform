#!/usr/bin/env python3
"""
Conviction Trading Platform - Entry Point
Run this script to launch the Flask web application:
    python3 run.py
Then open your browser to: http://localhost:5000
"""
import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from flask_app import app

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 CONVICTION TRADING PLATFORM")
    print("="*70)
    print("📊 Stock Analysis Tool with Apple Glass Design")
    print("\n   Starting Flask server on http://localhost:5000")
    print("   Press Ctrl+C to stop")
    print("="*70 + "\n")
    app.run(debug=True, port=5000, host='127.0.0.1')
