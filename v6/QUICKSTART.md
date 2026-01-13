# Quick Start Guide - Data Pipeline v2

**Last Updated**: January 10, 2026  
**Version**: 2.0.0

## ⚡ 5-Minute Quick Start

### 1. Initialize Database

```bash
cd v6/data-service
python << 'EOF'
from app.db.database import engine
from app.db import models
models.Base.metadata.create_all(bind=engine)
print("✓ Database initialized")
EOF
```

### 2. Test News Crawler (Optional)

```bash
python ../script/test_news_crawler.py --crawlers-only
```

### 3. Run Full Pipeline for VN30

```bash
python ../script/fetch_vn30_complete_pipeline.py
```

### 4. Check Results

```bash
# Results saved to pipeline_results/vn30_pipeline_*.json
# Data stored in PostgreSQL database
# View API endpoints
curl http://localhost:8001/api/v2/company/MBB.VN
```

## 📦 Installation

### Prerequisites

```bash
# Python packages (already in requirements.txt)
pip install yfinance beautifulsoup4 requests sqlalchemy pandas

# Database (PostgreSQL recommended)
# Update DATABASE_URL in app/db/database.py if needed
```

### Environment Setup

```bash
# Set conda environment
conda activate chatbot_env

# Or create new environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

## 🚀 Main Commands

### Fetch All VN30 Data

```bash
python script/fetch_vn30_complete_pipeline.py
```

**Options:**
```bash
--no-news                    # Skip news crawling
--workers 5                  # Use 5 parallel workers (default: 3)
--test-crawler               # Test crawlers only
--output-dir my_results      # Custom output directory
```

### Test Crawlers

```bash
# All tests
python script/test_news_crawler.py

# Specific tests
python script/test_news_crawler.py --crawlers-only
python script/test_news_crawler.py --aggregator-only
python script/test_news_crawler.py --service-only
```

## 🌐 API Endpoints

### Run FastAPI Server

```bash
# In v6/data-service directory
uvicorn app.main:app --reload --port 8001
```

### Available Endpoints

```
# Company Information
GET /api/v2/company/MBB.VN

# Financial Reports
GET /api/v2/financials/quarterly/MBB.VN
GET /api/v2/financials/annual/MBB.VN
GET /api/v2/financials/metrics/MBB.VN

# Stock Data
GET /api/v2/prices/MBB.VN?limit=100
GET /api/v2/dividends/MBB.VN

# News
GET /api/v2/news/MBB.VN?days=30&limit=50
GET /api/v2/news/sources

# All Data
GET /api/v2/data/MBB.VN?include_news=true

# Pipeline Logs
GET /api/v2/pipeline/logs
```

## 🐍 Python Usage

### Basic Data Retrieval

```python
from app.db.database import SessionLocal
from app.services.integrated_data_service import IntegratedDataService

db = SessionLocal()
service = IntegratedDataService(db)

# Get all data for one symbol
result = service.fetch_all_data_for_symbol('MBB.VN', include_news=True)
print(result)

db.close()
```

### Batch Processing

```python
db = SessionLocal()
service = IntegratedDataService(db)

# Fetch for multiple symbols
symbols = ['MBB.VN', 'VCB.VN', 'HPG.VN']
results = service.fetch_all_data_batch(symbols, max_workers=3, include_news=True)

# Results contain per-symbol statistics
for symbol, result in results['results'].items():
    print(f"{symbol}: {result['quarterly_reports']} quarterly, "
          f"{result['stock_prices']} prices, {result['news']} news")

db.close()
```

### Database Queries

```python
from app.db.database import SessionLocal
from app.db import models
from sqlalchemy import desc

db = SessionLocal()

# Get latest quarterly reports
reports = db.query(models.QuarterlyFinancialReport).filter(
    models.QuarterlyFinancialReport.symbol == 'MBB.VN'
).order_by(desc(models.QuarterlyFinancialReport.period_end_date)).limit(8).all()

for report in reports:
    print(f"Q{report.fiscal_quarter} {report.fiscal_year}: "
          f"Revenue={report.revenue}, NetIncome={report.net_income}")

