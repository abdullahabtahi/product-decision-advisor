"""Product Decision Advisor — ADK agent definition."""

import logging
import os
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext
from google.genai import types as genai_types

from .prompts import BASE_INSTRUCTION
from .skill_router import route_skill_callback

# Hard cap: search_transcripts may be called at most this many times per invocation.
# Prompts are suggestions; callbacks are laws. This prevents runaway loops.
_raw_search_cap = os.getenv("MAX_SEARCH_CALLS", "2")
try:
    _MAX_SEARCH_CALLS = int(_raw_search_cap)
except ValueError:
    raise ValueError(
        f"MAX_SEARCH_CALLS must be an integer, got: {_raw_search_cap!r}"
    ) from None

_logger = logging.getLogger(__name__)

# Module-level dict for search call counting per invocation.
# We do NOT use ADK session state here because session state writes in
# before_tool_callback are NOT visible to sibling callbacks in the same model
# turn (when the model issues multiple tool calls in a single response, all
# callbacks read state before any write is committed — classic race condition).
# Invocation IDs are UUIDs, so there is no cross-session interference.
# Cloud Run instances are short-lived; this dict stays naturally bounded.
_search_call_counts: dict[str, int] = {}


def _enforce_search_cap(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> dict[str, Any] | None:
    """Before-tool callback: hard-cap search_transcripts at _MAX_SEARCH_CALLS per invocation.

    Returns a synthetic tool response (blocking the real call) when the cap is
    hit, with a clear signal so the LLM knows to synthesize from what it has.
    Returns None for all other tools (pass-through).

    Uses a module-level dict keyed by invocation_id (not ADK session state)
    to avoid the race condition where sibling callbacks in the same model turn
    all read the same stale counter before any write is committed.
    """
    if tool.name != "search_transcripts":
        return None

    # Correct path: invocation_id lives on invocation_context, not ToolContext directly.
    ic = getattr(tool_context, "invocation_context", None)
    inv_id = getattr(ic, "invocation_id", None) if ic is not None else None
    key = str(inv_id) if inv_id else str(id(ic if ic is not None else tool_context))

    current = _search_call_counts.get(key, 0)

    if current >= _MAX_SEARCH_CALLS:
        _logger.warning(
            "search cap_reached inv=%s calls=%d limit=%d",
            key,
            current,
            _MAX_SEARCH_CALLS,
        )
        return {
            "result": (
                f"[search_transcripts] status=cap_reached result_count=0\n"
                f"next_actions: synthesize recommendation from previous results and injected framework\n"
                f"reason: maximum {_MAX_SEARCH_CALLS} searches per question reached\n"
                "---\n"
                "No additional search performed. Use results from prior calls to synthesize."
            )
        }

    _search_call_counts[key] = current + 1
    return None


def _normalize_search_output(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict[str, Any],
) -> dict[str, Any]:
    """After-tool callback: prefix search results with a result-count signal.

    Gives the LLM an explicit quality signal so it can apply the quality-gate
    logic from the system prompt (< 2 relevant results → fallback to frameworks).
    Only fires for search_transcripts; passes all other tools through unchanged.
    """
    if tool.name != "search_transcripts":
        return tool_response

    raw = tool_response.get("result", "") or ""
    # Count non-empty result blocks (lenny-mcp separates results with blank lines)
    blocks = [b.strip() for b in str(raw).split("\n\n") if b.strip()]
    count = len(blocks)

    status = "success" if count >= 2 else ("partial" if count == 1 else "empty")
    log_fn = _logger.info if status == "success" else _logger.warning
    log_fn("search_result status=%s result_count=%d", status, count)
    header = (
        f"[search_transcripts] status={status} result_count={count}\n"
        f"next_actions: {'synthesize recommendation' if count >= 2 else 'reformulate query or fall back to injected framework'}\n"
        "---\n"
    )
    return {**tool_response, "result": header + str(raw)}


root_agent = LlmAgent(
    name="product_decision_advisor",
    model="gemini-3-flash-preview",
    description=(
        "Answers PM and founder product decisions using Lenny's Podcast insights. "
        "Use for pricing, roadmap, growth, retention, hiring, and PMF questions."
    ),
    instruction=BASE_INSTRUCTION,
    generate_content_config=genai_types.GenerateContentConfig(
        # 0.7: enough variance for conversational voice and structural variety,
        # low enough to keep grounding to retrieved evidence (0.9 risks citation hallucination in RAG agents).
        temperature=0.7,
        # top_p=0.95: nucleus sampling — cuts only the bottom 5% probability tail.
        # Works with temperature to reduce repetitive top-token sampling without
        # enabling hallucinations from low-probability tokens.
        top_p=0.95,
        max_output_tokens=4096,
        # Safety: loosen DANGEROUS_CONTENT to BLOCK_ONLY_HIGH.
        # Business language ("killing features", "burning cash", "product is dying")
        # frequently triggers the default BLOCK_MEDIUM_AND_ABOVE threshold.
        # Other categories (hate speech, harassment, sexual) remain at defaults.
        safety_settings=[
            genai_types.SafetySetting(
                category=genai_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=genai_types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
        ],
        # HTTP retries: protects against transient Vertex AI 429s and brief
        # network interruptions on Cloud Run. 2 attempts with 2s initial delay
        # adds at most ~4s overhead on failure vs. hard-failing the request.
        http_options=genai_types.HttpOptions(
            retry_options=genai_types.HttpRetryOptions(
                initial_delay=2,
                attempts=2,
            ),
        ),
    ),
    before_model_callback=route_skill_callback,
    before_tool_callback=_enforce_search_cap,
    after_tool_callback=_normalize_search_output,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://lenny-mcp.onrender.com/mcp",
                timeout=90.0,  # Render free tier cold start can take 60-90s
            ),
            # search_transcripts: primary retrieval (hard-capped at 2 calls per invocation)
            # get_episode: deep-dive — only called when same episode surfaces 2+ times
            tool_filter=["search_transcripts", "get_episode"],
        )
    ],
)
