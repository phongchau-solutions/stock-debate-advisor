#!/usr/bin/env python3
"""
Simple demo to verify agents are having real conversations.
Runs a short debate on VNM stock to check if agents interact.
"""

import asyncio
import sys
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).parent))

from services.debate_orchestrator import DebateOrchestrator


async def main():
    print("=" * 80)
    print("AGENT CONVERSATION DEMO")
    print("=" * 80)
    print("\nThis demo will run a 3-round debate on VNM stock.")
    print("Watch for agent interactions and responses to each other.\n")
    
    # Check for GEMINI_API_KEY
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠ Warning: GEMINI_API_KEY not set in environment")
        print("Set it with: export GEMINI_API_KEY='your-key-here'")
        print("Demo will continue with fallback mode...\n")
    
    # Configure LLM
    llm_config = None
    if api_key:
        llm_config = {
            "config_list": [{
                "model": "gemini-1.5-flash",
                "api_type": "gemini",
                "api_key": api_key
            }],
            "timeout": 120
        }
    
    # Initialize orchestrator
    print("Initializing debate orchestrator...")
    orchestrator = DebateOrchestrator(
        rounds=3,  # Short demo
        llm_config=llm_config
    )
    
    # Run debate
    symbol = "VNM"
    print(f"Starting debate on {symbol}...\n")
    print("-" * 80)
    
    try:
        # Callback to print messages as they come
        def on_message(msg: dict):
            agent = msg.get("agent", "Unknown")
            round_num = msg.get("round", 0)
            
            print(f"\n[Round {round_num}] {agent}:")
            
            if "analysis" in msg:
                analysis = msg["analysis"]
                signal = analysis.get("signal", analysis.get("bias", "N/A"))
                confidence = analysis.get("confidence", 0)
                rationale = analysis.get("rationale", "No rationale provided")[:300]
                
                print(f"  Signal: {signal.upper()} | Confidence: {confidence:.0%}")
                print(f"  Rationale: {rationale}...")
            
            elif "consensus" in msg:
                consensus = msg["consensus"]
                print(f"\n{'=' * 80}")
                print(f"FINAL CONSENSUS")
                print(f"{'=' * 80}")
                print(f"Decision: {consensus.get('decision', 'N/A')}")
                print(f"Confidence: {consensus.get('confidence', 0):.0%}")
                print(f"Summary: {consensus.get('summary', '')[:300]}...")
            
            print("-" * 80)
        
        result = await orchestrator.run_debate(
            stock_symbol=symbol,
            period_days=30,
            on_message=on_message
        )
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        
        # Check for interaction indicators
        transcript = result.get("transcript", [])
        print(f"\nTotal messages in transcript: {len(transcript)}")
        
        agent_messages = {}
        for msg in transcript:
            agent = msg.get("agent", "Unknown")
            if agent not in agent_messages:
                agent_messages[agent] = []
            agent_messages[agent].append(msg)
        
        print(f"Agents participated: {len(agent_messages)}")
        for agent, msgs in agent_messages.items():
            print(f"  - {agent}: {len(msgs)} messages")
        
        # Check for interaction indicators in rationales
        interactions = 0
        interaction_examples = []
        for msg in transcript:
            if "analysis" in msg:
                rationale = msg["analysis"].get("rationale", "").lower()
                interaction_words = ['agree', 'disagree', 'however', 'but', 'although', 
                                    'considering', 'in response', 'contrary', 'support', 
                                    'challenge', 'debate', 'previous']
                
                for word in interaction_words:
                    if word in rationale:
                        interactions += 1
                        if len(interaction_examples) < 3:
                            interaction_examples.append({
                                "agent": msg.get("agent"),
                                "round": msg.get("round"),
                                "word": word,
                                "snippet": rationale[:150]
                            })
                        break
        
        print(f"\nInteraction indicators found: {interactions} messages")
        
        if interactions > 0:
            print("\n✓ Agents appear to be INTERACTING with each other")
            if interaction_examples:
                print("\nExamples:")
                for ex in interaction_examples:
                    print(f"  - Round {ex['round']} {ex['agent']}: contains '{ex['word']}'")
                    print(f"    \"{ex['snippet']}...\"")
        else:
            print("\n⚠ Agents may be INDEPENDENTLY generating text without interaction")
            print("   (This could mean they're not reading debate history)")
        
        # Check if responses are unique per round
        print("\n" + "=" * 80)
        print("UNIQUENESS CHECK")
        print("=" * 80)
        technical_messages = [m["analysis"].get("rationale", "")[:100] 
                             for m in agent_messages.get("TechnicalAnalyst", []) 
                             if "analysis" in m]
        
        if len(technical_messages) > 1:
            if technical_messages[0] != technical_messages[1]:
                print("✓ Technical agent generates DIFFERENT messages per round")
            else:
                print("✗ Technical agent generates SAME message per round (likely static)")
        
        print("\n" + "=" * 80)
        print(f"Debate transcript saved to: {orchestrator.log_dir}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error running debate: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
