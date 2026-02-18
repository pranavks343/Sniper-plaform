# Sniper Platform — Complete Step-by-Step Deployment Guide

**Target**: Deploy to Render (Recommended for college projects)
**Time**: ~30 minutes total
**Cost**: ~$7/month (PostgreSQL only, compute is free tier)

---

## 🎯 Prerequisites Checklist

Before starting, ensure you have:

- [ ] GitHub account (for pushing code)
- [ ] Render account (sign up at render.com)
- [ ] Clerk account with API keys (sign up at clerk.com)
- [ ] OpenAI API key (optional, for AI assistant)
- [ ] Git installed locally
- [ ] Terminal/command line access

---

## 📋 PART 1: Prepare Your Code (10 minutes)

### Step 1.1: Verify All Code is Committed

```bash
cd /Users/pranavks/project/sniper-platform

# Check status
git status

# Should show "nothing to commit, working tree clean"
# If not, commit your changes:
git add .
git commit -m "feat: deployment-ready with security hardening"
git push origin main
```

**Expected output:**
```
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

---

### Step 1.2: Verify Environment Files Exist

```bash
# Check frontend env example
ls -la apps/sniper/.env.example

# Check backend env example
ls -la apps/sniper-backend/.env.example
```

**Expected output:**
```
-rw-r--r--  1 pranavks  staff  XXX Feb 18 20:00 .env.example
```

---

### Step 1.3: Test Locally (Optional but Recommended)

```bash
# Start local services
docker-compose up -d

# Wait 30 seconds for services to start

# Test frontend
curl http://localhost:3000

# Test backend
curl http://localhost:8000/health

# Stop services
docker-compose down
```

---

## 🌐 PART 2: Deploy to Render (20 minutes)

### Step 2.1: Create Render Account

1. Go to **https://render.com**
2. Click **Sign Up**
3. Choose **Sign up with GitHub**
4. Authorize Render to access your GitHub account
5. Accept terms and create account

**Expected**: Dashboard loads with "New" button visible

---

### Step 2.2: Deploy PostgreSQL Database

1. In Render dashboard, click **New +**
2. Select **PostgreSQL**
3. Fill in:
   - **Name**: `sniper-db`
   - **Database**: `sniper`
   - **User**: `postgres`
   - **Region**: Choose closest to you (e.g., `us-east`)
   - **PostgreSQL Version**: `16`
4. Click **Create Database**
5. **Wait 2-3 minutes** for database to initialize

**You'll see:**
```
Status: Available ✓
```

6. Copy the connection string (under "Connections"):
   ```
   postgresql://user:password@host:5432/sniper
   ```
   Save this somewhere — you'll need it soon.

---

### Step 2.3: Deploy Backend (FastAPI)

1. Click **New +** → **Web Service**
2. **Connect your repository**:
   - Click **Connect a GitHub repository**
   - Search for `sniper-platform`
   - Click **Connect**
3. Fill in configuration:
   - **Name**: `sniper-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `apps/sniper-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**:
     ```
     alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
     ```

4. **Add Environment Variables** (scroll down):
   ```
   KEY                              VALUE
   ENVIRONMENT                      production
   DATABASE_URL                     [PASTE from step 2.2]
   ALLOWED_ORIGINS                  ["https://sniper-frontend.onrender.com"]
   CLERK_JWKS_URL                   https://your-instance.clerk.accounts.dev/.well-known/jwks.json
   OPENAI_API_KEY                   sk-[your key or leave blank]
   OPENAI_MODEL                     gpt-4o-mini
   ```

5. Click **Create Web Service**

6. **Wait 5-8 minutes** for build and deployment

**You'll see:**
```
=== Deploying main ✓
Build started
... [build logs] ...
Build succeeded ✓
```

7. Note your backend URL: `https://sniper-backend-xxxxx.onrender.com`

---

### Step 2.4: Deploy Frontend (Next.js)

1. Click **New +** → **Web Service**
2. **Connect your repository**:
   - Select `sniper-platform` (if not already shown)
