from typing import Awaitable, Callable

from fastapi import FastAPI

import crestron_bridge.services.telnet.lifetime as telnet
import crestron_bridge.services.state.lifetime as state
import crestron_bridge.services.commander.lifetime as commander


def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        await telnet.startup_event()
        await commander.startup_event()
        app.middleware_stack = None
        app.middleware_stack = app.build_middleware_stack()
        pass  # noqa: WPS420

    return _startup


def register_shutdown_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        await commander.shutdown_event()
        await telnet.shutdown_event()
        pass  # noqa: WPS420

    return _shutdown
