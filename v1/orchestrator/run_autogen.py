from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.aggregator_agent import AggregatorAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.crawler_agent import CrawlerAgent
from agents.debate_agent import DebateAgent
from agents.parser_agent import ParserAgent
from infra.observability import REQUESTS, init_tracing
from integrations.autogen_client import AutogenClient

logger = logging.getLogger(__name__)


def run_deterministic_workflow(session_id: Optional[str] = None) -> Dict[str, Any]:
    """Scaffolded deterministic workflow wiring agents via Autogen deterministic channels.

    This function is a local orchestrator for demonstration; in production Autogen would run this flow as deterministic tasks.
    """
    init_tracing("agentic-orchestrator")
    autogen = AutogenClient(deterministic=True)
    session = autogen.create_session(session_id)

    # Instantiate agents
    crawler = CrawlerAgent()
    parser = ParserAgent()
    analyzer = AnalyzerAgent()
    debate_f = DebateAgent(role="fundamental")
    debate_t = DebateAgent(role="technical")
    debate_s = DebateAgent(role="sentiment")
    aggregator = AggregatorAgent()

    # 1) Crawl (Enhanced with news sentiment analysis)
    crawl_inputs: Dict[str, Any] = {
        "tickers": ["VCB", "VNM"],
        "start_date": "2024-10-01",
        "end_date": "2024-11-01",
        "period": "quarterly",
        "include_market": True,
        "include_news": True,  # Enable news and sentiment analysis
    }
    crawl_out = crawler.process(crawl_inputs, session_id=session.get("session_id"))
    logger.info("Crawl output: %s", crawl_out)
    # 2) Parse
    parse_out = parser.process({"raw": crawl_out.payload}, session_id=session.get("session_id"))
    logger.info("Parse output: %s", parse_out)
    # 3) Analyze
    analysis = analyzer.process({"parsed": parse_out.payload}, session_id=session.get("session_id"))
    logger.info("Analysis: %s", analysis)

    # 4) Retrieval (stub): Top-K evidence is taken from parse_out
    evidence = parse_out.payload.get("documents", [])

    # 5) Debate in parallel (deterministically run sequentially here)
    d_f = debate_f.process({"evidence": evidence}, session_id=session.get("session_id"))
    d_t = debate_t.process({"evidence": evidence}, session_id=session.get("session_id"))
    d_s = debate_s.process({"evidence": evidence}, session_id=session.get("session_id"))

    debates = [d.model_dump()["payload"] for d in (d_f, d_t, d_s)]

    # 6) Aggregate
    agg = aggregator.process({"debates": debates}, session_id=session.get("session_id"))

    # Observability
    REQUESTS.inc()

    return {"session": session, "crawl": crawl_out.model_dump(), "parse": parse_out.model_dump(), "analysis": analysis.model_dump(), "debates": debates, "aggregate": agg.model_dump()}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    out = run_deterministic_workflow(session_id="local-demo-1")
    
    # Use safe JSON serialization for financial data
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from integrations.json_utils import safe_json_dumps

    print(safe_json_dumps(out, indent=2))
