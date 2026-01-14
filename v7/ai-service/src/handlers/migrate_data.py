"""
Data migration Lambda function
Loads stock data from v7/data_store/data JSON files into DynamoDB tables
Run once after initial deployment to populate database
"""
import json
import boto3
import os
from datetime import datetime
from pathlib import Path

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Event format:
    {
        "action": "migrate_from_s3",  // or "migrate_from_local"
        "data_bucket": "stock-data-source",
        "override": false
    }
    """
    
    companies_table = dynamodb.Table(os.environ['COMPANIES_TABLE'])
    financial_table = dynamodb.Table(os.environ['FINANCIAL_REPORTS_TABLE'])
    ohlc_table = dynamodb.Table(os.environ['OHLC_PRICES_TABLE'])
    
    action = event.get('action', 'migrate_from_s3')
    override = event.get('override', False)
    
    try:
        if action == 'migrate_from_local':
            # For testing: migrate from local data_store directory
            return migrate_from_local(
                companies_table, 
                financial_table, 
                ohlc_table,
                override
            )
        else:
            # Migrate from S3 bucket containing stock JSON files
            return migrate_from_s3(
                companies_table,
                financial_table,
                ohlc_table,
                event.get('data_bucket', 'stock-debate-data'),
                override
            )
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def migrate_from_local(companies_table, financial_table, ohlc_table, override):
    """Migrate from local file system (for testing)"""
    data_dir = Path('/tmp/stock_data_2026')  # Assumes data is staged
    
    if not data_dir.exists():
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Local data directory not found'})
        }
    
    stats = {
        'companies': 0,
        'financial_reports': 0,
        'ohlc_prices': 0,
        'errors': []
    }
    
    # Process each ticker directory
    for ticker_dir in data_dir.iterdir():
        if not ticker_dir.is_dir():
            continue
        
        ticker = ticker_dir.name.replace('.VN', '')
        
        try:
            # Load company info
            company_file = ticker_dir / 'company_info.json'
            if company_file.exists():
                with open(company_file) as f:
                    company_data = json.load(f)
                    company_data['ticker'] = ticker
                    companies_table.put_item(Item=company_data)
                    stats['companies'] += 1
            
            # Load financial reports
            financial_file = ticker_dir / 'financial_reports.json'
            if financial_file.exists():
                with open(financial_file) as f:
                    reports = json.load(f)
                    for report in reports:
                        report['ticker'] = ticker
                        report['timestamp'] = report.get('timestamp', datetime.utcnow().isoformat())
                        financial_table.put_item(Item=report)
                        stats['financial_reports'] += 1
            
            # Load OHLC prices
            ohlc_file = ticker_dir / 'ohlc_prices.json'
            if ohlc_file.exists():
                with open(ohlc_file) as f:
                    ohlc_data = json.load(f)
                    prices = ohlc_data.get('prices', [])
                    for price in prices:
                        price['ticker'] = ticker
                        price['date'] = price.get('date', '2026-01-01')
                        ohlc_table.put_item(Item=price)
                        stats['ohlc_prices'] += 1
        
        except Exception as e:
            stats['errors'].append(f"{ticker}: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(stats)
    }


def migrate_from_s3(companies_table, financial_table, ohlc_table, bucket, override):
    """Migrate from S3 bucket"""
    s3 = boto3.client('s3')
    
    stats = {
        'companies': 0,
        'financial_reports': 0,
        'ohlc_prices': 0,
        'errors': []
    }
    
    try:
        # List all objects in bucket
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket)
        
        for page in pages:
            if 'Contents' not in page:
                continue
            
            for obj in page['Contents']:
                key = obj['Key']
                
                # Parse key format: {ticker}/company_info.json, etc
                parts = key.split('/')
                if len(parts) < 2:
                    continue
                
                ticker = parts[0].replace('.VN', '')
                filename = parts[1]
                
                try:
                    # Download and parse file
                    response = s3.get_object(Bucket=bucket, Key=key)
                    data = json.loads(response['Body'].read())
                    
                    if filename == 'company_info.json':
                        data['ticker'] = ticker
                        companies_table.put_item(Item=data)
                        stats['companies'] += 1
                    
                    elif filename == 'financial_reports.json':
                        reports = data if isinstance(data, list) else [data]
                        for report in reports:
                            report['ticker'] = ticker
                            report['timestamp'] = report.get('timestamp', datetime.utcnow().isoformat())
                            financial_table.put_item(Item=report)
                            stats['financial_reports'] += 1
                    
                    elif filename == 'ohlc_prices.json':
                        prices_data = data if isinstance(data, dict) else {'prices': data}
                        prices = prices_data.get('prices', [])
                        for price in prices:
                            price['ticker'] = ticker
                            price['date'] = price.get('date', '2026-01-01')
                            ohlc_table.put_item(Item=price)
                            stats['ohlc_prices'] += 1
                
                except Exception as e:
                    stats['errors'].append(f"{key}: {str(e)}")
    
    except Exception as e:
        stats['errors'].append(f"S3 migration failed: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(stats)
    }
