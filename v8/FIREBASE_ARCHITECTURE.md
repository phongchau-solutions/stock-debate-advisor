# Stock Debate Advisor v8 - Firebase/GCP Architecture

**Version:** 8.0.0  
**Status:** Planning Phase  
**Date:** February 2026  
**Platform:** Firebase + Google Cloud Platform

---

## Executive Summary

Version 8 is built on Firebase and Google Cloud Platform, leveraging Google's AI capabilities and serverless infrastructure:

### Core Technologies

- **Frontend**: React 18 + Firebase Hosting
- **Backend**: Cloud Functions (Gen 2) + Cloud Run
- **AI Framework**: Google ADK (AI Development Kit) with Gemini models
- **Data Pipeline**: Cloud Composer (Apache Airflow) + Cloud Functions
- **Database**: Firestore + Cloud SQL (PostgreSQL)
- **Real-time**: Firebase Realtime Database
- **Analytics**: BigQuery
- **Authentication**: Firebase Authentication
- **Storage**: Cloud Storage
- **Caching**: Memorystore (Redis)
- **Monitoring**: Cloud Logging + Cloud Monitoring

---

## System Architecture

### Complete Architecture Diagram

```
┌───────────────────────────────────────────────────────────────┐
│            Firebase Hosting + Cloud CDN                        │
│            • Static asset hosting                              │
│            • Global CDN distribution                           │
│            • SSL/TLS termination                               │
│            • Cloud Armor (DDoS protection)                     │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│                  Frontend (React 18 SPA)                       │
│  • React 18 with TypeScript                                   │
│  • Vite build system                                          │
│  • Firebase SDK (Auth, Firestore, Realtime DB)               │
│  • TanStack Query for data fetching                           │
│  • Zustand for state management                               │
│  • shadcn/ui components                                       │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│              Firebase Authentication                           │
│  • Email/Password                                             │
│  • Google Sign-In                                             │
│  • OAuth 2.0 / SAML (enterprise)                              │
│  • Multi-factor authentication (MFA)                          │
│  • Custom claims (roles, permissions)                         │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│                    API Layer                                   │
│                                                                │
│  ┌─────────────────────────────────────────────────┐          │
│  │  Cloud Functions (Gen 2)                        │          │
│  │  • HTTP triggers (REST API)                     │          │
│  │  • Pub/Sub triggers (event-driven)              │          │
│  │  • Firestore triggers (reactive)                │          │
│  │  • Scheduled triggers (cron jobs)               │          │
│  │  Runtime: Node.js 20 / Python 3.12              │          │
│  └─────────────────────────────────────────────────┘          │
│                                                                │
│  ┌─────────────────────────────────────────────────┐          │
│  │  Cloud Run Services                             │          │
│  │  • Containerized microservices                  │          │
│  │  • Auto-scaling (0 to N instances)              │          │
│  │  • Long-running processes                       │          │
│  │  • WebSocket support                            │          │
│  └─────────────────────────────────────────────────┘          │
└────────────────────────┬──────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┐
           │                           │
           ↓                           ↓
┌────────────────────┐      ┌────────────────────┐
│  Cloud Pub/Sub     │      │  Cloud Tasks       │
│  • Event bus       │      │  • Task queues     │
│  • Async messaging │      │  • Rate limiting   │
│  • Fan-out         │      │  • Retries         │
└─────────┬──────────┘      └──────────┬─────────┘
          │                            │
          └────────────┬───────────────┘
                       │
                       ↓
┌───────────────────────────────────────────────────────────────┐
│                  Microservices (Cloud Run)                     │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Debate     │  │    Data      │  │     AI       │        │
│  │   Service    │  │   Service    │  │   Service    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Analytics   │  │    User      │  │ Notification │        │
│  │   Service    │  │   Service    │  │   Service    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│              Data Pipeline (Cloud Composer + Airflow)          │
│                                                                │
│  ┌─────────────────────────────────────────────────┐          │
│  │  Apache Airflow (Cloud Composer)                │          │
│  │  • DAG definitions (Python)                     │          │
│  │  • Workflow orchestration                       │          │
│  │  • Task scheduling                              │          │
│  │  • Monitoring & alerting                        │          │
│  └─────────────────────────────────────────────────┘          │
│                                                                │
│  Pipeline Stages:                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐                  │
│  │ Ingestion│ → │Processing│ → │Enrichment│                  │
│  │  (Cloud  │   │(Dataflow)│   │  (Cloud  │                  │
│  │Functions)│   │          │   │Functions)│                  │
│  └──────────┘   └──────────┘   └──────────┘                  │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│                AI Orchestration (Google ADK)                   │
│                                                                │
│  ┌─────────────────────────────────────────────────┐          │
│  │  Gemini Models (via Google ADK)                 │          │
│  │  • Gemini 2.0 Flash (fast, low-cost)            │          │
│  │  • Gemini 1.5 Pro (advanced reasoning)          │          │
│  │  • Gemini 1.5 Flash (balanced)                  │          │
│  │  • Context caching (cost optimization)          │          │
│  └─────────────────────────────────────────────────┘          │
│                                                                │
│  ┌─────────────────────────────────────────────────┐          │
│  │  Agent Framework (Google ADK)                   │          │
│  │  • Multi-agent orchestration                    │          │
│  │  • Function/Tool calling                        │          │
│  │  • Streaming responses                          │          │
│  │  • Code execution (optional)                    │          │
│  └─────────────────────────────────────────────────┘          │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                          │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Firestore   │  │  Cloud SQL   │  │   Cloud      │        │
│  │  (NoSQL)     │  │ (PostgreSQL) │  │  Storage     │        │
│  │  • Documents │  │  • Relations │  │  • Files     │        │
│  │  • Real-time │  │  • ACID      │  │  • Archives  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Memorystore  │  │   BigQuery   │  │  Realtime DB │        │
│  │   (Redis)    │  │  (Analytics) │  │ (Real-time)  │        │
│  │  • Cache     │  │  • Data WH   │  │  • Live data │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│                 Monitoring & Observability                     │
│  • Cloud Logging (centralized logs)                           │
│  • Cloud Monitoring (metrics, dashboards)                     │
│  • Cloud Trace (distributed tracing)                          │
│  • Error Reporting (automatic error tracking)                 │
│  • Cloud Profiler (performance profiling)                     │
└───────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend (React + Firebase)

**Hosting**: Firebase Hosting
- Automatic SSL/TLS certificates
- Global CDN distribution
- Custom domain support
- Preview channels for testing

**Technology Stack**:
```json
{
  "framework": "React 18",
  "language": "TypeScript 5",
  "build": "Vite 5",
  "firebase": {
    "auth": "firebase/auth",
    "firestore": "firebase/firestore",
    "realtimeDB": "firebase/database",
    "storage": "firebase/storage",
    "functions": "firebase/functions"
  },
  "state": "Zustand",
  "dataFetching": "TanStack Query",
  "ui": "shadcn/ui + Tailwind CSS",
  "charts": "Recharts"
}
```

**Key Features**:
- Real-time debate updates (Firestore onSnapshot)
- Live price updates (Realtime Database)
- Offline support (Firestore offline persistence)
- Progressive Web App (PWA)

### 2. Authentication (Firebase Auth)

**Providers**:
- Email/Password with email verification
- Google Sign-In (OAuth 2.0)
- GitHub (optional)
- SAML 2.0 for enterprise SSO

**Custom Claims**:
```typescript
interface UserClaims {
  role: 'admin' | 'analyst' | 'viewer';
  tenantId: string;
  permissions: string[];
}
```

**Security Rules**:
```javascript
// Firestore security rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /debates/{debateId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
                      request.auth.token.role in ['admin', 'analyst'];
    }
  }
}
```

### 3. Backend Services (Cloud Functions + Cloud Run)

#### Cloud Functions (Gen 2)

**Use Cases**:
- Simple HTTP endpoints (< 60 seconds)
- Event handlers (Firestore, Pub/Sub)
- Scheduled jobs (cron)

**Example Function**:
```typescript
// functions/src/debate-api.ts

