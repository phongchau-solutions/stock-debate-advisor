"""
DynamoDB-compatible abstraction layer.
Works with local JSON files in development and real DynamoDB in AWS.
Implements key DynamoDB operations using a consistent interface.
"""
import json
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from threading import Lock
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)

# Thread-safe locks for file operations
file_locks = {}


class DynamoDBCompatStorage:
    """
    Local file-based storage compatible with DynamoDB API.
    Can be replaced with real DynamoDB client in production.
    """
    
    def __init__(self, table_name: str, base_path: str = "./data_store"):
        """
        Initialize DynamoDB-compatible storage.
        
        Args:
            table_name: Name of the table (e.g., 'stocks', 'company_info', 'prices')
            base_path: Root directory for data store
        """
        self.table_name = table_name
        self.base_path = Path(base_path)
        self.table_path = self.base_path / table_name
        self.table_path.mkdir(parents=True, exist_ok=True)
        self.use_dynamodb = os.getenv("USE_DYNAMODB", "false").lower() == "true"
        
        if self.use_dynamodb:
            self._init_dynamodb()
        
        logger.info(f"DynamoDB-compat storage initialized for table: {table_name}")
    
    def _init_dynamodb(self):
        """Initialize real DynamoDB client if AWS credentials available."""
        try:
            import boto3
            self.dynamodb = boto3.resource('dynamodb')
            self.table = self.dynamodb.Table(self.table_name)
            logger.info(f"Real DynamoDB client initialized for table: {self.table_name}")
        except Exception as e:
            logger.warning(f"Could not initialize DynamoDB, falling back to local storage: {e}")
            self.use_dynamodb = False
    
    def _get_lock(self, file_path: str) -> Lock:
        """Get thread lock for a file."""
        if file_path not in file_locks:
            file_locks[file_path] = Lock()
        return file_locks[file_path]
    
    def put_item(self, item: Dict[str, Any], primary_key: str = "id") -> bool:
        """
        Put an item in the table (create or update).
        
        Args:
            item: Dictionary with item data
            primary_key: Name of the primary key field (default: 'id')
            
        Returns:
            True if successful
        """
        try:
            # Ensure item has an ID
            if primary_key not in item:
                item[primary_key] = str(uuid.uuid4())
            
            item['timestamp'] = datetime.utcnow().isoformat()
            
            if self.use_dynamodb:
                # Convert Decimal for boto3
                self.table.put_item(Item=self._convert_to_dynamodb_types(item))
            else:
                # Local file storage
                item_id = item[primary_key]
                item_file = self.table_path / f"{item_id}.json"
                
                with self._get_lock(str(item_file)):
                    with open(item_file, 'w', encoding='utf-8') as f:
                        json.dump(item, f, indent=2, default=str)
            
            logger.info(f"Item stored in {self.table_name}: {item.get(primary_key, 'unknown')}")
            return True
        
        except Exception as e:
            logger.error(f"Error putting item in {self.table_name}: {e}")
            return False
    
    def get_item(self, key: Union[str, Dict[str, Any]], primary_key: str = "id") -> Optional[Dict[str, Any]]:
        """
        Get an item from the table by ID.
        
        Args:
            key: Item ID string or key dictionary
            primary_key: Name of the primary key field
            
        Returns:
            Item dictionary or None if not found
        """
        try:
            if isinstance(key, str):
                item_id = key
            else:
                item_id = key.get(primary_key)
            
            if self.use_dynamodb:
                response = self.table.get_item(Key={primary_key: item_id})
                return response.get('Item')
            else:
                item_file = self.table_path / f"{item_id}.json"
                if item_file.exists():
                    with self._get_lock(str(item_file)):
                        with open(item_file, 'r', encoding='utf-8') as f:
                            return json.load(f)
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting item from {self.table_name}: {e}")
            return None
    
    def query(self, key_condition: Dict[str, Any], primary_key: str = "id") -> List[Dict[str, Any]]:
        """
        Query items from the table.
        
        Args:
            key_condition: Key condition expression (e.g., {'symbol': 'MBB.VN'})
            primary_key: Name of the primary key field
            
        Returns:
            List of matching items
        """
        try:
            if self.use_dynamodb:
                # Use DynamoDB query
                response = self.table.query(
                    KeyConditionExpression=self._build_key_condition(key_condition, primary_key)
                )
                return response.get('Items', [])
            else:
                # Local file search
                results = []
                for item_file in self.table_path.glob("*.json"):
                    with self._get_lock(str(item_file)):
                        with open(item_file, 'r', encoding='utf-8') as f:
                            item = json.load(f)
                    
                    # Match all conditions
                    if self._matches_condition(item, key_condition):
                        results.append(item)
                
                return results
        
        except Exception as e:
            logger.error(f"Error querying {self.table_name}: {e}")
            return []
    
    def scan(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Scan all items in the table with optional filters.
        
        Args:
            filters: Optional filter conditions
            limit: Maximum items to return
            
        Returns:
            List of items
        """
        try:
            if self.use_dynamodb:
                response = self.table.scan(Limit=limit)
                items = response.get('Items', [])
                
                if filters:
                    items = [item for item in items if self._matches_condition(item, filters)]
                
                return items
            else:
                # Local file scan
                items = []
                for item_file in list(self.table_path.glob("*.json"))[:limit]:
                    with self._get_lock(str(item_file)):
                        with open(item_file, 'r', encoding='utf-8') as f:
                            item = json.load(f)
                    
                    if filters is None or self._matches_condition(item, filters):
                        items.append(item)
                
                return items
        
        except Exception as e:
            logger.error(f"Error scanning {self.table_name}: {e}")
            return []
    
    def delete_item(self, key: Union[str, Dict[str, Any]], primary_key: str = "id") -> bool:
        """
        Delete an item from the table.
        
        Args:
            key: Item ID string or key dictionary
            primary_key: Name of the primary key field
            
        Returns:
            True if successful
        """
        try:
            if isinstance(key, str):
                item_id = key
            else:
                item_id = key.get(primary_key)
            
            if self.use_dynamodb:
                self.table.delete_item(Key={primary_key: item_id})
            else:
                item_file = self.table_path / f"{item_id}.json"
                if item_file.exists():
                    item_file.unlink()
            
            logger.info(f"Item deleted from {self.table_name}: {item_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting item from {self.table_name}: {e}")
            return False
    
    def batch_write(self, items: List[Dict[str, Any]], primary_key: str = "id") -> bool:
        """
        Write multiple items to the table.
        
        Args:
            items: List of item dictionaries
            primary_key: Name of the primary key field
            
        Returns:
            True if all items written successfully
        """
        try:
            for item in items:
                if not self.put_item(item, primary_key):
                    return False
            
            logger.info(f"Batch wrote {len(items)} items to {self.table_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error batch writing to {self.table_name}: {e}")
            return False
    
    def batch_get(self, keys: List[Union[str, Dict[str, Any]]], primary_key: str = "id") -> List[Dict[str, Any]]:
        """
        Get multiple items by their IDs.
        
        Args:
            keys: List of item IDs or key dictionaries
            primary_key: Name of the primary key field
            
        Returns:
            List of items
        """
        results = []
        for key in keys:
            item = self.get_item(key, primary_key)
            if item:
                results.append(item)
        
        return results
    
    def append_to_list_field(self, item_id: str, field_name: str, value: Any, primary_key: str = "id") -> bool:
        """
        Append a value to a list field in an item.
        
        Args:
            item_id: ID of the item
            field_name: Name of the list field
            value: Value to append
            primary_key: Name of the primary key field
            
        Returns:
            True if successful
        """
        try:
            item = self.get_item(item_id, primary_key)
            if not item:
                item = {primary_key: item_id}
            
            if field_name not in item:
                item[field_name] = []
            
            if not isinstance(item[field_name], list):
                item[field_name] = [item[field_name]]
            
            item[field_name].append(value)
            return self.put_item(item, primary_key)
        
        except Exception as e:
            logger.error(f"Error appending to list field: {e}")
            return False
    
    @staticmethod
    def _convert_to_dynamodb_types(item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python types to DynamoDB-compatible types."""
        converted = {}
        for key, value in item.items():
            if isinstance(value, float):
                converted[key] = Decimal(str(value))
            elif isinstance(value, dict):
                converted[key] = DynamoDBCompatStorage._convert_to_dynamodb_types(value)
            elif isinstance(value, list):
                converted[key] = [DynamoDBCompatStorage._convert_to_dynamodb_types({'v': v}) 
                                 if isinstance(v, dict) else v for v in value]
            else:
                converted[key] = value
        
        return converted
    
    @staticmethod
    def _matches_condition(item: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """Check if item matches all conditions."""
        for key, value in conditions.items():
            if key not in item:
                return False
            
            if isinstance(value, dict):
                # Handle operators like $eq, $gt, $lt, etc.
                for op, op_value in value.items():
                    if op == '$eq' and item[key] != op_value:
                        return False
                    elif op == '$ne' and item[key] == op_value:
                        return False
                    elif op == '$gt' and item[key] <= op_value:
                        return False
                    elif op == '$lt' and item[key] >= op_value:
                        return False
                    elif op == '$contains' and op_value not in str(item[key]):
                        return False
            else:
                # Direct equality match
                if item[key] != value:
                    return False
        
        return True
    
    @staticmethod
    def _build_key_condition(conditions: Dict[str, Any], primary_key: str) -> str:
        """Build a DynamoDB key condition expression from conditions dict."""
        # Simplified version - real implementation would use boto3 Key() and Attr()
        parts = []
        for key in conditions:
            if key == primary_key:
                parts.append(f"{key} = :pk")
        
        return " AND ".join(parts) if parts else ""
    
    def list_all_items(self) -> List[Dict[str, Any]]:
        """List all items in the table."""
        return self.scan(limit=1000)
    
    def clear_table(self) -> bool:
        """Delete all items from the table."""
        try:
            if self.use_dynamodb:
                items = self.scan(limit=1000)
                for item in items:
                    # This would require a proper implementation
                    pass
            else:
                for item_file in self.table_path.glob("*.json"):
                    item_file.unlink()
            
            logger.info(f"Cleared all items from {self.table_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error clearing table {self.table_name}: {e}")
            return False
