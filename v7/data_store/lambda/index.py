"""
Data Loader Lambda - Minimal data retrieval service
Fetches financial data and caches in DynamoDB
"""

import json
import os
from datetime import datetime
import boto3

dynamodb = boto3.resource('dynamodb')
stock_cache_table = dynamodb.Table(os.environ['STOCK_CACHE_TABLE'])
CACHE_TTL = int(os.environ.get('CACHE_TTL', '86400'))


def handler(event, context):
    """
    Handler for data retrieval requests
    Supports: GET /data/{symbol}
    """
    try:
        symbol = event['pathParameters']['symbol'].upper()
        
        # Check cache first
        cached_data = get_cached_data(symbol)
        if cached_data:
            return success_response(cached_data)
        
        # Fetch fresh data
        data = fetch_stock_data(symbol)
        
        # Cache the data
        cache_data(symbol, data)
        
        return success_response(data)
    
    except Exception as e:
        print(f"Error in data loader: {str(e)}")
        return error_response(str(e), 500)


def get_cached_data(symbol: str):
    """Retrieve data from DynamoDB cache"""
    try:
        response = stock_cache_table.get_item(Key={'symbol': symbol})
        
        if 'Item' not in response:
            return None
        
        item = response['Item']
        
        # Check if cache is still valid
        if 'ttl' in item and item['ttl'] < int(datetime.now().timestamp()):
            return None
        
        return item.get('data')
    
    except Exception as e:
        print(f"Error getting cached data: {str(e)}")
        return None


def fetch_stock_data(symbol: str) -> dict:
    """
    Fetch stock data from external sources
    Minimal implementation - can be extended with more data sources
    """
    try:
        # Simple implementation - can be extended with yfinance, Alpha Vantage, etc.
        data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'prices': {
                'current': 100.00,  # Placeholder
                'high_52w': 120.00,
                'low_52w': 80.00,
            },
            'fundamentals': {
                'pe_ratio': 15.5,
                'market_cap': '10B',
                'eps': 6.45,
            },
            'technical': {
                'rsi': 45,
                'macd': 'positive',
                'sma_200': 95.00,
            },
        }
        return data
    
    except Exception as e:
        print(f"Error fetching stock data: {str(e)}")
        raise


def cache_data(symbol: str, data: dict):
    """Store data in DynamoDB with TTL"""
    try:
        ttl = int(datetime.now().timestamp()) + CACHE_TTL
        
        stock_cache_table.put_item(
            Item={
                'symbol': symbol,
                'data': data,
                'ttl': ttl,
                'cached_at': datetime.now().isoformat(),
            }
        )
    
    except Exception as e:
        print(f"Error caching data: {str(e)}")


def success_response(data: dict, status_code: int = 200) -> dict:
    """Format successful response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(data),
    }


def error_response(message: str, status_code: int = 400) -> dict:
    """Format error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({'error': message}),
    }
