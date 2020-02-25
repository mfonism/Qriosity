from aiohttp import web

from app import demo_options, init_test_app
from reloading import HotReloader
from config import basedir


def main():
    # have to import the routes file
    # so that the routes will be registered
    import routes  # noqa

    web.run_app(init_test_app(**demo_options))


if __name__ == "__main__":
    HotReloader.run(basedir, main)
