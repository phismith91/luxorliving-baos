"""Tests for circuit breaker."""

import asyncio

import pytest

from luxorliving_baos import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenException,
    CircuitBreakerState,
)


class TestCircuitBreakerConfig:
    """Test CircuitBreakerConfig."""

    def test_default_config(self):
        """Test default circuit breaker config."""
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60.0
        assert config.success_threshold == 3
        assert config.timeout == 10.0

    def test_custom_config(self):
        """Test custom circuit breaker config."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30.0,
            success_threshold=2,
            timeout=15.0,
        )
        assert config.failure_threshold == 3
        assert config.recovery_timeout == 30.0
        assert config.success_threshold == 2
        assert config.timeout == 15.0


class TestCircuitBreakerInit:
    """Test CircuitBreaker initialization."""

    def test_init_default(self):
        """Test initialization with default config."""
        breaker = CircuitBreaker("test")
        assert breaker.name == "test"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker._failure_count == 0
        assert breaker._success_count == 0
        assert breaker._call_count == 0

    def test_init_custom_config(self):
        """Test initialization with custom config."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker("test", config)
        assert breaker.config.failure_threshold == 3


class TestCircuitBreakerCall:
    """Test circuit breaker call execution."""

    @pytest.mark.asyncio
    async def test_call_success(self):
        """Test successful call."""
        breaker = CircuitBreaker("test")

        async def success_func():
            return "success"

        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED

    @pytest.mark.asyncio
    async def test_call_failure(self):
        """Test failed call."""
        breaker = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=1))

        async def fail_func():
            raise ValueError("test error")

        with pytest.raises(ValueError):
            await breaker.call(fail_func)

        assert breaker.state == CircuitBreakerState.OPEN

    @pytest.mark.asyncio
    async def test_call_open_circuit(self):
        """Test call when circuit is open."""
        breaker = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=1))

        async def fail_func():
            raise ValueError("test error")

        # First call fails, opens circuit
        with pytest.raises(ValueError):
            await breaker.call(fail_func)

        assert breaker.state == CircuitBreakerState.OPEN

        # Second call is rejected immediately
        with pytest.raises(CircuitBreakerOpenException):
            await breaker.call(fail_func)


class TestCircuitBreakerStats:
    """Test circuit breaker statistics."""

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test get_stats returns correct data."""
        breaker = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))

        async def success_func():
            return "success"

        await breaker.call(success_func)
        stats = breaker.get_stats()

        assert stats["name"] == "test"
        assert stats["state"] == "closed"
        assert stats["failure_count"] == 0
        assert stats["success_count"] == 0
        assert stats["call_count"] == 1
        assert stats["config"]["failure_threshold"] == 3
