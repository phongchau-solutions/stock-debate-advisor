"""
JSON serialization utility for handling numpy and pandas data types.
"""

import json
import numpy as np
import pandas as pd
from typing import Any

class FinancialDataEncoder(json.JSONEncoder):
    """Custom JSON encoder for financial data with numpy/pandas types."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif pd.isna(obj):
            return None
        return super().default(obj)

def safe_json_dumps(data: Any, **kwargs) -> str:
    """JSON dumps with financial data type handling."""
    return json.dumps(data, cls=FinancialDataEncoder, **kwargs)