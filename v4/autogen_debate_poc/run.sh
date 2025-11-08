#!/bin/bash
# Quick start script for Gemini Debate PoC

set -e

echo "🚀 Gemini Multi-Agent Stock Debate PoC - Quick Start"
echo "======================================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env and add your GEMINI_API_KEY"
    exit 1
fi

# Load environment
source .env

# Check API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set in .env file"
    exit 1
fi

echo "✓ Environment loaded"

# Determine stock symbol from argument or default
STOCK="${1:-VNM}"
ROUNDS="${2:-3}"

echo "📊 Running debate for: $STOCK ($ROUNDS rounds)"
echo ""

# Run the debate
python app.py \
    --stock "$STOCK" \
    --rounds "$ROUNDS" \
    --period 30 \
    --output "logs/${STOCK}_debate_$(date +%s).json"

echo ""
echo "✨ Debate complete! Check logs/ directory for results."
