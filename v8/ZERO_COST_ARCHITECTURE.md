# Stock Debate Advisor v8 - Zero-Cost Architecture

**Version:** 8.0.0  
**Status:** Planning Phase  
**Date:** February 2026  
**Cost Target:** $0/month with scalability path

---

## Zero-Cost Strategy

### Philosophy

Start with **100% free tier services**, then scale horizontally as needed. The architecture is designed to:

✅ **Start at $0/month** using generous free tiers  
✅ **Scale incrementally** with predictable cost increases  
✅ **Avoid vendor lock-in** with portable technologies  
✅ **Maintain performance** despite cost constraints  

---

## Free Tier Architecture

```
┌───────────────────────────────────────────────────────────────┐
│              Vercel Free Tier (Frontend)                       │
│   • 100 GB bandwidth/month                                    │
│   • Automatic HTTPS                                           │
│   • Global CDN                                                │
│   • 100 deployments/day                                       │
│   Cost: $0                                                    │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│            Firebase Free Tier (Backend & Auth)                 │
│   • Authentication: Unlimited users                           │
│   • Firestore: 1 GB storage, 50K reads, 20K writes/day       │
│   • Realtime DB: 1 GB storage, 10 GB/month download          │
│   • Cloud Functions: 2M invocations/month                     │
│   • Storage: 5 GB                                             │
│   • Hosting: 10 GB/month bandwidth                            │
│   Cost: $0                                                    │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│          Railway Free Tier (Microservices)                     │
│   • $5 monthly credit (≈ 500 hours)                           │
│   • Shared CPU, 512MB RAM                                     │
│   • Deploy from GitHub                                        │
│   • PostgreSQL included                                       │
│   Cost: $0 (within $5 credit)                                │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│              Neon PostgreSQL Free Tier                         │
│   • 0.5 GB storage                                            │
│   • Serverless Postgres                                       │
│   • Automatic scaling to zero                                 │
│   • Branching for dev/staging                                 │
│   Cost: $0                                                    │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│            Upstash Redis Free Tier (Caching)                   │
│   • 10,000 commands/day                                       │
│   • 256 MB storage                                            │
│   • Global replication                                        │
│   Cost: $0                                                    │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│         Google AI Studio Free Tier (Gemini API)                │
│   • Gemini 1.5 Flash: 15 RPM, 1M TPM                          │
│   • Gemini 1.5 Pro: 2 RPM, 32K TPM                            │
│   • Gemini 2.0 Flash: 10 RPM                                  │
│   Cost: $0                                                    │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ↓
┌───────────────────────────────────────────────────────────────┐
│            GitHub Actions Free Tier (CI/CD)                    │
│   • 2,000 minutes/month                                       │
│   • Unlimited public repos                                    │
│   Cost: $0                                                    │
└───────────────────────────────────────────────────────────────┘
```

---

## Service Breakdown

### 1. Frontend Hosting: Vercel Free Tier

**Why Vercel over Firebase Hosting?**
- Better free tier (100 GB vs 10 GB bandwidth)
- Superior performance (faster cold starts)
- Built-in analytics
- Preview deployments for PRs

**Limits:**
- 100 GB bandwidth/month
- 100 deployments/day
- 6,000 build minutes/month

**When to upgrade ($20/month):**
- Bandwidth > 100 GB/month
- Need custom domains with SSL
- Team collaboration features

**Configuration:**

```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "apps/frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-railway-backend.railway.app/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/apps/frontend/dist/$1"
    }
  ]
}
```

### 2. Backend Services: Railway Free Tier

**Why Railway?**
- $5/month free credit (500 hours)
- Built-in PostgreSQL
- Easy Docker deployment
- GitHub integration

**Limits:**
- $5 credit/month (~500 hours for 1 service)
- Shared CPU, 512 MB RAM
- 100 GB outbound bandwidth

