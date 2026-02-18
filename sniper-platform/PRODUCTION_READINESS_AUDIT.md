# Sniper Platform — Production/Deployment Readiness Audit

**Audit date:** February 18, 2026  
**Scope:** TypeScript/code quality, env vars, security, API, database, error handling, performance, deployment, dependencies, missing features.

---

## Fixes applied (post-audit)

The following were implemented after the audit:

- **Backend API auth:** All `/api/v1` routes except `/auth/register` and `/auth/login` now require `Authorization: Bearer <token>`. Token is validated via `AuthService.get_user_for_token`. Frontend must call `POST /api/v1/auth/login` and store the returned `token` in `localStorage` (key `token`); the existing api-client already sends it.
- **Circuit breaker:** Deactivation now requires `CIRCUIT_BREAKER_ADMIN_SECRET` in env; `admin_password` is checked with constant-time comparison. Documented in `.env.example`.
- **500 handler:** In non-`dev` environment, responses return a generic "Internal server error" instead of `str(exc)`.
- **CORS / env:** `ALLOWED_ORIGINS` (comma-separated) and `ENVIRONMENT` added to `sniper-backend/.env.example`; config parses `allowed_origins` from env.
- **Rate limiting:** `RateLimitMiddleware` added (auth 15/min, AI 30/min, API 120/min per IP).
- **.dockerignore:** Added for `sniper-backend` to exclude `.env`, `.venv`, tests, cache.
- **DB pool:** `database_pool_size`, `database_max_overflow`, `database_pool_recycle_seconds` added to config and `app/db/session.py`.
- **Root package.json:** `packageManager` added for Turborepo workspace resolution.
- **Next.js:** Bumped to `14.2.35` (security fixes).
- **Frontend env:** `NEXT_PUBLIC_WS_BASE_URL` documented in `apps/sniper/.env.local.example`.
- **Lazy loading:** `TradingViewChart` in trading-workspace is loaded via `next/dynamic` with `ssr: false`.
- **Circuit breaker API:** `deactivate_breaker` now returns 400 with a clear message when the secret is wrong or not set.

**Still required for production:** Set `ENVIRONMENT=production`, `ALLOWED_ORIGINS` to your frontend origin(s), and `CIRCUIT_BREAKER_ADMIN_SECRET` to a strong secret. Rotate any keys that were ever committed. Ensure the frontend obtains a backend token (e.g. via `/auth/login`) and sends it for all API calls.

---

## Executive Summary

| Area | Status | Critical | High | Medium | Low |
|------|--------|----------|------|--------|-----|
| TypeScript & Code Quality | ✅ Pass | 0 | 0 | 1 | 0 |
| Environment Variables | ⚠️ Review | 1 | 0 | 1 | 0 |
| Security | 🔴 Fail | 3 | 3 | 2 | 1 |
| API Integration | ⚠️ Review | 0 | 1 | 2 | 0 |
| Database | ⚠️ Review | 0 | 0 | 2 | 0 |
| Error Handling | ⚠️ Review | 0 | 1 | 1 | 0 |
| Performance | ⚠️ Review | 0 | 0 | 2 | 1 |
| Deployment Config | ⚠️ Review | 0 | 1 | 2 | 0 |
| Dependencies | ⚠️ Review | 0 | 1 | 0 | 1 |
| Missing Features | ⚠️ Review | 0 | 2 | 2 | 0 |

**Recommendation:** Do not deploy to production until Critical and High security/configuration issues are resolved.

---

## 1. TypeScript & Code Quality

### 1.1 TypeScript (`tsc --noEmit`)

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Low** | Monorepo `npm run typecheck` fails: Turborepo cannot resolve workspaces (missing `packageManager` in root `package.json`). | `package.json` (root) | Add `"packageManager": "npm@10.x"` (or your npm version) to root `package.json`. |
| ✅ | Per-app typecheck passes: `cd apps/sniper && npx tsc --noEmit` completes with no type errors. | `apps/sniper` | — |

### 1.2 Unused imports / console.log / TODO

- **console.log / console.debug / console.info:** None found in `.ts`/`.tsx`/`.js` (no cleanup needed).
- **TODO / FIXME / XXX / HACK:** None found in codebase.
- **Unused imports:** Not automatically verified; consider running `eslint-plugin-unused-imports` or your linter.

---

## 2. Environment Variables

### 2.1 Backend (`sniper-backend/`)

**Required / optional variables (from `.env.example` and `app/config.py`):**

