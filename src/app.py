import sqlite3
from pathlib import Path

from aiohttp import web

router = web.RouteTableDef()


@router.post("/users/")
async def handle_user_create(request):
    data = await request.json()
    username = data["username"]
    email = data["email"]
    return web.json_response(
        {"status": "ok", "data": {"username": username, "email": email}}
    )


async def init_app(db_conn_initializer):
    """
    Initialize the app.
    """
    app = web.Application()
    app.add_routes(router)
    app.cleanup_ctx.append(db_conn_initializer)
    return app


def _get_db_conn_initializer(db_path):
    """
    Wrap an async database connection initializer.

    This makes it possible to swap paths for the database while testing.
    """

    async def init_db_conn(app):
        """
        Initialize a database connection.
        """
        with sqlite3.connect(str(db_path)) as conn:
            app["DB_CONN"] = conn
            yield

    return init_db_conn


def run(db_path):
    web.run_app(init_app(_get_db_conn_initializer(db_path)))


if __name__ == "__main__":
    DB_PATH = Path(__file__).absolute().parent.joinpath("db.sqlite")
    run(DB_PATH)