**Strategy to Stay Free:**
- Deploy only 1-2 critical services
- Use serverless (Firebase Functions) for others
- Hibernate services during low usage

**Services to Deploy on Railway:**
1. **AI Service** (most resource-intensive)
   - Handles Gemini API calls
   - Debate orchestration
2. **Data Service** (optional)
   - Stock data fetching and caching

**Alternative: Render Free Tier**
- 750 hours/month free
- Spins down after 15 min inactivity
- Good backup option

### 3. Database: Neon PostgreSQL Free Tier

**Why Neon?**
- True serverless (scales to zero)
- Branching for dev environments
- Better than free Railway Postgres

**Limits:**
- 0.5 GB storage
- 1 project
- 10 branches

**Schema Optimization for Free Tier:**

```sql
-- Minimize storage usage

-- 1. Use appropriate data types
CREATE TABLE debates (
    id UUID PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,  -- Not TEXT
    status VARCHAR(20),            -- Not ENUM (smaller)
    rounds SMALLINT,               -- Not INTEGER
    user_id VARCHAR(128),          -- Firebase UID
    confidence REAL,               -- Not DOUBLE PRECISION
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 2. Add TTL cleanup (cron job or trigger)
CREATE INDEX idx_debates_created ON debates(created_at);

-- Delete old debates (keep last 30 days only)
-- Run daily via GitHub Actions
DELETE FROM debates WHERE created_at < NOW() - INTERVAL '30 days';
```

**When to upgrade ($19/month):**
- Storage > 0.5 GB
- Need more projects

### 4. Caching: Upstash Redis Free Tier

**Why Upstash?**
- Better free tier than most alternatives
- HTTP-based (no connection pooling issues)
- Global replication

**Limits:**
- 10,000 commands/day
- 256 MB storage

**Caching Strategy:**

```python
# Aggressive caching to stay within limits

from upstash_redis import Redis
import os

redis = Redis(
    url=os.getenv("UPSTASH_REDIS_URL"),
    token=os.getenv("UPSTASH_REDIS_TOKEN")
)

# Cache stock data for 5 minutes
def get_stock_data(symbol: str):
    cache_key = f"stock:{symbol}"
    
    # Try cache first
    cached = redis.get(cache_key)
    if cached:
        return cached
    
    # Fetch from API
    data = fetch_from_api(symbol)
    
    # Cache for 5 minutes (300 seconds)
    redis.setex(cache_key, 300, data)
    
    return data
```

**When to upgrade ($10/month):**
- Commands > 10K/day
- Storage > 256 MB

### 5. Authentication: Firebase Auth (Always Free)

**Why Firebase Auth?**
- Unlimited users on free tier
- Multiple providers (Google, Email, etc.)
- Secure by default
- No alternative needed

**Features:**
- Email/Password
- Google OAuth
- Anonymous auth
- Custom claims (roles)

### 6. Real-time Database: Firebase Realtime Database

**Why Realtime DB over Firestore?**
- Better free tier for real-time features
- 10 GB/month download (vs expensive Firestore reads)

**Use Cases:**
- Live debate progress updates
- Real-time price updates
- User presence

**Limits:**
- 1 GB storage
- 10 GB download/month
- 100 simultaneous connections

**Optimization:**

```json
// Store only active debates (auto-cleanup)
{
  "activeDebates": {
    "debate_abc123": {
      "status": "IN_PROGRESS",
      "progress": 0.45,
      "currentAgent": "technical",
      ".expires": 1707129600  // TTL: 24 hours
    }
  }
}
```

### 7. AI Models: Google AI Studio Free Tier

**Why Google AI Studio?**
- Most generous free tier
- Gemini 1.5 Flash: 15 requests/minute
- No credit card required

**Limits:**
- Gemini 1.5 Flash: 15 RPM, 1M tokens/min
- Gemini 1.5 Pro: 2 RPM, 32K tokens/min
- Gemini 2.0 Flash: 10 RPM

