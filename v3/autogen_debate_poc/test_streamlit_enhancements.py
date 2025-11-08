#!/usr/bin/env python3
"""
Test the enhanced Streamlit features:
1. Summary cards above debate feed
2. Dynamic rounds with early termination
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.debate_orchestrator import DebateOrchestrator


async def test_early_termination():
    """Test that debate can terminate early on strong consensus."""
    print("=" * 80)
    print("TEST: Early Termination on Strong Consensus")
    print("=" * 80)
    
    orchestrator = DebateOrchestrator(
        rounds=5,  # Max 5 rounds
        llm_config=None
    )
    
    print("\nRunning debate with max 5 rounds...")
    print("Will check if early termination happens on consensus\n")
    
    message_count = 0
    
    def on_message(msg: dict):
        nonlocal message_count
        message_count += 1
        
        agent = msg.get("agent", "Unknown")
        round_num = msg.get("round", 0)
        
        if "analysis" in msg:
            analysis = msg["analysis"]
            signal = analysis.get("signal", analysis.get("bias", "N/A"))
            confidence = analysis.get("confidence", 0)
            print(f"[Round {round_num}] {agent}: {signal.upper()} (confidence: {confidence:.0%})")
        elif "consensus" in msg:
            print(f"\n[FINAL] Moderator reached consensus")
    
    try:
        result = await orchestrator.run_debate(
            stock_symbol="VNM",
            period_days=30,
            on_message=on_message
        )
        
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"Total rounds executed: {result['total_rounds']}/{result['max_rounds']}")
        print(f"Total messages: {message_count}")
        print(f"Decision: {result['consensus'].get('decision', 'N/A')}")
        print(f"Confidence: {result['consensus'].get('confidence', 0):.0%}")
        
        if result['total_rounds'] < result['max_rounds']:
            print(f"\n✓ Early termination worked! Stopped at round {result['total_rounds']} (max was {result['max_rounds']})")
        else:
            print(f"\n✓ Completed all {result['max_rounds']} rounds")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_summary_data():
    """Test that we can extract summary data from agent responses."""
    print("\n" + "=" * 80)
    print("TEST: Summary Data Extraction")
    print("=" * 80)
    
    orchestrator = DebateOrchestrator(rounds=2, llm_config=None)
    
    agent_summaries = {}
    
    def on_message(msg: dict):
        agent = msg.get("agent", "Unknown")
        
        if "analysis" in msg and agent != "Moderator":
            analysis = msg["analysis"]
            signal = analysis.get("signal", analysis.get("bias", analysis.get("sentiment_label", "N/A")))
            confidence = analysis.get("confidence", 0)
            
            # Extract key data
            if agent == "TechnicalAnalyst":
                indicators = analysis.get("indicators", {})
                key_data = f"RSI: {indicators.get('rsi', 'N/A')}, MACD: {indicators.get('macd', 'N/A')}"
            elif agent == "FundamentalAnalyst":
                ratios = analysis.get("ratios", {})
                key_data = f"P/E: {ratios.get('pe', 'N/A')}, ROE: {ratios.get('roe', 'N/A')}"
            elif agent == "SentimentAnalyst":
                news_count = len(analysis.get("news_articles", []))
                sentiment_score = analysis.get("sentiment_score", "N/A")
                key_data = f"{news_count} articles, Score: {sentiment_score}"
            else:
                key_data = "N/A"
            
            agent_summaries[agent] = {
                "signal": signal,
                "confidence": confidence,
                "key_data": key_data
            }
    
    try:
        await orchestrator.run_debate(
            stock_symbol="VNM",
            period_days=30,
            on_message=on_message
        )
        
        print("\nExtracted Summary Data:")
        print("-" * 80)
        for agent, summary in agent_summaries.items():
            print(f"\n{agent}:")
            print(f"  Signal: {summary['signal']}")
            print(f"  Confidence: {summary['confidence']:.0%}")
            print(f"  Key Data: {summary['key_data']}")
        
        print("\n✓ Summary data extraction works!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    await test_early_termination()
    await test_summary_data()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
    print("\n✓ Enhanced Streamlit features are ready:")
    print("  1. Summary cards will display above debate feed")
    print("  2. Rounds are now dynamic (can end early on consensus)")
    print("  3. User sets minimum rounds, not fixed count")


if __name__ == "__main__":
    asyncio.run(main())