3. Fill in configuration:
   - **Name**: `sniper-frontend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `apps/sniper`
   - **Runtime**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`

4. **Add Environment Variables**:
   ```
   KEY                                    VALUE
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY      pk_test_[your key]
   NEXT_PUBLIC_API_BASE_URL               https://sniper-backend-xxxxx.onrender.com/api/v1
   NODE_ENV                               production
   ```

5. Click **Create Web Service**

6. **Wait 5-8 minutes** for build and deployment

**You'll see:**
```
=== Deploying main ✓
Build started
... [build logs] ...
Build succeeded ✓
```

7. Note your frontend URL: `https://sniper-frontend-xxxxx.onrender.com`

---

## ✅ PART 3: Verify Deployment (5 minutes)

### Step 3.1: Check Backend Health

Open in browser or terminal:
```bash
curl https://sniper-backend-xxxxx.onrender.com/health
```

**Expected response:**
```json
{"status": "ok"}
```

---

### Step 3.2: Check Frontend Loads

1. Open browser
2. Go to: `https://sniper-frontend-xxxxx.onrender.com`
3. Should see Sniper login page

**If blank or error:**
- Wait another 2 minutes
- Check dashboard → frontend service → logs

---

### Step 3.3: Test Login

1. Click **Sign In** (or Sign Up if no account)
2. Use Clerk authentication
3. Should redirect to dashboard

---

### Step 3.4: Update Frontend Backend URL (If Needed)

If frontend can't reach backend:

1. Go to Render dashboard → **sniper-frontend**
2. Go to **Environment**
3. Update `NEXT_PUBLIC_API_BASE_URL` to your actual backend URL
4. Click **Save Changes**
5. Service auto-redeploys (wait 2 minutes)

---

## 🔐 PART 4: Configure Clerk (5 minutes)

### Step 4.1: Get Clerk Keys

1. Go to **https://dashboard.clerk.com**
2. Select your application
3. Go to **API Keys** (sidebar)
4. Copy **Publishable Key** (starts with `pk_test_` or `pk_live_`)
5. Copy **Secret Key** (starts with `sk_test_` or `sk_live_`)

---

### Step 4.2: Add to Render Frontend

1. Render dashboard → **sniper-frontend**
2. **Environment** section
3. Update `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` with your key
4. Save and auto-redeploys

---

### Step 4.3: Get JWKS URL (For Backend)

1. Clerk dashboard → **API Keys**
2. Under **Advanced**, find **JWKS URL**
3. Copy it (format: `https://[your-instance].clerk.accounts.dev/.well-known/jwks.json`)

---

### Step 4.4: Add to Render Backend

1. Render dashboard → **sniper-backend**
2. **Environment** section
3. Update `CLERK_JWKS_URL` with your URL
4. Save and auto-redeploys

---

## 🧪 PART 5: Test Key Features (5 minutes)

### Step 5.1: Test Authentication

```bash
# Get frontend URL
FRONTEND_URL="https://sniper-frontend-xxxxx.onrender.com"

# Visit in browser
open $FRONTEND_URL

# Click Sign In/Up, complete authentication
```

**Expected**: Redirects to dashboard after login

---

### Step 5.2: Test API Endpoint (With Auth)

1. Login to frontend
2. Open browser DevTools (F12)
3. Go to **Application** → **Local Storage**
4. Find token value
5. In terminal:
   ```bash
   TOKEN="[paste token here]"
   curl -H "Authorization: Bearer $TOKEN" \
     https://sniper-backend-xxxxx.onrender.com/api/v1/strategy/
   ```

**Expected**: Returns list of strategies (empty `[]` is OK)

---

### Step 5.3: Test Without Auth (Should Fail)

```bash
curl https://sniper-backend-xxxxx.onrender.com/api/v1/strategy/
```

**Expected response:**
```json
{"detail": "Missing Authorization header"}
```

✅ This means auth is working!

