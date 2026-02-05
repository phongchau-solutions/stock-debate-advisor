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
│  • Lambda functions per data source                         │
│  • Rate limiting & retry logic                              │
│  • Raw data validation                                      │
│  • S3 raw data storage                                      │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓ S3 Event Notification
┌─────────────────────────────────────────────────────────────┐
│                   Processing Layer                           │
│  • Step Functions workflow orchestration                    │
│  • Data cleaning & normalization                            │
│  • Technical indicator calculation                          │
│  • Data enrichment                                          │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│  • DynamoDB (hot data, <90 days)                            │
│  • Timestream (time-series data)                            │
│  • RDS Aurora (relational data)                             │
│  • S3 (processed data lake)                                 │
└────────────┬────────────────────────────────────────────────┘
             │
             ↓ DynamoDB Streams
┌─────────────────────────────────────────────────────────────┐
│                   Serving Layer                              │
│  • ElastiCache (Redis) - hot cache                          │
│  • API Gateway - RESTful endpoints                          │
│  • EventBridge - data update events                         │
└─────────────────────────────────────────────────────────────┘
```

### Event-Driven Flow

```
EventBridge Scheduler → Lambda (Ingestion) → S3 (Raw)
                                               │
                                               ↓
                                     Step Functions (Process)
                                               │
                                               ↓
                                     Multi-Store Write
                                     ┌────────┴─────────┐
                                     │                  │
                                     ↓                  ↓
                              DynamoDB             Timestream
                                     │                  │
                                     ↓                  ↓
                              DynamoDB Stream   EventBridge
                                     │                  │
                                     ↓                  ↓
                           Cache Invalidation    Notification
```

---

## Pipeline Implementation

### Pipeline 1: Real-time Price Data

**Schedule:** Every 1 minute (market hours: 9:30 AM - 4:00 PM ET, Mon-Fri)

**EventBridge Rule:**
```json
{
  "Name": "PriceDataIngestion",
  "ScheduleExpression": "rate(1 minute)",
  "State": "ENABLED",
  "Targets": [{
    "Arn": "arn:aws:lambda:us-east-1:123456789:function:PriceIngestionFunction",
    "Input": "{\"symbols\": [\"AAPL\", \"GOOGL\", \"MSFT\", ...]}"
  }]
}
```

**Lambda Function: `price-ingestion`**

```python
# data-pipelines/ingestion/price-fetcher/handler.py

import boto3
import requests
from datetime import datetime
import json

s3 = boto3.client('s3')
alpha_vantage_key = os.environ['ALPHA_VANTAGE_API_KEY']

def lambda_handler(event, context):
    """
    Fetch real-time price data for given symbols
    """
    symbols = event.get('symbols', [])
    results = []
    
    for symbol in symbols:
        try:
            # Fetch from Alpha Vantage
            url = f"https://www.alphavantage.co/query"
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
            
            # Save to S3 raw bucket
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            key = f"prices/raw/{symbol}/{timestamp}.json"
            
            s3.put_object(
                Bucket=os.environ['RAW_DATA_BUCKET'],
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json',
                Metadata={
                    'symbol': symbol,
                    'source': 'alphavantage',
                    'timestamp': timestamp
                }
            )
            
            results.append({
                'symbol': symbol,
                'status': 'success',
                's3_key': key
            })
            
        except Exception as e:
            print(f"Error fetching {symbol}: {str(e)}")
            results.append({
                'symbol': symbol,
                'status': 'error',
                'error': str(e)
            })
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': len(results),
            'results': results
        })
    }
```

**Step Function: `price-processing-workflow`**

```json
{
  "Comment": "Process raw price data",
  "StartAt": "ProcessPriceData",
  "States": {
    "ProcessPriceData": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:PriceProcessor",
      "Next": "CalculateTechnicalIndicators"
    },
    "CalculateTechnicalIndicators": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:TechnicalIndicatorCalculator",
      "Next": "StoreToDynamoDB"
    },
    "StoreToDynamoDB": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:DynamoDBWriter",
      "Next": "StoreToTimestream"
    },
    "StoreToTimestream": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:TimestreamWriter",
      "Next": "PublishEvent"
    },
    "PublishEvent": {
      "Type": "Task",
      "Resource": "arn:aws:states:::events:putEvents",
      "Parameters": {
        "Entries": [{
          "Source": "stock-data-pipeline",
          "DetailType": "PriceDataUpdated",
          "Detail.$": "$.detail"
        }]
      },
      "End": true
    }
  }
}
```

**Lambda Function: `price-processor`**

```python
# data-pipelines/processing/price-processor/handler.py

