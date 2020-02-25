import sqlite3
from pathlib import Path

from aiohttp import web

basedir = Path(__file__).absolute().parent

routes = web.RouteTableDef()


async def init_db_conn(app):
    """
    Initialize a database connection for argument app.
    """
    db_path = basedir.joinpath("{}db.sqlite".format("test_" if app["TEST"] else ""))
    with sqlite3.connect(str(db_path)) as conn:
        app["DB_CONN"] = conn
        yield
