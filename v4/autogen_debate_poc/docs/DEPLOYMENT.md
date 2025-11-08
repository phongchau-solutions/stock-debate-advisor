# Deployment Guide - Gemini Debate PoC v4

## Local Development

### Setup (5 minutes)

```bash
cd /home/x1e3/work/vmo/agentic/v4/autogen_debate_poc

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add GEMINI_API_KEY

# Test run
python app.py --stock VNM --rounds 2
```

### Directory Structure

```
v4/autogen_debate_poc/
├── app.py                 # Main entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Orchestration
├── README.md            # Documentation
├── DEPLOYMENT.md        # This file
├── .env.example         # Environment template
├── run.sh               # Quick start script
│
├── agents/              # Agent implementations
│   ├── base_agent.py    # Abstract base class
│   ├── fundamental_agent.py
│   ├── technical_agent.py
│   ├── sentiment_agent.py
│   ├── moderator_agent.py
│   └── judge_agent.py
│
├── services/            # Core services
│   ├── gemini_service.py    # LLM wrapper
│   ├── data_service.py      # Data fetching
│   └── debate_orchestrator.py # Orchestration
│
├── db/                  # Database layer
│   └── models.py       # SQLAlchemy models
│
├── prompts/             # Agent system prompts
│   ├── fundamental.txt
│   ├── technical.txt
│   ├── sentiment.txt
│   ├── moderator.txt
│   └── judge.txt
│
└── logs/                # Output logs
```

---

## Docker Deployment

### Single Container (No Database)

```bash
# Build
docker build -t gemini-debate:latest .

# Run
docker run \
  -e GEMINI_API_KEY=your-key \
  -v $(pwd)/logs:/app/logs \
  gemini-debate:latest \
    python app.py --stock VNM --rounds 3
```

### Full Stack (App + PostgreSQL)

```bash
# Setup environment
export GEMINI_API_KEY="your-key"
export STOCK_SYMBOL="VNM"
export DEBATE_ROUNDS="3"

# Launch
docker-compose up --build

# Check logs
docker-compose logs -f debate_app

# Stop
docker-compose down
```

### Database Persistence

```bash
# Access PostgreSQL
docker exec -it debate_postgres psql -U debate_user -d debate_poc

# Query debate logs
SELECT debate_id, stock_symbol, final_decision, confidence_score 
FROM debate_logs 
ORDER BY start_time DESC LIMIT 10;

# Export results
docker exec -i debate_postgres psql -U debate_user -d debate_poc \
  -c "COPY debate_logs TO STDOUT WITH CSV HEADER" > debates.csv
```

---

## Production Checklist

### Security
- [ ] Store `GEMINI_API_KEY` in secrets manager (AWS Secrets, Azure KeyVault)
- [ ] Use DB credentials from secrets, never in .env
- [ ] Enable SSL for database connections
- [ ] Restrict API endpoint access (firewall/VPC)
- [ ] Implement input validation on stock symbols
- [ ] Add rate limiting per API key
- [ ] Enable audit logging for all debates

### Monitoring
- [ ] Set up CloudWatch/DataDog for logs
- [ ] Create alerts for failed debates (retry exhaustion)
- [ ] Monitor Gemini API quota and costs
- [ ] Track debate latency (target < 5 min for 3 rounds)
- [ ] Monitor database storage growth

### Performance
- [ ] Enable PostgreSQL query caching
- [ ] Implement result caching (Redis) for same stock/period
- [ ] Use connection pooling with `pool_size=20`
- [ ] Add async debate processing (Celery + Redis)

### Reliability
- [ ] Database backups: daily automated to S3/Azure Blob
- [ ] Retry logic: exponential backoff (built-in via backoff)
- [ ] Gemini API failover: fallback to Anthropic Claude if needed
- [ ] Health checks: `/health` endpoint for Kubernetes
- [ ] Graceful shutdown: flush pending debates before termination

---

## Kubernetes Deployment

### Docker Registry

```bash
# Tag and push
docker tag gemini-debate:latest myregistry.azurecr.io/gemini-debate:latest
docker push myregistry.azurecr.io/gemini-debate:latest
```

