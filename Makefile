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

db-migrate:
	uv run alembic upgrade head

db-revision:
	uv run alembic revision --autogenerate -m "$(m)"

test-reliability:
	uv run pytest tests/faults -v

reliability:
	$(MAKE) quality
	$(MAKE) test-reliability
	
security-unit:
	uv run pytest tests/security -v

security-bandit:
	uv run bandit -r src

security-deps:
	uv run pip-audit

security:
	$(MAKE) security-unit
	$(MAKE) security-bandit
	$(MAKE) security-deps

frontend-dev:
	cd frontend && pnpm dev

frontend-typecheck:
	cd frontend && pnpm typecheck

frontend-lint:
	cd frontend && pnpm lint

frontend-build:
	cd frontend && pnpm build

frontend-quality:
	$(MAKE) frontend-typecheck
	$(MAKE) frontend-lint
	$(MAKE) frontend-build

quality-all:
	$(MAKE) quality
	$(MAKE) frontend-quality

.PHONY: \
	infra-up \
	infra-dev-up \
	infra-down \
	infra-build \
	infra-logs \
	infra-status \
	infra-reset \
	docker-quality


infra-build:
	docker compose build


infra-up:
	docker compose up -d


infra-dev-up:
	docker compose \
		-f compose.yaml \
		-f compose.dev.yaml \
		up -d


infra-down:
	docker compose down


infra-logs:
	docker compose logs -f


infra-status:
	docker compose ps


infra-reset:
	docker compose down -v

docker-quality:
	docker compose config
	docker compose build

docker-api:
	docker compose build api

docker-frontend:
	docker compose build frontend

docker-up-build:
	docker compose up -d --build

smoke:
	uv run python scripts/smoke_test.py
