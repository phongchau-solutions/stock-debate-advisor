# Agentic Service

Multi-agent debate orchestration using Google Agent Development Kit (ADK).

## Features

- Google ADK integration for multi-agent orchestration
- 5 specialized agents (Fundamental, Technical, Sentiment, Moderator, Judge)
- Structured debate framework
- Session-based conversation management
- FastAPI REST API
- Streamlit demo UI

## Running

```bash
docker compose up agentic-service
```

## Demo UI

```bash
streamlit run demo_app.py
```

## Environment

See `.env.example` for required environment variables (include Gemini API key).
