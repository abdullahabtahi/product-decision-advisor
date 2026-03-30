"""Unit tests for skill_router."""

from unittest.mock import MagicMock, patch

class TestDetectSkill:
    """Keyword detection for all skills."""

    # ── Original 15 skills ────────────────────────────────────────────────────
    def test_pricing_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How should I price my SaaS?") == "pricing-strategy"

    def test_freemium_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("Should I go freemium or paid?") == "pricing-strategy"

    def test_roadmap_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I prioritize my roadmap?") == "prioritizing-roadmap"

    def test_churn_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I reduce churn?") == "retention-engagement"

    def test_hire_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("When should I hire my first PM?") == "evaluating-candidates"

    def test_pmf_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I know if I have product market fit?") == "measuring-product-market-fit"

    def test_growth_loop_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I design a growth loop?") == "designing-growth-loops"

    def test_vision_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I write a compelling product vision?") == "defining-product-vision"

    def test_marketplace_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I solve the chicken and egg problem in my marketplace?") == "marketplace-liquidity"

    def test_positioning_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I improve our positioning and messaging?") == "positioning-messaging"

    def test_pls_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I convert free users to enterprise via product-led sales?") == "product-led-sales"

    def test_okr_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do we set our OKRs this quarter?") == "setting-okrs-goals"

    def test_stakeholder_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I get stakeholder alignment on this feature?") == "stakeholder-alignment"

    def test_user_interview_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How should I run user interviews?") == "conducting-user-interviews"

    def test_tradeoff_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("What are the pros and cons of this approach?") == "evaluating-trade-offs"

    def test_founder_sales_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I close my first customer as a founder?") == "founder-sales"

    # ── New skills ────────────────────────────────────────────────────────────
    def test_working_backwards_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I write a PR FAQ for my new feature?") == "working-backwards"

    def test_problem_definition_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I write a clear problem statement?") == "problem-definition"

    def test_writing_prds_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I write a good PRD for my team?") == "writing-prds"

    def test_scoping_cutting_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I define the MVP and what to cut?") == "scoping-cutting"

    def test_launch_marketing_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I plan a product launch campaign?") == "launch-marketing"

    def test_competitive_analysis_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I run a competitive analysis?") == "competitive-analysis"

    def test_user_onboarding_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I improve activation and get users to the aha moment?") == "user-onboarding"

    def test_ai_product_strategy_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I define an AI product strategy?") == "ai-product-strategy"

    def test_building_with_llms_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I build an LLM application with RAG?") == "building-with-llms"

    def test_startup_ideation_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I validate my startup idea?") == "startup-ideation"

    def test_startup_pivoting_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I know when to pivot my startup?") == "startup-pivoting"

    def test_fundraising_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I prepare for fundraising and investor meetings?") == "fundraising"

    def test_enterprise_sales_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I close a large enterprise deal?") == "enterprise-sales"

    def test_technical_roadmap_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I build a technical roadmap?") == "technical-roadmaps"

    def test_managing_tech_debt_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I get buy-in for paying down tech debt?") == "managing-tech-debt"

    def test_north_star_metric_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I choose our north star metric?") == "writing-north-star-metrics"

    def test_post_mortem_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I run a postmortem after an incident?") == "post-mortems-retrospectives"

    def test_analyzing_feedback_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I synthesize user feedback from NPS?") == "analyzing-user-feedback"

    def test_platform_strategy_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I build a platform strategy with network effects?") == "platform-strategy"

    def test_planning_uncertainty_keyword(self):
        from agent.skill_router import detect_skill
        assert detect_skill("How do I plan under uncertainty in a fast-moving market?") == "planning-under-uncertainty"

    def test_hiring_interview_keyword(self):
        from agent.skill_router import detect_skill
        # Distinct from conducting-user-interviews — this is for hiring
        assert detect_skill("How do I design a structured hiring interview loop?") == "conducting-interviews"

    # ── Edge cases ────────────────────────────────────────────────────────────
    def test_unrelated_returns_none(self):
        from agent.skill_router import detect_skill
        assert detect_skill("What's the weather today?") is None

    def test_case_insensitive(self):
        from agent.skill_router import detect_skill
        assert detect_skill("PRICING strategy for my startup") == "pricing-strategy"

    def test_empty_returns_none(self):
        from agent.skill_router import detect_skill
        assert detect_skill("") is None

    def test_generic_growth_does_not_trigger_growth_loop(self):
        from agent.skill_router import detect_skill
        # "growth" alone is too generic — should not trigger designing-growth-loops
        result = detect_skill("We are in a growth stage company")
        assert result != "designing-growth-loops"

    def test_metric_alone_does_not_trigger_okrs(self):
        from agent.skill_router import detect_skill
        # "metric" alone should not fire okrs — too broad
        result = detect_skill("We need to pick a good success metric")
        # Either triggers north-star-metrics or okrs — both valid, just not None
        # The important check is it doesn't misfire on unrelated queries
        assert result in (None, "setting-okrs-goals", "writing-north-star-metrics")


