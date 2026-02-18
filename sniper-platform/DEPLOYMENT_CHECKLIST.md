# Sniper Platform — Deployment Checklist

Use this checklist to track your deployment progress. Check off each item as you complete it.

---

## ✅ PRE-DEPLOYMENT SETUP (Before Day 1)

### Account Setup
- [ ] Created GitHub account
- [ ] Created Render account (render.com)
- [ ] Created Clerk account (clerk.com)
- [ ] Have OpenAI API key (optional, for AI assistant)

### Code Preparation
- [ ] All code committed to GitHub
- [ ] `git status` shows "working tree clean"
- [ ] Verified `.env.example` files exist:
  - [ ] `apps/sniper/.env.example`
  - [ ] `apps/sniper-backend/.env.example`
- [ ] Tested locally with `docker-compose up -d` (optional)

### Information Gathered
- [ ] Clerk Publishable Key (pk_...)
- [ ] Clerk Secret Key (sk_...)
- [ ] OpenAI API Key (sk-..., optional)
- [ ] GitHub repository URL ready

---

## 🗄️ DATABASE SETUP (Day 1 — 5 minutes)

### PostgreSQL on Render
- [ ] Logged into Render dashboard
- [ ] Created PostgreSQL database:
  - [ ] Name: `sniper-db`
  - [ ] Database: `sniper`
  - [ ] Region selected
- [ ] Database status shows "Available ✓"
- [ ] Copied connection string:
  ```
  DATABASE_URL = ___________________________________
  ```
  Save this!

---

## 🔙 BACKEND DEPLOYMENT (Day 1 — 8 minutes)

### Create Web Service for Backend
- [ ] Clicked **New +** → **Web Service**
- [ ] Connected GitHub repository: `sniper-platform`
- [ ] Filled configuration:
  - [ ] Name: `sniper-backend`
  - [ ] Region: Same as database
  - [ ] Branch: `main`
  - [ ] Root Directory: `apps/sniper-backend`
  - [ ] Runtime: `Python 3`
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Set Environment Variables
- [ ] `ENVIRONMENT` = `production`
- [ ] `DATABASE_URL` = [from database setup]
- [ ] `ALLOWED_ORIGINS` = `["https://sniper-frontend-xxxxx.onrender.com"]` (update later)
- [ ] `CLERK_JWKS_URL` = [from Clerk dashboard]
- [ ] `OPENAI_API_KEY` = [your key or leave blank]
- [ ] `OPENAI_MODEL` = `gpt-4o-mini`

### Deploy & Wait
- [ ] Clicked **Create Web Service**
- [ ] Build started (visible in Logs)
- [ ] Build completed successfully ✓
- [ ] Service shows as "Running"
- [ ] Noted backend URL:
  ```
  BACKEND_URL = https://sniper-backend-xxxxx.onrender.com
  ```

### Verify Backend
- [ ] Tested `/health` endpoint:
  ```bash
  curl https://sniper-backend-xxxxx.onrender.com/health
  ```
- [ ] Got `{"status": "ok"}` response

---

## 🎨 FRONTEND DEPLOYMENT (Day 1 — 8 minutes)

### Create Web Service for Frontend
- [ ] Clicked **New +** → **Web Service**
- [ ] Connected GitHub repository: `sniper-platform`
- [ ] Filled configuration:
  - [ ] Name: `sniper-frontend`
  - [ ] Region: Same as database
  - [ ] Branch: `main`
  - [ ] Root Directory: `apps/sniper`
  - [ ] Runtime: `Node`
  - [ ] Build Command: `npm install && npm run build`
  - [ ] Start Command: `npm start`

### Set Environment Variables
- [ ] `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` = [from Clerk]
- [ ] `NEXT_PUBLIC_API_BASE_URL` = `https://sniper-backend-xxxxx.onrender.com/api/v1`
- [ ] `NODE_ENV` = `production`

### Deploy & Wait
- [ ] Clicked **Create Web Service**
- [ ] Build started (visible in Logs)
- [ ] Build completed successfully ✓
- [ ] Service shows as "Running"
- [ ] Noted frontend URL:
  ```
  FRONTEND_URL = https://sniper-frontend-xxxxx.onrender.com
  ```

### Verify Frontend
- [ ] Opened frontend URL in browser
- [ ] Saw Sniper login page
- [ ] Page fully loaded (no blank screen)

---

## 🔐 AUTHENTICATION SETUP (Day 1 — 5 minutes)

