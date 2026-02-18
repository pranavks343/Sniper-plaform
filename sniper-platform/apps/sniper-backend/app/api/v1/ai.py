"""
AI Trading Copilot endpoint.

POST /api/v1/ai/chat
  body: { message: str, context: AIChatContext }
  reply: { reply: str }

Uses OpenAI Chat Completions via REST API.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings
from app.dependencies import Container, get_container, verify_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/ai', tags=['ai'])

# ── Request / response schemas ────────────────────────────────────────────────

class AIChatContext(BaseModel):
    strategy_id: str | None = None
    page: str | None = None          # dashboard | strategies | strategies-builder | live-trading | analytics | risk | assistant
    include_regime: bool = True
    include_risk: bool = True
    include_positions: bool = False
    include_backtest: bool = False


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    context: AIChatContext = Field(default_factory=AIChatContext)


class AIChatResponse(BaseModel):
    reply: str


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a concise expert Trading Copilot for the Sniper algorithmic trading platform.

You receive a Context block with:
- Current page the user is viewing
- Selected strategy: name, type, regime_filters, parameters, status
- Current market regime and confidence (TRENDING / MEAN_REVERTING / VOLATILE)
- Risk metrics: delta, gamma, theta, vega, daily PnL, drawdown, trading_allowed
- Risk violations (if any)
- Optionally: open positions summary, last backtest summary

Rules:
- Use ONLY the information in the context. Never invent numbers.
- Answer briefly and actionably (2-5 sentences unless more detail is needed).
- For "why did my algo pause?" — check trading_allowed, violations, and whether regime matches strategy regime_filters.
- For "is this strategy suited to current regime?" — compare regime_filters to current regime and confidence.
- For risk questions — explain in plain language and suggest concrete next steps.
- When relevant, reference: (1) market regime & confidence, (2) strategy regime_filters match/mismatch, (3) risk limits & violations, (4) daily PnL & drawdown.
- If context is missing (e.g. no strategy selected), say so and give general guidance.
- Be direct. No disclaimers or filler phrases."""


# ── LLM call (OpenAI) ─────────────────────────────────────────────────────────

async def _call_llm(
    system_prompt: str,
    context_blob: str,
    user_message: str,
    api_key: str,
    model: str,
    request_timeout_seconds: float,
    retry_delay_seconds: float,
    max_retries: int,
) -> str:
    """Call OpenAI Chat Completions API and return the model reply text."""
    url = 'https://api.openai.com/v1/chat/completions'
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"<Context>\n{context_blob}\n</Context>\n\nUser: {user_message}",
            }
        ],
        "temperature": 0.3,
        "max_tokens": 512,
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    timeout = httpx.Timeout(
        timeout=request_timeout_seconds,
        connect=min(10.0, request_timeout_seconds),
    )
    attempts = max(1, int(max_retries) + 1)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = None
        for attempt in range(attempts):
            try:
                resp = await client.post(url, json=payload, headers=headers)
            except httpx.TimeoutException as exc:
                raise HTTPException(
                    status_code=504,
                    detail='AI provider timed out. Please retry in a few seconds.',
                ) from exc
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=502,
                    detail='Failed to reach AI provider. Please retry shortly.',
                ) from exc

            if resp.status_code not in (429, 500, 502, 503, 504) or attempt == attempts - 1:
                break
            await asyncio.sleep(max(0.0, retry_delay_seconds))

    if resp is None:
        raise HTTPException(status_code=502, detail='AI provider did not return a response')

    if resp.status_code != 200:
        logger.error("OpenAI API error %s: %s", resp.status_code, resp.text[:500])
        if resp.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="AI rate limit exceeded. Please wait a moment and try again.",
            )
        if resp.status_code == 401:
            raise HTTPException(
                status_code=502,
                detail='Invalid OpenAI API key. Update OPENAI_API_KEY in sniper-backend/.env',
            )
        raise HTTPException(status_code=502, detail=f"LLM upstream error ({resp.status_code})")

    data = resp.json()
    try:
        content: Any = data["choices"][0]["message"]["content"]
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            text_parts = [part.get("text", "") for part in content if isinstance(part, dict)]
            return "".join(text_parts).strip()
        raise ValueError('unexpected content type')
    except (KeyError, IndexError) as exc:
        logger.error("Unexpected OpenAI response shape: %s", json.dumps(data)[:500])
        raise HTTPException(status_code=502, detail="Unexpected LLM response format") from exc
    except ValueError as exc:
        logger.error("Unexpected OpenAI content format: %s", json.dumps(data)[:500])
        raise HTTPException(status_code=502, detail="Unexpected LLM response format") from exc


# ── Context assembly ──────────────────────────────────────────────────────────

