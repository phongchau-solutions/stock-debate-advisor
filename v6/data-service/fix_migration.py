#!/usr/bin/env python3
"""Quick fix for news data path issue."""

import os
import shutil
from pathlib import Path

# Fix the MBB news data path
source = Path("/home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/data-service/data_store/2026/MBB/news_data.json")
target = Path("/home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/data-service/data_store/2026/MBB.VN/news_data.json")

if source.exists():
    shutil.copy2(source, target)
    shutil.rmtree(source.parent)
    print(f"Fixed: Moved news data to {target}")
else:
    print("Source file not found")

# Verify the structure
data_store_dir = Path("/home/x1e3/work/vmo/agentic/stock-debate-advisor/v6/data-service/data_store/2026")
stock_dirs = sorted([d.name for d in data_store_dir.iterdir() if d.is_dir()])
print(f"\nFound {len(stock_dirs)} stocks:")
for stock in stock_dirs:
    stock_path = data_store_dir / stock
    files = sorted([f.name for f in stock_path.iterdir()])
    print(f"  {stock}: {files}")
