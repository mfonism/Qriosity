import aiosqlite

import pytest

from src.config import basedir
from src.db import stmts
from src.db.utils import get_db_path


@pytest.fixture(name="basedir", scope="session")
def fixture_base_dir():
    """
    Return the base directory for source code.
    """
    return basedir


@pytest.fixture(name="test_db_path", scope="session")
def fixture_test_db_path():
    """
    Return the path to the test db.
    """
    return get_db_path(basedir, mode="test")


@pytest.fixture(name="manage_users_table")
async def fixture_manage_users_table(test_db_path):
    """
    Manage the creation and dropping of users table around tests.

    NOT SO MUCH A TRICK:
    This fixture ensures that the test starts with a fresh table
    by dropping stale table before test run, and creating fresh table afterwards.
    """

    table_create_stmt, table_drop_stmt = stmts.get_create_drop_stmts(
        stmts.users_table_create_template, table_name="users", mode="test"
    )

    async with aiosqlite.connect(str(test_db_path)) as conn:
        cursor = await conn.cursor()
        await cursor.execute(table_drop_stmt)
        await conn.commit()
        await cursor.execute(table_create_stmt)
        await conn.commit()
        yield cursor


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
