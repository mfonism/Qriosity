from pathlib import Path

import aiohttp
import pytest

BASE_URL = "http://localhost:8080"
TEST_DB_PATH = Path(__file__).absolute().parent.joinpath("test_db.sqlite")


def make_url(path):
    return "{}{}".format(BASE_URL, path)


@pytest.mark.asyncio
async def test_handle_user_create():
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    async with aiohttp.ClientSession(raise_for_status=True) as test_client:
        async with test_client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 200
            resp_json = await resp.json()
            print(resp_json)
            assert resp_json["status"] == "ok"
            assert resp_json["data"] == {
                "email": payload["email"],
                "username": payload["username"],
            }
