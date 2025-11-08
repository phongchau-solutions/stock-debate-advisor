#!/usr/bin/env python3
"""
Convert VietCap financial statement data to clean JSON format.
Uses field mapping to translate field codes to human-readable names.
"""
import json
from pathlib import Path
from collections import defaultdict

def load_field_mapping():
    """Load the field code to English name mapping."""
    mapping_file = Path(__file__).parent / 'field_mapping.json'
    with open(mapping_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_financial_statements():
    """Convert financial statement data to structured JSON."""
    
    # Load field mapping
    field_map = load_field_mapping()
    print(f"📖 Loaded {len(field_map)} field mappings")
    
    # Paths
    data_dir = Path(__file__).parent.parent.parent / 'data' / 'finance'
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'finance'
    
    # Find balance sheet file
    bs_file = data_dir / 'iq.vietcap.com.vn_api_iq-insight-service_v1_company_MBB_financial-statement_section=BALANCE_SHEET.txt'
    is_file = data_dir / 'iq.vietcap.com.vn_api_iq-insight-service_v1_company_MBB_financial-statement_section=INCOME_STATEMENT.txt'
    cf_file = data_dir / 'iq.vietcap.com.vn_api_iq-insight-service_v1_company_MBB_financial-statement_section=CASH_FLOW.txt'
    
    symbol = 'MBB'
    result = {
        'symbol': symbol,
        'years': []
    }
    
    # Process each statement type
    statements = {
        'balance_sheet': bs_file,
        'income_statement': is_file,
        'cash_flow': cf_file
    }
    
    for stmt_name, stmt_file in statements.items():
        if not stmt_file.exists():
            print(f"⚠️  {stmt_name} file not found")
            continue
            
        print(f"📊 Processing {stmt_name}...")
        
        with open(stmt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'data' in data and isinstance(data['data'], dict):
            years_data = data['data'].get('years', [])
            
            # Group by year
            year_map = defaultdict(lambda: {'statement_type': stmt_name, 'items': {}})
            
            # For each year in the data
            for year_dict in years_data if isinstance(years_data, list) else []:
                if not isinstance(year_dict, dict):
                    continue
                    
                year = year_dict.get('yearReport')
                if not year:
                    continue
                
                # Extract all financial line items
                for field_code, value in year_dict.items():
                    if field_code.startswith(('bsa', 'bsb', 'bss', 'bsi', 'isa', 'isb', 'cfa', 'cfb', 'nos')):
                        # Skip zero values for cleaner output
                        if value == 0 or value == 0.0:
                            continue
                            
                        # Get human-readable name
                        english_name = field_map.get(field_code, field_code)
                        
                        if year not in [y['year'] for y in result['years']]:
                            result['years'].append({
                                'year': year,
                                'balance_sheet': {},
                                'income_statement': {},
                                'cash_flow': {}
                            })
                        
                        # Find the year entry
                        year_entry = next(y for y in result['years'] if y['year'] == year)
                        year_entry[stmt_name][english_name] = value
    
    # Sort by year
    result['years'].sort(key=lambda x: x['year'])
    
    # Keep only last 5 years
    result['years'] = result['years'][-5:]
    
    # Save to JSON
    output_file = output_dir / f'{symbol.lower()}_financials.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Created: {output_file}")
    print(f"📅 Years: {[y['year'] for y in result['years']]}")
    
    # Show sample data
    if result['years']:
        latest_year = result['years'][-1]
        print(f"\n📋 Sample data for {latest_year['year']}:")
        
        # Show top 5 balance sheet items
        bs_items = list(latest_year['balance_sheet'].items())[:5]
        if bs_items:
            print(f"\n   Balance Sheet (showing {len(bs_items)} of {len(latest_year['balance_sheet'])}):")
            for name, value in bs_items:
                print(f"   - {name}: {value:,.0f}")
        
        # Show top 5 income statement items
        is_items = list(latest_year['income_statement'].items())[:5]
        if is_items:
            print(f"\n   Income Statement (showing {len(is_items)} of {len(latest_year['income_statement'])}):")
            for name, value in is_items:
                print(f"   - {name}: {value:,.0f}")

if __name__ == '__main__':
    print("=" * 70)
    print("🔄 Converting Financial Statements to JSON")
    print("=" * 70)
    convert_financial_statements()
    print("\n" + "=" * 70)
    print("✅ Conversion complete!")
    print("=" * 70)