| Variable | Required | Documented in .env.example | Notes |
|----------|----------|----------------------------|-------|
| `DATABASE_URL` | Yes | Yes | — |
| `DEFAULT_USER_ID` | Yes | Yes | — |
| `DATA_ENCRYPTION_KEY` | Optional | Yes | Empty ok for dev |
| `CONVEX_*` | Optional | Yes | — |
| `IBM_QUANTUM_*`, `QUANTUM_*` | Optional | Yes | — |
| `ZERODHA_*`, `UPSTOX_*`, `BROKER_PROVIDER` | For live brokers | Yes | — |
| `OPENAI_*` | For AI Copilot | Yes | — |
| `MAX_*` (risk) | Optional | Yes | — |
| **`ALLOWED_ORIGINS`** | **Production** | **No** | Not in `.env.example`; defaults to `['http://localhost:3000']`. |

### 2.2 Frontend (`apps/sniper/`)

**From `.env.local.example`:**

| Variable | Required | Documented | Notes |
|----------|----------|------------|-------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes (Clerk) | Yes | — |
| `CLERK_SECRET_KEY` | Yes (Clerk) | Yes | — |
| `NEXT_PUBLIC_CONVEX_URL` | Optional | Yes | — |
| `NEXT_PUBLIC_API_BASE_URL` | Optional | Yes | Default `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_WS_BASE_URL` | Used by WS client | No | Default in code: `ws://localhost:8000`; document for production. |

### 2.3 Issues

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Critical** | Real API key present in `sniper-backend/.env` (OPENAI_API_KEY). If this file was ever committed or shared, the key must be rotated. | `sniper-backend/.env` | Rotate key at provider; ensure `.env` is never committed (`.gitignore` already has `.env*`). |
| **Medium** | `ALLOWED_ORIGINS` not documented; production CORS may be too permissive or wrong. | `sniper-backend/.env.example`, `app/config.py` | Add `ALLOWED_ORIGINS=https://yourdomain.com` to `.env.example` and set in production. |

---

## 3. Security

### 3.1 Hardcoded secrets / exposed keys

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Critical** | Production `.env` file contains a real `OPENAI_API_KEY`. | `sniper-backend/.env` | Use secrets manager or env injection in production; never commit; rotate if exposed. |
| ✅ | Backend reads secrets from config/env (`app/config.py`); no hardcoded API keys in source. | `sniper-backend/app` | — |

### 3.2 Authentication & authorization

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Critical** | Backend does **not** validate Bearer tokens. All API routes (strategy, execution, risk, backtest, quantum, AI) are effectively public. | `sniper-backend/app/api/v1/*.py`, `app/dependencies.py` | Add a dependency (e.g. `get_current_user`) that validates `Authorization: Bearer <token>` (e.g. against AuthService token store or a signed JWT) and inject user identity; protect all routes except `/auth/register`, `/auth/login`, and `/health`. |
| **Critical** | Circuit breaker deactivation accepts any non-empty `admin_password`; there is no stored admin secret or verification. | `sniper-backend/app/core/risk_engine/circuit_breaker.py`, `app/api/v1/risk.py` | Require a verified admin secret (e.g. from env) and compare with `admin_password` using constant-time comparison before deactivating. |
| **High** | Auth tokens are stored in-memory only (`AuthService._tokens`); lost on restart and not validated on protected endpoints. | `sniper-backend/app/services/auth_service.py` | Either persist tokens (e.g. in DB with expiry) and validate on each request, or move to JWT/session and validate signature/session. |

### 3.3 CORS

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **High** | `allowed_origins` defaults to `['http://localhost:3000']`. If `ALLOWED_ORIGINS` is not set in production, production frontend origin will be rejected. | `sniper-backend/app/config.py`, `app/main.py` | Document and set `ALLOWED_ORIGINS` (e.g. comma-separated) for production in `.env.example` and deployment. |

### 3.4 SQL injection

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| ✅ | Queries use SQLAlchemy ORM `select()` and parameterized usage; raw `text()` is used only for schema/DDL with fixed schema names from `ALL_SCHEMAS`. | `sniper-backend/app/db/session.py`, services | No change required; avoid string-interpolated SQL with user input. |

### 3.5 XSS

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Low** | `dangerouslySetInnerHTML` used for a static theme script (no user input). | `apps/sniper/app/layout.tsx` | Acceptable; keep script static and minimal. |
| ✅ | Chart components use `innerHTML = ''` only to clear DOM; no user content. | e.g. `apps/sniper/components/charts/trading-view-chart.tsx` | — |

---

## 4. API Integration

