"""Routes user questions to the relevant Lenny skill framework."""

from __future__ import annotations

import logging
import re
from pathlib import Path

_logger = logging.getLogger(__name__)

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest

SKILLS_DIR = Path(__file__).parent / "skills"

# Truncate injected skill content to keep context budget lean.
# SKILL.md files average 4000+ chars; we only need Core Principles + How to Help.
_SKILL_CHAR_LIMIT = 2500

# ── Session context extraction ─────────────────────────────────────────────
# Detects company type, stage, and revenue from user messages and persists
# them in session state. Injected into every subsequent turn so the agent
# doesn't ask for information the user already provided.
_USER_CONTEXT_KEY = "user_context"

# Track which skill framework was last injected so we can re-inject when
# the user switches topic mid-session (e.g., pricing turn 1 → hiring turn 2).
# We intentionally do NOT re-inject the same skill on consecutive turns —
# it's already in context and re-injection wastes tokens.
_LAST_SKILL_KEY = "last_injected_skill"

# Checked in order — first match wins per category, so more specific signals
# (e.g. "B2B SaaS") must come before broader ones (e.g. "B2B").
_COMPANY_TYPE_SIGNALS: list[tuple[str, list[str]]] = [
    ("B2B SaaS", ["b2b saas"]),
    ("B2B", ["b2b", "business-to-business", "selling to businesses", "selling to companies", "enterprise customers", "smb"]),
    ("B2C", ["b2c", "consumer app", "consumer product", "business-to-consumer", "direct-to-consumer"]),
    ("marketplace", ["marketplace", "two-sided", "supply and demand platform"]),
    ("developer tools", ["developer tool", "dev tool", "api product"]),
]

_STAGE_SIGNALS: list[tuple[str, list[str]]] = [
    ("pre-launch", ["pre-launch", "pre-revenue", "haven't launched", "before launch"]),
    ("seed", ["seed stage", "seed round", "pre-series a", "early stage startup"]),
    ("Series A", ["series a", "raised our a", "post-series a"]),
    ("growth", ["series b", "growth stage", "scale-up"]),
    ("late stage", ["series c", "late stage", "pre-ipo"]),
]

# Matches revenue mentions like "$50k MRR", "$2m ARR", "$1.5M monthly recurring revenue"
_REVENUE_RE = re.compile(
    r"\$\s*\d[\d,.]*\s*(?:k|m)?\s*(?:mrr|arr|monthly recurring revenue|annual recurring revenue)",
    re.IGNORECASE,
)

