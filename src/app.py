from aiohttp import web

import config

demo_options = {
    "CLEANUP_CTX": [config.manage_db_conn],
    "ON_STARTUP": [config.create_tables],
    "ROUTER": config.routes,
}


def _init_app(**options):
    """
    Initialize an aiohttp web application.
    """
    app = web.Application()
    app["DEV"] = False
    app["TEST"] = False

    if options.get("ROUTER") is not None:
        app.add_routes(options["ROUTER"])

    if options.get("CLEANUP_CTX") is not None:
        for coro in options["CLEANUP_CTX"]:
            app.cleanup_ctx.append(coro)

    if options.get("ON_STARTUP") is not None:
        for coro in options["ON_STARTUP"]:
            app.on_startup.append(coro)

    return app


def init_prod_app(**options):
    """
    Initialize a production app.
    """
    return _init_app(**options)


def init_dev_app(**options):
    """
    Initialize a development app.
    """
    app = _init_app(**options)
    app["DEV"] = True
    return app


def init_test_app(**options):
    """
    Initialize a test app.
    """
    app = init_dev_app(**options)
    app["TEST"] = True
    return app