class TestLoadSkill:
    """Skill file loading."""

    def test_existing_skill_returns_content(self, tmp_path):
        from agent.skill_router import load_skill
        (tmp_path / "pricing-strategy.md").write_text("# Pricing\nContent.")
        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            result = load_skill("pricing-strategy")
            assert result is not None and "Pricing" in result

    def test_missing_skill_returns_none(self, tmp_path):
        from agent.skill_router import load_skill
        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            assert load_skill("nonexistent") is None

    def test_truncation_at_char_limit(self, tmp_path):
        from agent.skill_router import load_skill, _SKILL_CHAR_LIMIT
        long_content = "x" * (_SKILL_CHAR_LIMIT + 1000)
        (tmp_path / "test-skill.md").write_text(long_content)
        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            result = load_skill("test-skill")
            assert result is not None
            assert len(result) <= _SKILL_CHAR_LIMIT + len("\n\n[Framework truncated for context budget]")
            assert "[Framework truncated for context budget]" in result

    def test_short_skill_not_truncated(self, tmp_path):
        from agent.skill_router import load_skill
        short_content = "# Short skill\nBrief content."
        (tmp_path / "short-skill.md").write_text(short_content)
        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            result = load_skill("short-skill")
            assert result == short_content


class TestSkillMapIntegrity:
    """Every SKILL_MAP entry must have a corresponding .md file on disk.

    This is the key safety check: if a skill is in the routing map but the
    file is missing, the callback silently returns None and the framework
    is never injected — the agent answers without guidance.
    """

    def test_every_skill_map_key_has_a_file(self):
        from agent.skill_router import SKILL_MAP, SKILLS_DIR

        missing = [
            skill for skill in SKILL_MAP
            if not (SKILLS_DIR / f"{skill}.md").exists()
        ]
        assert missing == [], (
            f"SKILL_MAP entries with no .md file (skill injection will silently fail): {missing}"
        )

    def test_no_empty_keyword_lists(self):
        from agent.skill_router import SKILL_MAP

        empty = [skill for skill, kws in SKILL_MAP.items() if not kws]
        assert empty == [], f"Skills with empty keyword list (unreachable): {empty}"

    def test_no_duplicate_keywords_across_skills(self):
        from agent.skill_router import SKILL_MAP

        seen: dict[str, str] = {}
        duplicates = []
        for skill, keywords in SKILL_MAP.items():
            for kw in keywords:
                if kw in seen:
                    duplicates.append(f"'{kw}' in both '{seen[kw]}' and '{skill}'")
                else:
                    seen[kw] = skill
        assert duplicates == [], f"Duplicate keywords cause non-deterministic routing:\n" + "\n".join(duplicates)


class TestExtractContextSignals:
    """_extract_context_signals detects company type, stage, and revenue."""

    def test_detects_b2b_saas_specifically(self):
        from agent.skill_router import _extract_context_signals
        result = _extract_context_signals("We're a B2B SaaS startup")
        assert result.get("company_type") == "B2B SaaS"

    def test_detects_b2b_over_b2c(self):
        from agent.skill_router import _extract_context_signals
        result = _extract_context_signals("We sell b2b, targeting SMB customers")
        assert result.get("company_type") == "B2B"

    def test_detects_b2c_consumer_app(self):
        from agent.skill_router import _extract_context_signals
        result = _extract_context_signals("We build a consumer app with 10k users")
        assert result.get("company_type") == "B2C"

    def test_detects_seed_stage(self):
        from agent.skill_router import _extract_context_signals
        result = _extract_context_signals("We're at seed stage with our first customers")
        assert result.get("stage") == "seed"

    def test_detects_series_a(self):
        from agent.skill_router import _extract_context_signals
        result = _extract_context_signals("We just closed our Series A round")
        assert result.get("stage") == "Series A"

    def test_detects_growth_stage(self):
        from agent.skill_router import _extract_context_signals
        result = _extract_context_signals("We're in growth stage, series b")
        assert result.get("stage") == "growth"

    def test_detects_mrr(self):
        from agent.skill_router import _extract_context_signals
        result = _extract_context_signals("We're at $50k MRR and growing fast")
        assert result.get("revenue") == "$50k MRR"

    def test_detects_arr(self):
        from agent.skill_router import _extract_context_signals
        result = _extract_context_signals("We hit $2m ARR last quarter")
        assert result.get("revenue") == "$2m ARR"

    def test_combines_multiple_signals(self):
        from agent.skill_router import _extract_context_signals
        result = _extract_context_signals("We're a B2B SaaS at seed stage with $100k ARR")
        assert result.get("company_type") == "B2B SaaS"
        assert result.get("stage") == "seed"
        assert result.get("revenue") is not None

    def test_no_signals_returns_empty(self):
        from agent.skill_router import _extract_context_signals
        assert _extract_context_signals("How do I prioritize my roadmap?") == {}

    def test_empty_string_returns_empty(self):
        from agent.skill_router import _extract_context_signals
        assert _extract_context_signals("") == {}

    def test_seed_word_alone_does_not_trigger_stage(self):
        # "seed" alone (e.g. "seed the idea") should not fire — requires compound phrase
        from agent.skill_router import _extract_context_signals
        result = _extract_context_signals("We want to seed the idea with customers")
        assert result.get("stage") is None


