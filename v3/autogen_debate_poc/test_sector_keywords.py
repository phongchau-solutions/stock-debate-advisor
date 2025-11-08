"""
Test dynamic sector keyword fetching from Vietcap API
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.vietcap_service import VietcapService


async def test_sector_keywords():
    """Test dynamic sector keyword retrieval from Vietcap API"""
    print("=" * 80)
    print("DYNAMIC SECTOR KEYWORD FETCHING TEST")
    print("=" * 80)
    
    test_symbols = ['VNM', 'VCB', 'HPG', 'FPT', 'TCB', 'VIC']
    service = VietcapService()
    
    print(f"\n📊 Fetching sector keywords for {len(test_symbols)} stocks...\n")
    print(f"{'Symbol':<10} {'Keywords':<70}")
    print("-" * 80)
    
    for symbol in test_symbols:
        try:
            keywords = service._get_sector_keywords(symbol)
            keywords_str = ', '.join(keywords[:6])
            print(f"{symbol:<10} {keywords_str:<70}")
        except Exception as e:
            print(f"{symbol:<10} ❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print("\nIf you see rich sector keywords (not just 'symbol, vietnam, market'),")
    print("then the Vietcap API is successfully providing company information!")
    print("\nIf you see fallback keywords only, the API might be:")
    print("  - Blocked (403 error)")
    print("  - Not providing company.overview() data")
    print("  - Requiring authentication")


if __name__ == "__main__":
    asyncio.run(test_sector_keywords())
