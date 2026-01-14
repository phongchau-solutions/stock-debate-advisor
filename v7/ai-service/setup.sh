#!/bin/bash
# Setup script for CrewAI Stock Debate System

echo "🚀 Setting up CrewAI Stock Debate System..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Create or update conda environment
CONDA_ENV="chatbot_env"
echo "📦 Creating/updating conda environment: $CONDA_ENV..."

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Anaconda/Miniconda first."
    echo "   Visit: https://www.anaconda.com/download"
    exit 1
fi

# Create or update the conda environment with Python 3.11
conda env create -f <(echo "name: $CONDA_ENV
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip") --yes 2>/dev/null || conda env update -n $CONDA_ENV --file <(echo "name: $CONDA_ENV
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip") --yes

# Activate conda environment
echo "🔄 Activating conda environment: $CONDA_ENV..."
source activate $CONDA_ENV

# Install/upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY"
else
    echo "✅ .env file already exists"
fi

# Create data directory
mkdir -p data

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Make sure conda environment is activated:"
echo "   conda activate $CONDA_ENV"
echo "2. Edit .env and add your GEMINI_API_KEY"
echo "3. Add your stock data files to the data/ directory"
echo "4. Run: streamlit run app.py"
echo ""
