# Sniper Trading Platform — Deployment Guide

## 📋 Overview

Sniper is a monorepo containing:
- **Frontend** (`apps/sniper`): Next.js 14 + React + TypeScript + Tailwind
- **Backend** (`apps/sniper-backend`): FastAPI + Python 3.11 + PostgreSQL + Redis
- **Framework** (`/sniper-framework` external): Python ML/trading components

**Status**: ✅ **Production Ready** (All security fixes applied)

---

## 🚀 Deployment Options & Recommendations

### 1️⃣ **Local Development** (Fastest iteration)
```bash
cd /Users/pranavks/project/sniper-platform
docker-compose up -d
```
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Database**: PostgreSQL @ localhost:5432
- **Cache**: Redis @ localhost:6379

**Best for**: Development, testing, quick iteration

---

### 2️⃣ **Render** ⭐ (Recommended for College Project)

**Why Render?**
- ✅ Free tier available (with limitations)
- ✅ GitHub integration (auto-deploy on push)
- ✅ One-command PostgreSQL provisioning
- ✅ Environment variables UI-based
- ✅ Automatic HTTPS + custom domains
- ✅ Great for demos, portfolios, college submissions

**Setup Steps:**

#### A. Create Render Account
1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Create new **Web Service**

#### B. Deploy Frontend (Next.js)
1. **Connect GitHub repo** → Select `sniper-platform`
2. **Build Command**: `cd apps/sniper && npm install && npm run build`
3. **Start Command**: `cd apps/sniper && npm start`
4. **Environment Variables**:
   ```
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
   NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com/api/v1
   NEXT_PUBLIC_WS_URL=wss://your-backend.onrender.com/ws
   NODE_ENV=production
   ```
5. **Deploy** (takes ~5 mins)
6. Note frontend URL: `https://sniper-frontend.onrender.com`

#### C. Deploy Backend (FastAPI)
1. **Create new Web Service** → Select repo again
2. **Build Command**: `cd apps/sniper-backend && pip install -r requirements.txt`
3. **Start Command**: `cd apps/sniper-backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. **Environment Variables** (copy from `.env.example`):
   ```
   ENVIRONMENT=production
   DATABASE_URL=postgresql://user:password@render-postgres-host:5432/sniper
   ALLOWED_ORIGINS=["https://sniper-frontend.onrender.com"]
   CLERK_JWKS_URL=https://your-instance.clerk.accounts.dev/.well-known/jwks.json
   OPENAI_API_KEY=sk-...
   # ... other keys (see .env.example)
   ```
5. **Attach PostgreSQL Database**:
   - In Render dashboard → "PostgreSQL" → Create new
   - Auto-fills `DATABASE_URL` in environment
6. **Deploy** (takes ~8 mins)

#### D. Set Up Redis (optional but recommended)
1. Create **Redis** service on Render
2. Add `REDIS_URL` to backend environment

#### E. Update Frontend to Use Production Backend
- Change `NEXT_PUBLIC_API_BASE_URL` to production backend URL
- Redeploy frontend

**Cost**: ~$7/month (PostgreSQL) + free tier for compute
**Uptime**: 99.9% with SLA option

---

### 3️⃣ **DigitalOcean** (Recommended for scaling)

**Why DigitalOcean?**
- ✅ Managed databases + app platform (cheaper than AWS)
- ✅ $6/month droplets + $15/month PostgreSQL
- ✅ CDN included for static assets
- ✅ Great control + documentation
- ✅ GitHub Actions CI/CD integration

**Setup Steps:**

#### A. App Platform Deployment
1. Create account at [digitalocean.com](https://digitalocean.com)
2. Go to **App Platform** → Create App
3. Select GitHub repo
4. Add two components:
   - **Frontend Service** (Next.js build)
   - **Backend Service** (FastAPI)
5. Link managed **PostgreSQL Database**
6. Deploy

#### B. Environment Configuration
Set on DigitalOcean dashboard for each service (similar to Render)

**Cost**: ~$20/month total
**Uptime**: 99.99% SLA with backups

---

### 4️⃣ **AWS/GCP** (Enterprise)

**When to use**: High traffic, strict compliance, global scaling

**Stack**:
- **Frontend**: CloudFront + S3 (or EC2 instance)
- **Backend**: ECS Fargate + RDS PostgreSQL + ElastiCache
- **Auth**: Cognito or external (Clerk)

**Cost**: $50–500+/month depending on traffic
**Setup time**: 2–4 hours with terraform/CDK

---

## 📊 Deployment Comparison Matrix

| Feature | Local | Render | DigitalOcean | AWS |
|---------|-------|--------|--------------|-----|
| **Cost** | $0 | $7/mo | $20/mo | $50+ |
| **Setup Time** | 5 min | 20 min | 30 min | 2+ hrs |
| **HTTPS** | ❌ | ✅ | ✅ | ✅ |
| **Auto-scaling** | ❌ | ⚠️ | ✅ | ✅ |
| **GitHub Sync** | ❌ | ✅ | ✅ | ⚠️ |
| **Free Tier** | N/A | ✅ | ❌ | ✅ (1yr) |
| **Best For** | Dev | College/Demo | Production | Enterprise |

---

## 🔧 Pre-Deployment Checklist

### ✅ Code Quality
- [x] TypeScript: 0 errors
- [x] All endpoints protected with `verify_token`
- [x] CORS restricted (not `*`)
- [x] Security headers added
- [x] Error traces hidden in production
- [x] WebSocket error handling robust
- [x] `.env.example` files created

### ✅ Configuration
- [x] Database migrations in Dockerfile (`alembic upgrade head`)
- [x] Health check endpoint (`/health`)
- [x] Config supports all env vars
- [x] Clerk JWKS URL field added

### ✅ Secrets Management
- [ ] Never commit `.env` files (verify `.gitignore`)
- [ ] Store secrets in deployment platform (Render/DO/AWS dashboard)
- [ ] Use `ENVIRONMENT=production` in prod
- [ ] Rotate API keys if exposed

### ✅ Database
- [ ] Run migrations: `alembic upgrade head`
- [ ] Test with production data volume
- [ ] Backup strategy in place
- [ ] Connection pooling configured

### ✅ Monitoring
- [ ] Health check endpoint responding
- [ ] Error logs are captured
- [ ] Database connectivity tested
- [ ] External APIs (OpenAI, Clerk) reachable

---

## 🌐 Environment Variables by Deployment

### **Local Development** (.env.local for frontend, .env for backend)
```bash
# Frontend
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# Backend
ENVIRONMENT=dev
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sniper
OPENAI_API_KEY=sk-test...
```

### **Production (Render/DigitalOcean)**
```bash
# Frontend
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_API_BASE_URL=https://your-backend-prod.com/api/v1

