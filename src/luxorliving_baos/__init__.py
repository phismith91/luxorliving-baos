"""luxorliving-baos: Weinzierl BAOS 777 REST API client for Python."""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerState,
    get_knx_circuit_breaker,
    get_rest_api_circuit_breaker,
)
from .client import BAOSRestClient
from .exceptions import AuthenticationError, CircuitBreakerOpenException, TunnelingError

__version__ = "0.0.1"
__author__ = "Philipp Schmidt"
__license__ = "MIT"

__all__ = [
    "BAOSRestClient",
    "AuthenticationError",
    "TunnelingError",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerState",
    "CircuitBreakerOpenException",
    "get_knx_circuit_breaker",
    "get_rest_api_circuit_breaker",
]
