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
