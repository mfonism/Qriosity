import sqlite3

from aiohttp import web

from config import routes
from db.utils import get_table_fullname


@routes.post("/users/")
async def handle_user_create(request):
    data = await request.json()
    email = data["email"]
    username = data["username"]
    password = data["password"]

    mode = "test" if request.config_dict["TEST"] else ""
    users_table = get_table_fullname("users", mode)

    conn = request.config_dict["DB_CONN"]
    cursor = await conn.cursor()

    try:
        await cursor.execute(
            """
            INSERT INTO {table_fullname}
            (email, username, pwd_hash)
            VALUES
            (?,?,?)
            """.format(
                table_fullname=users_table
            ),
            (email, username, password),
        )
        await conn.commit()
        await cursor.execute(
            """
            SELECT id, username, email FROM {table_fullname} WHERE id = (?)
            """.format(
                table_fullname=users_table
            ),
            [cursor.lastrowid],
        )
        row = await cursor.fetchone()
    except sqlite3.IntegrityError as exc:
        await conn.rollback()
        if "email" in str(exc):
            return web.json_response(
                {"error": "user with that email already exists"},
                status=409,
                reason="conflict",
            )

    return web.json_response(
        {
            "status": "ok",
            "data": {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
            },
        }
    )
