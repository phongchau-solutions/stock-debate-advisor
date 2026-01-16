"""
API router for backend services
Provides REST endpoints for debate orchestration
"""

import logging
from typing import Dict, Any
from .orchestrator import DebateOrchestrator
from .data_service import DataService
from .database import DynamoDBClient

logger = logging.getLogger(__name__)


class APIRouter:
    """API router for backend services"""

    def __init__(
        self,
        db_client: DynamoDBClient,
        orchestrator: DebateOrchestrator,
        data_service: DataService
    ):
        """Initialize API router"""
        self.db = db_client
        self.orchestrator = orchestrator
        self.data_service = data_service

    def start_debate(
        self,
        symbol: str,
        rounds: int = 3,
        debate_results_table: str = "DebateResults"
    ) -> Dict[str, Any]:
        """
        Start a new debate session
        
        Args:
            symbol: Stock symbol
            rounds: Number of debate rounds
            debate_results_table: DynamoDB table name
            
        Returns:
            Debate session response
        """
        try:
            debate_id = self.orchestrator.initiate_debate(
                symbol, rounds, debate_results_table
            )
            return {
                "session_id": debate_id,
                "symbol": symbol,
                "rounds": rounds,
                "status": "initiated"
            }
        except Exception as e:
            logger.error(f"Failed to start debate: {e}")
            raise

    def get_debate_status(
        self,
        debate_id: str,
        debate_results_table: str = "DebateResults"
    ) -> Dict[str, Any]:
        """Get debate status"""
        result = self.orchestrator.get_debate_status(
            debate_id, debate_results_table
        )
        if not result:
            raise ValueError(f"Debate {debate_id} not found")
        return result

    def get_debate_results(
        self,
        debate_id: str,
        debate_results_table: str = "DebateResults"
    ) -> Dict[str, Any]:
        """Get debate results"""
        result = self.orchestrator.get_debate_results(
            debate_id, debate_results_table
        )
        if not result:
            raise ValueError(f"Debate {debate_id} not found")
        return result

    def get_company_data(
        self,
        symbol: str,
        companies_table: str = "Companies",
        financial_reports_table: str = "FinancialReports",
        ohlc_prices_table: str = "OHLCPrices"
    ) -> Dict[str, Any]:
        """Get company data"""
        return self.data_service.get_all_company_data(
            symbol,
            companies_table,
            financial_reports_table,
            ohlc_prices_table
        )

    def get_debate_history(
        self,
        symbol: str,
        debate_results_table: str = "DebateResults",
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get debate history for symbol"""
        history = self.orchestrator.get_debate_history(
            symbol, debate_results_table, limit
        )
        return {
            "symbol": symbol,
            "debates": history,
            "count": len(history)
        }
