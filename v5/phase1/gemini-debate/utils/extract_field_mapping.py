#!/usr/bin/env python3
"""
Extract field mapping from VietCap metrics API response.
This creates a mapping from field codes (e.g., 'bsa1', 'bsb109') to human-readable English names.
"""
import json
from pathlib import Path

def extract_mapping():
    """Extract field mapping from the metrics file."""
    
    # Read the metrics file
    metrics_file = Path(__file__).parent.parent.parent / 'data' / 'finance' / \
                   'iq.vietcap.com.vn_api_iq-insight-service_v1_company_MBB_financial-statement_metrics.txt'
    
    with open(metrics_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    field_map = {}
    
    # The 'data' field contains sections (BALANCE_SHEET, INCOME_STATEMENT, etc.)
    if 'data' in data and isinstance(data['data'], dict):
        for section_name, section_data in data['data'].items():
            # Each section contains a list of field definitions
            if isinstance(section_data, list):
                for item in section_data:
                    if isinstance(item, dict) and 'field' in item:
                        field_code = item['field']
                        # Use fullTitleEn or titleEn as the English name
                        english_name = item.get('fullTitleEn') or item.get('titleEn', field_code)
                        field_map[field_code] = english_name
        
        if field_map:
            # Save the mapping
            output_file = Path(__file__).parent / 'field_mapping.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(field_map, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Extracted {len(field_map)} field mappings")
            print(f"📄 Saved to: {output_file}")
            
            # Show some examples
            print("\n📋 Sample mappings:")
            for code, name in list(field_map.items())[:5]:
                print(f"   {code} → {name}")
            
            return field_map
    
    print("❌ Could not find field definitions in metrics file")
    return {}

if __name__ == '__main__':
    extract_mapping()