import boto3
import json
from decimal import Decimal

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Clean and normalize price data
    """
    bucket = event['bucket']
    key = event['key']
    
    # Read raw data from S3
    obj = s3.get_object(Bucket=bucket, Key=key)
    raw_data = json.loads(obj['Body'].read())
    
    # Extract metadata
    symbol = obj['Metadata']['symbol']
    
    # Parse time series data
    time_series = raw_data.get('Time Series (1min)', {})
    
    processed_data = []
    for timestamp, values in time_series.items():
        processed_data.append({
            'symbol': symbol,
            'timestamp': timestamp,
            'open': Decimal(values['1. open']),
            'high': Decimal(values['2. high']),
            'low': Decimal(values['3. low']),
            'close': Decimal(values['4. close']),
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

**Lambda Function: `technical-indicator-calculator`**

```python
# data-pipelines/processing/technical-indicators/handler.py

import pandas as pd
import numpy as np

def lambda_handler(event, context):
    """
    Calculate technical indicators (RSI, MACD, Bollinger Bands, etc.)
    """
    symbol = event['symbol']
    data = event['data']
    
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

**EventBridge Rule:**
```json
{
  "Name": "CompanyInfoIngestion",
  "ScheduleExpression": "cron(0 0 * * ? *)",
  "State": "ENABLED"
}
```

**Implementation:** Similar to price pipeline with different data source

### Pipeline 3: Financial Reports

**Schedule:** Daily at 01:00 UTC (after market close)

**Implementation:** Fetch quarterly and annual financial statements

### Pipeline 4: News Ingestion

**Schedule:** Every 15 minutes

**Implementation:**
- Fetch latest news articles for tracked symbols
- Perform sentiment analysis using AWS Comprehend
- Store results in DynamoDB with TTL (30 days)

### Pipeline 5: Sentiment Analysis

**Schedule:** Hourly

**Data Sources:**
- Reddit (r/wallstreetbets, r/stocks)
- News headlines (from Pipeline 4)

**Implementation:**
```python
# sentiment-analyzer/handler.py

import boto3
from textblob import TextBlob  # Alternative: AWS Comprehend

comprehend = boto3.client('comprehend')

def analyze_sentiment(text):
    """
    Analyze sentiment using AWS Comprehend
    """
    response = comprehend.detect_sentiment(
        Text=text[:5000],  # Max 5000 bytes
        LanguageCode='en'
    )
    
    return {
        'sentiment': response['Sentiment'],  # POSITIVE, NEGATIVE, NEUTRAL, MIXED
        'scores': response['SentimentScore']
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
| **Lambda Invocations** | 500K invocations, 512MB, 10s avg | $15 |
| **Step Functions** | 100K state transitions | $2.50 |
| **S3 Storage** | 500GB raw + processed | $15 |
| **S3 Requests** | 1M PUT, 10M GET | $10 |
| **DynamoDB** | 5M writes, 50M reads (on-demand) | $30 |
| **Timestream** | 50GB storage, 500K writes | $40 |
| **EventBridge** | 500K events | $0.50 |
| **CloudWatch** | Logs 50GB, metrics | $20 |
| **Total** | | **~$311/month** |

### Optimization Strategies

1. **API Cost Reduction**
   - Use free tier APIs for development
   - Cache frequently accessed data (ElastiCache)
   - Batch API requests where possible

2. **Lambda Optimization**
   - Right-size memory allocation
   - Reduce cold starts (provisioned concurrency for critical functions)
   - Use Lambda layers for dependencies

3. **Storage Optimization**
   - S3 Lifecycle policies (archive to Glacier after 90 days)
   - DynamoDB TTL (auto-delete old data)
   - Compress large data files

4. **Processing Optimization**
   - Process data in batches (not individual records)
   - Use Step Functions Express (cheaper for high-volume)
   - Parallel processing where possible

---

**Document Version:** 1.0  
**Last Updated:** February 5, 2026  
**Status:** Draft - Implementation Ready
