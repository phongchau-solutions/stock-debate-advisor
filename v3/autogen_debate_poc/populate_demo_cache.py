#!/usr/bin/env python3
"""
Pre-populate cache with demo data for reliable presentations.
This ensures the demo doesn't rely on slow/blocked external APIs.
"""
import asyncio
from datetime import datetime, timedelta
from services.data_cache_service import DataCacheService
import pandas as pd

# Demo stocks for Vietnamese market
DEMO_STOCKS = ['VNM', 'VIC', 'VCB', 'FPT', 'HPG']

def generate_demo_ohlcv(symbol: str, days: int = 30) -> pd.DataFrame:
    """Generate realistic OHLCV data for demo."""
    base_prices = {
        'VNM': 70000,   # Vinamilk
        'VIC': 45000,   # Vingroup
        'VCB': 95000,   # Vietcombank
        'FPT': 115000,  # FPT Corporation
        'HPG': 25000    # Hoa Phat Group
    }
    
    base_price = base_prices.get(symbol, 50000)
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days-1, -1, -1)]
    
    # Generate realistic price movement
    data = []
    current_price = base_price
    
    for date in dates:
        # Random walk with mean reversion
        change = (current_price * 0.02 * (pd.np.random.random() - 0.5))
        current_price = max(current_price + change, base_price * 0.8)
        current_price = min(current_price, base_price * 1.2)
        
        open_price = current_price
        high = open_price * (1 + pd.np.random.random() * 0.02)
        low = open_price * (1 - pd.np.random.random() * 0.02)
        close = low + (high - low) * pd.np.random.random()
        volume = int(1000000 + pd.np.random.random() * 5000000)
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
    
    return pd.DataFrame(data)

def generate_demo_financials(symbol: str) -> dict:
    """Generate realistic financial ratios for demo."""
    ratios = {
        'VNM': {'pe_ratio': 15.5, 'pb_ratio': 3.2, 'roe': 25.8, 'roa': 18.5, 'debt_to_equity': 0.35, 'current_ratio': 1.8},
        'VIC': {'pe_ratio': 12.3, 'pb_ratio': 1.9, 'roe': 18.2, 'roa': 8.5, 'debt_to_equity': 2.1, 'current_ratio': 1.2},
        'VCB': {'pe_ratio': 16.8, 'pb_ratio': 2.8, 'roe': 22.5, 'roa': 1.8, 'debt_to_equity': 8.5, 'current_ratio': 1.1},
        'FPT': {'pe_ratio': 18.2, 'pb_ratio': 4.5, 'roe': 28.3, 'roa': 15.2, 'debt_to_equity': 0.45, 'current_ratio': 2.1},
        'HPG': {'pe_ratio': 9.5, 'pb_ratio': 1.5, 'roe': 15.8, 'roa': 12.3, 'debt_to_equity': 0.85, 'current_ratio': 1.5}
    }
    
    return ratios.get(symbol, {
        'pe_ratio': 15.0,
        'pb_ratio': 2.5,
        'roe': 20.0,
        'roa': 12.0,
        'debt_to_equity': 1.0,
        'current_ratio': 1.5
    })

def generate_demo_news(symbol: str) -> list:
    """Generate demo news articles."""
    company_names = {
        'VNM': 'Vinamilk',
        'VIC': 'Vingroup',
        'VCB': 'Vietcombank',
        'FPT': 'FPT Corporation',
        'HPG': 'Hoa Phat Group'
    }
    
    company = company_names.get(symbol, symbol)
    
    articles = [
        {
            'title': f'{company} reports strong Q3 earnings growth',
            'url': f'https://example.com/news/{symbol.lower()}-q3-earnings',
            'source': 'VietStock',
            'published_date': datetime.now() - timedelta(days=2),
            'content': f'{company} announced impressive quarterly results with revenue growth exceeding market expectations.',
            'is_demo': True
        },
        {
            'title': f'Market analysts upgrade {company} stock rating',
            'url': f'https://example.com/news/{symbol.lower()}-upgrade',
            'source': 'VnEconomy',
            'published_date': datetime.now() - timedelta(days=5),
            'content': f'Leading financial analysts have upgraded their outlook for {company} citing strong fundamentals.',
            'is_demo': True
        },
        {
            'title': f'{company} expands operations in key markets',
            'url': f'https://example.com/news/{symbol.lower()}-expansion',
            'source': 'WSJ',
            'published_date': datetime.now() - timedelta(days=7),
            'content': f'{company} announces strategic expansion plans to capture growing market demand.',
            'is_demo': True
        }
    ]
    
    return articles

async def populate_cache():
    """Populate cache with demo data for all stocks."""
    cache = DataCacheService()
    
    print('🎯 Populating Demo Cache')
    print('=' * 60)
    
    for symbol in DEMO_STOCKS:
        print(f'\n📊 {symbol}:')
        
        # Generate and cache OHLCV data
        ohlcv = generate_demo_ohlcv(symbol, days=30)
        cache.cache_stock_prices(symbol, ohlcv, 'demo')
        print(f'   ✅ Cached {len(ohlcv)} days of price data')
        
        # Generate and cache financials
        financials = generate_demo_financials(symbol)
        cache.cache_financials(symbol, financials, 'demo')
        print(f'   ✅ Cached financial ratios (P/E: {financials.get("pe_ratio")})')
        
        # Generate and cache news
        news = generate_demo_news(symbol)
        cache.cache_news(symbol, news, 'demo')
        print(f'   ✅ Cached {len(news)} news articles')
    
    print('\n' + '=' * 60)
    print('🎉 Demo cache populated successfully!')
    print('\nYou can now run demos without external API calls.')
    print('Cache will be used for 24 hours before expiring.')

if __name__ == '__main__':
    asyncio.run(populate_cache())
