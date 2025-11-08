"""
Data converter to transform raw API data into CSV format for the debate system.
"""
import json
import pandas as pd
from pathlib import Path
import re


def load_field_mapping():
    """Load the field code to English name mapping."""
    mapping_file = Path(__file__).parent / 'field_mapping.json'
    if mapping_file.exists():
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def convert_vietcap_financial_data(input_dir: Path, output_dir: Path):
    """Convert VietCap financial data to CSV format."""
    
    print("📊 Converting financial data...")
    
    # Load field mapping
    field_map = load_field_mapping()
    
    # Find VCI files (or extract symbol from filenames)
    financial_files = {
        'balance_sheet': None,
        'income_statement': None,
        'cash_flow': None,
        'metrics': None,
        'price': None
    }
    
    for file in input_dir.glob("*.txt"):
        filename = file.name
        
        if "BALANCE_SHEET" in filename:
            financial_files['balance_sheet'] = file
        elif "INCOME_STATEMENT" in filename:
            financial_files['income_statement'] = file
        elif "CASH_FLOW" in filename:
            financial_files['cash_flow'] = file
        elif "financial-statement_metrics" in filename:
            financial_files['metrics'] = file
        elif "price-chart" in filename and "toCurrent=true" in filename:
            financial_files['price'] = file
    
    # Extract symbol (e.g., VCI from filename)
    symbol_match = re.search(r'_([A-Z]{3})_', str(financial_files['balance_sheet']))
    symbol = symbol_match.group(1) if symbol_match else 'VCI'
    
    print(f"  Processing symbol: {symbol}")
    
    # Convert financial statements with mapping
    if financial_files['balance_sheet']:
        try:
            # Read balance sheet
            with open(financial_files['balance_sheet'], 'r', encoding='utf-8') as f:
                bs_data = json.load(f)
            
            # Extract years from the data
            financial_records = []
            
            if isinstance(bs_data, dict) and 'data' in bs_data:
                data_section = bs_data['data']
                
                # Balance sheet has nested structure with specific line items
                # Get all balance sheet field codes that have data
                if isinstance(data_section, list) and len(data_section) > 0:
                    # Get years from the first item
                    first_item = data_section[0]
                    if 'yearReport' in first_item:
                        # Collect all year reports
                        years_set = set()
                        for item in data_section:
                            if 'yearReport' in item:
                                years_set.add(item['yearReport'])
                        
                        years = sorted(list(years_set), reverse=True)[:5]  # Last 5 years
                        
                        # Initialize records for each year
                        for year in years:
                            financial_records.append({
                                'symbol': symbol,
                                'year': year,
                            })
                        
                        # Extract key metrics from balance sheet
                        key_fields = ['bsa53', 'bsb97', 'bsb132', 'bsb157', 'bsb179']  # Total assets, SBV balance, Total liabilities, etc.
                        
                        for field_code in key_fields:
                            field_name = field_map.get(field_code, field_code)
                            # Find items with this field
                            for item in data_section:
                                if item.get('yearReport') in years:
                                    for record in financial_records:
                                        if record['year'] == item['yearReport']:
                                            # Get the value from the field code
                                            if field_code in item and item[field_code] != 0:
                                                record[field_name] = item[field_code]
            
            # Add income statement data
            if financial_files['income_statement']:
                with open(financial_files['income_statement'], 'r', encoding='utf-8') as f:
                    is_data = json.load(f)
                
                if isinstance(is_data, dict) and 'data' in is_data:
                    data_section = is_data['data']
                    if isinstance(data_section, list):
                        # Key income statement fields
                        key_fields = ['isi1', 'isi12', 'isi21', 'isi26']  # Net interest income, total income, operating profit, net profit
                        
                        for field_code in key_fields:
                            field_name = field_map.get(field_code, field_code)
                            for item in data_section:
                                if 'yearReport' in item:
                                    for record in financial_records:
                                        if record['year'] == item['yearReport']:
                                            if field_code in item and item[field_code] != 0:
                                                record[field_name] = item[field_code]
            
            if financial_records:
                df_financial = pd.DataFrame(financial_records)
                output_file = output_dir / f"{symbol.lower()}_financials.csv"
                df_financial.to_csv(output_file, index=False)
                print(f"  ✅ Created: {output_file}")
        
        except Exception as e:
            print(f"  ⚠️  Error processing financial data: {e}")
    
    # Convert price/OHLC data
    if financial_files['price']:
        try:
            with open(financial_files['price'], 'r', encoding='utf-8') as f:
                price_data = json.load(f)
            
            ohlc_records = []
            
            if isinstance(price_data, dict) and 'data' in price_data:
                for item in price_data['data']:
                    # Convert tradingTime (unix timestamp) to date if available
                    import datetime
                    date_str = ''
                    if 'tradingTime' in item:
                        try:
                            date_str = datetime.datetime.fromtimestamp(item['tradingTime']).strftime('%Y-%m-%d')
                        except:
                            date_str = str(item.get('tradingTime', ''))
                    
                    record = {
                        'date': date_str,
                        'open': item.get('openPrice', 0),
                        'high': item.get('highPrice', 0),
                        'low': item.get('lowPrice', 0),
                        'close': item.get('closingPrice', 0),
                        'volume': item.get('totalVol', item.get('volume', 0)),
                    }
                    ohlc_records.append(record)
            
            if ohlc_records:
                df_ohlc = pd.DataFrame(ohlc_records)
                output_file = output_dir / f"{symbol.lower()}_ohlc.csv"
                df_ohlc.to_csv(output_file, index=False)
                print(f"  ✅ Created: {output_file}")
        
        except Exception as e:
            print(f"  ⚠️  Error processing price data: {e}")