SKILL_MAP: dict[str, list[str]] = {
    # ── Core PM decisions (original 15) ──────────────────────────────────────
    "pricing-strategy": [
        "price",
        "pricing",
        "monetiz",
        "freemium",
        "paid plan",
        "subscription",
        "willingness to pay",
        "wtp",
        "revenue model",
        "charge",
        "tiering",
        "packaging",
    ],
    "prioritizing-roadmap": [
        "priorit",
        "product roadmap",
        "backlog",
        "which feature",
        "rice",
        "ice framework",
        "stack rank",
        "feature requests",
    ],
    "retention-engagement": [
        "retention",
        "churn",
        "engagement",
        "dau",
        "wau",
        "reduce churn",
        "keep users",
        "bring users back",
    ],
    "measuring-product-market-fit": [
        "product market fit",
        "pmf",
        "sean ellis",
        "do we have fit",
        "how do i know if",
        "validation",
    ],
    "designing-growth-loops": [
        "growth loop",
        "viral",
        "referral",
        "plg",
        "product-led growth",
        "k-factor",
        "word of mouth",
        "organic growth",
    ],
    "evaluating-candidates": [
        "first pm",
        "pm hire",
        "interview process",
        "when to hire",
        "hiring loop",
        "evaluate candidate",
        "assess candidate",
    ],
    "defining-product-vision": [
        "product vision",
        "mission statement",
        "where are we going",
        "long-term direction",
    ],
    "marketplace-liquidity": [
        "marketplace",
        "liquidity",
        "supply side",
        "demand side",
        "two-sided",
        "chicken and egg",
        "multi-sided",
    ],
    "positioning-messaging": [
        "positioning",
        "messaging",
        "differentiat",
        "tagline",
        "value proposition",
        "how do we describe",
        "what do we say",
    ],
    "product-led-sales": [
        "product-led sales",
        "pls",
        "sales motion",
        "expansion revenue",
        "bottom-up sales",
        "convert free to paid",
        "free to enterprise",
    ],
    "setting-okrs-goals": [
        "okr",
        "objective",
        "key result",
        "kpi",
        "how do we measure",
        "team goals",
        "quarterly goals",
    ],
    "stakeholder-alignment": [
        "stakeholder",
        "alignment",
        "executive buy-in",
        "get approval",
        "convince leadership",
        "executive support",
        "cross-functional alignment",
    ],
    "conducting-user-interviews": [
        "user interview",
        "user research",
        "customer discovery",
        "talk to users",
        "qualitative research",
        "discovery interview",
    ],
    "evaluating-trade-offs": [
        "trade-off",
        "tradeoff",
        "make vs buy",
        "dilemma",
        "pros and cons",
        "which option",
    ],
    "founder-sales": [
        "founder sales",
        "first customer",
        "close deal",
        "early sales",
        "sell myself",
        "do sales as founder",
    ],

    # ── Product definition & discovery ───────────────────────────────────────
    "working-backwards": [
        "work backwards",
        "working backwards",
        "pr faq",
        "press release",
        "amazon method",
        "start from customer",
        "future press release",
    ],
    "problem-definition": [
        "problem statement",
        "define the problem",
        "root cause",
        "problem space",
        "what problem",
        "problem worth solving",
        "frame the problem",
    ],
    "writing-prds": [
        "prd",
        "product requirements",
        "product spec",
        "requirements doc",
        "feature brief",
        "write a spec",
        "document requirements",
    ],
    "writing-specs-designs": [
        "technical spec",
        "design doc",
        "feature spec",
        "write a design",
        "spec for engineers",
        "architecture document",
    ],
    "scoping-cutting": [
        "scope creep",
        "scope cut",
        "mvp",
        "what to cut",
        "descope",
        "minimum viable",
        "reduce scope",
    ],
    "product-taste-intuition": [
        "product taste",
        "product intuition",
        "product judgment",
        "design quality",
        "good product",
        "what makes a great",
        "product sense",
    ],

    # ── Shipping & execution ──────────────────────────────────────────────────
    "shipping-products": [
        "ship faster",
        "shipping velocity",
        "release cadence",
        "how to launch",
        "launch process",
        "deploy to production",
        "release practice",
    ],
    "launch-marketing": [
        "product launch",
        "go to market",
        "gtm",
        "launch campaign",
        "product hunt",
        "generate buzz",
        "launch strategy",
        "announce",
    ],
    "planning-under-uncertainty": [
        "plan under uncertainty",
        "ambiguous timeline",
        "fast-moving market",
        "planning without knowing",
        "planning with ai",
        "unpredictable market",
        "how to plan when",
    ],
    "dogfooding": [
        "dogfood",
        "eat your own",
        "use your own product",
        "internal usage",
        "team using product",
        "build user empathy",
    ],
    "post-mortems-retrospectives": [
        "postmortem",
        "post-mortem",
        "retrospective",
        "retro",
        "what went wrong",
        "learn from failure",
        "incident review",
    ],

    # ── Growth & acquisition ──────────────────────────────────────────────────
    "user-onboarding": [
        "onboarding",
        "activation",
        "aha moment",
        "first time user",
        "new user experience",
        "day one",
        "time to value",
        "first 30 seconds",
    ],
    "competitive-analysis": [
        "competitor",
        "competitive analysis",
        "competitive moat",
        "versus competitor",
        "how to compete",
        "market threat",
        "war game",
        "beat competition",
    ],
    "community-building": [
        "community",
        "ambassador program",
        "community-led growth",
        "user community",
        "developer community",
        "build community",
    ],
    "analyzing-user-feedback": [
        "user feedback",
        "nps",
        "customer feedback",
        "support tickets",
        "feedback patterns",
        "synthesize feedback",
        "analyze feedback",
    ],
    "designing-surveys": [
        "survey",
        "survey design",
        "nps survey",
        "feedback form",
        "questionnaire",
        "measure satisfaction",
    ],
    "usability-testing": [
        "usability test",
        "user test",
        "prototype validation",
        "usability study",
        "why users struggle",
        "usability issue",
    ],

    # ── Technical & platform ──────────────────────────────────────────────────
    "technical-roadmaps": [
        "technical roadmap",
        "tech debt roadmap",
        "engineering roadmap",
        "architecture roadmap",
        "align tech and product",
    ],
    "managing-tech-debt": [
        "tech debt",
        "technical debt",
        "legacy code",
        "refactor",
        "rewrite vs",
        "build vs maintain",
    ],
    "platform-strategy": [
        "platform strategy",
        "platform business",
        "ecosystem",
        "api strategy",
        "developer platform",
        "network effects",
        "build a platform",
    ],
    "evaluating-new-technology": [
        "evaluate technology",
        "new technology",
        "build vs buy",
        "buy vs build",
        "ai vendor",
        "technical architecture decision",
        "which tool to use",
        "technology assessment",
    ],

    # ── AI & modern product ───────────────────────────────────────────────────
    "ai-product-strategy": [
        "ai product",
        "llm product",
        "ai roadmap",
        "ai feature",
        "where to apply ai",
        "ai in product",
        "ai integration",
        "build ai",
    ],
    "building-with-llms": [
        "build with llm",
        "language model",
        "ai agent",
        "rag",
        "prompt engineering",
        "ai output quality",
        "llm application",
        "genai product",
    ],

    # ── Sales & enterprise ────────────────────────────────────────────────────
    "enterprise-sales": [
        "enterprise",
        "enterprise deal",
        "buying committee",
        "procurement",
        "large deal",
        "b2b sales",
        "convert to enterprise",
    ],
    "sales-qualification": [
        "qualify leads",
        "lead qualification",
        "bad leads",
        "discovery call",
        "meddic",
        "champion",
        "sales conversion",
    ],
    "partnership-bd": [
        "partnership",
        "business development",
        "bd deal",
        "distribution partner",
        "strategic partner",
        "partner with",
        "channel partner",
    ],

    # ── Startup & org ─────────────────────────────────────────────────────────
    "startup-ideation": [
        "startup idea",
        "idea validation",
        "business idea",
        "find an idea",
        "evaluate idea",
        "new startup",
    ],
    "startup-pivoting": [
        "pivot",
        "pivoting",
        "change direction",
        "poor traction",
        "not working",
        "consider pivot",
        "when to pivot",
    ],
    "fundraising": [
        "fundraise",
        "fundraising",
        "raise capital",
        "pitch deck",
        "investor",
        "venture capital",
        "seed round",
        "series a",
    ],
    "product-operations": [
        "product ops",
        "product operations",
        "scale product team",
        "cross-functional coordination",
        "product process",
        "insights to product",
    ],
    "running-decision-processes": [
        "decision framework",
        "decision making",
        "analysis paralysis",
        "daci",
        "rapid",
        "how to decide",
        "high-stakes decision",
    ],
    "systems-thinking": [
        "systems thinking",
        "second-order effects",
        "complex dynamics",
        "platform ecosystem",
        "unintended consequence",
        "feedback loop",
    ],

    # ── Research methods ──────────────────────────────────────────────────────
    "conducting-interviews": [
        "hiring interview",
        "interview loop",
        "structured interview",
        "interview question",
        "interview process for hiring",
        "evaluate in interview",
    ],
    "behavioral-product-design": [
        "habit formation",
        "behavioral design",
        "reduce friction",
        "psychology",
        "nudge",
        "behavior change",
        "persuasive design",
    ],

    # ── Strategy & metrics ────────────────────────────────────────────────────
    "writing-north-star-metrics": [
        "north star metric",
        "primary metric",
        "key metric",
        "metric proliferation",
        "one metric",
        "what metric to track",
        "metric strategy",
    ],
}


