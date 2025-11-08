#!/usr/bin/env python3
"""
Main Application - Gemini Multi-Agent Stock Debate PoC

Run: python app.py --stock VNM --rounds 3
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/debate.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

from services.gemini_service import create_gemini_service
from services.data_service import DataService
from services.debate_orchestrator import DebateOrchestrator
from db.models import DatabaseManager


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Gemini Multi-Agent Stock Debate PoC"
    )
    parser.add_argument(
        "--stock",
        type=str,
        default="VNM",
        help="Stock symbol (e.g., VNM, VIC, VCB)",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=3,
        help="Number of debate rounds",
    )
    parser.add_argument(
        "--period",
        type=int,
        default=90,
        help="Analysis period in days",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Gemini API key (uses GEMINI_API_KEY env var if not provided)",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Database URL (uses DATABASE_URL env var or SQLite if not provided)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results.json",
        help="Output file for debate results",
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("Gemini Multi-Agent Stock Debate PoC")
    logger.info("=" * 80)
    logger.info(f"Stock: {args.stock}")
    logger.info(f"Rounds: {args.rounds}")
    logger.info(f"Period: {args.period} days")
    
    try:
        # Initialize Gemini service
        logger.info("Initializing Gemini service...")
        gemini_service = create_gemini_service(api_key=args.api_key)
        
        # Initialize database (optional)
        db_manager = None
        if args.db_url or os.getenv("DATABASE_URL"):
            logger.info("Initializing database...")
            db_manager = DatabaseManager(args.db_url)
            db_manager.init_db()
        
        # Fetch stock data
        logger.info(f"Fetching data for {args.stock}...")
        data_service = DataService()
        stock_data = data_service.fetch_stock_data(args.stock, args.period)
        logger.info(f"✓ Fetched data: price={stock_data.get('price')}, "
                   f"volume={stock_data.get('volume')}")
        
        # Initialize and run debate
        logger.info("Initializing debate orchestrator...")
        orchestrator = DebateOrchestrator(gemini_service, db_manager)
        
        logger.info(f"Starting {args.rounds}-round debate...")
        result = orchestrator.run_debate(
            stock_symbol=args.stock,
            stock_data=stock_data,
            num_rounds=args.rounds,
            period_days=args.period,
        )
        
        # Display result
        logger.info("=" * 80)
        logger.info("DEBATE RESULT")
        logger.info("=" * 80)
        logger.info(f"Stock: {result.stock_symbol}")
        logger.info(f"Decision: {result.final_decision}")
        logger.info(f"Confidence: {result.confidence:.0%}")
        logger.info(f"Summary: {result.summary}")
        logger.info(f"Rounds: {result.num_rounds}")
        logger.info(f"Duration: {(result.end_time - result.start_time).total_seconds():.1f}s")
        logger.info("=" * 80)
        
        # Save results to JSON
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(result.to_dict(), f, indent=2, default=str)
        
        logger.info(f"✓ Results saved to {output_path}")
        
        # Print verdict details
        logger.info("\nDECISION DETAILS:")
        logger.info(json.dumps(result.rationale, indent=2))
        
        if "key_catalysts" in result.rationale or "risks" in result.rationale:
            logger.info("\nKEY CATALYSTS & RISKS:")
            # Extract from rationale if present (depends on Judge output format)
        
        logger.info("\nDEBATE COMPLETE ✓")
        return 0
    
    except KeyboardInterrupt:
        logger.info("\nDebate interrupted by user")
        return 1
    
    except Exception as e:
        logger.exception(f"Error: {e}")
        return 1
    
    finally:
        if db_manager:
            db_manager.close()


if __name__ == "__main__":
    sys.exit(main())
