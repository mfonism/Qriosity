import random
import string

import aiohttp
import pytest

import auth


@pytest.mark.asyncio
async def test_handle_user_create(manage_users_table, make_url):
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    async with aiohttp.ClientSession() as test_client:
        async with test_client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 201
            assert resp.reason == "Created"
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
            assert resp.status == 201

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
            assert resp.status == 201
            resp_json = await resp.json()
            data = resp_json["data"]

            cursor = manage_users_table
            await cursor.execute("""SELECT id, email, username FROM test_users;""")
            row = await cursor.fetchone()

            assert row["id"] == data["id"]
            assert row["email"] == data["email"]
            assert row["username"] == data["username"]


@pytest.mark.asyncio
async def test_plaintext_password_is_not_stored_on_db(manage_users_table, make_url):
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    async with aiohttp.ClientSession() as client:
        async with client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 201

    cursor = manage_users_table
    await cursor.execute("""SELECT * FROM test_users;""")
    row = await cursor.fetchone()

    assert payload["password"] not in row


@pytest.mark.asyncio
async def test_salted_hashed_password_in_db(manage_users_table, make_url):
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    async with aiohttp.ClientSession() as client:
        async with client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 201

    cursor = manage_users_table
    await cursor.execute("""SELECT pwd_hash FROM test_users;""")
    row = await cursor.fetchone()

    assert auth.check_password_hash(payload["password"], row["pwd_hash"])


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
            assert resp.status == 201

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
            assert resp.status == 201

        # second instance of payload with username
        async with test_client.post(
            make_url("/users/"), json={**payload, "email": "notintin@gmail.com"}
        ) as resp:
            assert resp.status == 409
            assert resp.reason == "Conflict"
            resp_json = await resp.json()
            assert resp_json["error"] == "user with that username already exists"


pwd_alphabet = set(string.printable) - set(string.whitespace)
pwd_alphabet.add(" ")
pwd_alphabet = list(pwd_alphabet)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bad_data, expected_error",
    [
        # ------------------------------------------
        # INVALID USERNAME
        # ------------------------------------------
        # empty string
        ({"username": ""}, "invalid username"),
        # string containing only space chars
        ({"username": "\n   \t"}, "invalid username"),
        # string under four chars long
        ({"username": "abc"}, "invalid username"),
        # string under four chars long when stripped
        ({"username": "  abc  "}, "invalid username"),
        # ------------------------------------------
        # BAD PASSWORD
        # ------------------------------------------
        # password under min length when stripped
        ({"password": ""}, "bad password"),
        ({"password": "a5exyMe"}, "bad password"),
        ({"password": "  a5exyMe  "}, "bad password"),
        ({"password": "\n       \t"}, "bad password"),
        # password over max length
        (
            {"password": "".join(random.choice(pwd_alphabet) for i in range(65))},
            "bad password",
        ),
        # password with strong similarity to email
        ({"password": "pypylee1", "email": "pypyleecious@gmail.com"}, "bad password"),
        # password with strong similarity to username
        ({"password": "IAmTinboo", "username": "tinboobaby"}, "bad password"),
        # password in the list of common passwords
        ({"password": "bigpimpin1"}, "bad password"),
        ({"password": "nopassword"}, "bad password"),
    ],
)
async def test_cannot_create_user_with_bad_payload(
    manage_users_table, make_url, bad_data, expected_error
):
    payload = {
        "email": "tintin@gmail.com",
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    payload = {**payload, **bad_data}
    async with aiohttp.ClientSession() as client:
        async with client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 400
            assert resp.reason == "Bad Request"
            resp_json = await resp.json()
            assert resp_json["error"] == expected_error


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_email",
    [
        " ",
        " @ ",
        " @ . ",
        "plainaddress",
        "#@%^%#$@#$@#.com",
        "@example.com",
        "Joe Smith <email@example.com>",
        "email.example.com",
        "email@example@example.com",
        ".email@example.com",
        "email.@example.com",
        "email..email@example.com",
        "あいうえお@example.com",
        "email@example.com (Joe Smith)",
        "email@example",
        "email@-example.com",
        "email@example..com",
        "Abc..123@example.com",
        "”(),:;<>[\\]@example.com",
        "just”not”right@example.com",
        'this\\ is"really"not\\allowed@example.com',
    ],
)
async def test_cannot_create_user_with_invalid_email(
    manage_users_table, make_url, invalid_email
):
    """
    List of invalid email addresses are selected from the list at
    https://gist.github.com/cjaoude/fd9910626629b53c4d25
    """
    payload = {
        "username": "Tintin",
        "password": "y0u != n00b1e",
    }
    payload["email"] = invalid_email
    async with aiohttp.ClientSession() as client:
        async with client.post(make_url("/users/"), json=payload) as resp:
            assert resp.status == 400
            assert resp.reason == "Bad Request"
            resp_json = await resp.json()
            assert resp_json["error"] == "invalid email"