import { onRequest } from 'firebase-functions/v2/https';
import { onDocumentCreated } from 'firebase-functions/v2/firestore';

export const createDebate = onRequest(
  { region: 'us-central1', memory: '512MiB' },
  async (req, res) => {
    const { symbol, rounds } = req.body;
    
    // Create debate document
    const debateRef = await admin.firestore()
      .collection('debates')
      .add({
        symbol,
        rounds,
        status: 'INITIATED',
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
        userId: req.auth?.uid
      });
    
    // Trigger AI processing via Pub/Sub
    await publishMessage('debate-processing', {
      debateId: debateRef.id,
      symbol,
      rounds
    });
    
    res.json({ debateId: debateRef.id });
  }
);

export const onDebateCreated = onDocumentCreated(
  'debates/{debateId}',
  async (event) => {
    // Send notification
    // Update analytics
  }
);
```

#### Cloud Run Services

**Use Cases**:
- Long-running debates (> 60 seconds)
- WebSocket connections
- Complex microservices

**Services**:
1. **debate-service** - Debate lifecycle management
2. **ai-service** - Google ADK integration, multi-agent debates
3. **data-service** - Stock data fetching and caching
4. **analytics-service** - Advanced analytics and predictions

**Example Dockerfile**:
```dockerfile
# services/ai-service/Dockerfile

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 4. Google ADK (AI Development Kit) Integration

