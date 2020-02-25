import pytest


@pytest.fixture(name="base_url", scope="session")
def fixture_base_url():
    return "http://localhost:8080"


@pytest.fixture(name="make_url", scope="session")
def fixture_make_url(base_url):
    """
    Return helper which creates full url from a url path.
    """

    def _make_url(path):
        return "{}{}".format(base_url, path)

    return _make_url
