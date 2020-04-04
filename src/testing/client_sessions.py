import aiohttp

from src import auth


def force_authenticate(session, credentials):
    """
    Extend the input session with appropriate headers for authenticating a
    user identified with the argument credentials.
    """
    assert "id" in credentials, "'id' key not found in credentials"
    session._default_headers["Authorization"] = "Bearer {}".format(
        auth.gen_access_token(uid=credentials["id"])
    )
    return None


class TestClientSession:
    """Interface for making HTTP requests in tests.

    Extends the standard client session with a functionality for
    forcefully authenticating a user with respect to the current app
    using their email and password.

    Since inheritance from `aiohttp.ClientSession` has been deprecated
    https://github.com/aio-libs/aiohttp/issues/2691
    this class extends the functionality of the standard client session by aggregation.

    For proper `aiohttp.ClientSession` conforming behaviour, **always** use
    as context manager.

    ```
    with TestClientSession() as test_client:
        ...

    with TestClientSession().force_authenticate({'id': 1024}) as test_client:

    ```
    """

    def __init__(self, **kwargs):
        self.client_session = aiohttp.ClientSession(**kwargs)

    async def __aenter__(self) -> aiohttp.ClientSession:
        async with self.client_session as session:
            return session

    async def __aexit__(self, *args) -> None:
        await self.client_session.close()

    def force_authenticate(self, credentials):
        """
        Return the aggregated client extended with appropriate headers for
        authenticating a user identified with the argument credentials
        """
        force_authenticate(self.client_session, credentials)
        return self