### 4.1 Documentation

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| ✅ | FastAPI provides OpenAPI; `/docs` and `/redoc` are available by default. | `sniper-backend/app/main.py` | Optional: set `docs_url`/`redoc_url` per env (e.g. disable in prod or restrict by IP). |

### 4.2 Error handling

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **High** | Global exception handler returns `str(exc)` to the client; can leak stack traces or internal details in production. | `sniper-backend/app/main.py` (unhandled_exception_handler) | In production, return a generic message (e.g. "Internal server error") and log full `exc` server-side only. |
| **Medium** | Some endpoints catch `ValueError`/`KeyError` and return 4xx; others may propagate and hit the global 500 handler. | `sniper-backend/app/api/v1/*.py` | Consistently map business exceptions to HTTP status and safe messages; avoid leaking internals. |

### 4.3 Rate limiting & timeouts

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Medium** | No rate limiting on any endpoint; API is vulnerable to abuse/DoS. | `sniper-backend/app/main.py`, routers | Add rate limiting (e.g. slowapi, or reverse-proxy) for auth, AI, and execution endpoints. |
| ✅ | Frontend API client sets timeouts (35s default, 70s for AI chat); backend AI uses `OPENAI_REQUEST_TIMEOUT_SECONDS`. | `apps/sniper/lib/api-client.ts`, backend config | — |

---

## 5. Database

### 5.1 Migrations

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Medium** | Single Alembic revision found (`20260217_0001_ledger_baseline.py`). `init_db()` creates schemas/tables at startup; may diverge from migrations if schema is edited without new migration. | `sniper-backend/alembic/versions/`, `app/db/session.py` | Prefer running migrations in deployment (e.g. `alembic upgrade head`) and keep `init_db()` for minimal bootstrap only; add new migrations for every schema change. |

### 5.2 Schema & indexes

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| ✅ | Foreign keys have indexes (e.g. `strategy.user_id`, `Order.strategy_id`, `Order.broker_account_id`, etc.). | `sniper-backend/app/models/database/*.py` | — |
| **Medium** | No explicit connection pool size; SQLAlchemy defaults (e.g. pool_size=5) are used. For production load, tune pool. | `sniper-backend/app/db/session.py` | Add `pool_size`, `max_overflow`, and `pool_recycle` to `create_async_engine()` and document in runbooks. |

### 5.3 N+1 queries

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| ✅ | Services use single queries or explicit `select()`; no obvious N+1 pattern found in strategy, execution, auth, or backtest services. | `sniper-backend/app/services/*.py` | Continue to avoid loading relationships in loops without eager loading when adding new endpoints. |

---

## 6. Error Handling

### 6.1 Try/catch and logging

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| ✅ | Backend has a global exception handler and request logging (method, path, status, duration). | `sniper-backend/app/main.py` | — |
| **High** | 500 responses return raw exception message to client. | `sniper-backend/app/main.py` | Return generic message to client; log full exception server-side. |
| **Medium** | Frontend API interceptor maps network/timeout/504 to user-facing strings; other errors use `error.response.data.detail` or `error.message`, which may still be raw in some cases. | `apps/sniper/lib/api-client.ts` | Ensure backend never sends sensitive or stack data in `detail`; frontend can then surface `detail` safely. |

---

## 7. Performance

### 7.1 Bundle size & lazy loading

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Medium** | No `dynamic()` or `React.lazy` usage found; large routes (e.g. dashboard, charts) are in the main bundle. | `apps/sniper` | Consider `next/dynamic` for heavy components (e.g. TradingView, charts, assistant) to reduce first-load JS. |
| ✅ | Next.js build reports First Load JS per route (e.g. dashboard ~199 kB, live-trading ~255 kB); no single route excessively large. | Build output | — |

### 7.2 Images

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Low** | No use of `next/image` found; any images would be unoptimized. | `apps/sniper` | Use `next/image` for any images you add. |

### 7.3 useEffect cleanup (memory leaks)

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| ✅ | WebSocket hooks return cleanup that unsubscribes and clears intervals (`use-market-data.ts`, `use-trading-feed.ts`). | `apps/sniper/hooks/` | — |
| ✅ | Chart components (e.g. `AdvancedTradingChart`, `MultiSeriesLineChart`, `TradingViewChart`) clean up (resize observer, chart.remove(), refs, mounted flag). | `apps/sniper/components/charts/` | — |

---

## 8. Deployment Config

### 8.1 Build scripts

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| ✅ | `apps/sniper`: `npm run build` (Next.js) and `npx tsc --noEmit` succeed. | `apps/sniper/package.json` | — |
| **High** | Root `npm run typecheck` fails (Turborepo workspace resolution); CI or deploy that runs `npm run typecheck` from root will fail. | Root `package.json` | Add `packageManager` and fix workspace resolution, or run typecheck only from `apps/sniper`. |

