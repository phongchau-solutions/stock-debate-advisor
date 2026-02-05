# Stock Debate Advisor v8 - Data Pipeline Specification

**Version:** 8.0.0  
**Status:** Planning Phase  
**Date:** February 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Data Sources](#data-sources)
3. [Pipeline Architecture](#pipeline-architecture)
4. [Pipeline Implementation](#pipeline-implementation)
5. [Data Quality Framework](#data-quality-framework)
6. [Monitoring and Alerting](#monitoring-and-alerting)
7. [Cost Optimization](#cost-optimization)

---

## Overview

### Purpose

The data pipeline system is responsible for:
- **Ingestion**: Fetching data from external sources
- **Processing**: Cleaning, transforming, and enriching data
- **Storage**: Persisting processed data across multiple storage tiers
- **Serving**: Making data available via APIs with low latency

### Requirements

**Functional:**
- Real-time price updates (1-minute intervals during market hours)
- Daily financial statement updates
- Continuous news and sentiment monitoring
- Historical data backfilling
- Data quality validation

**Non-Functional:**
- **Reliability**: 99.9% pipeline success rate
- **Latency**: Data available within 1 minute of ingestion
- **Scalability**: Handle 10,000+ symbols
- **Cost**: < $200/month for data ingestion
- **Compliance**: Respect API rate limits, terms of service

---

## Data Sources

### Primary Data Sources

#### 1. Stock Prices (Real-time OHLCV)

**Provider: Alpha Vantage**
- **API**: https://www.alphavantage.co/
- **Endpoint**: `TIME_SERIES_INTRADAY`
- **Rate Limit**: 5 API requests per minute (free tier) / 75 per minute (premium)
- **Cost**: $49.99/month (premium)
- **Data Format**: JSON
- **Update Frequency**: Every 1 minute (market hours)

**Alternative: IEX Cloud**
- **API**: https://iexcloud.io/
- **Rate Limit**: 50,000 messages/month (free) / unlimited (paid)
- **Cost**: $9/month (starter) to $499/month (business)

**Alternative: Yahoo Finance (yfinance)**
- **API**: Unofficial API via Python library
- **Rate Limit**: Unspecified (soft limits exist)
- **Cost**: Free
- **Reliability**: Lower (unofficial API)

**Recommended**: Alpha Vantage (premium) for production, yfinance for dev/testing

#### 2. Company Information

**Provider: Financial Modeling Prep**
- **API**: https://financialmodelingprep.com/
- **Endpoints**: 
  - `profile` - Company overview
  - `company-outlook` - Full company details
- **Rate Limit**: 250 API calls/day (free) / 300 calls/minute (paid)
- **Cost**: $29/month (starter)
- **Update Frequency**: Daily

**Alternative: SEC EDGAR**
- **API**: https://www.sec.gov/
- **Cost**: Free
- **Format**: XML/JSON
- **Update Frequency**: Real-time for filings

#### 3. Financial Statements

**Provider: Financial Modeling Prep**
- **Endpoints**:
  - `income-statement` - Quarterly and annual income statements
  - `balance-sheet-statement` - Balance sheets
  - `cash-flow-statement` - Cash flow statements
  - `key-metrics` - Key financial ratios
- **Rate Limit**: 300 calls/minute (paid tier)
- **Update Frequency**: Daily (after market close)

**Alternative: Alpha Vantage**
- **Endpoints**: `INCOME_STATEMENT`, `BALANCE_SHEET`, `CASH_FLOW`
- **Included in**: Premium subscription

#### 4. News Articles

**Provider: NewsAPI.org**
- **API**: https://newsapi.org/
- **Endpoints**: `everything` with stock symbol query
- **Rate Limit**: 100 requests/day (free) / 1000 req/day (developer)
- **Cost**: $449/month (developer tier)
- **Update Frequency**: Every 15 minutes

**Alternative: Finnhub**
- **API**: https://finnhub.io/
- **Endpoint**: `news`
- **Rate Limit**: 60 API calls/minute (free)
- **Cost**: $99/month (starter)

**Recommended**: Finnhub for better cost/value ratio

#### 5. Social Media Sentiment

**Provider: Reddit API**
- **API**: https://www.reddit.com/dev/api/
- **Subreddits**: r/wallstreetbets, r/stocks, r/investing
- **Rate Limit**: 60 requests per minute
- **Cost**: Free
- **Update Frequency**: Every 30 minutes

**Provider: Twitter/X API (Optional)**
- **API**: https://developer.twitter.com/
- **Rate Limit**: Complex tiering
- **Cost**: $100+/month (Basic tier)
- **Status**: Consider in future phase

#### 6. Alternative Data (Future)

- **Insider Trading**: SEC Form 4 filings
- **Options Flow**: Unusual options activity
- **Analyst Ratings**: Aggregated ratings from investment banks
- **Economic Indicators**: Fed data, inflation, unemployment

---

## Pipeline Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Ingestion Layer                           │
│  • Cloud Functions per data source                          │
│  • Rate limiting & retry logic                              │
│  • Raw data validation                                      │
│  • Cloud Storage raw data storage                           │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓ Cloud Storage Notification → Pub/Sub
┌─────────────────────────────────────────────────────────────┐
│                   Processing Layer                           │
│  • Cloud Composer (Airflow) workflow orchestration          │
│  • Data cleaning & normalization                            │
│  • Technical indicator calculation                          │
│  • Data enrichment                                          │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│  • Firestore (hot data, <90 days)                           │
│  • BigQuery (time-series & analytics)                       │
│  • Cloud SQL (relational data)                              │
│  • Cloud Storage (processed data lake)                      │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓ Firestore Triggers / Pub/Sub
┌─────────────────────────────────────────────────────────────┐
│                   Serving Layer                              │
│  • Firestore (real-time subscriptions)                      │
│  • Cloud Endpoints / API Gateway - RESTful endpoints        │
│  • Pub/Sub - data update events                             │
│  • Memorystore (Redis) - optional hot cache                 │
└─────────────────────────────────────────────────────────────┘
```

### Event-Driven Flow

```
Cloud Scheduler → Pub/Sub → Cloud Function (Ingestion) → Cloud Storage (Raw)
                                                                 │
                                                                 ↓
                                                    Cloud Composer DAG (Process)
                                                                 │
                                                                 ↓
                                                       Multi-Store Write
                                                       ┌────────┴─────────┐
                                                       │                  │
                                                       ↓                  ↓
                                                  Firestore            BigQuery
                                                       │                  │
                                                       ↓                  ↓
                                              Firestore Trigger      Pub/Sub Event
                                                       │                  │
                                                       ↓                  ↓
                                             Cache Invalidation    Notification
```

---

## Pipeline Implementation

### Pipeline 1: Real-time Price Data

**Schedule:** Every 1 minute (market hours: 9:30 AM - 4:00 PM ET, Mon-Fri)

**Cloud Scheduler Job:**
```bash
gcloud scheduler jobs create pubsub price-data-ingestion \
  --schedule="* * * * *" \
  --topic=price-data-trigger \
  --message-body='{"symbols": ["AAPL", "GOOGL", "MSFT"]}' \
  --time-zone="America/New_York"
```

**Cloud Function: `price-ingestion`**

```python
# data-pipelines/ingestion/price-fetcher/main.py

import os
import json
import requests
from datetime import datetime
from google.cloud import storage
from google.cloud import pubsub_v1
import functions_framework

storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()

alpha_vantage_key = os.environ['ALPHA_VANTAGE_API_KEY']
bucket_name = os.environ['RAW_DATA_BUCKET']
project_id = os.environ['GCP_PROJECT']

@functions_framework.cloud_event
def price_ingestion(cloud_event):
    """
    Fetch real-time price data for given symbols
    Triggered by Pub/Sub message from Cloud Scheduler
    """
    # Decode Pub/Sub message
    import base64
    message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode()
    event_data = json.loads(message_data)
    
    symbols = event_data.get('symbols', [])
    results = []
    bucket = storage_client.bucket(bucket_name)
    
    for symbol in symbols:
        try:
            # Fetch from Alpha Vantage
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': '1min',
                'apikey': alpha_vantage_key,
                'outputsize': 'compact'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Validate response
            if 'Time Series (1min)' not in data:
                raise ValueError(f"Invalid response for {symbol}")
            
            # Save to Cloud Storage raw bucket
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            blob_name = f"prices/raw/{symbol}/{timestamp}.json"
            blob = bucket.blob(blob_name)
            
            blob.metadata = {
                'symbol': symbol,
                'source': 'alphavantage',
                'timestamp': timestamp
            }
            blob.upload_from_string(
                json.dumps(data),
                content_type='application/json'
            )
            
            # Publish to Pub/Sub for processing
            topic_path = publisher.topic_path(project_id, 'price-data-ready')
            message_data = json.dumps({
                'bucket': bucket_name,
                'blob': blob_name,
                'symbol': symbol
            })
            publisher.publish(topic_path, message_data.encode('utf-8'))
            
            results.append({
                'symbol': symbol,
                'status': 'success',
                'blob': blob_name
            })
            
        except Exception as e:
            # Security fix: Don't log full exception which may contain API keys
            error_type = e.__class__.__name__
            print(f"Error fetching {symbol}: {error_type}")
            results.append({
                'symbol': symbol,
                'status': 'error',
                'error': f"{error_type} while fetching data"
            })
    
    return {
        'processed': len(results),
        'results': results
    }
```

**Cloud Composer DAG: `price_processing_workflow`**

```python
# dags/price_processing_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.functions import CloudFunctionInvokeFunctionOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.sensors.pubsub import PubSubPullSensor
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'price_processing_workflow',
    default_args=default_args,
    description='Process raw price data and store in Firestore and BigQuery',
    schedule_interval=None,  # Triggered by Pub/Sub
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['stock-data', 'prices'],
) as dag:

    # Step 1: Process price data (clean and normalize)
    process_price_data = CloudFunctionInvokeFunctionOperator(
        task_id='process_price_data',
        function_id='price-processor',
        input_data='{{ dag_run.conf }}',
        location='us-central1',
    )

    # Step 2: Calculate technical indicators
    calculate_indicators = CloudFunctionInvokeFunctionOperator(
        task_id='calculate_technical_indicators',
        function_id='technical-indicator-calculator',
        input_data='{{ task_instance.xcom_pull(task_ids="process_price_data") }}',
        location='us-central1',
    )

    # Step 3: Store to Firestore (hot data)
    store_to_firestore = CloudFunctionInvokeFunctionOperator(
        task_id='store_to_firestore',
        function_id='firestore-writer',
        input_data='{{ task_instance.xcom_pull(task_ids="calculate_technical_indicators") }}',
        location='us-central1',
    )

    # Step 4: Store to BigQuery (time-series analytics)
    store_to_bigquery = CloudFunctionInvokeFunctionOperator(
        task_id='store_to_bigquery',
        function_id='bigquery-writer',
        input_data='{{ task_instance.xcom_pull(task_ids="calculate_technical_indicators") }}',
        location='us-central1',
    )

    # Step 5: Publish completion event
    def publish_completion_event(**context):
        from google.cloud import pubsub_v1
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path('your-project-id', 'price-data-updated')
        
        data = context['task_instance'].xcom_pull(task_ids='calculate_technical_indicators')
        message = json.dumps({
            'source': 'price-processing-pipeline',
            'type': 'PriceDataUpdated',
            'data': data
        })
        publisher.publish(topic_path, message.encode('utf-8'))
    
    publish_event = PythonOperator(
        task_id='publish_event',
        python_callable=publish_completion_event,
    )

    # Define task dependencies
    process_price_data >> calculate_indicators >> [store_to_firestore, store_to_bigquery] >> publish_event
```

**Cloud Function: `price-processor`**

```python
# data-pipelines/processing/price-processor/main.py

import json
from google.cloud import storage
import functions_framework

storage_client = storage.Client()

@functions_framework.http
def price_processor(request):
    """
    Clean and normalize price data
    """
    request_json = request.get_json()
    bucket_name = request_json['bucket']
    blob_name = request_json['blob']
    
    # Read raw data from Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    raw_data = json.loads(blob.download_as_text())
    
    # Extract metadata
    symbol = blob.metadata.get('symbol')
    
    # Parse time series data
    time_series = raw_data.get('Time Series (1min)', {})
    
    processed_data = []
    for timestamp, values in time_series.items():
        processed_data.append({
            'symbol': symbol,
            'timestamp': timestamp,
            'open': float(values['1. open']),
            'high': float(values['2. high']),
            'low': float(values['3. low']),
            'close': float(values['4. close']),
            'volume': int(values['5. volume'])
        })
    
    # Sort by timestamp (most recent first)
    processed_data.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return {
        'symbol': symbol,
        'data': processed_data[:60],  # Keep last 60 minutes
        'count': len(processed_data)
    }
```

**Cloud Function: `technical-indicator-calculator`**

```python
# data-pipelines/processing/technical-indicators/main.py

import pandas as pd
import numpy as np
import functions_framework

@functions_framework.http
def technical_indicator_calculator(request):
    """
    Calculate technical indicators (RSI, MACD, Bollinger Bands, etc.)
    """
    request_json = request.get_json()
    symbol = request_json['symbol']
    data = request_json['data']
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Calculate indicators
    
    # 1. RSI (Relative Strength Index)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 2. MACD (Moving Average Convergence Divergence)
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # 3. Bollinger Bands
    df['sma20'] = df['close'].rolling(window=20).mean()
    df['std20'] = df['close'].rolling(window=20).std()
    df['bollinger_upper'] = df['sma20'] + (2 * df['std20'])
    df['bollinger_lower'] = df['sma20'] - (2 * df['std20'])
    
    # 4. Moving Averages
    df['sma50'] = df['close'].rolling(window=50).mean()
    df['sma200'] = df['close'].rolling(window=200).mean()
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    
    # Convert back to list of dicts
    enriched_data = df.to_dict('records')
    
    return {
        'symbol': symbol,
        'data': enriched_data,
        'indicators_calculated': ['rsi', 'macd', 'bollinger', 'moving_averages']
    }
```

### Pipeline 2: Company Information

**Schedule:** Daily at 00:00 UTC

**Cloud Scheduler Job:**
```bash
gcloud scheduler jobs create pubsub company-info-ingestion \
  --schedule="0 0 * * *" \
  --topic=company-info-trigger \
  --time-zone="UTC"
```

**Implementation:** Similar to price pipeline with different data source

### Pipeline 3: Financial Reports

**Schedule:** Daily at 01:00 UTC (after market close)

**Implementation:** Fetch quarterly and annual financial statements

### Pipeline 4: News Ingestion

**Schedule:** Every 15 minutes

**Implementation:**
- Fetch latest news articles for tracked symbols
- Perform sentiment analysis using Cloud Natural Language API
- Store results in Firestore with TTL (30 days)

### Pipeline 5: Sentiment Analysis

**Schedule:** Hourly

**Data Sources:**
- Reddit (r/wallstreetbets, r/stocks)
- News headlines (from Pipeline 4)

**Implementation:**
```python
# sentiment-analyzer/main.py

from google.cloud import language_v1
import functions_framework

language_client = language_v1.LanguageServiceClient()

@functions_framework.http
def analyze_sentiment(request):
    """
    Analyze sentiment using Cloud Natural Language API
    """
    request_json = request.get_json()
    text = request_json.get('text', '')
    
    # Prepare the document
    document = language_v1.Document(
        content=text[:10000],  # Max 10KB for sentiment analysis
        type_=language_v1.Document.Type.PLAIN_TEXT
    )
    
    # Detect sentiment
    sentiment = language_client.analyze_sentiment(
        request={'document': document}
    ).document_sentiment
    
    # Classify sentiment category
    score = sentiment.score
    if score > 0.25:
        category = 'POSITIVE'
    elif score < -0.25:
        category = 'NEGATIVE'
    else:
        category = 'NEUTRAL'
    
    return {
        'sentiment': category,
        'score': score,
        'magnitude': sentiment.magnitude
    }
```

---

## Data Quality Framework

### Data Quality Dimensions

#### 1. Completeness
**Definition:** Percentage of non-null values

**Rule:**
```python
def check_completeness(data):
    required_fields = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
    
    for record in data:
        for field in required_fields:
            if record.get(field) is None:
                return False, f"Missing required field: {field}"
    
    return True, "Complete"
```

#### 2. Accuracy
**Definition:** Data within expected ranges

**Rules:**
- Price values > 0
- High >= Low
- Open, Close between Low and High
- Volume >= 0
- Timestamp within last 24 hours

```python
def check_accuracy(record):
    # Price validations
    if record['open'] <= 0 or record['close'] <= 0:
        return False, "Price must be positive"
    
    if record['high'] < record['low']:
        return False, "High price cannot be lower than low price"
    
    if not (record['low'] <= record['open'] <= record['high']):
        return False, "Open price must be between low and high"
    
    if not (record['low'] <= record['close'] <= record['high']):
        return False, "Close price must be between low and high"
    
    if record['volume'] < 0:
        return False, "Volume cannot be negative"
    
    return True, "Accurate"
```

#### 3. Timeliness
**Definition:** Data freshness

**Rule:**
```python
from datetime import datetime, timedelta

def check_timeliness(record):
    timestamp = datetime.fromisoformat(record['timestamp'])
    now = datetime.utcnow()
    
    age_minutes = (now - timestamp).total_seconds() / 60
    
    if age_minutes > 5:  # Data older than 5 minutes
        return False, f"Data is {age_minutes:.1f} minutes old"
    
    return True, "Fresh"
```

#### 4. Consistency
**Definition:** Cross-source validation

**Rule:**
```python
def check_consistency(data_source_a, data_source_b):
    """
    Compare data from two sources for the same symbol and timestamp
    """
    # Allow 1% price deviation
    price_diff = abs(data_source_a['close'] - data_source_b['close'])
    tolerance = data_source_a['close'] * 0.01
    
    if price_diff > tolerance:
        return False, f"Price discrepancy: {price_diff:.2f}"
    
    return True, "Consistent"
```

### Data Quality Monitoring

**CloudWatch Metrics:**
- `DataQuality/Completeness` - % complete records
- `DataQuality/Accuracy` - % accurate records
- `DataQuality/Timeliness` - Average data age (minutes)
- `DataQuality/PipelineSuccess` - % successful pipeline runs

**Alarms:**
- Completeness < 95% → Alert
- Accuracy < 99% → Alert
- Data age > 5 minutes → Alert
- Pipeline failure rate > 1% → Alert

---

## Monitoring and Alerting

### Pipeline Monitoring

**Key Metrics:**

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Pipeline Success Rate** | <99% | Page on-call |
| **Data Latency** | >5 min | Alert team |
| **API Error Rate** | >1% | Check API status |
| **Processing Duration** | >10 min | Investigate bottleneck |
| **Cost per Run** | >$0.10 | Optimize pipeline |

**CloudWatch Dashboard:**
```json
{
  "DashboardName": "DataPipelines",
  "Widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["DataPipeline", "PipelineRuns", {"stat": "Sum"}],
          [".", "PipelineFailures", {"stat": "Sum"}]
        ],
        "title": "Pipeline Executions"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["DataPipeline", "DataLatency", {"stat": "Average"}]
        ],
        "title": "Data Latency (minutes)"
      }
    }
  ]
}
```

### Alerting Strategy

**SNS Topic: `data-pipeline-alerts`**

**Subscribers:**
- Email: ops-team@company.com
- Slack: #data-pipeline-alerts
- PagerDuty: Critical alerts only

**Alert Levels:**
- **INFO**: Pipeline completed successfully (no notification)
- **WARNING**: Degraded performance, retrying (Slack only)
- **ERROR**: Pipeline failed after retries (Email + Slack)
- **CRITICAL**: Multiple pipeline failures, data outage (PagerDuty + Email + Slack)

---

## Cost Optimization

### Current Cost Estimate (Monthly)

| Component | Usage | Cost |
|-----------|-------|------|
| **Alpha Vantage API** | Premium subscription | $50 |
| **Financial Modeling Prep** | Starter plan | $29 |
| **Finnhub API** | Starter plan | $99 |
| **Cloud Functions** | 500K invocations, 512MB, 10s avg | $9 |
| **Cloud Composer** | Small environment (1 worker) | $50 |
| **Cloud Storage** | 500GB raw + processed | $10 |
| **Cloud Storage Operations** | 1M writes, 10M reads | $5 |
| **Firestore** | 5M writes, 50M reads | $25 |
| **BigQuery** | 50GB storage, 500K writes, 10GB queries | $35 |
| **Pub/Sub** | 500K messages | $2 |
| **Cloud Scheduler** | 10 jobs | $1 |
| **Cloud Logging** | 50GB logs | $25 |
| **Cloud Monitoring** | Metrics and dashboards | $8 |
| **Total** | | **~$348/month** |

### Optimization Strategies

1. **API Cost Reduction**
   - Use free tier APIs for development
   - Cache frequently accessed data (Firestore or Memorystore)
   - Batch API requests where possible

2. **Cloud Functions Optimization**
   - Right-size memory allocation (use 256MB if possible)
   - Reduce cold starts with min instances for critical functions
   - Use environment variables for configuration
   - Bundle dependencies efficiently

3. **Storage Optimization**
   - Cloud Storage lifecycle policies (archive to Nearline/Coldline after 90 days)
   - Firestore TTL (auto-delete old documents)
   - Compress large data files before upload
   - Use BigQuery partitioning and clustering

4. **Processing Optimization**
   - Process data in batches (not individual records)
   - Use Cloud Run for longer-running tasks (cheaper than Functions)
   - Parallel processing in Cloud Composer DAGs
   - Use BigQuery for heavy analytics instead of client-side processing

5. **Cloud Composer Optimization**
   - Use smallest environment size during development
   - Consider Cloud Workflows for simpler orchestration needs
   - Schedule resource-intensive DAGs during off-peak hours

---

**Document Version:** 1.0  
**Last Updated:** February 5, 2026  
**Status:** Draft - Implementation Ready
