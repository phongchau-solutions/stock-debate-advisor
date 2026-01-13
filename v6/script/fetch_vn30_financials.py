"""
Script to fetch and store all-time financial data for VN30 Vietnamese stocks using Yahoo Finance API.
Optimized for local storage and batch processing with comprehensive financial reports.
Supports quarterly and annual reports, historical prices, dividends, and key metrics.
"""
import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add data-service to path
data_service_path = Path(__file__).parent.parent / 'data-service'
sys.path.insert(0, str(data_service_path))

from app.services.financial_data_service import FinancialDataService

# Full VN30 list as of 2026 (using Yahoo Finance symbols with .VN suffix)
VN30_SYMBOLS = [
    'ACB.VN', 'BCM.VN', 'BID.VN', 'BVH.VN', 'CTG.VN', 'FPT.VN', 'GAS.VN', 'GVR.VN', 'HDB.VN', 'HPG.VN',
    'KDH.VN', 'MBB.VN', 'MSN.VN', 'MWG.VN', 'NVL.VN', 'PDR.VN', 'PLX.VN', 'POW.VN', 'SAB.VN', 'SHB.VN',
    'SSB.VN', 'SSI.VN', 'STB.VN', 'TCB.VN', 'TPB.VN', 'VCB.VN', 'VHM.VN', 'VIB.VN', 'VIC.VN', 'VJC.VN'
]

DATA_DIR = Path(__file__).parent.parent / 'data-service' / 'data' / 'financial'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Initialize service
service = FinancialDataService(cache_dir=DATA_DIR)

def fetch_and_store(symbol: str):
    """Fetch financial data for a symbol and store locally."""
    print(f"Fetching data for {symbol}...")
    try:
        data = service.fetch_and_cache(symbol)
        
        # Validate that actual data was fetched
        if not service.validate_data(data):
            raise ValueError(f"No valid financial data retrieved for {symbol}. Check API availability.")
        
        # Get summary of what was fetched
        summary = service.get_summary(symbol)
        available = [k for k, v in summary.get('data_available', {}).items() if v]
        
        print(f"✅ Stored {symbol}: {', '.join(available) if available else 'Basic info'}")
        return True
    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")
        return False

def main():
    print(f"{'='*70}")
    print(f"VN30 Financial Data Fetch - Yahoo Finance API")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"{'='*70}")
    print(f"Fetching data for {len(VN30_SYMBOLS)} stocks...")
    print()
    
    successful = 0
    failed = 0
    
    for symbol in VN30_SYMBOLS:
        if fetch_and_store(symbol):
            successful += 1
        else:
            failed += 1
    
    print()
    print(f"{'='*70}")
    print(f"Fetch Summary:")
    print(f"  Total Stocks: {len(VN30_SYMBOLS)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {(successful/len(VN30_SYMBOLS)*100):.1f}%")
    print(f"  Data Location: {DATA_DIR}")
    print(f"  Completed: {datetime.now().isoformat()}")
    print(f"{'='*70}")
    
    if failed > 0:
        raise RuntimeError(f"Failed to fetch data for {failed} symbols. Check API connectivity and symbol validity.")
    
    print("✅ All VN30 stocks successfully fetched and cached!")



if __name__ == "__main__":
    main()
