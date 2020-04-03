import aiohttp
import pytest


@pytest.mark.asyncio
async def test_handle_user_login(manage_users_table, make_url):
    login_user_payload = {
        "email": "tintin@gmail.com",
        "password": "y0u != n00b1e",
    }
    create_user_payload = {"username": "Tintin", **login_user_payload}
    async with aiohttp.ClientSession() as test_client:

        # create user
        async with test_client.post(
            make_url("/users/"), json=create_user_payload
        ) as resp:
            assert resp.status == 201
            resp_json = await resp.json()
            uid = resp_json["data"]["id"]

        # attempt to log em in
        async with test_client.post(
            make_url("/login/"), json=login_user_payload
        ) as resp:
            assert resp.status == 200
            resp_json = await resp.json()
            assert resp_json["data"]["id"] == uid


@pytest.mark.asyncio
async def test_tokens_are_returned_on_login(manage_users_table, make_url):
    login_user_payload = {
        "email": "tintin@gmail.com",
        "password": "y0u != n00b1e",
    }
    create_user_payload = {"username": "Tintin", **login_user_payload}

    async with aiohttp.ClientSession() as test_client:
        # create user
        async with test_client.post(
            make_url("/users/"), json=create_user_payload
        ) as resp:
            assert resp.status == 201

        # attempt to log them in
        async with test_client.post(
            make_url("/login/"), json=login_user_payload
        ) as resp:
            assert resp.status == 200
            resp_json = await resp.json()
            assert "access_token" in resp_json["data"]
            assert "refresh_token" in resp_json["data"]


@pytest.mark.asyncio
async def test_cannot_login_with_bad_credentials(manage_users_table, make_url):
    create_user_payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }

    async with aiohttp.ClientSession() as test_client:
        async with test_client.post(
            make_url("/users/"), json=create_user_payload
        ) as resp:
            assert resp.status == 201

        wrong_email = "wrongemail@gmail.com"
        wrong_password = "wr0ngPa55w0rd!"

        # attempt to log in with wrong email
        async with test_client.post(
            make_url("/login/"),
            json={"email": wrong_email, "password": create_user_payload["password"]},
        ) as resp:
            assert resp.status == 404
            resp_json = await resp.json()
            assert resp_json["error"] == "user with given credentials not found"

        # attempt to log in with wrong password
        async with test_client.post(
            make_url("/login/"),
            json={"email": create_user_payload["email"], "password": wrong_password},
        ) as resp:
            assert resp.status == 404
            resp_json = await resp.json()
            assert resp_json["error"] == "user with given credentials not found"
