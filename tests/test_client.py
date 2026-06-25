"""Tests for BAOSRestClient."""

import pytest

from luxorliving_baos import BAOSRestClient, AuthenticationError


class TestBAOSRestClientInit:
    """Test BAOSRestClient initialization."""

    def test_init_default_https(self, baos_host):
        """Test initialization with default HTTPS."""
        client = BAOSRestClient(baos_host)
        assert client.host == baos_host
        assert client.port == 443
        assert client.use_https is True
        assert client.base_url == f"https://{baos_host}:443"
        assert client.session_token is None
        assert client.tunneling_enabled is False
        assert client.is_authenticated is False

    def test_init_custom_port(self, baos_host):
        """Test initialization with custom port."""
        client = BAOSRestClient(baos_host, port=8443)
        assert client.port == 8443
        assert client.base_url == f"https://{baos_host}:8443"

    def test_init_http(self, baos_host):
        """Test initialization with HTTP."""
        client = BAOSRestClient(baos_host, use_https=False)
        assert client.use_https is False
        assert client.base_url == f"http://{baos_host}:443"

    def test_init_with_session(self, baos_host):
        """Test initialization with provided session."""
        from unittest.mock import MagicMock
        session = MagicMock()
        client = BAOSRestClient(baos_host, session=session)
        assert client._session is session
        assert client._owns_session is False

    def test_init_without_session(self, baos_host):
        """Test initialization without session (owns it)."""
        client = BAOSRestClient(baos_host)
        assert client._session is None
        assert client._owns_session is True


class TestBAOSRestClientAuthentication:
    """Test authentication-related methods."""

    def test_ensure_authenticated_not_logged_in(self, baos_host):
        """Test _ensure_authenticated raises when not logged in."""
        client = BAOSRestClient(baos_host)
        with pytest.raises(AuthenticationError, match="Not logged in"):
            client._ensure_authenticated()

    def test_get_diagnostics(self, baos_host):
        """Test get_diagnostics returns client state."""
        client = BAOSRestClient(baos_host)
        diag = client.get_diagnostics()

        assert diag["host"] == baos_host
        assert diag["port"] == 443
        assert diag["use_https"] is True
        assert diag["authenticated"] is False
        assert diag["session_token"] is False
        assert diag["tunneling_enabled"] is False


class TestBAOSRestClientAuthHeaders:
    """Test authentication header generation."""

    def test_get_auth_headers_no_token(self, baos_host):
        """Test _get_auth_headers with no token."""
        client = BAOSRestClient(baos_host)
        headers = client._get_auth_headers()
        assert headers == {}

    def test_get_auth_headers_with_token(self, baos_host):
        """Test _get_auth_headers with token."""
        client = BAOSRestClient(baos_host)
        client.session_token = "test_token_123"

        headers = client._get_auth_headers()
        assert "Cookie" in headers
        assert "Authorization" in headers
        assert "Token token=test_token_123" in headers["Authorization"]
        assert 'user=%22test_token_123%22' in headers["Cookie"]


class TestIsAuthenticated:
    """Test is_authenticated property."""

    def test_is_authenticated_no_token(self, baos_host):
        """Test is_authenticated when no token."""
        client = BAOSRestClient(baos_host)
        assert client.is_authenticated is False

    def test_is_authenticated_with_token_no_expiry(self, baos_host):
        """Test is_authenticated with token and no expiry."""
        from datetime import datetime, timedelta
        client = BAOSRestClient(baos_host)
        client.session_token = "test_token"
        client.session_expires = datetime.now() + timedelta(hours=1)

        assert client.is_authenticated is True

    def test_is_authenticated_with_expired_token(self, baos_host):
        """Test is_authenticated with expired token."""
        from datetime import datetime, timedelta
        client = BAOSRestClient(baos_host)
        client.session_token = "test_token"
        client.session_expires = datetime.now() - timedelta(seconds=1)

        assert client.is_authenticated is False
