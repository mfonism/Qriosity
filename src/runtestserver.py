import asyncio

from aiohttp import web

from app import demo_options, init_test_app
from reloading import AsyncHotReloader
from config import basedir


def main():
    # have to import the routes file
    # so that the routes will be registered
    import routes  # noqa

    web.run_app(init_test_app(**demo_options))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncHotReloader.arun(basedir, main))
