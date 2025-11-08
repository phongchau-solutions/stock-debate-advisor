# Agentic Financial Reasoning Suite — Gemini x Autogen Starter

This repository contains a minimal, production-oriented starter for a multi-agent financial reasoning system using Gemini (reasoning LLM) and Microsoft Autogen (orchestration).

Structure (minimal):

- `agents/` — agent implementations and base classes
- `integrations/` — Gemini and Autogen client wrappers
- `orchestrator/` — run_autogen.py wiring agents into deterministic flows
- `infra/` — infra manifests (docker-compose), Airflow DAG skeleton, observability init
- `pyproject.toml` / `requirements.txt` — dependencies

What this starter provides:

- Deterministic agent base class with pydantic output schemas and provenance metadata
- Stubs for Crawler, Parser, Analyzer, Debate, Aggregator, Chat agents
- Gemini client wrapper that enforces function-calling pattern and citation rules, with a confidence-based fallback hook
- Autogen orchestration skeleton showing deterministic channels
- Observability hooks (OpenTelemetry + Prometheus metrics) and security notes (Vault stub)
- Airflow DAG skeleton for ingestion

How to use (quick):

### Option A: Using Miniconda (recommended)

1. Install dependencies using conda:

```bash
# Make setup script executable
chmod +x setup_env.sh

# Create and setup conda environment
./setup_env.sh

# Activate the environment
conda activate agentic-financial
```

### Option B: Using pip/venv

1. Install dependencies (in venv):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Next steps

2. Read and configure `infra/config.yaml` for service endpoints and API keys.

3. Extend the agent process() methods to connect to real crawlers, parsers, and embeddings.

4. Run `orchestrator/run_autogen.py` as a local dry-run to test deterministic wiring (it is a scaffold — requires Autogen/Gemini credentials).

Notes and next steps:

- Replace placeholder SDK/package names with your project's actual client libs if needed.
- Wire secrets to Vault or environment variables; do not hardcode keys.
- Implement proper error handling and retries on network calls.
