"""Unit tests for agent.py callbacks."""

from unittest.mock import MagicMock


def _make_tool(name: str) -> MagicMock:
    t = MagicMock()
    t.name = name
    return t


def _make_context(invocation_id: str = "inv_test") -> MagicMock:
    ctx = MagicMock()
    ctx.invocation_id = invocation_id
    ctx.state = {}
    return ctx


class TestEnforceSearchCap:
    """_enforce_search_cap hard-caps search_transcripts at 2 calls per invocation."""

    def setup_method(self):
        from agent.agent import _search_call_counts
        _search_call_counts.clear()

    def test_first_call_passes_through(self):
        from agent.agent import _enforce_search_cap

        tool = _make_tool("search_transcripts")
        ctx = _make_context()
        result = _enforce_search_cap(tool, {"query": "pricing"}, ctx)
        assert result is None  # None = let the real call proceed

    def test_second_call_passes_through(self):
        from agent.agent import _enforce_search_cap

        tool = _make_tool("search_transcripts")
        ctx = _make_context()
        _enforce_search_cap(tool, {"query": "pricing"}, ctx)
        result = _enforce_search_cap(tool, {"query": "monetization"}, ctx)
        assert result is None

    def test_third_call_is_blocked(self):
        from agent.agent import _enforce_search_cap

        tool = _make_tool("search_transcripts")
        ctx = _make_context()
        _enforce_search_cap(tool, {"query": "pricing"}, ctx)
        _enforce_search_cap(tool, {"query": "monetization"}, ctx)
        result = _enforce_search_cap(tool, {"query": "willingness to pay"}, ctx)

        assert result is not None
        assert "cap_reached" in result["result"]
        assert "synthesize" in result["result"]

    def test_cap_response_has_next_actions(self):
        from agent.agent import _enforce_search_cap

        tool = _make_tool("search_transcripts")
        ctx = _make_context()
        for _ in range(2):
            _enforce_search_cap(tool, {"query": "q"}, ctx)
        result = _enforce_search_cap(tool, {"query": "q3"}, ctx)

        assert "next_actions" in result["result"]

    def test_cap_is_scoped_per_invocation(self):
        from agent.agent import _enforce_search_cap

        tool = _make_tool("search_transcripts")

        # Invocation A exhausts its cap
        ctx_a = _make_context("inv_a")
        for _ in range(2):
            _enforce_search_cap(tool, {"query": "q"}, ctx_a)
        assert _enforce_search_cap(tool, {"query": "q3"}, ctx_a) is not None

        # Invocation B has a fresh counter
        ctx_b = _make_context("inv_b")
        assert _enforce_search_cap(tool, {"query": "q1"}, ctx_b) is None
        assert _enforce_search_cap(tool, {"query": "q2"}, ctx_b) is None
        assert _enforce_search_cap(tool, {"query": "q3"}, ctx_b) is not None

    def test_other_tools_always_pass_through(self):
        from agent.agent import _enforce_search_cap

        ctx = _make_context()
        for tool_name in ("get_episode", "list_episodes", "some_other_tool"):
            tool = _make_tool(tool_name)
            assert _enforce_search_cap(tool, {}, ctx) is None

    def test_counter_increments_correctly(self):
        from agent.agent import _enforce_search_cap, _search_call_counts

        tool = _make_tool("search_transcripts")
        ctx = _make_context("inv_counter")

        # Determine the key used by the implementation (invocation_id via invocation_context)
        ic = ctx.invocation_context
        inv_id = ic.invocation_id
        key = str(inv_id)

        _enforce_search_cap(tool, {}, ctx)
        assert _search_call_counts.get(key, 0) == 1

        _enforce_search_cap(tool, {}, ctx)
        assert _search_call_counts.get(key, 0) == 2