**Installation**:
```bash
pip install google-genai
```

**Configuration**:
```python
# services/ai-service/src/adk_client.py

from google import genai
from google.genai import types

client = genai.Client(
    api_key=os.environ['GOOGLE_AI_API_KEY'],
    http_options={'api_version': 'v1alpha'}
)

# Multi-agent debate implementation
class DebateOrchestrator:
    def __init__(self):
        self.client = client
        
    async def run_debate(self, symbol: str, company_data: dict, rounds: int):
        """
        Orchestrate multi-agent debate using Google ADK
        """
        # Define agents
        fundamental_agent = {
            'name': 'fundamental_analyst',
            'model': 'gemini-1.5-pro',
            'system_instruction': '''
                You are a fundamental analyst specializing in stock analysis.
                Analyze the company's financials, business model, and competitive position.
                Provide BUY/HOLD/SELL recommendation with confidence level.
            ''',
            'tools': [
                self.calculate_pe_ratio,
                self.calculate_dcf_valuation,
                self.analyze_growth_trends
            ]
        }
        
        technical_agent = {
            'name': 'technical_analyst',
            'model': 'gemini-1.5-flash',
            'system_instruction': '''
                You are a technical analyst specializing in chart patterns and indicators.
                Analyze price trends, support/resistance levels, and technical indicators.
            ''',
            'tools': [
                self.calculate_rsi,
                self.identify_chart_patterns,
                self.analyze_volume
            ]
        }
        
        sentiment_agent = {
            'name': 'sentiment_analyst',
            'model': 'gemini-2.0-flash',
            'system_instruction': '''
                You are a sentiment analyst monitoring news and social media.
                Analyze market sentiment, news impact, and investor behavior.
            ''',
            'tools': [
                self.analyze_news_sentiment,
                self.get_social_media_buzz
            ]
        }
        
        judge_agent = {
            'name': 'judge',
            'model': 'gemini-1.5-pro',
            'system_instruction': '''
                You are an impartial judge evaluating investment arguments.
                Synthesize all perspectives and deliver final verdict.
            '''
        }
        
        # Run debate rounds
        debate_history = []
        
        for round_num in range(rounds):
            # Each agent provides analysis
            fundamental_view = await self.get_agent_response(
                fundamental_agent, 
                company_data, 
                debate_history
            )
            
            technical_view = await self.get_agent_response(
                technical_agent, 
                company_data, 
                debate_history
            )
            
            sentiment_view = await self.get_agent_response(
                sentiment_agent, 
                company_data, 
                debate_history
            )
            
            # Judge synthesizes
            round_summary = await self.get_agent_response(
                judge_agent,
                {
                    'fundamental': fundamental_view,
                    'technical': technical_view,
                    'sentiment': sentiment_view
                },
                debate_history
            )
            
            debate_history.append({
                'round': round_num + 1,
                'fundamental': fundamental_view,
                'technical': technical_view,
                'sentiment': sentiment_view,
                'summary': round_summary
            })
        
        # Final verdict
        verdict = await self.get_final_verdict(judge_agent, debate_history)
        
        return {
            'debate_history': debate_history,
            'verdict': verdict
        }
    
    async def get_agent_response(self, agent, data, history):
        """
        Get response from agent using Google ADK
        """
        # Use context caching for cost optimization
        cache_config = types.CachedContentCreateConfig(
            model=agent['model'],
            system_instruction=agent['system_instruction'],
            contents=[self.format_company_data(data)]
        )
        
        response = await self.client.aio.models.generate_content(
            model=agent['model'],
            contents=self.format_prompt(agent, data, history),
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
                tools=agent.get('tools', [])
            )
        )
        
        return response.text
```

