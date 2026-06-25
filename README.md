# luxorliving-baos

Weinzierl BAOS 777 REST API client for Python. Async/await support with circuit breaker resilience.

A standalone Python library for communicating with the Theben LUXORliving KNX system via the IP1 interface's BAOS REST API.

## Installation

```bash
pip install luxorliving-baos
```

## Quick Start

```python
import asyncio
from luxorliving_baos import BAOSRestClient

async def main():
    async with BAOSRestClient("192.168.1.3") as client:
        # Login with credentials
        token = await client.login("admin", "your_password")
        print(f"✅ Logged in. Token: {token[:20]}...")

        # Enable KNX tunneling
        await client.enable_tunneling()
        print("✅ KNX Tunneling enabled")

        # Check tunneling status
        status = await client.get_tunneling_status()
        print(f"📊 Status: {status}")

        # Logout (auto-disables tunneling)
        await client.logout()
        print("✅ Logged out")

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- **Async/Await**: Fully asynchronous with asyncio
- **Session Management**: Automatic login/logout with 24-hour session expiry tracking
- **KNX Tunneling**: Enable/disable KNX tunneling via REST API
- **Circuit Breaker**: Resilient error handling with automatic recovery
- **TLS Legacy Support**: Custom SSL context for IP1's legacy TLS requirements
- **No Blocking I/O**: Pure async, safe for use in Home Assistant and other async frameworks

## API Reference

### BAOSRestClient

Main client class for BAOS 777 REST API communication.

```python
client = BAOSRestClient(
    host="192.168.1.3",
    port=443,
    use_https=True,
    session=None  # Optional: provide your own aiohttp.ClientSession
)
```

#### Methods

- `async login(username: str, password: str) -> str` — Login and return session token
- `async logout()` — Logout and end session (auto-disables tunneling)
- `async enable_tunneling() -> bool` — Enable KNX tunneling
- `async disable_tunneling() -> bool` — Disable KNX tunneling
- `async get_tunneling_status() -> dict` — Get tunneling status
- `is_authenticated` — Property: check if client is authenticated
- `get_diagnostics() -> dict` — Get diagnostic info

#### Exceptions

- `AuthenticationError` — Login failed or session expired
- `TunnelingError` — Tunneling activation failed
- `CircuitBreakerOpenException` — Circuit breaker is open (service recovering)

### Circuit Breaker

The library includes a resilient circuit breaker pattern for REST API calls. It automatically:

- Opens after 3 consecutive failures
- Waits 30 seconds before attempting recovery
- Closes after 2 consecutive successes
- Times out operations after 15 seconds

## Using with Home Assistant

The library is designed to work with Home Assistant's async patterns:

```python
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from luxorliving_baos import BAOSRestClient

async def setup(hass, config):
    # Use Home Assistant's shared session
    session = async_get_clientsession(hass, verify_ssl=False)
    client = BAOSRestClient("192.168.1.3", session=session)
    
    await client.login("admin", "password")
    # ... rest of setup
```

## Development

### Setup

```bash
git clone https://github.com/phismith91/luxorliving-baos
cd luxorliving-baos
pip install -e ".[dev]"
pre-commit install
```

### Testing

```bash
# Run tests
pytest tests/ -n 1

# With coverage
pytest tests/ --cov=src/luxorliving_baos --cov-report=html

# Type checking
mypy src/

# Linting
flake8 src/ tests/
pylint src/
bandit src/
```

### Pre-commit Hooks

The repo uses pre-commit hooks for code quality (black, isort, flake8, bandit, etc.).

```bash
pre-commit run --all-files
```

## Requirements

- Python >= 3.13
- aiohttp >= 3.10.0

## License

MIT License - see LICENSE file

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## References

- [Theben LUXORliving Documentation](https://www.theben.de/)
- [Home Assistant Integration](https://github.com/phismith91/luxorliving)
