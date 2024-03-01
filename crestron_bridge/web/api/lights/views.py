from fastapi import APIRouter

from crestron_bridge.web.api.lights import media_room, foyer, kitchen

router = APIRouter()

router.include_router(media_room.router, prefix="/media-room", tags=["media-room"])
router.include_router(foyer.router, prefix="/foyer", tags=["foyer"])
router.include_router(kitchen.router, prefix="/kitchen", tags=["kitchen"])