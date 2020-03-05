import sqlite3

from aiohttp import web

import auth
from config import routes
from db.utils import get_table_fullname


@routes.post("/users/")
async def handle_user_create(request):
    data = await request.json()
    email = data["email"].strip()
    username = data["username"].strip()
    password = data["password"].strip()

    if not auth.validate_username(username):
        return web.json_response(
            {"error": "invalid username"}, status=400, reason="Bad Request"
        )

    if not auth.validate_password(password):
        return web.json_response(
            {"error": "bad password"}, status=400, reason="Bad Request"
        )

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
            (email, username, auth.get_password_hash(password)),
        )
    except sqlite3.IntegrityError as exc:
        await conn.rollback()
        if "email" in str(exc):
            return web.json_response(
                {"error": "user with that email already exists"},
                status=409,
                reason="Conflict",
            )
        if "username" in str(exc):
            return web.json_response(
                {"error": "user with that username already exists"},
                status=409,
                reason="Conflict",
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

    return web.json_response(
        {
            "data": {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
            },
        }
    )