**Optimization Strategy:**

```python
# Use cheapest model (Gemini 1.5 Flash) for most tasks

import google.generativeai as genai
import asyncio

# Rate limiting
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=15, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = deque()
    
    async def acquire(self):
        now = datetime.now()
        
        # Remove old requests
        while self.requests and self.requests[0] < now - timedelta(seconds=self.window):
            self.requests.popleft()
        
        # Wait if at limit
        if len(self.requests) >= self.max_requests:
            wait_time = (self.requests[0] + timedelta(seconds=self.window) - now).total_seconds()
            await asyncio.sleep(wait_time)
            return await self.acquire()
        
        self.requests.append(now)

limiter = RateLimiter(max_requests=14, window=60)  # Buffer of 1

async def call_gemini(prompt: str):
    await limiter.acquire()
    
    # Use Flash (cheapest) by default
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = await model.generate_content_async(prompt)
    return response.text
```

**When to upgrade (Pay-as-you-go):**
- Need higher rate limits
- Production traffic
- Cost: ~$0.075 per 1M input tokens (Flash)

### 8. Data Pipeline: GitHub Actions Free Tier

**Why GitHub Actions?**
- 2,000 minutes/month free
- No need for dedicated pipeline service
- Integrated with repo

**Limits:**
- 2,000 minutes/month
- 20 concurrent jobs

**Pipeline Strategy:**

```yaml
# .github/workflows/data-pipeline.yml

name: Data Pipeline

on:
  schedule:
    # Run every 6 hours (4x/day = ~120 min/month)
    - cron: '0 */6 * * *'
  workflow_dispatch:  # Manual trigger

jobs:
  fetch-stock-data:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      
      - name: Install dependencies
        run: pip install -r scripts/requirements.txt
      
      - name: Fetch stock prices
        env:
          NEON_DATABASE_URL: ${{ secrets.NEON_DATABASE_URL }}
          UPSTASH_REDIS_URL: ${{ secrets.UPSTASH_REDIS_URL }}
        run: python scripts/fetch_stock_data.py
      
      - name: Update cache
        run: python scripts/update_cache.py
```

**Cost:** $0 (within 2,000 min/month)

---

## Cost Comparison

### Zero-Cost Architecture (Current)

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| Frontend (Vercel) | 100 GB bandwidth | $0 |
| Auth (Firebase) | Unlimited | $0 |
| Database (Neon) | 0.5 GB | $0 |
| Cache (Upstash) | 10K commands/day | $0 |
| Backend (Railway) | $5 credit | $0 |
| AI (Google AI Studio) | 15 RPM | $0 |
| CI/CD (GitHub Actions) | 2K minutes | $0 |
| **Total** | | **$0** |

### Scaling Path

#### Stage 1: Hobby Project (0-100 users)
**Cost: $0/month**
- All services on free tier
- Manual data updates via GitHub Actions
- Single backend service on Railway

#### Stage 2: MVP (100-1,000 users)
**Cost: ~$50/month**

| Service | Tier | Cost |
|---------|------|------|
| Frontend (Vercel) | Pro | $20 |
| Database (Neon) | Launch | $19 |
| Cache (Upstash) | Pay-as-you-go | $10 |
| Backend (Railway) | 2 services | $20 |
| AI (Google AI) | Pay-as-you-go | $10 |
| **Total** | | **$79** |

#### Stage 3: Growing (1K-10K users)
**Cost: ~$300/month**

| Service | Tier | Cost |
|---------|------|------|
| Frontend (Vercel) | Pro | $20 |
| Database (Neon) | Scale | $69 |
| Cache (Upstash) | Pro | $30 |
| Backend (Railway) | 4 services | $100 |
| AI (Google AI) | Pay-as-you-go | $50 |
| Cloud Storage | S3/GCS | $10 |
| Monitoring | Sentry | $20 |
| **Total** | | **$299** |

