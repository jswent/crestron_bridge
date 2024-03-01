from fastapi.routing import APIRouter

from crestron_bridge.web.api import echo, monitoring, mediaRoom, lights

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(mediaRoom.router, prefix="/media-room", tags=["media-room"])
api_router.include_router(lights.router, prefix="/lts", tags=["lights"])