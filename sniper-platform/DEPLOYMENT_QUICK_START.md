# 🚀 Quick Start Deployment (College Project)

**TL;DR**: Use **Render** for easiest free deployment.

## 3 Steps to Production

### Step 1: Push to GitHub (5 min)
```bash
cd /Users/pranavks/project/sniper-platform
git add .
git commit -m "feat: deployment-ready with security hardening"
git push origin main
```

### Step 2: Deploy to Render (15 min)
1. Go to [render.com](https://render.com) → Sign in with GitHub
2. Create **Web Service** → Select your `sniper-platform` repo
3. **Frontend** service:
   - Root dir: `apps/sniper`
   - Build: `npm install && npm run build`
   - Start: `npm start`
4. **Backend** service:
   - Root dir: `apps/sniper-backend`
   - Build: `pip install -r requirements.txt`
   - Start: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. **PostgreSQL**: Create new → Render auto-fills DATABASE_URL
6. **Environment Variables** (for backend):
   ```
   ENVIRONMENT=production
   CLERK_JWKS_URL=https://your-clerk.clerk.accounts.dev/.well-known/jwks.json
   OPENAI_API_KEY=sk-...
   # (rest from .env.example)
   ```

### Step 3: Test Live (5 min)
- Frontend: `https://sniper-frontend.onrender.com`
- Backend: `https://sniper-backend.onrender.com/health`
- Update frontend's `NEXT_PUBLIC_API_BASE_URL` → redeploy

## Cost
**Free tier**: Limited RAM, OK for demo
**Paid tier**: ~$7/month (PostgreSQL) + $7-20/month (backend)

## If Issues
- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for troubleshooting
- Render logs: Dashboard → Service → Logs tab
