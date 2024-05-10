from fastapi import APIRouter

from crestron_bridge.web.api.lights import media_room, foyer, kitchen
from crestron_bridge.web.api.lights.dependencies import Room, CustomRoom
from crestron_bridge.web.api.lights.custom_rooms import CustomRooms

router = APIRouter()

# router.include_router(media_room.router, prefix="/media-room", tags=["media-room"])
# router.include_router(foyer.router, prefix="/foyer", tags=["foyer"])
# router.include_router(kitchen.router, prefix="/kitchen", tags=["kitchen"])
router.include_router(Room("MEDIA ROOM").router, prefix="/media-room", tags=["media-room"])
router.include_router(Room("FOYER").router, prefix="/foyer", tags=["foyer"])
router.include_router(Room("KITCHEN").router, prefix="/kitchen", tags=["kitchen"])
router.include_router(Room("LIVING").router, prefix="/living-room", tags=["living-room"]) 
router.include_router(Room("DINING").router, prefix="/dining-room", tags=["dining-room"])

router.include_router(Room("JAKE OFFICE").router, prefix="/jake-office", tags=["jake-office"])
router.include_router(Room("JAKE BED").router, prefix="/jake-bedroom", tags=["jake-bedroom"])
router.include_router(Room("MBED").router, prefix="/master-bedroom", tags=["master-bedroom"])
router.include_router(Room("GAME ROOM").router, prefix="/game-room", tags=["game-room"])
router.include_router(CustomRoom(CustomRooms.jake_bath()).router, prefix="/jake-bathroom", tags=["jake-bathroom"])

router.include_router(Room("JWS OFFICE").router, prefix="/jws-office", tags=["jws-office"])  
router.include_router(Room("STAFF RM").router, prefix="/staff-room", tags=["staff-room"])