"""
Orchestrator service for debate coordination
Manages debate lifecycle and agent communication
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from .models import DebateRecord, DebateStatus, Recommendation, ConfidenceLevel
from .database import DynamoDBClient

logger = logging.getLogger(__name__)


class DebateOrchestrator:
    """Orchestrates multi-agent debate sessions"""

    def __init__(self, db_client: DynamoDBClient, bedrock_client=None):
        """
        Initialize orchestrator
        
        Args:
            db_client: DynamoDB client for persistence
            bedrock_client: Bedrock client for AI model access
        """
        self.db = db_client
        self.bedrock = bedrock_client

    def initiate_debate(
        self,
        symbol: str,
        rounds: int = 3,
        debate_results_table: str = "DebateResults"
    ) -> str:
        """
        Create a new debate session
        
        Args:
            symbol: Stock symbol to debate
            rounds: Number of debate rounds
            debate_results_table: DynamoDB table name
            
        Returns:
            Debate ID (session identifier)
        """
        debate_id = f"debate_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}"
        
        record = DebateRecord(
            debate_id=debate_id,
            symbol=symbol,
            status=DebateStatus.INITIATED,
            rounds=rounds,
            created_at=datetime.utcnow().isoformat()
        )
        
        try:
            self.db.put_debate_record(debate_results_table, record)
            logger.info(f"Initiated debate {debate_id} for {symbol} with {rounds} rounds")
            return debate_id
        except Exception as e:
            logger.error(f"Failed to initiate debate: {e}")
            raise

    def get_debate_status(
        self,
        debate_id: str,
        debate_results_table: str = "DebateResults"
    ) -> Optional[Dict[str, Any]]:
        """
        Get current debate status
        
        Args:
            debate_id: Debate session ID
            debate_results_table: DynamoDB table name
            
        Returns:
            Debate status dict or None if not found
        """
        try:
            record = self.db.get_debate_record(debate_results_table, debate_id)
            if record:
                return {
                    "session_id": record.debate_id,
                    "symbol": record.symbol,
                    "status": record.status.value,
                    "created_at": record.created_at,
                    "completed_at": record.completed_at,
                    "verdict": record.verdict,
                    "error": record.error_message
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get debate status: {e}")
            raise

    def get_debate_results(
        self,
        debate_id: str,
        debate_results_table: str = "DebateResults"
    ) -> Optional[Dict[str, Any]]:
        """
        Get full debate results
        
        Args:
            debate_id: Debate session ID
            debate_results_table: DynamoDB table name
            
        Returns:
            Complete debate results or None if not found
        """
        try:
            record = self.db.get_debate_record(debate_results_table, debate_id)
            if record:
                return {
                    "session_id": record.debate_id,
                    "symbol": record.symbol,
                    "status": record.status.value,
                    "rounds": record.rounds,
                    "created_at": record.created_at,
                    "completed_at": record.completed_at,
                    "verdict": record.verdict,
                    "summary": record.debate_summary,
                    "duration_seconds": record.duration_seconds
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get debate results: {e}")
            raise

    def update_debate_in_progress(
        self,
        debate_id: str,
        debate_results_table: str = "DebateResults"
    ) -> bool:
        """Mark debate as in progress"""
        try:
            self.db.update_debate_status(
                debate_results_table,
                debate_id,
                DebateStatus.IN_PROGRESS,
                started_at=datetime.utcnow().isoformat()
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update debate status: {e}")
            raise

    def complete_debate(
        self,
        debate_id: str,
        verdict: Dict[str, Any],
        summary: str,
        duration_seconds: float,
        debate_results_table: str = "DebateResults"
    ) -> bool:
        """Mark debate as completed with results"""
        try:
            self.db.update_debate_status(
                debate_results_table,
                debate_id,
                DebateStatus.COMPLETED,
                completed_at=datetime.utcnow().isoformat(),
                verdict=json.dumps(verdict),
                debate_summary=summary,
                duration_seconds=duration_seconds
            )
            return True
        except Exception as e:
            logger.error(f"Failed to complete debate: {e}")
            raise

    def fail_debate(
        self,
        debate_id: str,
        error_message: str,
        debate_results_table: str = "DebateResults"
    ) -> bool:
        """Mark debate as failed"""
        try:
            self.db.update_debate_status(
                debate_results_table,
                debate_id,
                DebateStatus.FAILED,
                completed_at=datetime.utcnow().isoformat(),
                error_message=error_message
            )
            return True
        except Exception as e:
            logger.error(f"Failed to fail debate: {e}")
            raise

    def get_debate_history(
        self,
        symbol: str,
        debate_results_table: str = "DebateResults",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get debate history for a symbol"""
        try:
            records = self.db.query_debates_by_symbol(debate_results_table, symbol, limit)
            return [
                {
                    "debate_id": r.debate_id,
                    "status": r.status.value,
                    "created_at": r.created_at,
                    "completed_at": r.completed_at,
                    "verdict": r.verdict
                }
                for r in records
            ]
        except Exception as e:
            logger.error(f"Failed to get debate history: {e}")
            raise