class TestNormalizeSearchOutput:
    """_normalize_search_output adds quality signal header to search results."""

    def test_success_status_for_two_plus_blocks(self):
        from agent.agent import _normalize_search_output

        tool = _make_tool("search_transcripts")
        ctx = _make_context()
        response = {"result": "Block one content\n\nBlock two content"}
        result = _normalize_search_output(tool, {}, ctx, response)
        assert "status=success" in result["result"]
        assert "result_count=2" in result["result"]

    def test_partial_status_for_one_block(self):
        from agent.agent import _normalize_search_output

        tool = _make_tool("search_transcripts")
        ctx = _make_context()
        response = {"result": "Only one block here"}
        result = _normalize_search_output(tool, {}, ctx, response)
        assert "status=partial" in result["result"]
        assert "result_count=1" in result["result"]

    def test_empty_status_for_no_results(self):
        from agent.agent import _normalize_search_output

        tool = _make_tool("search_transcripts")
        ctx = _make_context()
        response = {"result": ""}
        result = _normalize_search_output(tool, {}, ctx, response)
        assert "status=empty" in result["result"]
        assert "result_count=0" in result["result"]

    def test_next_actions_hint_for_success(self):
        from agent.agent import _normalize_search_output

        tool = _make_tool("search_transcripts")
        ctx = _make_context()
        response = {"result": "A\n\nB"}
        result = _normalize_search_output(tool, {}, ctx, response)
        assert "synthesize recommendation" in result["result"]

    def test_next_actions_hint_for_partial(self):
        from agent.agent import _normalize_search_output

        tool = _make_tool("search_transcripts")
        ctx = _make_context()
        response = {"result": "Only one"}
        result = _normalize_search_output(tool, {}, ctx, response)
        assert "reformulate" in result["result"] or "fall back" in result["result"]

    def test_get_episode_passes_through_unchanged(self):
        from agent.agent import _normalize_search_output

        tool = _make_tool("get_episode")
        ctx = _make_context()
        original = {"result": "Full episode transcript here"}
        result = _normalize_search_output(tool, {}, ctx, dict(original))
        assert result == original

    def test_original_content_preserved_after_header(self):
        from agent.agent import _normalize_search_output

        tool = _make_tool("search_transcripts")
        ctx = _make_context()
        content = "Guest: Patrick Campbell\n\nGuest: Madhavan Ramanujam"
        response = {"result": content}
        result = _normalize_search_output(tool, {}, ctx, response)
        assert "Patrick Campbell" in result["result"]
        assert "Madhavan Ramanujam" in result["result"]


def _make_ctx(invocation_id: str) -> MagicMock:
    """Alias helper matching task spec — delegates to _make_context."""
    return _make_context(invocation_id)


class TestSearchCapLogging:
    """_enforce_search_cap should log when the cap is hit."""

    def setup_method(self):
        from agent.agent import _search_call_counts
        _search_call_counts.clear()

    def test_cap_hit_emits_warning(self, caplog):
        import logging

        from agent.agent import _enforce_search_cap

        tool = MagicMock()
        tool.name = "search_transcripts"
        ctx = _make_ctx("inv-log-1")

        with caplog.at_level(logging.WARNING, logger="agent.agent"):
            _enforce_search_cap(tool, {}, ctx)
            _enforce_search_cap(tool, {}, ctx)
            _enforce_search_cap(tool, {}, ctx)

        assert any("cap_reached" in r.message for r in caplog.records), (
            "Expected a WARNING log containing 'cap_reached'"
        )

    def test_non_search_tool_no_log(self, caplog):
        import logging

        from agent.agent import _enforce_search_cap

        tool = MagicMock()
        tool.name = "get_episode"
        ctx = _make_ctx("inv-log-2")

        with caplog.at_level(logging.DEBUG, logger="agent.agent"):
            _enforce_search_cap(tool, {}, ctx)

        assert not caplog.records, "Non-search tool should not emit logs"


class TestNormalizeSearchOutputLogging:
    """_normalize_search_output should log result quality signal."""

    def test_empty_result_emits_warning(self, caplog):
        import logging

        from agent.agent import _normalize_search_output

        tool = MagicMock()
        tool.name = "search_transcripts"
        ctx = _make_ctx("inv-log-3")

        with caplog.at_level(logging.WARNING, logger="agent.agent"):
            _normalize_search_output(tool, {}, ctx, {"result": ""})

        assert any("empty" in r.message for r in caplog.records)

    def test_success_result_emits_info(self, caplog):
        import logging

        from agent.agent import _normalize_search_output

        tool = MagicMock()
        tool.name = "search_transcripts"
        ctx = _make_ctx("inv-log-4")
        good_result = {"result": "block one\n\nblock two\n\nblock three"}

        with caplog.at_level(logging.INFO, logger="agent.agent"):
            _normalize_search_output(tool, {}, ctx, good_result)

        assert any("success" in r.message for r in caplog.records)
