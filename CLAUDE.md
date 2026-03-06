# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pmls** is a Python CLI tool for interacting with Polymarket prediction markets. It provides market lookup via the GAMMA API, local configuration management, and real-time CLOB orderbook streaming. The final objective is to implement some pre-defined trading strategy that requires L2 authentication on Polymarket.

## Commands

### Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

### Running

```bash
pmls get-markets <event-slug>
pmls set-config --market <slug> [--clob-id <id>]
pmls orderbook <market-slug> [--interval <sec>] [--depth <levels>] [--once]
```

### Testing

```bash
pytest
```

Note: `tests/` directory is configured in pyproject.toml but does not yet exist.

## Architecture

### Module Responsibilities

- **cli.py** — argparse-based CLI entry point (`pmls.cli:main`). Defines subcommand handlers for `get-markets`, `set-config`, and `orderbook`. Uses `Decimal` for price formatting (0–1 range → 0–100 display).
- **config.py** — Manages `.pmls/config.json` in the current working directory. Stores `current_market` and `current_clob_id` defaults.
- **credentials.py** — Loads CLOB credentials (`PMLS_CLOB_*` env vars) via python-dotenv. Defines `ClobCredentials` dataclass and `CredentialError`.
- **gamma_client.py** — HTTP client for the GAMMA API (`https://gamma-api.polymarket.com`). Fetches event metadata and extracts market slugs.
- **orderbook_client.py** — Fetches orderbook data via `py_clob_client.ClobClient` (CLOB API on Polygon, chain ID 137). Defines `DisplayOutcome` Pydantic model. Sorts/selects top N ask/bid price levels.

### Data Flow

1. **Market lookup**: CLI → `gamma_client.fetch_event_markets()` → GAMMA API → print slugs
2. **Orderbook streaming**: CLI loop → `orderbook_client.fetch_market_orderbooks()` → GAMMA API (market metadata) + CLOB API (orderbook per token) → formatted table output

### External APIs

- **GAMMA API** (`gamma-api.polymarket.com`): Event/market metadata (`/events/slug/{slug}`, `/markets?slug={slug}`)
- **CLOB API** (`clob.polymarket.com`): Orderbook data via `py_clob_client`

### Key Dependencies

- `py-clob-client` — Polymarket CLOB protocol client (also brings in pydantic)
- `requests` — HTTP calls to GAMMA API
- `python-dotenv` — `.env` file loading for credentials
- Python >=3.11 required

## General principles

1. Always run code in venv.

## Code Organization

When implementing a feature:

1. When something is unclear, ask first.
2. Review related code, use existing functions if possible or suggest better interface for existing functions.
3. Define data classes and function interfaces first
4. Propose implementation plans before making changes.
5. The main objective is to create an architectural plan for the implementation.