### 8.2 Dockerfile

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Medium** | `sniper-backend/Dockerfile` uses `COPY . .`; build context may include unnecessary files. | `sniper-backend/Dockerfile` | Add a `.dockerignore` to exclude tests, `.env`, `.venv`, `__pycache__`, etc. |
| **Medium** | No `.dockerignore` in `sniper-backend/`. | `sniper-backend/` | Create `.dockerignore` (e.g. `.env`, `.venv`, `tests`, `*.pyc`, `.git`). |

### 8.3 Docker Compose

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Medium** | Backend service uses `env_file: ./sniper-backend/.env.example`; production should use real env or secrets, not example. | `docker-compose.yml` | Document that production must override `env_file` or use secrets; never deploy with `.env.example` containing empty or dev-only values. |
| ✅ | Services: frontend (node), backend (uvicorn), postgres (TimescaleDB), redis; backend depends on postgres and redis. | `docker-compose.yml` | — |

---

## 9. Dependencies

### 9.1 npm audit

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **High** | 1 high severity: Next.js 10.0.0–15.5.9 (advisories: DoS with Server Components, Image Optimizer, HTTP request deserialization). Current: 14.2.32. | `apps/sniper/package.json` | Run `npm audit` and apply fixes; `npm audit fix --force` may suggest next@14.2.35—evaluate and upgrade within your range. |

### 9.2 Deprecated / version mismatch

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Low** | npm warning: unknown env config "devdir". | Local/env | Fix or remove `devdir` from npm config to avoid future breakage. |

---

## 10. Missing Features / Wiring

### 10.1 Clerk auth

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| ✅ | Clerk is wired: `ClerkProvider` in root layout, `clerkMiddleware` protects dashboard/strategies/risk/etc., SignIn/SignUp on login/register. | `apps/sniper/app/layout.tsx`, `middleware.ts`, auth pages | — |
| **High** | Backend does not use Clerk; it has its own email/password auth and in-memory tokens. Frontend can protect routes with Clerk while backend remains open. | Backend vs frontend | Decide: either (1) validate Clerk JWT/session on backend and drop backend login, or (2) keep backend auth and add token validation so all non-public endpoints require a valid backend token. |

### 10.2 Database connection pooling

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Medium** | SQLAlchemy async engine created without explicit `pool_size`/`max_overflow`/`pool_recycle`. | `sniper-backend/app/db/session.py` | Set pool parameters for production and document. |

### 10.3 Logging

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| ✅ | Backend uses `app.utils.logger` (dictConfig, console handler, root INFO). | `sniper-backend/app/utils/logger.py`, `app/main.py` | Optional: add structured logging (JSON) and log level from env for production. |

### 10.4 Monitoring / alerting

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **Medium** | No APM, health checks beyond `/health`, or alerting detected. | — | Add health checks for DB/Redis/Convex; consider Prometheus/OpenTelemetry and alerting (e.g. PagerDuty, Slack) for errors and latency. |

---

## Summary of Fixes by Priority

### Critical (fix before production)

1. **Backend API auth:** Add token (or Clerk) verification and protect all non-public endpoints.
2. **Circuit breaker admin:** Verify `admin_password` against a stored secret (e.g. from env); do not accept any non-empty string.
3. **Secrets:** Rotate OPENAI key if `.env` was ever committed or shared; use secret manager in production.

### High

4. **500 error body:** Stop returning `str(exc)` to client; return generic message and log full error.
5. **CORS:** Document and set `ALLOWED_ORIGINS` for production.
6. **Root typecheck:** Add `packageManager` (or equivalent) so `npm run typecheck` works from root.
7. **Next.js:** Address npm audit high severity (upgrade Next.js within supported range).
8. **Clerk vs backend auth:** Unify strategy (Clerk-only with backend JWT validation, or backend token validation for all protected routes).

### Medium

9. Add rate limiting (auth, AI, execution).
10. Document `NEXT_PUBLIC_WS_BASE_URL` and production CORS in env examples.
11. Add `.dockerignore` for backend; avoid copying `.env` and dev artifacts.
12. Prefer Alembic migrations for schema changes; tune DB pool for production.
13. Consider `next/dynamic` for heavy dashboard/chart components.
14. Add monitoring/alerting and structured logging for production.

### Low

15. Add `packageManager` to root `package.json` for Turborepo.
16. Use `next/image` for any new images.

---

*End of audit.*