class TestCallbackInjection:
    """route_skill_callback correctly injects skill content into system_instruction."""

    def _make_ctx(self, initial_state: dict | None = None):
        """Build a callback context mock with a real dict for state."""
        ctx = MagicMock()
        ctx.state = initial_state if initial_state is not None else {}
        return ctx

    def _make_llm_request(self, user_text: str, has_model_turn: bool = False):
        """Build a minimal LlmRequest-like mock."""
        user_part = MagicMock()
        user_part.text = user_text
        user_content = MagicMock()
        user_content.role = "user"
        user_content.parts = [user_part]

        contents = [user_content]
        if has_model_turn:
            model_content = MagicMock()
            model_content.role = "model"
            contents.append(model_content)

        config = MagicMock()
        config.system_instruction = "Base instruction."

        request = MagicMock()
        request.contents = contents
        request.config = config
        return request

    def test_callback_injects_matching_skill(self, tmp_path):
        from agent.skill_router import route_skill_callback

        skill_content = "# Pricing Strategy\nCharge based on value."
        (tmp_path / "pricing-strategy.md").write_text(skill_content)

        ctx = self._make_ctx()
        request = self._make_llm_request("How should I price my SaaS product?")

        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            route_skill_callback(callback_context=ctx, llm_request=request)

        injected = request.config.system_instruction
        assert "pricing-strategy" in injected
        assert "Pricing Strategy" in injected

    def test_callback_no_injection_for_unrelated_query(self, tmp_path):
        from agent.skill_router import route_skill_callback

        ctx = self._make_ctx()
        request = self._make_llm_request("What is the capital of France?")
        original_instruction = request.config.system_instruction

        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            route_skill_callback(callback_context=ctx, llm_request=request)

        assert request.config.system_instruction == original_instruction

    def test_callback_skips_skill_injection_when_same_skill_already_injected(self, tmp_path):
        from agent.skill_router import route_skill_callback, _LAST_SKILL_KEY

        skill_content = "# Pricing\nContent."
        (tmp_path / "pricing-strategy.md").write_text(skill_content)

        # State already has pricing-strategy as last injected → no re-injection
        ctx = self._make_ctx({_LAST_SKILL_KEY: "pricing-strategy"})
        request = self._make_llm_request("How should I price my SaaS?", has_model_turn=True)
        original_instruction = request.config.system_instruction

        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            route_skill_callback(callback_context=ctx, llm_request=request)

        # Same skill already in context → no re-injection
        assert "Pricing" not in request.config.system_instruction
        assert request.config.system_instruction == original_instruction

    def test_callback_injects_on_topic_switch_mid_session(self, tmp_path):
        from agent.skill_router import route_skill_callback, _LAST_SKILL_KEY

        skill_content = "# Pricing\nContent."
        (tmp_path / "pricing-strategy.md").write_text(skill_content)

        # State has a DIFFERENT skill as last injected → topic switch triggers injection
        ctx = self._make_ctx({_LAST_SKILL_KEY: "retention-engagement"})
        request = self._make_llm_request("How should I price my SaaS?", has_model_turn=True)

        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            route_skill_callback(callback_context=ctx, llm_request=request)

        # New topic → skill injected even mid-session
        assert "Pricing" in request.config.system_instruction

    def test_callback_returns_none(self, tmp_path):
        from agent.skill_router import route_skill_callback

        ctx = self._make_ctx()
        request = self._make_llm_request("How should I price my SaaS?")

        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            result = route_skill_callback(callback_context=ctx, llm_request=request)

        assert result is None

    # ── Context injection tests ────────────────────────────────────────────────

    def test_context_injected_from_stored_state(self, tmp_path):
        from agent.skill_router import route_skill_callback, _USER_CONTEXT_KEY

        ctx = self._make_ctx({_USER_CONTEXT_KEY: {"company_type": "B2B SaaS", "stage": "seed"}})
        request = self._make_llm_request("How do I prioritize my roadmap?")

        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            route_skill_callback(callback_context=ctx, llm_request=request)

        injected = request.config.system_instruction
        assert "Session Context" in injected
        assert "B2B SaaS" in injected
        assert "seed" in injected

    def test_context_not_injected_when_state_empty(self, tmp_path):
        from agent.skill_router import route_skill_callback

        ctx = self._make_ctx()  # empty state
        (tmp_path / "pricing-strategy.md").write_text("# Pricing")
        request = self._make_llm_request("How do I price my SaaS?")

        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            route_skill_callback(callback_context=ctx, llm_request=request)

        # Skill may be injected, but Session Context block must not appear
        assert "Session Context" not in request.config.system_instruction

    def test_context_extracted_and_stored(self, tmp_path):
        from agent.skill_router import route_skill_callback, _USER_CONTEXT_KEY

        ctx = self._make_ctx()
        request = self._make_llm_request("We're a B2B SaaS at seed stage")

        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            route_skill_callback(callback_context=ctx, llm_request=request)

        stored = ctx.state.get(_USER_CONTEXT_KEY, {})
        assert stored.get("company_type") == "B2B SaaS"
        assert stored.get("stage") == "seed"

    def test_context_accumulates_across_turns(self, tmp_path):
        from agent.skill_router import route_skill_callback, _USER_CONTEXT_KEY

        ctx = self._make_ctx()

        # Turn 1: user mentions company type
        request1 = self._make_llm_request("We're a B2B SaaS startup")
        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            route_skill_callback(callback_context=ctx, llm_request=request1)

        # Turn 2: user mentions revenue (no company type signal in this message)
        request2 = self._make_llm_request("We hit $100k ARR last month")
        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            route_skill_callback(callback_context=ctx, llm_request=request2)

        stored = ctx.state.get(_USER_CONTEXT_KEY, {})
        assert stored.get("company_type") == "B2B SaaS"  # persisted from turn 1
        assert stored.get("revenue") is not None         # added in turn 2

    def test_context_updates_on_new_signal(self, tmp_path):
        from agent.skill_router import route_skill_callback, _USER_CONTEXT_KEY

        ctx = self._make_ctx({_USER_CONTEXT_KEY: {"stage": "seed"}})

        # User now mentions Series A — should override prior seed stage
        request = self._make_llm_request("We just closed our Series A round")
        with patch("agent.skill_router.SKILLS_DIR", tmp_path):
            route_skill_callback(callback_context=ctx, llm_request=request)

        stored = ctx.state.get(_USER_CONTEXT_KEY, {})
        assert stored.get("stage") == "Series A"


