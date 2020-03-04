import aiohttp
import pytest


@pytest.mark.asyncio
async def test_handle_user_create(manage_users_table, make_url):
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    async with aiohttp.ClientSession() as test_client:
        async with test_client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 200
            assert resp.reason == "OK"
            resp_json = await resp.json()
            assert resp_json["data"] == {
                "id": 1,
                "email": payload["email"],
                "username": payload["username"],
            }


@pytest.mark.asyncio
async def test_num_users_in_db(manage_users_table, make_url):
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }

    cursor = manage_users_table
    await cursor.execute("""SELECT COUNT(*) FROM test_users""")
    row = await cursor.fetchone()
    assert row[0] == 0

    async with aiohttp.ClientSession() as test_client:
        async with test_client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 200
            assert resp.reason == "OK"

    await cursor.execute("""SELECT COUNT(*) FROM test_users""")
    row = await cursor.fetchone()
    assert row[0] == 1


@pytest.mark.asyncio
async def test_created_user_data_in_db(manage_users_table, make_url):
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    async with aiohttp.ClientSession() as test_client:
        async with test_client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 200
            assert resp.reason == "OK"
            resp_json = await resp.json()
            data = resp_json["data"]

            cursor = manage_users_table
            await cursor.execute("""SELECT id, email, username FROM test_users;""")
            row = await cursor.fetchone()

            assert row[0] == data["id"]
            assert row[1] == data["email"]
            assert row[2] == data["username"]


@pytest.mark.asyncio
async def test_plaintext_password_is_not_stored_on_db(manage_users_table, make_url):
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    async with aiohttp.ClientSession() as client:
        async with client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 200
            assert resp.reason == "OK"

    cursor = manage_users_table
    await cursor.execute("""SELECT * FROM test_users;""")
    row = await cursor.fetchone()

    assert payload["password"] not in row


@pytest.mark.asyncio
async def test_cannot_create_user_with_duplicate_email(manage_users_table, make_url):
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    async with aiohttp.ClientSession() as test_client:
        # first instance of payload with email
        async with test_client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 200
            assert resp.reason == "OK"

        # second instance of payload with email
        async with test_client.post(
            make_url("/users/"), json={**payload, "username": "NotTintin"}
        ) as resp:
            assert resp.status == 409
            assert resp.reason == "Conflict"
            resp_json = await resp.json()
            assert resp_json["error"] == "user with that email already exists"


@pytest.mark.asyncio
async def test_cannot_create_user_with_duplicate_username(manage_users_table, make_url):
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    async with aiohttp.ClientSession() as test_client:
        # first instance of payload with username
        async with test_client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 200
            assert resp.reason == "OK"

        # second instance of payload with username
        async with test_client.post(
            make_url("/users/"), json={**payload, "email": "notintin@gmail.com"}
        ) as resp:
            assert resp.status == 409
            assert resp.reason == "Conflict"
            resp_json = await resp.json()
            assert resp_json["error"] == "user with that username already exists"
