"""
Simple example demonstrating how to use the debate system programmatically.
"""
from orchestrator import DebateOrchestrator
import json


def run_simple_debate():
    """Run a simple debate and display results."""
    
    print("=" * 70)
    print("🎯 Gemini Multi-Agent Stock Debate - Simple Example")
    print("=" * 70)
    
    # Initialize orchestrator
    print("\n1️⃣ Initializing orchestrator...")
    try:
        orch = DebateOrchestrator()
        print("   ✅ Orchestrator ready")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return
    
    # Get available symbols
    print("\n2️⃣ Finding available stocks...")
    symbols = orch.get_available_symbols()
    
    if not symbols:
        print("   ⚠️  No stock data found")
        print("   Please add CSV files to:")
        print("   - /v5/data/finance/ (for financial and technical data)")
        print("   - /v5/data/news/ (for sentiment data)")
        return
    
    print(f"   ✅ Found {len(symbols)} stocks: {', '.join(symbols)}")
    
    # Select first available symbol
    symbol = symbols[0]
    print(f"\n3️⃣ Running debate for {symbol}...")
    
    try:
        # Run the debate
        result = orch.run_full_debate(symbol, "3 months")
        
        print(f"   ✅ Debate completed!")
        print(f"   - Total statements: {len(result['transcript'])}")
        
        # Display data availability
        print("\n4️⃣ Data availability:")
        for data_type, available in result['data_availability'].items():
            status = "✅" if available else "❌"
            print(f"   {status} {data_type.title()}")
        
        # Display debate transcript
        print("\n5️⃣ Debate Transcript:")
        print("=" * 70)
        
        for entry in result['transcript']:
            agent = entry['agent']
            round_num = entry.get('round', '-')
            statement = entry['statement']
            
            # Agent emoji
            emoji_map = {
                "Fundamental": "💼",
                "Technical": "📈",
                "Sentiment": "💭",
                "Moderator": "⚖️",
                "Judge": "👨‍⚖️"
            }
            emoji = emoji_map.get(agent, "🤖")
            
            print(f"\n{emoji} {agent} (Round {round_num})")
            print("-" * 70)
            print(statement)
        
        # Highlight final verdict
        print("\n" + "=" * 70)
        print("📊 FINAL VERDICT")
        print("=" * 70)
        print(result['verdict'])
        print("=" * 70)
        
        # Export option
        export_file = f"debate_{symbol.lower()}_transcript.json"
        orch.export_transcript(export_file)
        print(f"\n💾 Transcript saved to: {export_file}")
        
    except Exception as e:
        print(f"   ❌ Error during debate: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_simple_debate()
