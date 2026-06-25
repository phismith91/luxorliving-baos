"""Pytest configuration and shared fixtures for luxorliving-baos tests."""

import pytest


@pytest.fixture
def baos_host():
    """Return test BAOS host."""
    return "192.168.1.3"


@pytest.fixture
def baos_port():
    """Return test BAOS port."""
    return 443


@pytest.fixture
def baos_credentials():
    """Return test credentials."""
    return {"username": "admin", "password": "password"}
