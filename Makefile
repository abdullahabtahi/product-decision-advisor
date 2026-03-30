
# ==============================================================================
# Installation & Setup
# ==============================================================================

# Install dependencies using uv package manager
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync

# ==============================================================================
# Playground Targets
# ==============================================================================

# Launch local dev playground
playground:
	@echo "==============================================================================="
	@echo "| 🚀 Starting your agent playground...                                        |"
	@echo "|                                                                             |"
	@echo "| 💡 Try asking: What's the weather in San Francisco?                         |"
	@echo "|                                                                             |"
	@echo "| 🔍 IMPORTANT: Select the 'agent' folder to interact with your agent.        |"
	@echo "==============================================================================="
	uv run adk web . --port 8501 --reload_agents

# ==============================================================================
# Local Development Commands
# ==============================================================================

# Launch local development server with hot-reload
# Usage: make local-backend [PORT=8000] - Specify PORT for parallel scenario testing
local-backend:
	uv run uvicorn agent.fast_api_app:app --host localhost --port $(or $(PORT),8000) --reload

# ==============================================================================
# Backend Deployment Targets
# ==============================================================================

# Deploy the agent remotely
# Usage: make deploy [IAP=true] [PORT=8080] - Set IAP=true to enable Identity-Aware Proxy, PORT to specify container port
deploy:
	PROJECT_ID=$$(gcloud config get-value project) && \
	gcloud beta run deploy prod-decision-advisor \
		--source . \
		--memory "4Gi" \
		--project $$PROJECT_ID \
		--region "us-central1" \
		--no-allow-unauthenticated \
		--no-cpu-throttling \
		--labels "created-by=adk" \
		--update-build-env-vars "AGENT_VERSION=$(shell awk -F'"' '/^version = / {print $$2}' pyproject.toml || echo '0.0.0')" \
		--update-env-vars \
		"" \
		$(if $(IAP),--iap) \
		$(if $(PORT),--port=$(PORT))

# Alias for 'make deploy' for backward compatibility
backend: deploy

# ==============================================================================
# Testing & Code Quality
# ==============================================================================

# Run unit and integration tests
test:
	uv sync --dev
	uv run pytest tests/unit && uv run pytest tests/integration

# ==============================================================================
# Agent Evaluation
# ==============================================================================

# Run agent evaluation using ADK eval
# Usage: make eval [EVALSET=tests/eval/evalsets/basic.evalset.json] [EVAL_CONFIG=tests/eval/eval_config.json]
eval:
	@echo "==============================================================================="
	@echo "| Running Agent Evaluation                                                    |"
	@echo "==============================================================================="
	uv sync --dev --extra eval
	uv run adk eval ./agent $${EVALSET:-tests/eval/evalsets/basic.evalset.json} \
		$(if $(EVAL_CONFIG),--config_file_path=$(EVAL_CONFIG),$(if $(wildcard tests/eval/eval_config.json),--config_file_path=tests/eval/eval_config.json,))

# Run eval cases sequentially (one at a time) to avoid overwhelming Render free tier.
# Use this when `make eval` hits MCP timeouts from parallel case execution.
eval-sequential:
	@echo "==============================================================================="
	@echo "| Running Eval Cases Sequentially (Render-safe)                              |"
	@echo "==============================================================================="
	@uv sync --dev --extra eval
	@echo "Warming up Render (cold start can take 60-90s)..."; $(MAKE) check-mcp
	@PASS=0; FAIL=0; ERRORS=0; \
	for eval_id in $$(uv run python3 -c "import json; data=json.load(open('tests/eval/evalsets/basic.evalset.json')); [print(c['eval_id']) for c in data['eval_cases']]"); do \
		echo ""; echo "▶ Running: $$eval_id"; \
		OUTPUT=$$(uv run adk eval ./agent "tests/eval/evalsets/basic.evalset.json:$$eval_id" \
			--config_file_path=tests/eval/eval_config.json 2>&1); \
		echo "$$OUTPUT" | grep -E "Tests (passed|failed)"; \
		echo "$$OUTPUT" | grep -q "Tests passed: 1" && PASS=$$((PASS+1)) || FAIL=$$((FAIL+1)); \
		sleep 8; \
	done; \
	echo ""; echo "=== Results: $$PASS passed, $$FAIL failed ==="

# Run evaluation with all evalsets
eval-all:
	@echo "==============================================================================="
	@echo "| Running All Evalsets                                                        |"
	@echo "==============================================================================="
	@for evalset in tests/eval/evalsets/*.evalset.json; do \
		echo ""; \
		echo "▶ Running: $$evalset"; \
		$(MAKE) eval EVALSET=$$evalset || exit 1; \
	done
	@echo ""
	@echo "✅ All evalsets completed"

# Verify lenny-mcp MCP endpoint is reachable
# Catches transport/connectivity issues before running playground or eval
check-mcp:
	@echo "Checking lenny-mcp connectivity..."
	@HTTP_CODE=$$(curl -s -o /dev/null -w "%{http_code}" https://lenny-mcp.onrender.com/mcp); \
	if [ "$$HTTP_CODE" = "200" ] || [ "$$HTTP_CODE" = "400" ] || [ "$$HTTP_CODE" = "405" ]; then \
		echo "✅ lenny-mcp reachable (HTTP $$HTTP_CODE — POST-only endpoint, GET rejected as expected)"; \
	elif [ "$$HTTP_CODE" = "000" ]; then \
		echo "❌ lenny-mcp unreachable — connection refused, cold start may take 30–60s"; exit 1; \
	else \
		echo "❌ lenny-mcp returned HTTP $$HTTP_CODE — check https://lenny-mcp.onrender.com"; exit 1; \
	fi

# Run code quality checks (codespell, ruff, ty)
lint:
	uv sync --dev --extra lint
	uv run codespell
	uv run ruff check . --diff
	uv run ruff format . --check --diff
	uv run ty check .