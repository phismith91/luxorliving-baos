"""Exceptions for luxorliving-baos package."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class TunnelingError(Exception):
    """Raised when tunneling activation fails."""

    pass


class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is open."""

    pass
