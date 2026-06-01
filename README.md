# StockGenie

AI-powered financial advisor for high-net-worth individuals.

## Setup

1. Clone the repository.
2. Install dependencies with `uv`:
   ```bash
   uv sync
   ```
3. Copy `.env.example` to `.env` and fill in your API keys.
4. Run the application:
   ```bash
   make run
   ```

## Development

- `make lint` — run linting
- `make test` — run tests
- `make run` — start the Flask dev server

## Project Structure

- `app/` — Flask web application and templates
- `core/` — LangGraph agent orchestration
- `tools/` — Agent tools (finance, market, news, inventory)
- `config/` — Settings and prompts
- `db/` — Database clients (ChromaDB)
- `tests/` — Test suite
- `scripts/` — One-off utilities
- `notebooks/` — Jupyter notebooks