db.close()
```

## 📊 Data Schema Quick Reference

### Company Info
```
symbol, name, industry, sector, market_cap, website, description
```

### Quarterly Reports (last 8)
```
fiscal_year, fiscal_quarter, period_end_date
revenue, operating_income, net_income, gross_profit
total_assets, total_equity, current_assets, current_liabilities
operating_cash_flow, free_cash_flow, eps
```

### Annual Reports (last 5)
```
fiscal_year, period_end_date
[Same fields as quarterly]
```

### Financial Metrics
```
metric_date, pe_ratio, pb_ratio, ps_ratio, peg_ratio
roe, roa, roic, margins (gross/operating/net)
ratios (current, quick, debt_to_equity)
growth (revenue, earnings)
```

### Stock Prices (Daily)
```
price_date, open, high, low, close, adj_close, volume
```

### News
```
title, url, source (yahoo_finance, cafef, vneconomy, vietstock)
published_at, sentiment_score, keywords
```

## 🔧 Configuration

### Database Connection

Edit `app/db/database.py`:
```python
# Default: SQLite for development
DATABASE_URL = "sqlite:///./stock_data.db"

# PostgreSQL for production
DATABASE_URL = "postgresql://user:password@localhost/stock_data"

# MySQL
DATABASE_URL = "mysql://user:password@localhost/stock_data"
```

### News Crawler Configuration

Edit `app/crawlers/news_crawler_v2.py`:
```python
# Adjust timeout (seconds)
response = self.session.get(url, timeout=10)

# Adjust number of articles per source
articles = crawler.search_articles(symbol, days=7)[:20]  # Top 20
```

### Pipeline Workers

```python
# In script or service calls
service.fetch_all_data_batch(symbols, max_workers=5)  # 1-10 recommended
```

## 📈 Performance Tips

1. **Increase Workers for Speed** (up to 5-8)
   ```bash
   python script/fetch_vn30_complete_pipeline.py --workers 8
   ```

2. **Skip News to Speed Up** (2x faster)
   ```bash
   python script/fetch_vn30_complete_pipeline.py --no-news
   ```

3. **Use PostgreSQL for Large Data**
   ```
   SQLite: Good for development (<100 MB)
   PostgreSQL: Good for production (unlimited)
   ```

4. **Index Frequently Queried Columns**
   ```sql
   CREATE INDEX idx_news_symbol_date ON company_news(symbol, published_at);
   ```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution**: Run from data-service directory
```bash
cd v6/data-service
python ../script/test_news_crawler.py
```

### Issue: "No such table" error

**Solution**: Initialize database first
```python
from app.db.database import engine
from app.db import models
models.Base.metadata.create_all(bind=engine)
```

### Issue: News crawler returns 0 articles

**Solution**: This is normal - web scraping may fail due to website changes. Use fallback API methods or check manually:
```python
from app.crawlers.news_crawler_v2 import NewsAggregator
agg = NewsAggregator()
articles = agg.crawl_for_symbol('MBB.VN')
```

### Issue: Yahoo Finance API errors

**Solution**: Check network and retry. Service has automatic retry logic:
```python
# Automatically retries 3 times with exponential backoff
service.fetch_and_store_stock_prices('MBB.VN')
```

## 📚 Documentation

- **DATA_PIPELINE_V2.md**: Complete architecture
- **DATA_PIPELINE_V2.md**: Complete data pipeline architecture and schema documentation
- **.archive/ARCHIVE_README.md**: Historical documentation and archived files reference

## 🎯 Next Steps

1. **Deploy to Production**
   - Set up PostgreSQL database
   - Configure environment variables
   - Deploy FastAPI service
   - Schedule Airflow DAG

2. **Add Sentiment Analysis**
   - Process news articles
   - Calculate sentiment scores
   - Track sentiment trends

3. **Build Analytics**
   - Create dashboards
   - Implement ML models
   - Generate reports

4. **Integrate with Agentic Service**
   - Use data in stock debates
   - Feed to analysis service
   - Create trading signals

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review documentation files
3. Check logs (vn30_pipeline.log)
4. Inspect database directly
5. Test individual components

---

**Quick Reference**:
- Main Script: `v6/script/fetch_vn30_complete_pipeline.py`
- API Server: `v6/data-service/app/main.py`
- Services: `v6/data-service/app/services/`
- Database: `v6/data-service/app/db/models.py`
- Documentation: `v6/DATA_PIPELINE_V2.md`