# Backend
ENVIRONMENT=production
ALLOWED_ORIGINS=["https://your-frontend-prod.com"]
CLERK_JWKS_URL=https://your-instance.clerk.accounts.dev/.well-known/jwks.json
DATABASE_URL=postgresql://user:pass@managed-db-host:5432/sniper
OPENAI_API_KEY=sk-...
```

---

## 📦 Docker Build & Deployment

### Build Frontend Image
```bash
cd apps/sniper
docker build -t sniper-frontend:latest .
docker push your-registry/sniper-frontend:latest
```

### Build Backend Image
```bash
cd apps/sniper-backend
docker build -t sniper-backend:latest .
docker push your-registry/sniper-backend:latest
```

### Docker Compose (Production)
```yaml
version: '3.9'
services:
  frontend:
    image: your-registry/sniper-frontend:latest
    ports:
      - '3000:3000'
    environment:
      NEXT_PUBLIC_API_BASE_URL: https://backend.example.com/api/v1
    restart: always

  backend:
    image: your-registry/sniper-backend:latest
    ports:
      - '8000:8000'
    environment:
      ENVIRONMENT: production
      DATABASE_URL: postgresql://...
    restart: always
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secure-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

---

## 🎯 Recommended Flow for College Project

### Week 1: Prepare
```bash
# 1. Ensure all code committed to GitHub
git add .
git commit -m "feat: deployment-ready backend with auth and security hardening"
git push

# 2. Test locally
docker-compose up -d
# Visit http://localhost:3000 and test core flows
```

### Week 2: Deploy to Render (Free)
1. Sign up at Render
2. Deploy frontend (~5 mins)
3. Deploy backend (~8 mins)
4. Link PostgreSQL
5. Test production endpoints

### Week 3: Polish & Demo
- Share live links with instructors
- Showcase features on production (faster, no localhost)
- Collect feedback

---

## 🚨 Troubleshooting

### Frontend can't reach backend
```
Error: "Backend unreachable"
Solution: Check NEXT_PUBLIC_API_BASE_URL matches deployed backend URL
```

### Database migration fails
```
Error: "alembic upgrade head" fails
Solution: Check DATABASE_URL is correct; ensure user has permissions
```

### WebSocket connection fails
```
Error: "WebSocket connection refused"
Solution: Ensure backend is running; check NEXT_PUBLIC_WS_URL matches backend
```

### Out of memory on Render
```
Error: "Killed: 9" in logs
Solution: Upgrade to paid tier (currently on free tier with 512MB RAM)
```

---

**Status**: ✅ Ready for deployment
