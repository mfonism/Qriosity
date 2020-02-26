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
            "status": "ok",
            "data": {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
            },
        }
    )
