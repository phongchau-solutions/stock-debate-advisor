"""AWS Bedrock-powered debate engine for Stock Debate Advisor using Claude Sonnet 3.5"""
from typing import Dict, Any
import json
import os
import sys
import boto3
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.constants import AGENT_PROMPTS
from src.core.config import settings

class DataLoaderDynamoDB:
    """Load stock data from DynamoDB tables"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.companies_table = self.dynamodb.Table(os.environ.get('COMPANIES_TABLE', settings.COMPANIES_TABLE))
        self.financial_table = self.dynamodb.Table(os.environ.get('FINANCIAL_REPORTS_TABLE', settings.FINANCIAL_REPORTS_TABLE))
        self.ohlc_table = self.dynamodb.Table(os.environ.get('OHLC_PRICES_TABLE', settings.OHLC_PRICES_TABLE))
    
    def load_stock_data(self, ticker: str) -> Dict[str, Any]:
        try:
            company_response = self.companies_table.get_item(Key={'ticker': ticker})
            company_data = company_response.get('Item', {})
            
            if not company_data:
                return {'error': f'No data found for {ticker}'}
            
            financial_response = self.financial_table.query(
                KeyConditionExpression='ticker = :ticker',
                ExpressionAttributeValues={':ticker': ticker},
                ScanIndexForward=False,
                Limit=4
            )
            financial_data = financial_response.get('Items', [])
            
            ohlc_response = self.ohlc_table.query(
                KeyConditionExpression='ticker = :ticker',
                ExpressionAttributeValues={':ticker': ticker},
                ScanIndexForward=False,
                Limit=60
            )
            ohlc_data = ohlc_response.get('Items', [])
            
            return {
                'company_info': company_data,
                'financial_reports': financial_data,
                'ohlc_prices': {'prices': ohlc_data}
            }
        
        except Exception as e:
            return {'error': f'Failed to load data from DynamoDB: {str(e)}'}


class DebateEngineBedrock:
    """Multi-agent debate engine using Amazon Bedrock with Claude Sonnet 3.5"""
    
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name=settings.BEDROCK_REGION)
        self.model_id = settings.BEDROCK_MODEL  # Claude Sonnet 3.5: anthropic.claude-3-5-sonnet-20241022-v2:0
        self.data_loader = DataLoaderDynamoDB()
        self.debate_history = []
    
    def _call_bedrock(self, prompt: str) -> str:
        """Call Claude Sonnet 3.5 via Bedrock"""
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-06-01',
                    'max_tokens': settings.MAX_TOKENS,
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'temperature': settings.TEMPERATURE
                })
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
        
        except Exception as e:
            return f"Error calling Bedrock: {str(e)}"
    
    def debate(self, ticker: str, timeframe: str, min_rounds: int, max_rounds: int) -> Dict[str, Any]:
        """Execute iterative debate with Judge control"""
        stock_data = self.data_loader.load_stock_data(ticker)
        if 'error' in stock_data:
            raise ValueError(stock_data['error'])
        
        rounds_data = []
        current_round = 1
        should_continue = True
        
        while should_continue and current_round <= max_rounds:
            round_result = self._run_debate_round(ticker, timeframe, current_round, stock_data)
            rounds_data.append(round_result)
            
            judge_decision = round_result.get('judge_decision', '')
            should_continue = 'CONTINUE' in judge_decision and current_round < max_rounds
            should_continue = should_continue or current_round < min_rounds
            
            current_round += 1
        
        final_verdict = self._extract_final_verdict(rounds_data[-1]['judge_decision'])
        
        # Cache debate result in DynamoDB (optional)
        self._cache_debate_result(ticker, timeframe, rounds_data, final_verdict)
        
        return {
            'ticker': ticker,
            'timeframe': timeframe,
            'actual_rounds': current_round - 1,
            'rounds': rounds_data,
            'final_recommendation': final_verdict.get('recommendation', 'HOLD'),
            'confidence': final_verdict.get('confidence', 'Medium'),
            'rationale': final_verdict.get('reasoning', ''),
            'risks': final_verdict.get('risks', ''),
            'monitor': final_verdict.get('monitor', '')
        }
    
    def _run_debate_round(self, ticker: str, timeframe: str, round_num: int, stock_data: Dict) -> Dict[str, str]:
        """Execute single debate round with all 3 analysts + judge"""
        context = f"Analyzing {ticker} for {timeframe} timeframe. Round {round_num}."
        history_context = "\n".join(self.debate_history[-3:]) if self.debate_history else ""
        
        responses = {}
        for analyst in ["fundamental", "technical", "sentiment"]:
            prompt = f"{AGENT_PROMPTS[analyst]}\n\n{context}\n\nPrevious discussion:\n{history_context}\n\nProvide your {analyst} analysis with specific data points and recommendation for {timeframe} timeframe."
            result = self._call_bedrock(prompt)
            responses[analyst] = result
            self.debate_history.append(f"Round {round_num} {analyst.upper()}: {result[:200]}")
        
        judge_prompt = f"{AGENT_PROMPTS['judge']}\n\nRound {round_num} Debate Summary:\n" + \
                      "\n".join([f"{k}: {v[:100]}" for k, v in responses.items()]) + \
                      f"\n\nEvaluate the debate quality and decide: CONTINUE for more debate (if additional analysis needed) or CONCLUDE if sufficient evidence for {timeframe} timeframe investment decision.\n\nRespond with CONTINUE or CONCLUDE followed by your reasoning."
        
        judge_result = self._call_bedrock(judge_prompt)
        
        return {
            'round_num': round_num,
            'fundamental': responses.get('fundamental', ''),
            'technical': responses.get('technical', ''),
            'sentiment': responses.get('sentiment', ''),
            'judge_decision': judge_result
        }
    
    def _extract_final_verdict(self, judge_output: str) -> Dict[str, str]:
        """Parse final investment verdict from judge decision"""
        lines = judge_output.split("\n")
        verdict = {
            'recommendation': 'HOLD',
            'confidence': 'Medium',
            'reasoning': judge_output[:300],
            'risks': '',
            'monitor': ''
        }
        
        for line in lines:
            line_lower = line.lower()
            if "buy" in line_lower and "for" in line_lower:
                verdict['recommendation'] = 'BUY'
            elif "sell" in line_lower and "for" in line_lower:
                verdict['recommendation'] = 'SELL'
            elif "confidence" in line_lower:
                if "high" in line_lower:
                    verdict['confidence'] = 'High'
                elif "low" in line_lower:
                    verdict['confidence'] = 'Low'
            elif "risk" in line_lower:
                verdict['risks'] = line.replace("Risk:", "").strip()
            elif "monitor" in line_lower:
                verdict['monitor'] = line.replace("Monitor:", "").strip()
        
        return verdict
    
    def _cache_debate_result(self, ticker: str, timeframe: str, rounds: list, verdict: dict):
        """Cache debate result in DynamoDB for future lookups"""
        try:
            dynamodb = boto3.resource('dynamodb')
            debate_table = dynamodb.Table(os.environ.get('DEBATE_RESULTS_TABLE', settings.DEBATE_RESULTS_TABLE))
            
            timestamp = datetime.utcnow().isoformat()
            
            debate_table.put_item(
                Item={
                    'pk': f"{ticker}#{timeframe}",
                    'sk': timestamp,
                    'created_at': timestamp,
                    'ticker': ticker,
                    'timeframe': timeframe,
                    'rounds': len(rounds),
                    'recommendation': verdict.get('recommendation', 'HOLD'),
                    'confidence': verdict.get('confidence', 'Medium'),
                    'rationale': verdict.get('reasoning', '')[:500],
                    'ttl': int(datetime.utcnow().timestamp()) + (7 * 24 * 60 * 60)  # 7 day TTL
                }
            )
        except Exception as e:
            print(f"Failed to cache debate result: {e}")