async def _assemble_context(ctx: AIChatContext, container: Container) -> str:
    lines: list[str] = []

    # Page
    lines.append(f"Page: {ctx.page or 'unknown'}")
    lines.append("")

    # Strategy
    if ctx.strategy_id:
        try:
            strat = await container.strategy_service.get(ctx.strategy_id)
            lines.append("=== Selected Strategy ===")
            lines.append(f"Name       : {strat.get('name', 'N/A')}")
            lines.append(f"Type       : {strat.get('type', 'N/A')}")
            lines.append(f"Status     : {strat.get('status', 'N/A')}")
            regime_filters = strat.get("regime_filters") or strat.get("parameters", {}).get("regime_filters", [])
            lines.append(f"Regime filters: {regime_filters if regime_filters else 'not set'}")
            params = strat.get("parameters", {})
            param_summary = ", ".join(f"{k}={v}" for k, v in list(params.items())[:6]) if params else "none"
            lines.append(f"Parameters : {param_summary}")
        except (KeyError, Exception):
            lines.append("Selected Strategy: not found or unavailable")
    else:
        lines.append("Selected Strategy: none")
    lines.append("")

    # Market regime (derived from quantum/strategy service or simple heuristic)
    if ctx.include_regime:
        lines.append("=== Market Regime ===")
        try:
            # Try quantum status for regime data
            qstatus = container.quantum_service.get_status()
            regime = getattr(qstatus, "regime", None) or "UNKNOWN"
            confidence = getattr(qstatus, "regime_confidence", None)
        except Exception:
            regime, confidence = "UNKNOWN", None
        # Fallback: use risk metrics volatility proxy
        if regime == "UNKNOWN":
            try:
                risk = await container.risk_service.get_metrics()
                vega = abs(float(risk.get("vega", 0)))
                # crude heuristic: high vega → volatile
                if vega > 8000:
                    regime, confidence = "VOLATILE", 0.70
                elif vega < 2000:
                    regime, confidence = "TRENDING", 0.75
                else:
                    regime, confidence = "MEAN_REVERTING", 0.65
            except Exception:
                regime, confidence = "UNKNOWN", None
        conf_str = f"{confidence:.0%}" if confidence else "N/A"
        lines.append(f"Current Regime    : {regime}")
        lines.append(f"Regime Confidence : {conf_str}")
        lines.append("")

    # Risk metrics
    if ctx.include_risk:
        lines.append("=== Risk Metrics ===")
        try:
            risk = await container.risk_service.get_metrics()
            lines.append(f"Daily P&L      : {risk.get('daily_pnl', 'N/A')}")
            lines.append(f"Drawdown       : {risk.get('drawdown', 'N/A')}")
            lines.append(f"Delta          : {risk.get('delta', 'N/A')}")
            lines.append(f"Gamma          : {risk.get('gamma', 'N/A')}")
            lines.append(f"Theta          : {risk.get('theta', 'N/A')}")
            lines.append(f"Vega           : {risk.get('vega', 'N/A')}")
            trading_allowed = risk.get("trading_allowed", True)
            lines.append(f"Trading Allowed: {'YES' if trading_allowed else 'NO — circuit breaker or limit hit'}")
        except Exception as exc:
            lines.append(f"Risk metrics unavailable: {exc}")
        try:
            violations = await container.risk_service.get_violations()
            if violations:
                lines.append(f"Violations     : {len(violations)} active")
                for v in violations[:3]:
                    lines.append(f"  - {v.get('type', '?')}: {v.get('message', str(v))}")
            else:
                lines.append("Violations     : none")
        except Exception:
            lines.append("Violations     : unavailable")
        lines.append("")

    # Positions
    if ctx.include_positions:
        lines.append("=== Open Positions ===")
        try:
            positions = container.execution_service.get_positions()
            if positions:
                lines.append(f"Total open: {len(positions)}")
                for p in positions[:5]:
                    sym = p.get("symbol", "?")
                    qty = p.get("quantity", 0)
                    pnl = p.get("pnl", 0)
                    lines.append(f"  {sym}: qty={qty}, pnl={pnl:.2f}")
            else:
                lines.append("No open positions.")
        except Exception as exc:
            lines.append(f"Positions unavailable: {exc}")
        lines.append("")

    # Last backtest
    if ctx.include_backtest and ctx.strategy_id:
        lines.append("=== Last Backtest ===")
        try:
            all_bt = await container.backtest_service.list_backtests()
            # find most recent for this strategy
            relevant = [b for b in all_bt if str(b.get("strategy_id")) == ctx.strategy_id]
            if relevant:
                bt = relevant[-1]
                metrics = bt.get("metrics", {}) or {}
                lines.append(f"Status        : {bt.get('status', 'N/A')}")
                lines.append(f"Net PnL       : {metrics.get('net_pnl', 'N/A')}")
                lines.append(f"Sharpe        : {metrics.get('sharpe_ratio', 'N/A')}")
                lines.append(f"Win Rate      : {metrics.get('win_rate', 'N/A')}")
                lines.append(f"Max Drawdown  : {metrics.get('max_drawdown', 'N/A')}")
            else:
                lines.append("No backtest found for this strategy.")
        except Exception as exc:
            lines.append(f"Backtest unavailable: {exc}")
        lines.append("")

    return "\n".join(lines)


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    payload: AIChatRequest,
    container: Container = Depends(get_container),
    _: str = Depends(verify_token),
) -> AIChatResponse:
    settings = get_settings()
    api_key: str = getattr(settings, "openai_api_key", "") or ""
    model: str = getattr(settings, "openai_model", "gpt-4o-mini") or "gpt-4o-mini"
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI Copilot is not configured. Set OPENAI_API_KEY in sniper-backend/.env",
        )

    context_blob = await _assemble_context(payload.context, container)
    reply = await _call_llm(
        SYSTEM_PROMPT,
        context_blob,
        payload.message,
        api_key,
        model,
        float(getattr(settings, 'openai_request_timeout_seconds', 45.0)),
        float(getattr(settings, 'openai_retry_delay_seconds', 1.5)),
        int(getattr(settings, 'openai_max_retries', 1)),
    )
    return AIChatResponse(reply=reply)
