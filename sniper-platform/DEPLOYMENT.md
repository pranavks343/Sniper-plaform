# Deployment checklist

## 1. Rotate secrets if .env was ever committed or shared

If `sniper-backend/.env` (or any file containing real keys) was ever committed to git or shared:

- **OpenAI:** Create a new API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys), delete the old one, and set `OPENAI_API_KEY` in your deployment env.
- **Clerk:** Rotate keys in the Clerk Dashboard if your Clerk secret was in a committed file.
- **Any other secrets** in `.env`: rotate them at their providers and update your deployment config.

`.env` is in `.gitignore`; keep it that way and use your host’s env or secrets manager in production.

---

## 2. Production environment variables

When deploying the **backend**, set at least:

| Variable | Example | Notes |
|----------|---------|--------|
| `ENVIRONMENT` | `production` | Hides internal error details in 500 responses |
| `ALLOWED_ORIGINS` | `https://your-app.example.com` | Comma-separated CORS origins for your frontend |
| `CIRCUIT_BREAKER_ADMIN_SECRET` | *(strong secret)* | Required to deactivate the circuit breaker |

**Generate a circuit breaker secret:**

```bash
cd sniper-backend && python scripts/generate-circuit-breaker-secret.py
```

Paste the output into `CIRCUIT_BREAKER_ADMIN_SECRET` in your production `.env` or secrets.

**Optional:** Use `sniper-backend/.env.production.example` as a template and fill in real values. Never commit the actual `.env` used in production.

---

## 3. Auth: Clerk + backend

The backend accepts **either**:

1. **Backend token** from `POST /api/v1/auth/login` (stored in frontend as `localStorage.token`), or  
2. **Clerk JWT** from the frontend (Clerk’s `getToken()`), if the backend is configured for Clerk.

**To use Clerk-only login (no separate backend login):**

1. **Backend:** Set `CLERK_JWKS_URL` in `sniper-backend/.env` to your Clerk JWKS URL. You can get it in either way:
   - **From the Clerk Dashboard:** Go to [dashboard.clerk.com](https://dashboard.clerk.com) → your application → **API Keys**. On that page you’ll see your **Frontend API** (or Issuer) URL, e.g. `https://something.clerk.accounts.dev`. Your JWKS URL is that URL + `/.well-known/jwks.json` (e.g. `https://something.clerk.accounts.dev/.well-known/jwks.json`).
   - **From your frontend publishable key:** The value after `pk_test_` or `pk_live_` is base64‑encoded. Decode it to get your Clerk domain (e.g. `assured-lobster-59.clerk.accounts.dev`). Then use `https://<that-domain>/.well-known/jwks.json` as `CLERK_JWKS_URL`. (Strip any trailing `$` from the decoded string.)

2. **Frontend:** When users sign in with Clerk, `ClerkTokenSync` (in the root layout) writes Clerk’s session token to `localStorage` so the API client sends it. No extra login step is required.

If `CLERK_JWKS_URL` is not set, the backend only accepts tokens from `POST /api/v1/auth/login` (email/password).
