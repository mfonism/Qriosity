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

    if not auth.validate_email(email):
        return web.json_response(
            {"error": "invalid email"}, status=400, reason="Bad Request"
        )

    if not auth.validate_password(password, username=username, email=email):
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
        },
        status=201,
        reason="Created",
    )


@routes.post("/login/")
async def handle_user_login(request):
    data = await request.json()
    email = data["email"].strip()
    password = data["password"].strip()

    mode = "test" if request.config_dict["TEST"] else ""
    users_table = get_table_fullname("users", mode)

    conn = request.config_dict["DB_CONN"]
    cursor = await conn.cursor()

    await cursor.execute(
        """
        SELECT id, pwd_hash FROM {table_fullname} WHERE email = (?)
        """.format(
            table_fullname=users_table
        ),
        [email],
    )
    row = await cursor.fetchone()

    if not (row and auth.check_password_hash(password, row["pwd_hash"])):
        return web.json_response(
            {"error": "user with given credentials not found"},
            status=404,
            reason="Not Found",
        )

    access_token = auth.gen_access_token(uid=row["id"])
    refresh_token = auth.gen_refresh_token(uid=row["id"], password_hash=row["pwd_hash"])

    return web.json_response(
        {
            "data": {
                "id": row["id"],
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        },
        status=200,
        reason="Ok",
    )
