"""AWS Lambda handler for Stock Debate API"""
import json
import os
from typing import Any, Dict
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    from src.core.engine_bedrock import DebateEngineBedrock as DebateEngine
else:
    from src.core.engine import DebateEngine

engine = None

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    global engine
    
    if engine is None:
        engine = DebateEngine()
    
    method = event.get('httpMethod', 'GET').upper()
    path = event.get('path', '/').lstrip('/prod')
    
    try:
        if path == '/health' and method == 'GET':
            return success_response({'status': 'healthy', 'version': '2.0'})
        elif path == '/debate' and method == 'POST':
            return debate_handler(event, engine)
        else:
            return error_response(404, {'error': f'Route {method} /{path} not found'})
    except Exception as e:
        return error_response(500, {'error': str(e)})

def debate_handler(event: Dict[str, Any], engine: DebateEngine) -> Dict[str, Any]:
    try:
        body = json.loads(event.get('body', '{}'))
        ticker = body.get('ticker', '').upper().strip()
        timeframe = body.get('timeframe', '3 months')
        min_rounds = int(body.get('min_rounds', 1))
        max_rounds = int(body.get('max_rounds', 5))
        
        if not ticker or len(ticker) < 2:
            return error_response(400, {'error': 'Invalid ticker'})
        
        if min_rounds < 1 or max_rounds < min_rounds or max_rounds > 10:
            return error_response(400, {'error': 'Invalid round configuration'})
        
        result = engine.debate(ticker, timeframe, min_rounds, max_rounds)
        return success_response(result)
    
    except ValueError as e:
        return error_response(400, {'error': str(e)})
    except Exception as e:
        return error_response(500, {'error': f'Debate failed: {str(e)}'})

def success_response(data: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(data)
    }

def error_response(status_code: int, error: Dict[str, str]) -> Dict[str, Any]:
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps(error)
    }