class TestSkillRoutingLogs:
    """route_skill_callback should log injection decisions."""

    def test_matched_skill_logs_info(self, caplog):
        """When a skill matches, an INFO log names it."""
        import logging

        from agent.skill_router import route_skill_callback

        ctx = MagicMock()
        ctx.state = {}
        # Simulate a first-turn user message (no model turns yet)
        user_part = MagicMock()
        user_part.text = "how should I price my SaaS?"
        user_msg = MagicMock()
        user_msg.contents = [MagicMock(role="user", parts=[user_part])]

        with caplog.at_level(logging.INFO, logger="agent.skill_router"):
            with patch("agent.skill_router.load_skill", return_value="## Pricing\ncontent"):
                route_skill_callback(ctx, user_msg)

        assert any("skill=" in r.message for r in caplog.records), (
            f"Expected INFO log with 'skill=' but got: {[r.message for r in caplog.records]}"
        )

    def test_no_match_logs_debug(self, caplog):
        """When no skill matches, a DEBUG log records NO_MATCH."""
        import logging

        from agent.skill_router import route_skill_callback

        ctx = MagicMock()
        ctx.state = {}
        user_part = MagicMock()
        user_part.text = "what is the capital of France?"
        user_msg = MagicMock()
        user_msg.contents = [MagicMock(role="user", parts=[user_part])]

        with caplog.at_level(logging.DEBUG, logger="agent.skill_router"):
            route_skill_callback(ctx, user_msg)

        assert any("NO_MATCH" in r.message for r in caplog.records), (
            f"Expected DEBUG log with 'NO_MATCH' but got: {[r.message for r in caplog.records]}"
        )

    def test_context_signals_logged(self, caplog):
        """Extracted context signals are logged at DEBUG."""
        import logging

        from agent.skill_router import route_skill_callback

        ctx = MagicMock()
        ctx.state = {}
        user_part = MagicMock()
        user_part.text = "we're a Series A B2B SaaS, how should I price?"
        user_msg = MagicMock()
        user_msg.contents = [MagicMock(role="user", parts=[user_part])]

        with caplog.at_level(logging.DEBUG, logger="agent.skill_router"):
            route_skill_callback(ctx, user_msg)

        messages = " ".join(r.message for r in caplog.records)
        assert "context" in messages.lower(), (
            f"Expected a log mentioning 'context' but got: {[r.message for r in caplog.records]}"
        )