def _extract_context_signals(text: str) -> dict[str, str]:
    """Extract company type, stage, and revenue signals from a user message.

    Returns only keys for signals detected. An empty dict means no recognisable
    context in this message — the caller should not update state.
    """
    if not text:
        return {}

    result: dict[str, str] = {}
    lower = text.lower()

    for label, keywords in _COMPANY_TYPE_SIGNALS:
        if any(kw in lower for kw in keywords):
            result["company_type"] = label
            break

    for label, keywords in _STAGE_SIGNALS:
        if any(kw in lower for kw in keywords):
            result["stage"] = label
            break

    revenue_match = _REVENUE_RE.search(text)
    if revenue_match:
        result["revenue"] = revenue_match.group(0).strip()

    return result


def _append_to_system_instruction(llm_request: LlmRequest, text: str) -> None:
    """Append text to llm_request.config.system_instruction in-place."""
    if llm_request.config is None:
        return

    si = llm_request.config.system_instruction
    if si is None:
        llm_request.config.system_instruction = text
    elif isinstance(si, str):
        llm_request.config.system_instruction = si + text
    else:
        parts = list(getattr(si, "parts", []) or [])
        if parts and hasattr(parts[-1], "text"):
            from google.genai import types as genai_types

            llm_request.config.system_instruction = genai_types.Content(
                role=getattr(si, "role", "system"),
                parts=[*parts[:-1], genai_types.Part(text=parts[-1].text + text)],
            )


