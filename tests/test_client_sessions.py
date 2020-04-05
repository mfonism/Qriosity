import aiohttp
import pytest
from datetime import datetime

from src import auth
from src.testing.client_sessions import TestClientSession


@pytest.mark.asyncio
async def test_test_client_session():
    """
    Assert that the class `TestClientSession` conforms to the interface of
    `aiohttp.ClientSession` when used in a context manager.
    """
    async with TestClientSession() as test_client:
        assert isinstance(test_client, aiohttp.ClientSession)


@pytest.mark.asyncio
async def test_forcefully_authenticated_test_client_session():
    """
    Assert that the class `TestClientSession` conforms to the interface of
    `aiohttp.ClientSession` when used in a context manager.
    """
    async with TestClientSession().force_authenticate(
        credentials={"id": 1}
    ) as test_client:
        assert isinstance(test_client, aiohttp.ClientSession)


@pytest.mark.asyncio
async def test_test_client_session_not_so_useful_outside_context_manager():
    """
    **For now...**
    Assert that when used outside a context manager, the class `TestClientSession`
    does not conform to the interface of `aiohttp.ClientSession`
    """
    test_client_ish = TestClientSession()
    assert not isinstance(test_client_ish, aiohttp.ClientSession)

    test_client_ish = TestClientSession().force_authenticate(credentials={"id": 1})
    assert not isinstance(test_client_ish, aiohttp.ClientSession)


@pytest.mark.asyncio
@pytest.mark.freeze_time(datetime.utcnow())
async def test_authorization_header_on_forced_authentication():
    """
    Assert that the appropriate headers are set in test client session
    on forced authentication.
    """
    uid = 1024
    async with TestClientSession().force_authenticate({"id": uid}) as test_client:
        headers = test_client._prepare_headers(dict())
        assert headers == {
            "Authorization": "Bearer {}".format(auth.gen_access_token(uid))
        }