### Kubernetes Manifests

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gemini-debate
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gemini-debate
  template:
    metadata:
      labels:
        app: gemini-debate
    spec:
      containers:
      - name: debate
        image: myregistry.azurecr.io/gemini-debate:latest
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-secrets
              key: api-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: connection-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 30
          periodSeconds: 10

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: gemini-debate-service
spec:
  selector:
    app: gemini-debate
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

### Deploy

```bash
kubectl create namespace debate-poc
kubectl create secret generic gemini-secrets -n debate-poc \
  --from-literal=api-key=your-key
kubectl create secret generic db-secrets -n debate-poc \
  --from-literal=connection-url=postgresql://...

kubectl apply -n debate-poc -f deployment.yaml
kubectl apply -n debate-poc -f service.yaml

# Verify
kubectl get pods -n debate-poc
kubectl logs -n debate-poc -l app=gemini-debate -f
```

---

## Cloud Deployment Options

### Azure Container Instances

```bash
az container create \
  --resource-group debate-rg \
  --name gemini-debate \
  --image myregistry.azurecr.io/gemini-debate:latest \
  --cpu 1 \
  --memory 1 \
  --environment-variables GEMINI_API_KEY=$GEMINI_API_KEY
```

### AWS Lambda (Serverless)

```python
# lambda_handler.py
import json
import subprocess
import os

def lambda_handler(event, context):
    stock = event.get('stock', 'VNM')
    rounds = event.get('rounds', 3)
    
    result = subprocess.run([
        'python', 'app.py',
        '--stock', stock,
        '--rounds', str(rounds)
    ], capture_output=True, text=True)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Debate complete',
            'stock': stock,
            'output': result.stdout
        })
    }
```

### Google Cloud Run

```bash
gcloud run deploy gemini-debate \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,DATABASE_URL=$DB_URL
```

---

## Scaling Considerations

### Horizontal Scaling
- **Current Design**: Single-instance debates (complete within minutes)
- **Scale Strategy**: Job queue (Celery) + Workers for batch debates
- **Database**: Connection pooling handles multiple concurrent requests

### Optimization
- Cache yfinance data (1-hour TTL)
- Batch sentiment analysis (aggregate news source calls)
- Pre-compute technical indicators (incremental updates)

### Cost Estimation
- **Gemini API**: ~$0.50 per debate (3 agents + moderator + judge = 5 calls)
- **PostgreSQL**: ~$15/month (managed service, 10GB storage)
- **Compute**: $5-20/month (local) or $50-200/month (cloud)

---

## Troubleshooting

### Issue: API Rate Limiting
```
Error: 429 Too Many Requests
```
**Solution**: Built-in exponential backoff handles this. If persists:
- Increase `max_retries` in `GeminiService.__init__`
- Add `time.sleep(2)` between debates
- Check API quota in Google Cloud Console

### Issue: Database Connection Pool Exhausted
```
Error: QueuePool limit exceeded
```
**Solution**: Increase pool size in `db/models.py`:
```python
create_engine(db_url, pool_size=30, max_overflow=10)
```

### Issue: Memory Usage High
```
INFO: Memory usage 85%
```
**Solution**:
- Increase container memory limit
- Reduce analysis period (fewer OHLCV candles)
- Disable debate transcript storage in memory

---

## Maintenance

### Updating Dependencies
```bash
pip install --upgrade -r requirements.txt
docker build --no-cache -t gemini-debate:latest .
```

### Database Migrations
```bash
# If adding new fields to debate schema:
sqlalchemy-admin create-all  # Auto-migration for SQLAlchemy models
```

### Log Rotation
```bash
# Ensure logs don't bloat (configure logrotate or use centralized logging)
echo "/app/logs/*.log {
  daily
  rotate 7
  compress
  delaycompress
}" | sudo tee /etc/logrotate.d/gemini-debate
```

---

## Success Metrics

After deployment, verify:
- ✅ Debates complete in < 5 minutes (3 rounds)
- ✅ Confidence scores between 0.5-0.9 (well-calibrated)
- ✅ No API retry exhaustion over 7 days
- ✅ Database storage < 100MB/month
- ✅ 0 security issues (no API keys in logs)

---

## Support

For issues or questions:
- Check `logs/debate.log` for detailed traces
- Review README.md for architecture details
- Check Gemini API status: https://status.cloud.google.com/