### 5. Data Pipeline (Cloud Composer + Airflow)

**Cloud Composer Setup**:
```bash
# Create Composer environment
gcloud composer environments create stock-data-pipeline \
    --location us-central1 \
    --python-version 3 \
    --machine-type n1-standard-2 \
    --disk-size 30
```

**Airflow DAG Example**:
```python
# dags/price_data_pipeline.py

from airflow import DAG
from airflow.providers.google.cloud.operators.functions import CloudFunctionsInvokeFunctionOperator
from airflow.providers.google.cloud.operators.dataflow import DataflowCreatePythonJobOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'price_data_pipeline',
    default_args=default_args,
    description='Fetch and process real-time stock prices',
    schedule_interval='*/1 * * * *',  # Every minute
    start_date=days_ago(1),
    catchup=False,
    tags=['stock-data', 'real-time'],
)

# Task 1: Fetch prices from API
fetch_prices = CloudFunctionsInvokeFunctionOperator(
    task_id='fetch_prices',
    function_name='price-ingestion',
    location='us-central1',
    input_data={'symbols': ['AAPL', 'GOOGL', 'MSFT', 'AMZN']},
    dag=dag,
)

# Task 2: Process with Dataflow
process_prices = DataflowCreatePythonJobOperator(
    task_id='process_prices',
    py_file='gs://stock-data-pipeline/dataflow/process_prices.py',
    job_name='process-prices-{{ ds_nodash }}',
    options={
        'project': 'your-project-id',
        'region': 'us-central1',
        'temp_location': 'gs://stock-data-pipeline/temp',
    },
    dag=dag,
)

# Task 3: Store to BigQuery
store_to_bigquery = CloudFunctionsInvokeFunctionOperator(
    task_id='store_to_bigquery',
    function_name='bigquery-writer',
    location='us-central1',
    dag=dag,
)

# Task 4: Invalidate cache
invalidate_cache = CloudFunctionsInvokeFunctionOperator(
    task_id='invalidate_cache',
    function_name='cache-invalidator',
    location='us-central1',
    dag=dag,
)

# Define task dependencies
fetch_prices >> process_prices >> [store_to_bigquery, invalidate_cache]
```

### 6. Data Storage

#### Firestore (Primary NoSQL Database)

**Collections**:
```
/debates/{debateId}
  - symbol: string
  - status: string
  - rounds: number
  - createdAt: timestamp
  - userId: string
  - verdict: map (optional)

/users/{userId}
  - email: string
  - displayName: string
  - role: string
  - preferences: map

/companies/{symbol}
  - name: string
  - sector: string
  - marketCap: number
  - lastUpdated: timestamp

/prices/{symbol}/historical/{date}
  - open: number
  - high: number
  - low: number
  - close: number
  - volume: number
```

