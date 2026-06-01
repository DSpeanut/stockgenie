PHONY: run test lint format typecheck clean

run:
	python -m app.api

test:
	pytest tests/ -v

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy app core tools config db services

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
