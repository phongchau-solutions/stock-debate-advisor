# Stock Debate Advisor v8 - Architecture Design Document

**Version:** 8.0.0  
**Status:** Planning Phase  
**Date:** February 2026  
**Author:** Architecture Team

---

## Executive Summary

Version 8 represents a major evolution of the Stock Debate Advisor platform, introducing:
- **Firebase-First Architecture**: Leveraging Google Cloud Platform and Firebase ecosystem
- **Scheduled Data Pipelines**: Automated pipelines using Firebase Functions and Apache Airflow
- **Enhanced AI Orchestration**: Google ADK (AI Development Kit) for Gemini models
- **Event-Driven Architecture**: Real-time streaming with Firestore and Firebase Realtime Database
- **Advanced Analytics**: BigQuery for data warehouse and time-series analysis
- **Serverless Microservices**: Cloud Functions and Cloud Run for scalable services
- **Enterprise Features**: Firebase Authentication, Cloud IAM, audit logging, and compliance

### Technology Stack Shift: AWS → Firebase/GCP

| Component | v7 (AWS) | v8 (Firebase/GCP) |
|-----------|----------|-------------------|
| **Compute** | Lambda + ECS Fargate | Cloud Functions + Cloud Run |
| **Database** | DynamoDB | Firestore + Cloud SQL |
| **AI/ML** | AWS Bedrock (Claude) | Google ADK (Gemini) |
| **Auth** | Cognito | Firebase Authentication |
| **Storage** | S3 | Cloud Storage |
| **Data Pipeline** | Step Functions + EventBridge | Cloud Composer (Airflow) + Pub/Sub |
| **Analytics** | Timestream | BigQuery |
| **Caching** | ElastiCache | Firestore (native), Memorystore |
| **Real-time** | API Gateway WebSocket | Firebase Realtime Database |
| **CDN** | CloudFront | Firebase Hosting + Cloud CDN |
| **Monitoring** | CloudWatch | Cloud Logging + Cloud Monitoring |

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Component Architecture](#component-architecture)
4. [Data Pipeline Architecture](#data-pipeline-architecture)
5. [AI Orchestration Architecture](#ai-orchestration-architecture)
6. [Data Flow and Integration](#data-flow-and-integration)
7. [Security Architecture](#security-architecture)
8. [Scalability and Performance](#scalability-and-performance)
9. [Monitoring and Observability](#monitoring-and-observability)
10. [Disaster Recovery](#disaster-recovery)

---

## System Overview

### High-Level Architecture (Firebase/GCP)

```
┌────────────────────────────────────────────────────────────────┐
│              Firebase Hosting + Cloud CDN                       │
│            Global Edge Caching & Cloud Armor WAF                │
└────────────┬───────────────────────────────────┬───────────────┘
             │                                   │
             ↓                                   ↓
┌────────────────────────────┐    ┌─────────────────────────────┐
│   Web Application          │    │   Mobile/API Clients        │
│   (React SPA)              │    │   (REST/Firebase SDK)       │
└────────────┬───────────────┘    └──────────────┬──────────────┘
             │                                   │
             └───────────────┬───────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                     API Layer (Firebase)                         │
│   • Cloud Functions (HTTP triggers)                              │
│   • Cloud Run (containerized services)                           │
│   • Firebase Authentication (JWT tokens)                         │
│   • Cloud Endpoints (API management)                             │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ↓                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Microservices Layer                             │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  Debate Service│  │  Data Service  │  │  AI Service    │   │
│  │  (Cloud Run)   │  │  (Cloud Run)   │  │  (Cloud Run)   │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │ Analytics Svc  │  │  User Service  │  │ Notification   │   │
│  │ (Cloud Run)    │  │ (Cloud Func)   │  │ (Cloud Func)   │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
    ┌────────────────────────┴────────────────────────┐
    │                                                  │
    ↓                                                  ↓
┌─────────────────────────────┐      ┌───────────────────────────┐
│   Cloud Pub/Sub             │      │   Cloud Tasks             │
│   • Event bus               │      │   • Task distribution     │
│   • Service events          │      │   • Scheduled jobs        │
│   • System events           │      │   • Rate limiting         │
└────────────┬────────────────┘      └────────────┬──────────────┘
             │                                    │
             ↓                                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Data Pipeline Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Ingestion   │  │  Processing  │  │  Enrichment  │          │
│  │  Pipeline    │→ │  Pipeline    │→ │  Pipeline    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  Step Functions Orchestration + EventBridge Scheduler           │
└─────────────────────────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    AI Orchestration Layer                        │
│  ┌──────────────────────────────────────────────────┐           │
│  │  Model Router (Intelligent Selection)            │           │
│  │  • AWS Bedrock (Claude 3.5, Haiku, Opus)         │           │
│  │  • OpenAI GPT-4/GPT-3.5 (Fallback)               │           │
│  │  • Anthropic Direct (Optional)                   │           │
│  │  • Custom Models (SageMaker)                     │           │
│  └──────────────────────────────────────────────────┘           │
│  ┌──────────────────────────────────────────────────┐           │
│  │  Agent Framework                                  │           │
│  │  • Multi-agent coordination                      │           │
│  │  • Tool integration                              │           │
│  │  • Memory management                             │           │
│  │  • Context optimization                          │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  DynamoDB    │  │  RDS Aurora  │  │  S3 Data     │          │
│  │  (Hot Data)  │  │  (Relations) │  │  Lake        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  ElastiCache │  │  OpenSearch  │  │  Timestream  │          │
│  │  (Cache)     │  │  (Search)    │  │  (Time-series)│         │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────────────────┐
│              Monitoring & Observability Layer                    │
│  • CloudWatch (Logs, Metrics, Dashboards, Alarms)               │
│  • X-Ray (Distributed Tracing)                                   │
│  • OpenTelemetry (Custom Instrumentation)                        │
│  • Grafana (Visualization)                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Key Improvements from v7

| Feature | v7 | v8 |
|---------|----|----|
| **Data Ingestion** | Manual/On-demand | Scheduled pipelines (real-time & batch) |
| **AI Models** | Single (Claude 3.5) | Multi-model with intelligent routing |
| **Real-time Updates** | Polling | WebSocket + Server-Sent Events |
| **Data Storage** | DynamoDB only | Multi-tier (DynamoDB, RDS, S3, Timestream) |
| **Service Architecture** | Monolithic backend | Microservices with event-driven communication |
| **Analytics** | Basic | Advanced (time-series, ML predictions) |
| **Authentication** | Basic | Multi-tenant with SSO, MFA, RBAC |
| **Monitoring** | CloudWatch basic | Full observability stack |
| **Search** | None | OpenSearch with fuzzy matching |
| **Caching** | None | Multi-layer (CDN, Redis, Application) |

---

## Architecture Principles

### 1. Event-Driven Architecture
- Services communicate through events (EventBridge)
- Loose coupling between components
- Async processing for long-running operations
- Event sourcing for audit and replay capabilities

### 2. Microservices Design
- Domain-driven design (DDD)
- Single responsibility per service
- Independent deployment and scaling
- API-first development

### 3. Serverless-First
- Prefer managed services (Lambda, Fargate, Aurora Serverless)
- Auto-scaling by default
- Pay-per-use pricing model
- Minimal operational overhead

### 4. Data-Driven
- Comprehensive data pipelines
- Multiple data sources and formats
- Real-time and batch processing
- Data quality and validation

### 5. AI-Native
- Multiple AI models for different tasks
- Intelligent model selection
- Cost-optimized inference
- Context-aware prompting

### 6. Security by Design
- Zero-trust architecture
- Encryption at rest and in transit
- Least-privilege access (IAM)
- Comprehensive audit logging

### 7. Observable by Default
- Structured logging
- Distributed tracing
- Real-time metrics and dashboards
- Proactive alerting

---

## Component Architecture

### Frontend (React SPA)

**Technology Stack:**
- React 18+ with TypeScript
- Vite for build tooling
- TanStack Query (React Query) for data fetching
- Zustand for state management
- TailwindCSS + shadcn/ui for styling
- Recharts for data visualization
- WebSocket client for real-time updates

**Key Features:**
- Server-Side Rendering (SSR) support via Vite SSR
- Progressive Web App (PWA) capabilities
- Real-time debate updates via WebSocket
- Advanced charting and visualization
- Responsive design for mobile/tablet
- Offline-first with service workers

**Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── debate/        # Debate-specific components
│   │   ├── analytics/     # Charts and visualizations
│   │   ├── common/        # Reusable UI components
│   │   └── layout/        # Layout components
│   ├── features/
│   │   ├── auth/          # Authentication feature
│   │   ├── debates/       # Debates feature
│   │   ├── analytics/     # Analytics feature
│   │   └── settings/      # Settings feature
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API clients
│   ├── stores/            # State management
│   ├── types/             # TypeScript types
│   └── utils/             # Utility functions
├── public/                # Static assets
└── tests/                 # Test files
```

### Backend Services (Microservices)

#### 1. Debate Service
**Responsibility:** Manage debate lifecycle, orchestration, and results

**Technology:**
- Runtime: Python 3.12 (Lambda + ECS Fargate)
- Framework: FastAPI
- Database: DynamoDB + RDS Aurora
- Queue: SQS

**API Endpoints:**
- `POST /v1/debates` - Create new debate
- `GET /v1/debates/{id}` - Get debate details
- `GET /v1/debates/{id}/status` - Poll debate status
- `GET /v1/debates` - List debates (with filters)
- `DELETE /v1/debates/{id}` - Cancel debate
- `POST /v1/debates/{id}/retry` - Retry failed debate

#### 2. Data Service
**Responsibility:** Fetch, process, and serve stock market data

**Technology:**
- Runtime: Python 3.12 (Lambda + Fargate)
- Framework: FastAPI
- Database: DynamoDB, Timestream, S3
- Cache: ElastiCache (Redis)

**API Endpoints:**
- `GET /v1/stocks/{symbol}` - Get stock overview
- `GET /v1/stocks/{symbol}/financials` - Financial statements
- `GET /v1/stocks/{symbol}/prices` - Historical prices
- `GET /v1/stocks/{symbol}/news` - Recent news
- `GET /v1/stocks/{symbol}/sentiment` - Sentiment analysis
- `POST /v1/stocks/refresh` - Trigger data refresh

#### 3. AI Service
**Responsibility:** AI model orchestration, agent coordination

**Technology:**
- Runtime: Python 3.12 (ECS Fargate for long debates)
- Framework: LangChain + custom orchestration
- Models: Bedrock, OpenAI, custom
- Cache: Redis (conversation history)

**Capabilities:**
- Multi-agent debate coordination
- Intelligent model routing
- Context management and optimization
- Tool/function calling
- Streaming responses

#### 4. Analytics Service
**Responsibility:** Advanced analytics, predictions, pattern recognition

**Technology:**
- Runtime: Python 3.12 (Lambda + Fargate)
- Framework: FastAPI + Pandas + Scikit-learn
- Database: Timestream, S3, RDS
- ML: SageMaker (optional)

**API Endpoints:**
- `GET /v1/analytics/trends/{symbol}` - Trend analysis
- `GET /v1/analytics/predictions/{symbol}` - Price predictions
- `GET /v1/analytics/patterns/{symbol}` - Pattern recognition
- `GET /v1/analytics/comparisons` - Stock comparisons
- `GET /v1/analytics/portfolio` - Portfolio analysis

#### 5. User Service
**Responsibility:** User management, profiles, preferences

**Technology:**
- Runtime: Python 3.12 (Lambda)
- Framework: FastAPI
- Database: RDS Aurora (PostgreSQL)
- Auth: Cognito + custom

**API Endpoints:**
- `GET /v1/users/me` - Current user profile
- `PUT /v1/users/me` - Update profile
- `GET /v1/users/me/preferences` - User preferences
- `PUT /v1/users/me/preferences` - Update preferences
- `GET /v1/users/me/history` - Debate history
- `GET /v1/users/me/favorites` - Favorite stocks

#### 6. Notification Service
**Responsibility:** Multi-channel notifications (email, SMS, push, WebSocket)

**Technology:**
- Runtime: Python 3.12 (Lambda)
- Framework: FastAPI
- Queue: SQS
- Services: SNS, SES, WebSocket API

**Capabilities:**
- Real-time WebSocket notifications
- Email notifications (SES)
- SMS notifications (SNS)
- Push notifications (mobile)
- Notification preferences management

---

## Data Pipeline Architecture

### Pipeline Overview

```
┌───────────────────────────────────────────────────────────────┐
│                    Data Sources                                │
│  • Financial APIs (Alpha Vantage, Yahoo Finance, IEX)         │
│  • News APIs (NewsAPI, Finnhub)                               │
│  • Social Media (Twitter/X API, Reddit)                       │
│  • SEC EDGAR (Financial Filings)                              │
│  • Alternative Data (Sentiment, Web Scraping)                 │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 ↓
┌───────────────────────────────────────────────────────────────┐
│              Ingestion Layer (Lambda Functions)                │
│  • API Fetchers (rate-limited, authenticated)                 │
│  • Data Validators (schema validation)                        │
│  • Error Handlers (retry logic, DLQ)                          │
│  Triggers: EventBridge Scheduler (cron-based)                 │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 ↓
┌───────────────────────────────────────────────────────────────┐
│                Raw Data Storage (S3)                           │
│  Bucket: stock-data-raw-{env}                                 │
│  Structure: /source/year/month/day/data.json                  │
│  Lifecycle: Archive to Glacier after 90 days                  │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 ↓
┌───────────────────────────────────────────────────────────────┐
│         Processing Layer (Step Functions Workflow)             │
│  1. Data Cleaning                                             │
│     • Remove duplicates                                       │
│     • Handle missing values                                   │
│     • Normalize formats                                       │
│  2. Data Transformation                                       │
│     • Calculate technical indicators                          │
│     • Aggregate time-series                                   │
│     • Enrich with metadata                                    │
│  3. Data Validation                                           │
│     • Schema validation                                       │
│     • Business rule validation                                │
│     • Anomaly detection                                       │
│  4. Quality Scoring                                           │
│     • Completeness score                                      │
│     • Freshness score                                         │
│     • Accuracy score                                          │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 ↓
┌───────────────────────────────────────────────────────────────┐
│              Processed Data Storage                            │
│  • DynamoDB (Hot data, <90 days)                              │
│  • Timestream (Time-series data)                              │
│  • RDS Aurora (Relational data)                               │
│  • S3 (Processed data lake)                                   │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 ↓
┌───────────────────────────────────────────────────────────────┐
│               Serving Layer (APIs + Cache)                     │
│  • ElastiCache (Redis) - Hot cache                            │
│  • API Gateway - RESTful endpoints                            │
│  • GraphQL API - Flexible queries                             │
│  • WebSocket - Real-time streaming                            │
└───────────────────────────────────────────────────────────────┘
```

### Pipeline Schedules

| Pipeline | Frequency | Duration | Priority |
|----------|-----------|----------|----------|
| **Price Updates** | Every 1 minute (market hours) | ~10s | Critical |
| **Company Info** | Daily at 00:00 UTC | ~5 min | High |
| **Financial Reports** | Daily at 01:00 UTC | ~30 min | High |
| **News Ingestion** | Every 15 minutes | ~2 min | Medium |
| **Sentiment Analysis** | Hourly | ~10 min | Medium |
| **Social Media** | Every 30 minutes | ~5 min | Low |
| **SEC Filings** | Daily at 02:00 UTC | ~1 hour | Medium |
| **Data Quality Check** | Daily at 03:00 UTC | ~15 min | High |

---

## AI Orchestration Architecture

### Multi-Model Strategy

#### Model Configuration

| Model | Use Case | Cost | Latency | Max Context |
|-------|----------|------|---------|-------------|
| **Claude 3 Opus** | Complex debates, research | High | ~5s | 200K tokens |
| **Claude 3.5 Sonnet** | Standard debates | Medium | ~3s | 200K tokens |
| **Claude 3 Haiku** | Quick queries, summaries | Low | <1s | 200K tokens |
| **GPT-4** | Fallback, code analysis | High | ~4s | 128K tokens |
| **GPT-3.5 Turbo** | Basic tasks | Low | ~1s | 16K tokens |
| **Custom (SageMaker)** | Specialized tasks | Variable | Variable | Variable |

### Agent Architecture

```
┌────────────────────────────────────────────────────────────┐
│                  Agent Coordinator                          │
│  • Task decomposition                                       │
│  • Agent selection and scheduling                           │
│  • Context management                                       │
│  • Result aggregation                                       │
└────────────┬───────────────────────────────────────────────┘
             │
    ┌────────┴────────┬──────────────┬──────────────┐
    │                 │              │              │
    ↓                 ↓              ↓              ↓
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Analyst │    │Technical│    │Sentiment│    │  Judge  │
│  Agent  │    │  Agent  │    │  Agent  │    │  Agent  │
└────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
     │              │              │              │
     ↓              ↓              ↓              ↓
┌─────────────────────────────────────────────────────────┐
│                    Tool Registry                         │
│  • Data retrieval tools                                  │
│  • Calculation tools                                     │
│  • Search tools                                          │
│  • Validation tools                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Authentication & Authorization

**Multi-Tenant Architecture:**
```
User → Cognito User Pool → JWT Token
         ↓
    Custom Claims:
    - tenant_id
    - role (admin, analyst, viewer)
    - permissions []
         ↓
    API Gateway Authorizer
         ↓
    Service validates tenant_id + permissions
```

**Authorization Matrix:**

| Role | Create Debate | View Debates | Admin Panel | API Access |
|------|---------------|--------------|-------------|------------|
| **Viewer** | ❌ | Own only | ❌ | Read-only |
| **Analyst** | ✅ | Own + shared | ❌ | Full |
| **Admin** | ✅ | All | ✅ | Full |

---

## Monitoring and Observability

### Key Metrics

**Application Metrics:**
- Debates created/completed/failed (per hour)
- Average debate duration
- AI model usage by type
- API request rate (per endpoint)
- Error rate (per service)
- User active sessions

**Infrastructure Metrics:**
- Lambda invocations, duration, errors
- ECS task count, CPU, memory
- DynamoDB consumed capacity, throttles
- RDS connections, CPU, storage
- ElastiCache hit/miss rate
- SQS queue depth

---

## Cost Optimization

### Estimated Monthly Costs (Production)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **Lambda** | 10M requests, 5GB-sec avg | $50 |
| **ECS Fargate** | 5 tasks x 24/7, 2vCPU 8GB | $200 |
| **DynamoDB** | 10M reads, 1M writes | $25 |
| **RDS Aurora Serverless** | 2 ACU average | $90 |
| **ElastiCache** | 1x cache.r6g.large | $130 |
| **S3** | 1TB storage, 10M requests | $30 |
| **Timestream** | 100GB, 1M queries | $60 |
| **CloudFront** | 500GB transfer | $45 |
| **API Gateway** | 10M requests | $35 |
| **Bedrock** | 50M tokens | $150 |
| **CloudWatch** | Logs 100GB, metrics | $40 |
| **EventBridge** | 1M events | $1 |
| **Other** | SES, SNS, Route53, etc. | $20 |
| **Total** | | **~$876/month** |

---

**Document Version:** 1.0  
**Last Updated:** February 5, 2026  
**Status:** Draft - Under Review
