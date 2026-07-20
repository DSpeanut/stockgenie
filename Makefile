PHONY: run test lint format typecheck clean mlflow

run:
	python -m app.api

mlflow:
	mlflow server --backend-store-uri sqlite:///observatory/mlflow.db --default-artifact-root ./observatory/mlartifacts --host 127.0.0.1 --port 5001

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
