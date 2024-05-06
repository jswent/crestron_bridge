from importlib import metadata

from fastapi import FastAPI, Request, Response
from fastapi.responses import UJSONResponse

from crestron_bridge.web.api.router import api_router
from crestron_bridge.web.lifetime import register_shutdown_event, register_startup_event

from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        print(f"Outgoing response: {response.status_code}")
        return response

def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="crestron_bridge",
        version=metadata.version("crestron_bridge"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    app.add_middleware(LoggingMiddleware)

    return app