#### Cloud SQL (PostgreSQL)

**Use Cases**:
- Complex joins
- Financial reports (normalized)
- User analytics
- Transactional data

**Schema**:
```sql
CREATE TABLE financial_reports (
    id UUID PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    report_type VARCHAR(20) NOT NULL,
    revenue DECIMAL(20, 2),
    net_income DECIMAL(20, 2),
    eps DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, report_date, report_type)
);

CREATE INDEX idx_financial_symbol_date ON financial_reports(symbol, report_date DESC);
```

#### BigQuery (Analytics & Data Warehouse)

**Tables**:
- `stock_prices` - Historical OHLCV data
- `debate_events` - All debate events (event sourcing)
- `user_activity` - User behavior analytics
- `market_sentiment` - Aggregated sentiment data

**Example Query**:
```sql
-- Analyze debate outcomes by symbol
SELECT 
    symbol,
    verdict.recommendation,
    AVG(verdict.confidence) as avg_confidence,
    COUNT(*) as debate_count
FROM `project.dataset.debates`
WHERE status = 'COMPLETED'
    AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY symbol, verdict.recommendation
ORDER BY debate_count DESC
LIMIT 20;
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + TypeScript + Vite | UI framework |
| **Hosting** | Firebase Hosting + Cloud CDN | Static hosting |
| **Auth** | Firebase Authentication | User management |
| **API** | Cloud Functions Gen 2 + Cloud Run | Serverless backend |
| **AI** | Google ADK (Gemini models) | AI orchestration |
| **Data Pipeline** | Cloud Composer (Airflow) | ETL orchestration |
| **NoSQL DB** | Firestore | Primary database |
| **SQL DB** | Cloud SQL (PostgreSQL) | Relational data |
| **Real-time** | Firebase Realtime Database | Live updates |
| **Cache** | Memorystore (Redis) | In-memory cache |
| **Analytics** | BigQuery | Data warehouse |
| **Storage** | Cloud Storage | File storage |
| **Messaging** | Cloud Pub/Sub | Event bus |
| **Tasks** | Cloud Tasks | Task queues |
| **Monitoring** | Cloud Logging + Monitoring | Observability |
| **IaC** | Terraform | Infrastructure |

---

## Cost Estimation (Monthly)

### Firebase Services

| Service | Usage | Cost |
|---------|-------|------|
| **Firebase Hosting** | 10GB storage, 50GB transfer | $0.65 |
| **Firestore** | 10M reads, 1M writes | $1.88 |
| **Realtime Database** | 10GB storage, 100GB download | $10 |
| **Firebase Auth** | 10K MAU | Free |
| **Firebase Functions** | 2M invocations (1GB-sec) | $0.74 |
| **Total Firebase** | | **~$13.27** |

### Google Cloud Services

| Service | Usage | Cost |
|---------|-------|------|
| **Cloud Functions** | 5M invocations, 512MB avg | $25 |
| **Cloud Run** | 5 services, 24/7 | $180 |
| **Cloud Composer** | 1 environment (small) | $300 |
| **Cloud SQL** | db-n1-standard-2 | $140 |
| **Memorystore** | 1GB Redis | $45 |
| **BigQuery** | 1TB queries, 100GB storage | $55 |
| **Cloud Storage** | 1TB storage, 100GB egress | $38 |
| **Pub/Sub** | 1M messages | $0.40 |
| **Gemini API** | 50M tokens | $175 |
| **Total GCP** | | **~$958.40** |

### **Grand Total: ~$972/month**

### Cost Optimization

- Use Gemini 2.0 Flash for simple queries (10x cheaper)
- Enable BigQuery BI Engine for caching
- Use Cloud Storage coldline for archives
- Optimize Cloud Composer to n1-standard-1
- Use Firestore offline persistence (reduce reads)

**Optimized Total: ~$650/month**

---

**Document Version:** 1.0  
**Last Updated:** February 5, 2026  
**Platform:** Firebase + Google Cloud Platform  
**Status:** Ready for Implementation
