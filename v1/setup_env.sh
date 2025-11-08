#!/usr/bin/env bash
# Setup script for creating and activating the Miniconda environment

set -e

echo "===== Agentic Financial Suite - Environment Setup ====="
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: conda is not installed or not in PATH"
    echo "Please install Miniconda or Anaconda from:"
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✓ Found conda: $(conda --version)"
echo ""

# Create conda environment from environment.yml
echo "Creating conda environment 'agentic-financial' from environment.yml..."
conda env create -f environment.yml

echo ""
echo "===== Setup Complete ====="
echo ""
echo "To activate the environment, run:"
echo "  conda activate agentic-financial"
echo ""
echo "Then you can run the orchestrator demo:"
echo "  python orchestrator/run_autogen.py"
echo ""