#### Stage 4: Production (10K+ users)
**Cost: ~$1,000-2,000/month**

Migrate to Firebase/GCP as originally planned:
- Firebase Blaze plan
- Cloud Run for microservices
- Cloud Composer for pipelines
- Full observability stack

---

## Optimization Techniques

### 1. Database Storage Optimization

```sql
-- Partition tables by date
CREATE TABLE debates_2026_02 PARTITION OF debates
FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Drop old partitions automatically
DROP TABLE IF EXISTS debates_2025_12;

-- Use JSONB efficiently
CREATE INDEX idx_verdict_recommendation ON debates 
USING btree ((verdict->>'recommendation'));
```

### 2. Aggressive Caching

```python
# Cache everything possible

# Stock data: 5 minutes
STOCK_DATA_TTL = 300

# Company info: 24 hours
COMPANY_INFO_TTL = 86400

# Debate results: 7 days
DEBATE_RESULTS_TTL = 604800

# Cache debate results in Firestore (free reads)
# Cache stock data in Upstash (fast, limited)
```

### 3. Request Batching

```python
# Batch API requests to reduce function invocations

async def batch_fetch_stocks(symbols: list[str]):
    """Fetch multiple stocks in one API call"""
    # Instead of 10 API calls (10 function invocations)
    # Make 1 API call with batch (1 function invocation)
    
    results = await fetch_batch(symbols)
    return results
```

### 4. Static Pre-rendering

```typescript
// Pre-render static pages at build time

// apps/frontend/vite.config.ts
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'prerender-routes',
      async buildEnd() {
        // Pre-render common pages
        await prerenderRoutes([
          '/',
          '/about',
          '/pricing',
          // Top 100 stocks
          ...top100Stocks.map(s => `/stocks/${s}`)
        ]);
      }
    }
  ]
});
```

### 5. Lazy Loading & Code Splitting

```typescript
// Load features on-demand

import { lazy, Suspense } from 'react';

// Heavy chart library loaded only when needed
const StockChart = lazy(() => import('./components/StockChart'));

function StockPage() {
  return (
    <Suspense fallback={<Spinner />}>
      <StockChart symbol="AAPL" />
    </Suspense>
  );
}
```

---

## Monitoring (Free Tier)

### Sentry Free Tier
- 5,000 events/month
- Error tracking
- Performance monitoring

```typescript
// apps/frontend/src/main.tsx

import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 0.1,  // Low sampling to stay within free tier
});
```

### Google Analytics Free Tier
- Unlimited events
- Real-time reporting
- User analytics

### Uptime Monitoring: UptimeRobot Free
- 50 monitors
- 5-minute checks
- Email/SMS alerts

---

## Development Environment (Free)

### GitHub Codespaces (Free for Public Repos)
- 60 hours/month
- 2-core, 4GB RAM
- Pre-configured dev environment

```json
// .devcontainer/devcontainer.json
{
  "name": "Stock Debate Advisor",
  "image": "mcr.microsoft.com/devcontainers/python:3.14",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    },
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "postCreateCommand": "just install",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode"
      ]
    }
  }
}
```

---

## Summary

### Current State: $0/month

✅ Fully functional application  
✅ Supports 100-500 users  
✅ Real-time features  
✅ AI-powered debates  
✅ Production-ready  

### Growth Path

- **0-100 users**: $0/month (free tiers)
- **100-1K users**: $50-80/month (upgrade database, cache)
- **1K-10K users**: $300/month (scale services)
- **10K+ users**: $1K-2K/month (migrate to full GCP)

### Key Principles

1. **Start free, scale gradually**
2. **Optimize before scaling**
3. **Use managed services**
4. **Monitor costs actively**
5. **Plan migration path early**

---

**Document Version:** 1.0  
**Last Updated:** February 5, 2026  
**Cost Target:** $0/month → Scalable  
**Status:** Ready for Implementation