def detect_skill(user_message: str) -> str | None:
    """Return best-matching skill name, or None."""
    if not user_message:
        return None
    msg = user_message.lower()
    for skill_name, keywords in SKILL_MAP.items():
        if any(kw in msg for kw in keywords):
            return skill_name
    return None


def load_skill(skill_name: str) -> str | None:
    """Return SKILL.md content (truncated), or None if not found."""
    path = SKILLS_DIR / f"{skill_name}.md"
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    if len(content) > _SKILL_CHAR_LIMIT:
        content = (
            content[:_SKILL_CHAR_LIMIT] + "\n\n[Framework truncated for context budget]"
        )
    return content


def route_skill_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> None:
    """Before-model callback: extract session context and inject matching SKILL.md.

    Two responsibilities, in order:
    1. Context extraction (every turn): detect company type / stage / revenue from
       the latest user message, persist in session state, and inject a "Session
       Context" block into the system instruction so the model never asks for info
       the user already provided.
    2. Skill injection (first user turn only): append the matching SKILL.md
       framework. Skipped on turns where the model has already responded to avoid
       mid-reasoning confusion and wasted tokens.
    """
    # Find the latest user message in the conversation
    user_message = ""
    for content in reversed(llm_request.contents or []):
        if getattr(content, "role", None) == "user":
            for part in getattr(content, "parts", []) or []:
                text = getattr(part, "text", None)
                if text:
                    user_message = text
                    break
        if user_message:
            break

    if not user_message:
        return None

    # ── 1. Context extraction & injection (every turn) ────────────────────────
    new_signals = _extract_context_signals(user_message)
    if new_signals:
        _logger.debug("context signals=%r", new_signals)
        # Immutably merge new signals into stored context
        stored = dict(callback_context.state.get(_USER_CONTEXT_KEY, {}))
        stored.update(new_signals)
        callback_context.state[_USER_CONTEXT_KEY] = stored

    stored_context: dict[str, str] = callback_context.state.get(_USER_CONTEXT_KEY, {})
    if stored_context:
        lines = [
            f"- {k.replace('_', ' ').title()}: {v}"
            for k, v in stored_context.items()
        ]
        context_note = (
            "\n\n---\n## Session Context\n"
            + "\n".join(lines)
            + "\nApply this context to tailor recommendations."
            " Do not ask for information already listed above."
        )
        _append_to_system_instruction(llm_request, context_note)

    # ── 2. Skill injection: first turn OR topic change ─────────────────────────
    # Detect skill from current message. Inject if topic changes or first turn.
    has_model_turn = any(
        getattr(content, "role", None) == "model"
        for content in (llm_request.contents or [])
    )

    skill_name = detect_skill(user_message)
    last_injected = callback_context.state.get(_LAST_SKILL_KEY)

    # Decide whether to inject
    is_first_turn = not has_model_turn
    is_topic_switch = bool(skill_name and skill_name != last_injected)
    should_inject = is_first_turn or is_topic_switch

    if not should_inject or not skill_name:
        _logger.debug("skill=NO_MATCH user_message=%r", user_message[:80])
        return None

    skill_content = load_skill(skill_name)
    if not skill_content:
        return None

    _append_to_system_instruction(
        llm_request,
        f"\n\n---\n## Injected Framework: {skill_name}\n\n{skill_content}",
    )
    # Persist the injected skill so we don't re-inject it on the next turn.
    callback_context.state[_LAST_SKILL_KEY] = skill_name
    _logger.info("skill=%s injected", skill_name)
    return None
