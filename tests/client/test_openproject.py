"""
Tests for OpenProjectClient.

Concepts learned:
- AsyncMock: simulates async functions/methods
- patch: temporarily replace real dependencies with mocks
- Verifying mock calls (assert_called_once, assert_called_with, etc.)

Why mock? We don't want to create a real httpx.AsyncClient in tests.
We want to verify the client is CONFIGURED correctly without network calls.
"""
import httpx
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.client.openproject import OpenProjectClient


# ============================================================================
# FIXTURE: Fake settings for tests
# ============================================================================

@pytest.fixture
def fake_settings():
    """A fake settings object for testing (no .env file needed)."""
    settings = MagicMock()
    settings.OPENPROJECT_TOKEN = "test-token-123"
    settings.OPENPROJECT_APIROOT = "http://fake-server:8080"
    return settings


# ============================================================================
# CLIENT TESTS
# ============================================================================

@patch("src.client.openproject.httpx.AsyncClient")
def test_client_creates_httpx_with_correct_config(mock_async_client, fake_settings):
    """
    Does OpenProjectClient configure httpx.AsyncClient correctly?

    We patch httpx.AsyncClient so it doesn't create a real HTTP client.
    Instead, mock_async_client is returned whenever httpx.AsyncClient() is called.
    """
    client = OpenProjectClient(fake_settings)

    # Verify httpx.AsyncClient was called with correct arguments
    mock_async_client.assert_called_once_with(
        base_url="http://fake-server:8080",
        auth=mock_async_client.call_args.kwargs["auth"],  # check auth separately
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        timeout=10.0,
    )


@patch("src.client.openproject.httpx.AsyncClient")
def test_client_auth_is_basic_auth(mock_async_client, fake_settings):
    """
    Is the auth configured as httpx.BasicAuth with username "apikey"?

    OpenProject uses API key auth where username is literally "apikey".

    Lesson: httpx.BasicAuth stores credentials internally, not as _auth.username.
    We verify by checking the type and using auth's own properties.
    """
    client = OpenProjectClient(fake_settings)

    # Get the auth object that was passed to httpx.AsyncClient
    call_kwargs = mock_async_client.call_args.kwargs
    auth = call_kwargs["auth"]

    # Verify it's a BasicAuth instance
    assert isinstance(auth, httpx.BasicAuth)

    # httpx.BasicAuth has a .auth_flow() method that uses the credentials
    # The simplest way to verify: check the repr or use the internal tuple
    # httpx.BasicAuth stores as (username, password) in _auth or via properties
    # In httpx 0.28+, we can decode from the authorization header
    import base64
    decoded = base64.b64decode(auth._auth_header.split(" ")[1]).decode()
    username, password = decoded.split(":", 1)
    assert username == "apikey"
    assert password == "test-token-123"


@patch("src.client.openproject.httpx.AsyncClient")
def test_client_get_client_returns_inner_client(mock_async_client, fake_settings):
    """
    Does get_client() return the httpx.AsyncClient instance?

    Our tool functions need the raw httpx client to make HTTP calls.
    get_client() provides access to it.
    """
    client = OpenProjectClient(fake_settings)
    inner_client = client.get_client()

    # Should return the same mock that httpx.AsyncClient() created
    assert inner_client is mock_async_client.return_value


@pytest.mark.asyncio
@patch("src.client.openproject.httpx.AsyncClient")
async def test_client_close_calls_aclose(mock_async_client, fake_settings):
    """
    Does close() call aclose() on the httpx client?

    Proper cleanup is important — we need to close HTTP connections.

    Lesson: When testing async code, the mock must be an AsyncMock
    so that `await mock.aclose()` works. A regular MagicMock would fail
    with "object MagicMock can't be used in 'await' expression".
    """
    # Make the return value an AsyncMock so aclose() can be awaited
    mock_inner_client = AsyncMock()
    mock_async_client.return_value = mock_inner_client

    client = OpenProjectClient(fake_settings)
    await client.close()

    # Verify aclose was called on the inner httpx client
    mock_inner_client.aclose.assert_called_once()
