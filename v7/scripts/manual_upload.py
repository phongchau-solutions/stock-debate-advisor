#!/usr/bin/env python3
"""
Manual Data Upload Script - Upload stock data to DynamoDB
Can be run locally or scheduled via EventBridge/Lambda
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import argparse        
import boto3
from botocore.exceptions import ClientError

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def discover_dynamodb_tables(region: str = None):
    """
    Auto-discover DynamoDB tables from the stack.
    Looks for tables with names containing 'Companies', 'FinancialReports', 'OhlcPrices'
    """
    try:
        client = boto3.client('dynamodb', region_name=region)
        response = client.list_tables()
        tables = response.get('TableNames', [])
        
        companies_table = None
        financial_table = None
        ohlc_table = None
        
        for table in tables:
            if 'Companies' in table and not companies_table:
                companies_table = table
            elif 'FinancialReports' in table and not financial_table:
                financial_table = table
            elif 'OhlcPrices' in table and not ohlc_table:
                ohlc_table = table
        
        if companies_table and financial_table and ohlc_table:
            print(f"✓ Auto-discovered DynamoDB tables:")
            print(f"  - Companies: {companies_table}")
            print(f"  - Financial Reports: {financial_table}")
            print(f"  - OHLC Prices: {ohlc_table}\n")
            return {
                'companies_table': companies_table,
                'financial_table': financial_table,
                'ohlc_table': ohlc_table
            }
        else:
            print("Warning: Could not auto-discover all required tables.")
            print(f"  Found: Companies={companies_table}, Financial={financial_table}, OHLC={ohlc_table}")
            if not any([companies_table, financial_table, ohlc_table]):
                print("  No matching tables found in region.")
            return None
    except Exception as e:
        print(f"Warning: Could not auto-discover tables: {str(e)}")
        return None

def upload_data_locally(data_store_path: str, tables_config: dict, region: str = None):
    """
    Upload data to DynamoDB from local data_store
    
    Args:
        data_store_path: Path to data_store/data directory
        tables_config: Dict with table names
        region: AWS region name (e.g., 'us-east-1')
    
    Example:
        python manual_upload.py --data-path ../data_store/data \\
            --companies-table companies \\
            --financial-table financial_reports \\
            --ohlc-table ohlc_prices \\
            --region us-east-1
    """
    
    data_path = Path(data_store_path)
    if not data_path.exists():
        print(f"Error: Data path not found: {data_store_path}")
        sys.exit(1)
    
    # Create DynamoDB resource with region
    if region:
        dynamodb = boto3.resource('dynamodb', region_name=region)
    else:
        dynamodb = boto3.resource('dynamodb')
    
    # Get table references
    companies_table = dynamodb.Table(tables_config['companies_table'])
    financial_table = dynamodb.Table(tables_config['financial_table'])
    ohlc_table = dynamodb.Table(tables_config['ohlc_table'])
    
    stats = {
        'companies': 0,
        'financial': 0,
        'ohlc': 0,
        'errors': []
    }
    
    # Process each year directory
    for year_dir in sorted(data_path.iterdir()):
        if not year_dir.is_dir():
            continue
        
        print(f"\n📁 Processing year: {year_dir.name}")
        
        # Process each ticker
        for ticker_dir in sorted(year_dir.iterdir()):
            if not ticker_dir.is_dir():
                continue
            
            ticker = ticker_dir.name.replace('.VN', '')
            
            try:
                # Upload company info
                company_file = ticker_dir / 'company_info.json'
                if company_file.exists():
                    with open(company_file) as f:
                        company_data = json.load(f)
                    
                    item = {
                        'ticker': ticker,
                        'symbol': company_data.get('symbol', ticker),
                        'timestamp': company_data.get('timestamp', datetime.utcnow().isoformat()),
                        'name': company_data.get('info', {}).get('name', ''),
                        'sector': company_data.get('info', {}).get('sector', ''),
                        'industry': company_data.get('info', {}).get('industry', ''),
                        'market_cap': company_data.get('info', {}).get('market_cap', 0),
                        'website': company_data.get('info', {}).get('website', ''),
                        'description': company_data.get('info', {}).get('description', '')[:500],
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    
                    companies_table.put_item(Item=item)
                    stats['companies'] += 1
                    print(f"  ✓ {ticker} company info")
                
                # Upload financial reports
                financial_file = ticker_dir / 'financial_reports.json'
                if financial_file.exists():
                    with open(financial_file) as f:
                        financial_data = json.load(f)
                    
                    reports = financial_data.get('reports', [])
                    if isinstance(reports, dict):
                        reports = [reports]
                    
                    for report in reports:
                        try:
                            timestamp = report.get('timestamp', datetime.utcnow().isoformat())
                            item = {
                                'ticker': ticker,
                                'timestamp': timestamp,
                                'pe_ratio': Decimal(str(report.get('metrics', {}).get('pe_ratio', 0))),
                                'pb_ratio': Decimal(str(report.get('metrics', {}).get('pb_ratio', 0))),
                                'dividend_yield': Decimal(str(report.get('metrics', {}).get('dividend_yield', 0))),
                                'eps': Decimal(str(report.get('metrics', {}).get('eps', 0))),
                                'roe': Decimal(str(report.get('metrics', {}).get('roe', 0))),
                                'roa': Decimal(str(report.get('metrics', {}).get('roa', 0))),
                                'debt_to_equity': Decimal(str(report.get('metrics', {}).get('debt_to_equity', 0))),
                                'current_ratio': Decimal(str(report.get('metrics', {}).get('current_ratio', 0))),
                                'revenue': Decimal(str(report.get('metrics', {}).get('revenue', 0))),
                                'net_income': Decimal(str(report.get('metrics', {}).get('net_income', 0))),
                                'updated_at': datetime.utcnow().isoformat()
                            }
                            
                            financial_table.put_item(Item=item)
                            stats['financial'] += 1
                        except Exception as e:
                            stats['errors'].append(f"Financial report for {ticker}: {str(e)}")
                    
                    if stats['financial'] > 0:
                        print(f"  ✓ {ticker} financial reports ({len(reports)})")
                
                # Upload OHLC prices
                ohlc_file = ticker_dir / 'ohlc_prices.json'
                if ohlc_file.exists():
                    with open(ohlc_file) as f:
                        ohlc_data = json.load(f)
                    
                    prices = ohlc_data.get('prices', [])
                    if isinstance(prices, dict):
                        prices = [prices]
                    
                    for price_record in prices:
                        try:
                            date = price_record.get('date', price_record.get('timestamp', datetime.utcnow().isoformat()))
                            item = {
                                'ticker': ticker,
                                'date': date,
                                'open': Decimal(str(price_record.get('open', 0))),
                                'high': Decimal(str(price_record.get('high', 0))),
                                'low': Decimal(str(price_record.get('low', 0))),
                                'close': Decimal(str(price_record.get('close', 0))),
                                'volume': int(price_record.get('volume', 0)),
                                'adjusted_close': Decimal(str(price_record.get('adjusted_close', price_record.get('close', 0)))),
                                'updated_at': datetime.utcnow().isoformat()
                            }
                            
                            ohlc_table.put_item(Item=item)
                            stats['ohlc'] += 1
                        except Exception as e:
                            stats['errors'].append(f"OHLC record for {ticker}: {str(e)}")
                    
                    if stats['ohlc'] > 0:
                        print(f"  ✓ {ticker} OHLC prices ({len(prices)})")
                
            except Exception as e:
                error_msg = f"Error processing {ticker}: {str(e)}"
                print(f"  ✗ {error_msg}")
                stats['errors'].append(error_msg)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 UPLOAD SUMMARY")
    print("="*60)
    print(f"Companies:        {stats['companies']}")
    print(f"Financial reports: {stats['financial']}")
    print(f"OHLC prices:      {stats['ohlc']}")
    if stats['errors']:
        print(f"\n⚠️  Errors: {len(stats['errors'])}")
        for error in stats['errors'][:5]:
            print(f"   - {error}")
        if len(stats['errors']) > 5:
            print(f"   ... and {len(stats['errors']) - 5} more")
    else:
        print("\n✅ All data uploaded successfully!")
    print("="*60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload stock data to DynamoDB')
    parser.add_argument('--data-path', default='./data_store/data', help='Path to data_store/data')
    parser.add_argument('--companies-table', default=None, help='Companies table name (auto-discovered if not provided)')
    parser.add_argument('--financial-table', default=None, help='Financial reports table name (auto-discovered if not provided)')
    parser.add_argument('--ohlc-table', default=None, help='OHLC prices table name (auto-discovered if not provided)')
    parser.add_argument('--region', default=os.getenv('AWS_REGION', 'us-east-1'), help='AWS region (default: AWS_REGION env or us-east-1)')
    parser.add_argument('--auto-discover', action='store_true', default=True, help='Auto-discover table names (default: True)')
    
    args = parser.parse_args()
    
    # Auto-discover tables if not provided
    if args.auto_discover and (not args.companies_table or not args.financial_table or not args.ohlc_table):
        print(f"🔍 Auto-discovering DynamoDB tables in region: {args.region}\n")
        discovered = discover_dynamodb_tables(args.region)
        if discovered:
            tables_config = discovered
        else:
            print("❌ Failed to auto-discover tables. Please provide table names explicitly.")
            sys.exit(1)
    else:
        # Use provided table names
        tables_config = {
            'companies_table': args.companies_table or 'companies',
            'financial_table': args.financial_table or 'financial_reports',
            'ohlc_table': args.ohlc_table or 'ohlc_prices'
        }
    
    upload_data_locally(args.data_path, tables_config, args.region)
