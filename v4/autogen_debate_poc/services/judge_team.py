"""
Judge Team Implementation
3-member financial expert consensus voting system using Autogen Teams API.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class JudgeVote:
    """Individual judge's vote."""
    judge_name: str
    decision: str  # BUY, HOLD, SELL
    confidence: float  # 0-100
    reasoning: str
    timestamp: datetime


@dataclass
class AggregatedDecision:
    """Aggregated team decision."""
    final_decision: str  # BUY, HOLD, SELL
    confidence: float  # 0-100
    votes: List[JudgeVote]
    voting_rationale: str
    unanimity_score: float  # 0-100, how aligned votes are


class JudgeTeam:
    """
    3-member financial expert team for debate judgment.
    
    Members:
    1. Fundamental Judge (valuation expert)
    2. Technical Judge (momentum/chart expert)
    3. Sentiment Judge (risk/news expert)
    
    Process:
    1. Each judge independently evaluates evidence
    2. Produces independent verdict + confidence
    3. Aggregation combines votes with weighting
    4. Consensus decision output
    """
    
    def __init__(self, llm_service):
        """
        Initialize Judge Team.
        
        Args:
            llm_service: Gemini LLM service for judge reasoning
        """
        self.llm_service = llm_service
        self.judges = {
            "fundamental": {
                "name": "Judge Fundamental",
                "expertise": "Valuation & Financial Health",
                "weight": 0.35,  # 35% weight
            },
            "technical": {
                "name": "Judge Technical",
                "expertise": "Momentum & Chart Patterns",
                "weight": 0.33,  # 33% weight
            },
            "sentiment": {
                "name": "Judge Sentiment",
                "expertise": "Market Sentiment & Risk",
                "weight": 0.32,  # 32% weight
            },
        }
        self.votes: List[JudgeVote] = []
        logger.info("Initialized JudgeTeam with 3 experts")
    
    def judge_fundamental_analysis(
        self,
        stock_symbol: str,
        fundamental_data: Dict[str, Any],
        analyst_reasoning: str,
    ) -> JudgeVote:
        """
        Judge 1: Evaluate fundamental analysis.
        
        Args:
            stock_symbol: Stock being analyzed
            fundamental_data: Financial metrics
            analyst_reasoning: Fundamental analyst's reasoning
            
        Returns:
            JudgeVote from fundamental expert
        """
        judge_prompt = f"""
You are a Fundamental Analysis Judge, expert in valuation and financial health.

Stock: {stock_symbol}
Financial Data: {fundamental_data}
Analyst's Reasoning: {analyst_reasoning}

Evaluate this fundamental analysis independently and provide:
1. Your verdict (BUY/HOLD/SELL)
2. Confidence level (0-100)
3. Key reasoning points

Focus on:
- P/E ratio fairness
- ROE sustainability  
- Debt levels & ratios
- Growth prospects
- Dividend safety
"""
        
        try:
            response = self.llm_service.generate_response(judge_prompt)
            
            # Parse response for verdict and confidence
            verdict = self._extract_verdict(response)
            confidence = self._extract_confidence(response)
            
            vote = JudgeVote(
                judge_name="Judge Fundamental",
                decision=verdict,
                confidence=confidence,
                reasoning=response,
                timestamp=datetime.utcnow(),
            )
            
            logger.info(
                f"Fundamental Judge: {verdict} ({confidence}%) "
                f"- {stock_symbol}"
            )
            
            return vote
        
        except Exception as e:
            logger.error(f"Error in fundamental judgment: {e}")
            # Default conservative vote on error
            return JudgeVote(
                judge_name="Judge Fundamental",
                decision="HOLD",
                confidence=50.0,
                reasoning=f"Error during analysis: {str(e)}",
                timestamp=datetime.utcnow(),
            )
    
    def judge_technical_analysis(
        self,
        stock_symbol: str,
        technical_data: Dict[str, Any],
        analyst_reasoning: str,
    ) -> JudgeVote:
        """
        Judge 2: Evaluate technical analysis.
        
        Args:
            stock_symbol: Stock being analyzed
            technical_data: Chart patterns, indicators
            analyst_reasoning: Technical analyst's reasoning
            
        Returns:
            JudgeVote from technical expert
        """
        judge_prompt = f"""
You are a Technical Analysis Judge, expert in price action and indicators.

Stock: {stock_symbol}
Technical Data: {technical_data}
Analyst's Reasoning: {analyst_reasoning}

Evaluate this technical analysis independently and provide:
1. Your verdict (BUY/HOLD/SELL)
2. Confidence level (0-100)
3. Key reasoning points

Focus on:
- Trend direction & strength
- Support/resistance levels
- Momentum indicators (RSI, MACD)
- Moving average positioning
- Volume confirmation
"""
        
        try:
            response = self.llm_service.generate_response(judge_prompt)
            
            verdict = self._extract_verdict(response)
            confidence = self._extract_confidence(response)
            
            vote = JudgeVote(
                judge_name="Judge Technical",
                decision=verdict,
                confidence=confidence,
                reasoning=response,
                timestamp=datetime.utcnow(),
            )
            
            logger.info(
                f"Technical Judge: {verdict} ({confidence}%) "
                f"- {stock_symbol}"
            )
            
            return vote
        
        except Exception as e:
            logger.error(f"Error in technical judgment: {e}")
            return JudgeVote(
                judge_name="Judge Technical",
                decision="HOLD",
                confidence=50.0,
                reasoning=f"Error during analysis: {str(e)}",
                timestamp=datetime.utcnow(),
            )
    
    def judge_sentiment_analysis(
        self,
        stock_symbol: str,
        sentiment_data: Dict[str, Any],
        analyst_reasoning: str,
    ) -> JudgeVote:
        """
        Judge 3: Evaluate sentiment & risk analysis.
        
        Args:
            stock_symbol: Stock being analyzed
            sentiment_data: News, catalysts, sentiment
            analyst_reasoning: Sentiment analyst's reasoning
            
        Returns:
            JudgeVote from sentiment expert
        """
        judge_prompt = f"""
You are a Sentiment & Risk Judge, expert in market sentiment and catalysts.

Stock: {stock_symbol}
Sentiment Data: {sentiment_data}
Analyst's Reasoning: {analyst_reasoning}

Evaluate this sentiment analysis independently and provide:
1. Your verdict (BUY/HOLD/SELL)
2. Confidence level (0-100)
3. Key reasoning points

Focus on:
- Overall sentiment tone
- Positive vs negative catalysts
- Risk factors & mitigation
- Timeframe of catalysts
- Market cycle position
"""
        
        try:
            response = self.llm_service.generate_response(judge_prompt)
            
            verdict = self._extract_verdict(response)
            confidence = self._extract_confidence(response)
            
            vote = JudgeVote(
                judge_name="Judge Sentiment",
                decision=verdict,
                confidence=confidence,
                reasoning=response,
                timestamp=datetime.utcnow(),
            )
            
            logger.info(
                f"Sentiment Judge: {verdict} ({confidence}%) "
                f"- {stock_symbol}"
            )
            
            return vote
        
        except Exception as e:
            logger.error(f"Error in sentiment judgment: {e}")
            return JudgeVote(
                judge_name="Judge Sentiment",
                decision="HOLD",
                confidence=50.0,
                reasoning=f"Error during analysis: {str(e)}",
                timestamp=datetime.utcnow(),
            )
    
    def aggregate_votes(self) -> AggregatedDecision:
        """
        Aggregate individual judge votes into final team decision.
        
        Returns:
            AggregatedDecision with consensus verdict
        """
        if not self.votes or len(self.votes) < 3:
            logger.error("Cannot aggregate: insufficient votes")
            return AggregatedDecision(
                final_decision="HOLD",
                confidence=0.0,
                votes=self.votes,
                voting_rationale="Insufficient votes for aggregation",
                unanimity_score=0.0,
            )
        
        # Count votes
        vote_counts = {
            "BUY": 0,
            "HOLD": 0,
            "SELL": 0,
        }
        
        weighted_confidence = 0.0
        
        for i, vote in enumerate(self.votes):
            vote_counts[vote.decision] += 1
            
            # Get judge weight
            judge_key = (
                "fundamental" if "Fundamental" in vote.judge_name
                else "technical" if "Technical" in vote.judge_name
                else "sentiment"
            )
            weight = self.judges[judge_key]["weight"]
            
            # Add weighted confidence
            weighted_confidence += vote.confidence * weight
        
        # Determine final decision (majority vote)
        final_decision = max(vote_counts, key=vote_counts.get)
        
        # Calculate unanimity score (0-100)
        # 100 = all agree, 33 = all different
        max_votes = max(vote_counts.values())
        unanimity_score = (max_votes / 3.0) * 100
        
        # Generate voting rationale
        rationale = self._generate_rationale(vote_counts, self.votes)
        
        aggregated = AggregatedDecision(
            final_decision=final_decision,
            confidence=weighted_confidence,
            votes=self.votes,
            voting_rationale=rationale,
            unanimity_score=unanimity_score,
        )
        
        logger.info(
            f"Team Decision: {final_decision} "
            f"({weighted_confidence:.1f}% confidence, "
            f"{unanimity_score:.0f}% unanimity)"
        )
        
        return aggregated
    
    def _extract_verdict(self, response: str) -> str:
        """Extract BUY/HOLD/SELL verdict from LLM response."""
        response_upper = response.upper()
        
        if "BUY" in response_upper:
            return "BUY"
        elif "SELL" in response_upper:
            return "SELL"
        else:
            return "HOLD"
    
    def _extract_confidence(self, response: str) -> float:
        """Extract confidence level (0-100) from LLM response."""
        import re
        
        # Look for patterns like "confidence: 75%" or "75 percent"
        patterns = [
            r"confidence[:\s]+(\d+)%?",
            r"(\d+)\s*(?:%|percent)",
            r"(\d+)/100",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                confidence = float(match.group(1))
                return min(100.0, max(0.0, confidence))  # Clamp 0-100
        
        # Default to 50 if no pattern found
        return 50.0
    
    def _generate_rationale(
        self,
        vote_counts: Dict[str, int],
        votes: List[JudgeVote],
    ) -> str:
        """Generate human-readable rationale for team decision."""
        lines = []
        
        # Majority verdict
        for vote in votes:
            decision_emoji = {
                "BUY": "📈",
                "SELL": "📉",
                "HOLD": "⏸️",
            }.get(vote.decision, "❓")
            
            lines.append(
                f"{decision_emoji} {vote.judge_name}: {vote.decision} "
                f"({vote.confidence:.0f}%)"
            )
        
        # Summary
        lines.append("")
        lines.append("Team Analysis:")
        lines.append(
            f"- Consensus: {vote_counts['BUY']} BUY, "
            f"{vote_counts['HOLD']} HOLD, {vote_counts['SELL']} SELL"
        )
        
        return "\n".join(lines)
    
    def reset(self) -> None:
        """Reset for next debate."""
        self.votes.clear()
        logger.info("JudgeTeam reset")


def create_judge_team(llm_service) -> JudgeTeam:
    """Factory function to create JudgeTeam."""
    return JudgeTeam(llm_service)
