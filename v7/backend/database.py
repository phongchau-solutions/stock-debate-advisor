"""
DynamoDB data access layer
Provides database operations with error handling and retries
"""

import boto3
import logging
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from .models import (
    DebateRecord, CompanyRecord, FinancialReportRecord, OhlcPriceRecord,
    DebateStatus
)

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass


class DynamoDBClient:
    """DynamoDB client wrapper with error handling"""

    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize DynamoDB client"""
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.client = boto3.client('dynamodb', region_name=region_name)

    def get_table(self, table_name: str):
        """Get DynamoDB table"""
        try:
            return self.dynamodb.Table(table_name)
        except ClientError as e:
            logger.error(f"Failed to get table {table_name}: {e}")
            raise DatabaseError(f"Table not found: {table_name}")

    def put_debate_record(self, table_name: str, record: DebateRecord) -> bool:
        """Save debate record to DynamoDB"""
        try:
            table = self.get_table(table_name)
            table.put_item(Item=record.to_item())
            logger.info(f"Saved debate record: {record.debate_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to save debate record: {e}")
            raise DatabaseError(f"Failed to save debate record: {e}")

    def get_debate_record(self, table_name: str, debate_id: str) -> Optional[DebateRecord]:
        """Retrieve debate record from DynamoDB"""
        try:
            table = self.get_table(table_name)
            response = table.get_item(Key={'debate_id': debate_id})
            if 'Item' in response:
                return DebateRecord.from_item(response['Item'])
            return None
        except ClientError as e:
            logger.error(f"Failed to get debate record {debate_id}: {e}")
            raise DatabaseError(f"Failed to get debate record: {e}")

    def update_debate_status(
        self, 
        table_name: str, 
        debate_id: str, 
        status: DebateStatus,
        **kwargs
    ) -> bool:
        """Update debate status and optional fields"""
        try:
            table = self.get_table(table_name)
            update_expr = "SET #status = :status"
            expr_values = {":status": status.value}

            # Add optional fields
            for key, value in kwargs.items():
                if value is not None:
                    update_expr += f", {key} = :{key}"
                    expr_values[f":{key}"] = value

            table.update_item(
                Key={'debate_id': debate_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues=expr_values
            )
            logger.info(f"Updated debate {debate_id} status to {status}")
            return True
        except ClientError as e:
            logger.error(f"Failed to update debate record {debate_id}: {e}")
            raise DatabaseError(f"Failed to update debate record: {e}")

    def query_debates_by_symbol(
        self, 
        table_name: str, 
        symbol: str,
        limit: int = 10
    ) -> List[DebateRecord]:
        """Query debates for a specific symbol"""
        try:
            table = self.get_table(table_name)
            response = table.query(
                IndexName='symbol-created_at-index',
                KeyConditionExpression='symbol = :symbol',
                ExpressionAttributeValues={':symbol': symbol},
                Limit=limit,
                ScanIndexForward=False  # Newest first
            )
            return [DebateRecord.from_item(item) for item in response.get('Items', [])]
        except ClientError as e:
            logger.error(f"Failed to query debates for {symbol}: {e}")
            raise DatabaseError(f"Failed to query debates: {e}")

    def put_company_record(self, table_name: str, record: CompanyRecord) -> bool:
        """Save company record"""
        try:
            table = self.get_table(table_name)
            table.put_item(Item=record.to_item())
            logger.info(f"Saved company record: {record.symbol}")
            return True
        except ClientError as e:
            logger.error(f"Failed to save company record: {e}")
            raise DatabaseError(f"Failed to save company record: {e}")

    def get_company_record(self, table_name: str, symbol: str) -> Optional[CompanyRecord]:
        """Retrieve company record"""
        try:
            table = self.get_table(table_name)
            response = table.get_item(Key={'symbol': symbol})
            if 'Item' in response:
                return CompanyRecord.from_item(response['Item'])
            return None
        except ClientError as e:
            logger.error(f"Failed to get company record {symbol}: {e}")
            raise DatabaseError(f"Failed to get company record: {e}")

    def query_financial_reports(
        self,
        table_name: str,
        symbol: str,
        limit: int = 10
    ) -> List[FinancialReportRecord]:
        """Query financial reports for a symbol"""
        try:
            table = self.get_table(table_name)
            response = table.query(
                KeyConditionExpression='symbol = :symbol',
                ExpressionAttributeValues={':symbol': symbol},
                Limit=limit,
                ScanIndexForward=False
            )
            return [FinancialReportRecord.from_item(item) for item in response.get('Items', [])]
        except ClientError as e:
            logger.error(f"Failed to query financial reports for {symbol}: {e}")
            raise DatabaseError(f"Failed to query financial reports: {e}")

    def query_ohlc_prices(
        self,
        table_name: str,
        symbol: str,
        limit: int = 100
    ) -> List[OhlcPriceRecord]:
        """Query OHLC price data for a symbol"""
        try:
            table = self.get_table(table_name)
            response = table.query(
                KeyConditionExpression='symbol = :symbol',
                ExpressionAttributeValues={':symbol': symbol},
                Limit=limit,
                ScanIndexForward=False
            )
            return [OhlcPriceRecord.from_item(item) for item in response.get('Items', [])]
        except ClientError as e:
            logger.error(f"Failed to query OHLC prices for {symbol}: {e}")
            raise DatabaseError(f"Failed to query OHLC prices: {e}")