---

## 🚀 PART 6: Next Steps & Customization

### Option A: Use Paid Render Tier (Recommended for Production)

Current setup uses **free compute tier** (512MB RAM). For production:

1. Render dashboard → **sniper-backend**
2. Click **Upgrade** button
3. Choose plan (Starter ~$7/month)
4. Benefits: More RAM, better performance, paid support

---

### Option B: Add Custom Domain

1. Render dashboard → **sniper-frontend**
2. **Custom Domain** section
3. Add your domain (e.g., `trading.yourdomain.com`)
4. Follow DNS setup instructions

---

### Option C: Enable Auto-Deploy on GitHub Push

Already enabled! Any push to `main` branch auto-deploys.

To disable:
1. Render dashboard → Service
2. **Settings** → Uncheck **Auto-Deploy**

---

## 📊 Monitor Deployment

### Check Status Anytime

```bash
# Backend
curl https://sniper-backend-xxxxx.onrender.com/health

# Frontend (browser)
open https://sniper-frontend-xxxxx.onrender.com
```

---

### View Logs

1. Render dashboard → Select service
2. **Logs** tab shows real-time output
3. Useful for debugging

---

### Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| **502 Bad Gateway** | Backend crashed; check logs, restart service |
| **Frontend blank** | Wait 2 min for build, check `NEXT_PUBLIC_API_BASE_URL` |
| **Can't authenticate** | Check Clerk publishable key, JWKS URL |
| **Database connection error** | Check `DATABASE_URL`, ensure PostgreSQL is running |
| **"Killed: 9"** | Out of memory; upgrade to paid tier |

---

## 🎯 Final Checklist

- [ ] GitHub repository pushed
- [ ] PostgreSQL deployed and running
- [ ] Backend deployed and `/health` responding
- [ ] Frontend deployed and loads
- [ ] Clerk authentication working
- [ ] Backend API requires auth token
- [ ] Backend URL in frontend config
- [ ] Frontend accessible from browser
- [ ] Can login and see dashboard

---

## 📝 Save These URLs

```
Frontend: https://sniper-frontend-xxxxx.onrender.com
Backend: https://sniper-backend-xxxxx.onrender.com
Database: postgresql://user:pass@host:5432/sniper
```

---

## 🚀 You're Live!

Your Sniper trading platform is now deployed to production.

**Share with:**
- ✅ College instructors
- ✅ Team members
- ✅ Friends & family
- ✅ LinkedIn/portfolio

**Total cost**: ~$7/month for PostgreSQL (compute is free)

---

## 📞 Troubleshooting

### If Frontend Won't Load

```bash
# 1. Check if service is running
# Render dashboard → sniper-frontend → check Status

# 2. View build logs
# Render dashboard → sniper-frontend → Logs

# 3. Verify environment variables
# Render dashboard → sniper-frontend → Environment
# Check: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY exists

# 4. Restart service
# Render dashboard → sniper-frontend → Manual Deploy
```

---

### If Backend Returns Errors

```bash
# 1. Check database connection
# Render dashboard → PostgreSQL → check Status

# 2. View application logs
# Render dashboard → sniper-backend → Logs

# 3. Check environment variables
# Render dashboard → sniper-backend → Environment
# Verify all keys are set

# 4. Restart service
# Render dashboard → sniper-backend → Manual Deploy
```

---

### If Authentication Fails

```bash
# 1. Verify Clerk keys match
# Clerk dashboard → API Keys → Copy exact values
# Render dashboard → Update environment variables

# 2. Check JWKS URL format
# Should be: https://[instance].clerk.accounts.dev/.well-known/jwks.json

# 3. Test with curl (see Part 5.2)

# 4. Check browser console (F12 → Console)
# Look for Clerk-related errors
```

---

## 🎓 Learning Resources

- [Render Docs](https://render.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Clerk Documentation](https://clerk.com/docs)

---

**Good luck with your deployment! 🚀**

Last updated: 2025-02-18
