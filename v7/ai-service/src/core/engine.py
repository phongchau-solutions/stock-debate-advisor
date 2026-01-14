from typing import Dict, Any
import json
from pathlib import Path
import google.generativeai as genai
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.core.config import settings
from src.core.constants import AGENT_PROMPTS

class DataLoader:
    def __init__(self):
        self.data_path = settings.DATA_STORE_PATH

    def load_stock_data(self, ticker: str) -> Dict[str, Any]:
        ticker_path = self.data_path / f"{ticker}.VN"
        if not ticker_path.exists():
            ticker_path = self.data_path / ticker
        
        if not ticker_path.exists():
            return {"error": f"No data found for {ticker}"}
        
        data = {}
        for file in ["company_info.json", "financial_reports.json", "ohlc_prices.json"]:
            file_path = ticker_path / file
            if file_path.exists():
                with open(file_path) as f:
                    data[file.replace(".json", "")] = json.load(f)
        
        return data

class DebateEngine:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.data_loader = DataLoader()
        self.debate_history = []

    def _call_gemini(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.TEMPERATURE,
                    max_output_tokens=settings.MAX_TOKENS,
                )
            )
            return response.text if response.text else "No response generated"
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"

    def debate(self, ticker: str, timeframe: str, min_rounds: int, max_rounds: int) -> Dict[str, Any]:
        stock_data = self.data_loader.load_stock_data(ticker)
        if "error" in stock_data:
            raise ValueError(stock_data["error"])
        
        rounds_data = []
        current_round = 1
        should_continue = True
        
        while should_continue and current_round <= max_rounds:
            round_result = self._run_debate_round(ticker, timeframe, current_round, stock_data)
            rounds_data.append(round_result)
            
            judge_decision = round_result.get("judge_decision", "")
            should_continue = "CONTINUE" in judge_decision and current_round < max_rounds
            should_continue = should_continue or current_round < min_rounds
            
            current_round += 1
        
        final_verdict = self._extract_final_verdict(rounds_data[-1]["judge_decision"])
        
        return {
            "ticker": ticker,
            "timeframe": timeframe,
            "actual_rounds": current_round - 1,
            "rounds": rounds_data,
            "final_recommendation": final_verdict.get("recommendation", "HOLD"),
            "confidence": final_verdict.get("confidence", "Medium"),
            "rationale": final_verdict.get("reasoning", ""),
            "risks": final_verdict.get("risks", ""),
            "monitor": final_verdict.get("monitor", "")
        }

    def _run_debate_round(self, ticker: str, timeframe: str, round_num: int, stock_data: Dict) -> Dict[str, str]:
        context = f"Analyzing {ticker} for {timeframe} timeframe. Round {round_num}."
        history_context = "\n".join(self.debate_history[-3:]) if self.debate_history else ""
        
        responses = {}
        for analyst in ["fundamental", "technical", "sentiment"]:
            prompt = f"{AGENT_PROMPTS[analyst]}\n\n{context}\n\nPrevious discussion:\n{history_context}\n\nProvide your {analyst} analysis with specific data points and recommendation for {timeframe} timeframe."
            result = self._call_gemini(prompt)
            responses[analyst] = result
            self.debate_history.append(f"Round {round_num} {analyst.upper()}: {result[:200]}")
        
        judge_prompt = f"{AGENT_PROMPTS['judge']}\n\nRound {round_num} Debate Summary:\n" + \
                      "\n".join([f"{k}: {v[:100]}" for k, v in responses.items()]) + \
                      f"\n\nEvaluate the debate quality and decide: CONTINUE for more debate (if additional analysis needed) or CONCLUDE if sufficient evidence for {timeframe} timeframe investment decision.\n\nRespond with CONTINUE or CONCLUDE followed by your reasoning."
        
        judge_result = self._call_gemini(judge_prompt)
        
        return {
            "round_num": round_num,
            "fundamental": responses.get("fundamental", ""),
            "technical": responses.get("technical", ""),
            "sentiment": responses.get("sentiment", ""),
            "judge_decision": judge_result
        }

    def _extract_final_verdict(self, judge_output: str) -> Dict[str, str]:
        lines = judge_output.split("\n")
        verdict = {
            "recommendation": "HOLD",
            "confidence": "Medium",
            "reasoning": judge_output[:300],
            "risks": "",
            "monitor": ""
        }
        
        for line in lines:
            line_lower = line.lower()
            if "buy" in line_lower and "for" in line_lower:
                verdict["recommendation"] = "BUY"
            elif "sell" in line_lower and "for" in line_lower:
                verdict["recommendation"] = "SELL"
            elif "confidence" in line_lower:
                if "high" in line_lower:
                    verdict["confidence"] = "High"
                elif "low" in line_lower:
                    verdict["confidence"] = "Low"
            elif "risk" in line_lower:
                verdict["risks"] = line.replace("Risk:", "").strip()
            elif "monitor" in line_lower:
                verdict["monitor"] = line.replace("Monitor:", "").strip()
        
        return verdict
