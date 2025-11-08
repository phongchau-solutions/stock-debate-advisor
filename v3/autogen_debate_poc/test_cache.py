#!/usr/bin/env python3
"""Test caching system"""
import asyncio
from services.stock_data_service import StockDataService

async def test_cache():
    service = StockDataService(use_cache=True, cache_max_age_hours=24)
    
    print('📊 First fetch (should hit API or generate synthetic)...')
    data1 = await service.fetch_stock_data('VNM', period_days=30)
    print(f'✅ Got data with {len(data1["ohlcv"])} days of OHLCV')
    print(f'   Source: {data1.get("source", "unknown")}')
    
    print('\n📊 Second fetch (should hit cache)...')
    data2 = await service.fetch_stock_data('VNM', period_days=30)
    print(f'✅ Got data with {len(data2["ohlcv"])} days of OHLCV')
    print(f'   Source: {data2.get("source", "unknown")}')
    
    print('\n🎉 Caching test complete!')

if __name__ == '__main__':
    asyncio.run(test_cache())
