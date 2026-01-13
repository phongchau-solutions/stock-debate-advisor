"""
Updated API Endpoints for Stock Debate Advisor
Includes knowledge management and data access endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/session/{session_id}", tags=["Session"])
async def get_session_info(session_id: str):
    """Get detailed information about a debate session"""
    from orchestrator_v2 import get_orchestrator
    
    try:
        orchestrator = get_orchestrator()
        info = orchestrator.get_session_info(session_id)
        
        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/session/{session_id}/knowledge/fundamental", tags=["Knowledge"])
async def get_fundamental_knowledge(session_id: str):
    """Get fundamental analysis knowledge for a session"""
    from orchestrator_v2 import get_orchestrator
    from knowledge_manager import get_knowledge_manager
    
    try:
        orchestrator = get_orchestrator()
        knowledge_manager = get_knowledge_manager()
        
        session_info = orchestrator.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        knowledge = knowledge_manager.get_fundamental_knowledge(session_id)
        return {
            "session_id": session_id,
            "type": "fundamental",
            "knowledge": knowledge
        }
        
    except Exception as e:
        logger.error(f"Error getting fundamental knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/session/{session_id}/knowledge/technical", tags=["Knowledge"])
async def get_technical_knowledge(session_id: str):
    """Get technical analysis knowledge for a session"""
    from orchestrator_v2 import get_orchestrator
    from knowledge_manager import get_knowledge_manager
    
    try:
        orchestrator = get_orchestrator()
        knowledge_manager = get_knowledge_manager()
        
        session_info = orchestrator.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        knowledge = knowledge_manager.get_technical_knowledge(session_id)
        return {
            "session_id": session_id,
            "type": "technical",
            "knowledge": knowledge
        }
        
    except Exception as e:
        logger.error(f"Error getting technical knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/session/{session_id}/knowledge/sentiment", tags=["Knowledge"])
async def get_sentiment_knowledge(session_id: str):
    """Get sentiment analysis knowledge for a session"""
    from orchestrator_v2 import get_orchestrator
    from knowledge_manager import get_knowledge_manager
    
    try:
        orchestrator = get_orchestrator()
        knowledge_manager = get_knowledge_manager()
        
        session_info = orchestrator.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        knowledge = knowledge_manager.get_sentiment_knowledge(session_id)
        return {
            "session_id": session_id,
            "type": "sentiment",
            "knowledge": knowledge
        }
        
    except Exception as e:
        logger.error(f"Error getting sentiment knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/session/{session_id}/knowledge/all", tags=["Knowledge"])
async def get_all_knowledge(session_id: str):
    """Get all knowledge loaded for a session"""
    from orchestrator_v2 import get_orchestrator
    from knowledge_manager import get_knowledge_manager
    
    try:
        orchestrator = get_orchestrator()
        knowledge_manager = get_knowledge_manager()
        
        session_info = orchestrator.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        fundamental = knowledge_manager.get_fundamental_knowledge(session_id)
        technical = knowledge_manager.get_technical_knowledge(session_id)
        sentiment = knowledge_manager.get_sentiment_knowledge(session_id)
        
        return {
            "session_id": session_id,
            "symbol": session_info["symbol"],
            "knowledge": {
                "fundamental": fundamental,
                "technical": technical,
                "sentiment": sentiment
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting all knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/session/{session_id}/status", tags=["Session"])
async def get_debate_status(session_id: str):
    """Get current status of a debate session"""
    from orchestrator_v2 import get_orchestrator
    
    try:
        orchestrator = get_orchestrator()
        info = orchestrator.get_session_info(session_id)
        
        if not info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "symbol": info["symbol"],
            "current_round": info["current_round"],
            "data": info["data"],
            "created_at": info["created_at"]
        }
        
    except Exception as e:
        logger.error(f"Error getting debate status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/session/{session_id}/round/{round_num}", tags=["Debate"])
async def run_debate_round(session_id: str, round_num: int):
    """Run a specific round of debate"""
    from orchestrator_v2 import get_orchestrator
    
    try:
        orchestrator = get_orchestrator()
        
        # Check session exists
        session_info = orchestrator.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Run the round
        result = orchestrator.run_debate_round(session_id, round_num)
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail=result.get("error")
            )
        
        return {
            "session_id": session_id,
            "round": round_num,
            "status": "completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error running debate round: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/session/{session_id}/results", tags=["Results"])
async def get_debate_results(session_id: str):
    """Get complete debate results"""
    from orchestrator_v2 import get_orchestrator
    
    try:
        orchestrator = get_orchestrator()
        results = orchestrator.get_debate_results(session_id)
        
        if "error" in results:
            raise HTTPException(status_code=404, detail=results["error"])
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting debate results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/session/{session_id}", tags=["Session"])
async def end_session(session_id: str):
    """End a debate session and clean up resources"""
    from orchestrator_v2 import get_orchestrator
    
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.end_debate_session(session_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        logger.info(f"Session {session_id} ended")
        return result
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/data/{symbol}/financials", tags=["Data"])
async def get_financial_data(symbol: str):
    """Get financial data for a symbol"""
    from knowledge_manager import get_knowledge_manager
    
    try:
        km = get_knowledge_manager()
        reports = km.load_financial_reports(symbol)
        
        if not reports:
            raise HTTPException(status_code=404, detail=f"No financial data for {symbol}")
        
        return {
            "symbol": symbol,
            "reports": [
                {
                    "period": r.period,
                    "company": r.company,
                    "metrics": r.metrics
                }
                for r in reports
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting financial data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/data/{symbol}/technical", tags=["Data"])
async def get_technical_data(symbol: str):
    """Get technical data for a symbol"""
    from knowledge_manager import get_knowledge_manager
    
    try:
        km = get_knowledge_manager()
        tech_data = km.load_technical_data(symbol)
        
        if not tech_data:
            raise HTTPException(status_code=404, detail=f"No technical data for {symbol}")
        
        return {
            "symbol": symbol,
            "current_price": tech_data.current_price,
            "data_points": len(tech_data.closes),
            "period": f"{tech_data.dates[-1]} to {tech_data.dates[0]}",
            "latest_ohlc": {
                "date": tech_data.dates[0],
                "open": tech_data.opens[0],
                "high": tech_data.highs[0],
                "low": tech_data.lows[0],
                "close": tech_data.closes[0],
                "volume": tech_data.volumes[0]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting technical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/data/{symbol}/news", tags=["Data"])
async def get_news_data(symbol: str):
    """Get news articles for a symbol"""
    from knowledge_manager import get_knowledge_manager
    
    try:
        km = get_knowledge_manager()
        articles = km.load_news_articles(symbol)
        
        if not articles:
            raise HTTPException(status_code=404, detail=f"No news data for {symbol}")
        
        return {
            "symbol": symbol,
            "total_articles": len(articles),
            "articles": [
                {
                    "title": a.title,
                    "summary": a.summary,
                    "date": a.date,
                    "sentiment": a.sentiment,
                    "source": a.source
                }
                for a in articles
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting news data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
