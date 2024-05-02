from fastapi import APIRouter

from crestron_bridge.web.api.lights import media_room, foyer, kitchen
from crestron_bridge.web.api.lights.dependencies import Room

router = APIRouter()

router.include_router(media_room.router, prefix="/media-room", tags=["media-room"])
router.include_router(foyer.router, prefix="/foyer", tags=["foyer"])
router.include_router(kitchen.router, prefix="/kitchen", tags=["kitchen"])
router.include_router(Room("JAKE OFFICE").router, prefix="/jake-office", tags=["jake-office"])
router.include_router(Room("JWS OFFICE").router, prefix="/jws-office", tags=["jws-office"])  
router.include_router(Room("LIVING ROOM").router, prefix="/living-room", tags=["living-room"]) 
router.include_router(Room("STAFF ROOM").router, prefix="/staff-room", tags=["staff-room"])
router.include_router(Room("MBED").router, prefix="/master-bedroom", tags=["master-bedroom"])
router.include_router(Room("GAME ROOM").router, prefix="/game-room", tags=["game-room"])
router.include_router(Room("DINING").router, prefix="/dining-room", tags=["dining-room"])