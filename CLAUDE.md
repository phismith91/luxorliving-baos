# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Library Does

**luxorliving-baos** is a standalone Python REST API client for Weinzierl BAOS 777 (Theben LUXORliving KNX interface). It extracts the HTTP communication layer that the Home Assistant integration previously embedded, enabling reusable, testable, and PyPI-publishable code.

Core flows:
1. **Session Management**: Login → token → 24-hour expiry tracking
2. **KNX Tunneling**: Activate/deactivate via REST API with circuit breaker protection
3. **Error Resilience**: Circuit breaker auto-opens after 3 failures, retries after 30s

## Architecture

**Minimal (655 LOC source):**
- `src/luxorliving_baos/client.py` — BAOSRestClient: login, tunneling control, status queries
- `src/luxorliving_baos/circuit_breaker.py` — CircuitBreaker: resilience pattern (state machine: CLOSED → OPEN → HALF_OPEN)
- `src/luxorliving_baos/exceptions.py` — AuthenticationError, TunnelingError, CircuitBreakerOpenException
- `src/luxorliving_baos/__init__.py` — Public API exports

**Key design:**
- Pure async (no blocking I/O), safe for Home Assistant
- Optional session injection (`BAOSRestClient(host, session=hass_session)`) for HA's shared session
- Falls back to own session with custom SSL context for IP1's legacy TLS
- All REST calls wrapped by circuit breaker (failure threshold: 3, recovery: 30s, success threshold: 2)

## Common Commands

```bash
# Install dev environment
pip install -e ".[dev]"
pre-commit install

# Test with coverage
pytest tests/ -n 1 --cov=src/luxorliving_baos --cov-report=html

# Single test
pytest tests/test_circuit_breaker.py::TestCircuitBreakerCall::test_call_success -v

# Type check
mypy src/

# Lint & format
flake8 src/ tests/
black --check src/ tests/
pre-commit run --all-files

# Build
python -m build

# Publish (manual, requires PyPI token)
twine upload dist/*
```

## Critical Notes

- **Tests don't use Home Assistant fixtures** — this is a standalone library, not an HA integration. Tests use plain unittest.mock.
- **Async-only** — all public methods are async. No blocking calls.
- **Circuit breaker is singleton** — `get_rest_api_circuit_breaker()` and `get_knx_circuit_breaker()` return module-level instances. State persists across client instances.
- **Session ownership** — if you don't pass a session, the client creates and owns one. You close it in `__aexit__`. If you pass a session, you own its lifecycle.
- **TLS legacy workaround** — IP1 ships with self-signed cert + legacy cipher. Client auto-creates SSL context with `@SECLEVEL=0` if needed.

## Integration with Home Assistant

The luxorliving integration (sibling repo) imports this as a PyPI dependency:
```python
from luxorliving_baos import BAOSRestClient, AuthenticationError, TunnelingError
```

The refactoring (2026-06-25) removed embedded copies of rest_client.py and circuit_breaker.py from luxorliving, making this repo the single source of truth.

## Git Workflow

**Branch Strategy:**

- Never commit directly to `main`
- All changes via feature branch: `git checkout -b feature/your-feature-name`
- Prefix branches: `feature/`, `fix/`, `docs/`, `chore/`
- Example: `feature/add-tunneling-timeout`, `fix/circuit-breaker-race-condition`

**Merge to Main:**

1. Create pull request from feature branch
2. Pass all pre-merge checks (see below)
3. Code review approval required
4. Merge with commit message referencing the branch: `Merge branch 'feature/name' into main`

## Pre-Merge Checks

**All of these must pass before merging to main:**

```bash
# 1. Unit tests (serial, no parallel execution)
pytest tests/ -n 1 --cov=src/luxorliving_baos --cov-report=term-missing

# 2. Coverage threshold: 44%+ (or existing baseline, whichever is higher)
# Check output: look for "TOTAL" line, must show >= 44%

# 3. Type hints: mypy passes without errors
mypy src/

# 4. Linting: all tools pass
flake8 src/ tests/
black --check src/ tests/
isort --check-only src/ tests/

# 5. Security audit: bandit finds no HIGH or CRITICAL issues
bandit -r src/

# 6. Code builds successfully
python -m build

# 7. Package installs and imports work
pip install -e . && python -c "from luxorliving_baos import BAOSRestClient, get_knx_circuit_breaker; print('OK')"
```

**If any check fails:** Fix locally on feature branch, push, and re-run checks. CI/CD (GitHub Actions) will also run these automatically.

## For Future Changes

**New feature checklist:**
- Keep client focused on REST communication (no KNX parsing, no HA entity mapping — that's luxorliving's job)
- Circuit breaker is not user-configurable (thresholds are baked in); if tuning needed, add a config object to CircuitBreakerConfig
- Type hints required (mypy passes)
- Async all the way — no sync wrappers
- No external deps beyond aiohttp

**Testing:**
- 20+ tests currently cover initialization and circuit breaker state machine
- Future tests should mock aiohttp.ClientSession, not hit real servers
- Aim for 44%+ overall coverage (currently at baseline after extraction)
