# V7 Local Development & Deployment Guide

## Local Development (Simple - No Docker)

### Option 1: Show Instructions
```bash
./dev-local.sh
```

This will display instructions for running both services.

### Option 2: Manual Setup

**Terminal 1 - Frontend (Vite)**
```bash
cd frontend
npm install  # First time only
npm run dev
```
Frontend runs on: **http://localhost:5173**

**Terminal 2 - AI Service (Streamlit)**
```bash
conda activate chatbot_env
cd ai-service
pip install -r requirements.txt  # First time only
streamlit run app.py
```
AI Service runs on: **http://localhost:8501**

## Frontend Production Deployment (S3)

### Prerequisites
```bash
# AWS CLI configured with credentials
aws configure

# Node.js 18+ installed
node --version
npm --version
```

### Deploy Frontend to S3

1. **Set S3 bucket name in `.env.local`**
   ```dotenv
   S3_BUCKET=your-bucket-name
   CLOUDFRONT_DIST_ID=your-dist-id  # Optional: for CloudFront invalidation
   ```

2. **Create S3 bucket (if needed)**
   ```bash
   aws s3 mb s3://your-bucket-name --region us-east-1
   ```

3. **Configure S3 for static website hosting**
   ```bash
   aws s3 website s3://your-bucket-name \
       --index-document index.html \
       --error-document index.html
   ```

4. **Deploy**
   ```bash
   ./deploy-frontend.sh
   ```

   Or with custom bucket:
   ```bash
   S3_BUCKET=my-bucket CLOUDFRONT_DIST_ID=E123ABC ./deploy-frontend.sh
   ```

### What deploy-frontend.sh Does
- ✅ Runs `npm run build` to create optimized production build
- ✅ Uploads `dist/` folder to S3 bucket
- ✅ Sets proper cache-control headers:
  - HTML: no-cache (always fetch latest)
  - Assets: 1 hour cache (for efficient updates)
- ✅ Optionally invalidates CloudFront cache

## Development Workflow

### Local Development
```bash
# Terminal 1
cd frontend && npm run dev

# Terminal 2
conda activate chatbot_env && cd ai-service && streamlit run app.py
```

### Testing Production Build Locally
```bash
cd frontend
npm run build
npm run preview  # Preview production build at http://localhost:5173
```

### Deploy to S3
```bash
./deploy-frontend.sh
```

## Environment Variables

**.env.local** for local development:
```dotenv
GEMINI_API_KEY=your_api_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=stock-debate-frontend
CLOUDFRONT_DIST_ID=E123ABC  # Optional
```

## Troubleshooting

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### AI Service won't start
```bash
conda activate chatbot_env
pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### S3 deployment fails
```bash
# Verify AWS credentials
aws sts get-caller-identity

# Verify bucket exists
aws s3 ls s3://your-bucket-name

# Check permissions
aws s3api head-bucket --bucket your-bucket-name
```

## Next Steps

1. **Local Development** → `npm run dev` + `streamlit run app.py`
2. **Test in Browser** → http://localhost:5173 & http://localhost:8501
3. **Build for Production** → `npm run build`
4. **Deploy Frontend** → `./deploy-frontend.sh`
5. **Deploy Backend/AI** → Use CDK: `cd cdk && cdk deploy`

See `DEPLOYMENT_GUIDE.md` for full AWS infrastructure deployment.

