from pathlib import Path

import aiosqlite
from aiohttp import web

from db import stmts
from db.utils import get_db_path

basedir = Path(__file__).absolute().parent
routes = web.RouteTableDef()


async def manage_db_conn(app):
    """
    Initialize a database connection for argument app.
    Cleanup connection at end of app's lifecycle.

    https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Application.cleanup_ctx
    """
    mode = "test" if app["TEST"] else ""
    db_path = str(get_db_path(basedir, mode=mode))

    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        app["DB_CONN"] = conn
        yield


async def manage_tables(app):
    """
    Manage the creation and dropping of tables at the
    beginning and end (respectively) of argument app's lifecycle.

    https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Application.cleanup_ctx
    """
    mode = "test" if app["TEST"] else ""
    db_path = str(get_db_path(basedir, mode=mode))

    users_table_create_stmt, users_table_drop_stmt = stmts.get_create_drop_stmts(
        stmts.users_table_create_template, table_name="users", mode=mode
    )

    # execute CREATE statements
    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.cursor()
        await cursor.execute(users_table_create_stmt)
        await conn.commit()

    yield

    # execute DROP statements
    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.cursor()
        await cursor.execute(users_table_drop_stmt)
        await conn.commit()
