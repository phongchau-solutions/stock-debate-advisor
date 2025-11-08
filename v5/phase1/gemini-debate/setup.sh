#!/bin/bash

# Setup script for Gemini Multi-Agent Stock Debate System

set -e  # Exit on error

echo "🚀 Setting up Gemini Multi-Agent Stock Debate System..."
echo ""

# Check if running in correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the gemini-debate directory"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "   ⚠️  Please edit .env and add your GEMINI_API_KEY"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Check for conda
if command -v conda &> /dev/null; then
    echo "🐍 Setting up conda environment..."
    
    # Check if environment already exists
    if conda env list | grep -q "gemini-debate"; then
        echo "   Environment 'gemini-debate' already exists"
        read -p "   Do you want to recreate it? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            conda env remove -n gemini-debate -y
            conda env create -f environment.yml -y
            echo "   ✅ Conda environment recreated"
        else
            echo "   ⏭️  Skipping environment creation"
        fi
    else
        conda env create -f environment.yml -y
        echo "   ✅ Conda environment created"
    fi
    
    echo ""
    echo "   To activate: conda activate gemini-debate"
    echo ""
else
    echo "📦 Installing dependencies with pip..."
    
    # Check if in virtual environment
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "   ⚠️  Not in a virtual environment. Creating one..."
        python3 -m venv venv
        source venv/bin/activate
        echo "   ✅ Virtual environment created and activated"
    fi
    
    pip install -r requirements.txt
    echo "   ✅ Dependencies installed"
    echo ""
fi

# Create necessary directories
echo "📁 Setting up directories..."
mkdir -p logs
mkdir -p utils examples
mkdir -p ../../data/finance
mkdir -p ../../data/news
echo "   ✅ Directories created"
echo ""

# Check data directories
echo "📊 Checking data availability..."
finance_count=$(ls -1 ../../data/finance/*.csv 2>/dev/null | wc -l)
news_count=$(ls -1 ../../data/news/*.csv 2>/dev/null | wc -l)

if [ "$finance_count" -eq 0 ]; then
    echo "   ⚠️  Finance data directory is empty"
    echo "      Please add CSV files to: ../../data/finance/"
else
    echo "   ✅ Found $finance_count finance data files"
fi

if [ "$news_count" -eq 0 ]; then
    echo "   ⚠️  News data directory is empty"
    echo "      Please add CSV files to: ../../data/news/"
else
    echo "   ✅ Found $news_count news data files"
fi
echo ""

# Clean up cache
echo "🧹 Cleaning up cache files..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "   ✅ Cache cleaned"
echo ""

echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Edit .env and add your GEMINI_API_KEY"
echo "   2. Add stock data to ../../data/finance/ and ../../data/news/"
echo "   3. Activate environment: conda activate gemini-debate"
echo "   4. Run the app: streamlit run app.py"
echo ""
echo "🧪 Or run tests:"
echo "   python examples/quick_test.py"
echo "   python examples/example_debate.py"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your GEMINI_API_KEY"
echo "  2. Add data files to ../../data/finance and ../../data/news"
echo "  3. Run the application:"
echo "     - Local: streamlit run app.py"
echo "     - Docker: docker-compose up"
echo ""
