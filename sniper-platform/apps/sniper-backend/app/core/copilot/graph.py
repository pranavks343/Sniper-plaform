"""LangGraph agent that powers the Trading Copilot.

Instead of firing a single LLM call, the copilot runs a small **state graph**:

    classify ──▶ (conditional routing) ──▶ risk / regime / strategy / backtest / general ──▶ END

* ``classify`` inspects the user's question and tags it with an intent.
* A conditional edge routes to a *specialist* node, each of which injects a
  focused instruction on top of the shared system prompt before calling the LLM.
* Every specialist converges on ``END`` with a populated ``reply``.

The graph is built once and cached. Nodes are async so the underlying
``llm_fn`` (an async OpenAI call) can be awaited inside ``graph.ainvoke``.

If LangGraph is not installed the module degrades gracefully: ``build_graph``
returns ``None`` and the caller falls back to a single LLM call.
"""
from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from typing import TypedDict

try:  # LangGraph is an optional dependency.
    from langgraph.graph import END, StateGraph

    _LANGGRAPH_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only when dep missing
    StateGraph = None  # type: ignore[assignment]
    END = "__end__"  # type: ignore[assignment]
    _LANGGRAPH_AVAILABLE = False


# An async callable: (system_prompt, context_blob, user_message) -> reply text.
LLMFn = Callable[[str, str, str], Awaitable[str]]


class CopilotState(TypedDict, total=False):
    """Shared state passed between graph nodes."""

    message: str
    context_blob: str
    category: str
    reply: str


# ── Intent classification ──────────────────────────────────────────────────────

# Keyword buckets keep classification deterministic, fast and free (no extra LLM
# round-trip just to route). Order matters: the first bucket with a hit wins.
_INTENT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "risk",
        re.compile(
            r"\b(risk|drawdown|delta|gamma|theta|vega|pnl|p&l|loss|losing|"
            r"circuit\s*breaker|limit|paused?|halt|stopped|exposure|var)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "regime",
        re.compile(
            r"\b(regime|trend(ing)?|mean[\s-]*revert(ing)?|volatil(e|ity)|"
            r"market\s+condition|choppy|sideways)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "backtest",
        re.compile(
            r"\b(backtest|back[\s-]*test|sharpe|win\s*rate|historical|"
            r"performance|returns?|equity\s+curve)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "strategy",
        re.compile(
            r"\b(strateg(y|ies)|signal|parameter|indicator|ema|rsi|macd|"
            r"entry|exit|suited?|configure|tune|filter)\b",
            re.IGNORECASE,
        ),
    ),
]


def classify_intent(message: str) -> str:
    """Return one of: risk | regime | backtest | strategy | general."""
    for label, pattern in _INTENT_PATTERNS:
        if pattern.search(message or ""):
            return label
    return "general"


# Specialist instructions appended to the base system prompt for each intent.
_SPECIALIST_INSTRUCTIONS: dict[str, str] = {
    "risk": (
        "FOCUS: This is a RISK question. Lead with trading_allowed status and any "
        "active violations. Explain drawdown / daily PnL / Greeks in plain language "
        "and give one concrete next step. If trading is halted, explain exactly why."
    ),
    "regime": (
        "FOCUS: This is a MARKET REGIME question. Lead with the current regime and "
        "its confidence. State whether the selected strategy's regime_filters match "
        "the current regime, and what that implies for taking signals right now."
    ),
    "backtest": (
        "FOCUS: This is a BACKTEST / PERFORMANCE question. Cite Sharpe, win rate, "
        "net PnL and max drawdown from the Last Backtest block. Do not invent "
        "numbers; if no backtest is present, say so and suggest running one."
    ),
    "strategy": (
        "FOCUS: This is a STRATEGY question. Reference the selected strategy's type, "
        "parameters and regime_filters. Tie advice back to the current regime and "
        "risk posture. If no strategy is selected, say so and give general guidance."
    ),
    "general": (
        "FOCUS: General assistance. Use whatever context is relevant and keep the "
        "answer brief and actionable."
    ),
}


# ── Graph construction ──────────────────────────────────────────────────────────

def build_graph(base_system_prompt: str, llm_fn: LLMFn):
    """Compile the copilot StateGraph, or return ``None`` if LangGraph is absent.

    ``llm_fn`` is captured by closure so specialist nodes can await it.
    """
    if not _LANGGRAPH_AVAILABLE:
        return None

    async def classify_node(state: CopilotState) -> CopilotState:
        return {"category": classify_intent(state["message"])}

    def _make_specialist(category: str):
        instruction = _SPECIALIST_INSTRUCTIONS[category]

        async def _node(state: CopilotState) -> CopilotState:
            system_prompt = f"{base_system_prompt}\n\n{instruction}"
            reply = await llm_fn(
                system_prompt,
                state.get("context_blob", ""),
                state["message"],
            )
            return {"reply": reply}

        _node.__name__ = f"{category}_node"
        return _node

    graph = StateGraph(CopilotState)
    graph.add_node("classify", classify_node)
    for category in _SPECIALIST_INSTRUCTIONS:
        graph.add_node(category, _make_specialist(category))

    graph.set_entry_point("classify")
    graph.add_conditional_edges(
        "classify",
        lambda state: state["category"],
        {category: category for category in _SPECIALIST_INSTRUCTIONS},
    )
    for category in _SPECIALIST_INSTRUCTIONS:
        graph.add_edge(category, END)

    return graph.compile()


async def run_copilot(
    base_system_prompt: str,
    context_blob: str,
    message: str,
    llm_fn: LLMFn,
) -> str | None:
    """Run the copilot graph end-to-end. Returns ``None`` if the graph is unavailable.

    The graph is compiled per call (construction is cheap and the captured
    ``llm_fn`` carries per-request transport config).
    """
    graph = build_graph(base_system_prompt, llm_fn)
    if graph is None:
        return None
    result = await graph.ainvoke(
        {"message": message, "context_blob": context_blob}
    )
    return result.get("reply")
