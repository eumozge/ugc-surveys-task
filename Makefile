.PHONY: sync format

sync:
	uv sync --all-groups

format:
	uv run ruff format .
	uv run ruff check --fix .