def convert_news_data(input_dir: Path, output_dir: Path):
    """Convert news data to CSV format."""
    
    print("\n📰 Converting news data...")
    
    # Group files by symbol (e.g., MBB)
    symbol_files = {}
    
    for file in input_dir.glob("*.txt"):
        # Extract symbol from filename
        symbol_match = re.search(r'([A-Z]{3})', file.name)
        if symbol_match:
            symbol = symbol_match.group(1)
            if symbol not in symbol_files:
                symbol_files[symbol] = []
            symbol_files[symbol].append(file)
    
    for symbol, files in symbol_files.items():
        print(f"  Processing news for: {symbol}")
        
        news_records = []
        
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Try to parse as JSON
                try:
                    data = json.loads(content)
                    
                    # Extract news items (format may vary)
                    if isinstance(data, dict):
                        if 'data' in data:
                            items = data['data']
                        elif 'items' in data:
                            items = data['items']
                        elif 'news' in data:
                            items = data['news']
                        else:
                            items = [data]
                        
                        for item in items[:20]:  # Max 20 news items
                            record = {
                                'symbol': symbol,
                                'date': item.get('date', item.get('publishedDate', '')),
                                'title': item.get('title', item.get('headline', ''))[:200],
                                'source': file.stem.split('_')[0],
                                'sentiment': 0.0,  # Placeholder
                            }
                            news_records.append(record)
                
                except json.JSONDecodeError:
                    # Plain text file - create simple record
                    record = {
                        'symbol': symbol,
                        'date': '',
                        'title': content[:200],
                        'source': file.stem.split('_')[0],
                        'sentiment': 0.0,
                    }
                    news_records.append(record)
            
            except Exception as e:
                print(f"    ⚠️  Error reading {file.name}: {e}")
        
        if news_records:
            df_news = pd.DataFrame(news_records)
            output_file = output_dir / f"{symbol.lower()}_news.csv"
            df_news.to_csv(output_file, index=False)
            print(f"  ✅ Created: {output_file} ({len(news_records)} articles)")


def main():
    """Main conversion function."""
    
    print("=" * 70)
    print("🔄 Data Converter - Raw API Data to CSV")
    print("=" * 70)
    
    # Paths
    base_dir = Path(__file__).parent.parent.parent / "data"
    finance_input = base_dir / "finance"
    news_input = base_dir / "news"
    
    # Create output directories if needed
    finance_input.mkdir(parents=True, exist_ok=True)
    news_input.mkdir(parents=True, exist_ok=True)
    
    # Convert data
    convert_vietcap_financial_data(finance_input, finance_input)
    convert_news_data(news_input, news_input)
    
    print("\n" + "=" * 70)
    print("✅ Conversion complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