### Clerk Configuration
- [ ] Logged into Clerk dashboard
- [ ] Found Publishable Key (pk_...)
- [ ] Found Secret Key (sk_...)
- [ ] Found JWKS URL (https://[instance].clerk.accounts.dev/.well-known/jwks.json)

### Update Render Services
- [ ] Frontend service updated with correct Clerk key:
  - [ ] Render dashboard → sniper-frontend
  - [ ] Environment tab
  - [ ] `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` = [exact value from Clerk]
  - [ ] Saved (auto-redeploy started)
- [ ] Backend service updated with JWKS URL:
  - [ ] Render dashboard → sniper-backend
  - [ ] Environment tab
  - [ ] `CLERK_JWKS_URL` = [exact value from Clerk]
  - [ ] Saved (auto-redeploy started)
- [ ] Waited 2-3 minutes for redeployment

---

## 🧪 TESTING (Day 1 — 5 minutes)

### Backend Authentication Test
- [ ] Tested without auth (should fail):
  ```bash
  curl https://sniper-backend-xxxxx.onrender.com/api/v1/strategy/
  ```
  - [ ] Got `{"detail": "Missing Authorization header"}`
- [ ] ✅ Auth is working!

### Frontend Login Test
- [ ] Opened frontend URL
- [ ] Clicked **Sign In** or **Sign Up**
- [ ] Completed Clerk authentication
- [ ] Successfully logged in
- [ ] Saw dashboard page
- [ ] Could navigate app

### API Integration Test (Optional)
- [ ] Opened DevTools (F12)
- [ ] Went to **Application** → **Local Storage**
- [ ] Found auth token
- [ ] Made API request with token:
  ```bash
  curl -H "Authorization: Bearer [token]" \
    https://sniper-backend-xxxxx.onrender.com/api/v1/strategy/
  ```
  - [ ] Got valid response (empty list `[]` is OK)

---

## 📊 VERIFY LOGS & MONITORING (Day 1 — 5 minutes)

### Check Backend Logs
- [ ] Render dashboard → sniper-backend
- [ ] **Logs** tab
- [ ] No error messages visible
- [ ] App started successfully
- [ ] Database connected successfully

### Check Frontend Logs
- [ ] Render dashboard → sniper-frontend
- [ ] **Logs** tab
- [ ] Build completed without errors
- [ ] Next.js server started successfully

### Check Database Status
- [ ] Render dashboard → sniper-db (PostgreSQL)
- [ ] Status shows "Available ✓"
- [ ] Memory and CPU usage normal
- [ ] No connection errors

---

## 🎯 FINAL VERIFICATION (Day 1 — 10 minutes)

### Full User Flow Test
- [ ] Opened frontend in browser
- [ ] Can see login page
- [ ] Can click "Sign In"
- [ ] Can authenticate with Clerk
- [ ] Redirected to dashboard
- [ ] Dashboard loads without errors
- [ ] Can see main interface elements
- [ ] No 502/503 errors in console

### Functionality Test (Optional)
- [ ] Can view strategies (if any)
- [ ] Can create new strategy (if enabled)
- [ ] Can view analytics
- [ ] Can access settings
- [ ] No console errors (F12 → Console)

### Performance Check
- [ ] Frontend loads in under 5 seconds
- [ ] Backend responds within 2 seconds
- [ ] Database queries complete quickly
- [ ] No timeout errors

---

## 📝 SAVE YOUR URLS & CREDENTIALS

Copy these and save somewhere safe (password manager or notes):

```
=== PRODUCTION URLS ===
Frontend: https://sniper-frontend-xxxxx.onrender.com
Backend: https://sniper-backend-xxxxx.onrender.com/api/v1
Health Check: https://sniper-backend-xxxxx.onrender.com/health

=== DATABASE ===
Connection String: postgresql://user:pass@host:5432/sniper
Host: [host from Render]
Port: 5432
User: postgres
Password: [password from Render]

=== API KEYS ===
Clerk Publishable Key: pk_[...] (frontend visible)
Clerk Secret Key: sk_[...] (backend secret)
JWKS URL: https://[instance].clerk.accounts.dev/.well-known/jwks.json
OpenAI Key: sk-[...] (if using AI features)

=== GITHUB ===
Repository: https://github.com/[user]/sniper-platform
Main branch: master or main
```

---

## 🚀 YOU'RE LIVE!

- [ ] **Checklist 100% complete**
- [ ] **Both services running**
- [ ] **Database connected**
- [ ] **Authentication working**
- [ ] **User can login**
- [ ] **URL ready to share**

---

## 📤 SHARE YOUR PROJECT

Your project is now live! You can share with:

- [ ] Professors/instructors
- [ ] Team members
- [ ] Friends & family
- [ ] LinkedIn portfolio
- [ ] GitHub profile
- [ ] Resume

Example message:
```
🚀 I deployed my trading platform!
Frontend: [Your URL]
Built with: Next.js + FastAPI + PostgreSQL + Quantum Computing
Check it out!
```

---

## 🔧 ONGOING MAINTENANCE

### Daily
- [ ] Check Render dashboard for errors
- [ ] Monitor database usage
- [ ] Watch for deployment failures

### Weekly
- [ ] Review logs for anomalies
- [ ] Check performance metrics
- [ ] Update environment variables if needed

### Monthly
- [ ] Back up database
- [ ] Review cost ($7 for PostgreSQL)
- [ ] Plan upgrades if needed

---

## 📞 IF SOMETHING BREAKS

### Restart Service
1. Render dashboard → Service name
2. Click **Manual Deploy**
3. Wait 2-3 minutes

### Check Logs
1. Render dashboard → Service name
2. **Logs** tab
3. Look for error messages
4. Search for key error words

### Common Fixes

| Problem | Fix |
|---------|-----|
| 502 Bad Gateway | Restart service, check logs |
| Blank page | Check browser console (F12), wait for build |
| Can't login | Verify Clerk keys in environment |
| Database error | Check DATABASE_URL, verify PostgreSQL status |
| Out of memory | Upgrade to paid tier |

---

## ✅ DEPLOYMENT COMPLETE

You did it! 🎉

Your Sniper trading platform is now live on the internet.

**Next steps:**
1. Share the URL
2. Test with real users
3. Gather feedback
4. Plan improvements
5. Consider upgrading for production

---

**Date Deployed**: _______________
**Deployed By**: _______________
**Notes**: _______________

---

Last updated: 2025-02-18
