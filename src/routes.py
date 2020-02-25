from aiohttp import web

from config import routes


@routes.post("/users/")
async def handle_user_create(request):
    return web.json_response(
        {"status": "ok", "data": {"username": "Tintin", "email": "tintin@gmail.com"}}
    )
