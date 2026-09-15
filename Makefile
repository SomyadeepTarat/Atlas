.PHONY: run test test-integration format lint typecheck quality

run:
	uv run uvicorn atlas.main:app --app-dir src --reload

test:
	uv run pytest

test-integration:
	RUN_INTEGRATION_TESTS=1 uv run pytest

format:
	uv run ruff format .

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

quality:
	uv run ruff format .
	uv run ruff check . --fix
	uv run mypy src
	uv run pytest

qdrant-start:
	docker start atlas-qdrant

qdrant-stop:
	docker stop atlas-qdrant

eval-retrieval:
	uv run python scripts/run_retrieval_evals.py

eval:
	$(MAKE) eval-retrieval

mcp-dev:
	uv run mcp dev mcp_server.py

mcp-run:
	uv run python scripts/run_mcp_server.py

test-mcp:
	uv run pytest tests/mcp

run-observed:
	TELEMETRY_ENABLED=true \
	uv run uvicorn atlas.main:app --app-dir src --reload

run-trace-console:
	TELEMETRY_ENABLED=true \
	TELEMETRY_CONSOLE_EXPORT=true \
	uv run uvicorn atlas.main:app --app-dir src --reload

infra-up:
	docker compose up -d

infra-down:
	docker compose down

infra-status:
	docker compose ps

db-migrate:
	uv run alembic upgrade head

db-revision:
	uv run alembic revision --autogenerate -m "$(m)"

test-reliability:
	uv run pytest tests/faults -v

reliability:
	$(MAKE) quality
	$(MAKE) test-reliability