from fastapi import APIRouter

from crestron_bridge.web.api.audio import deck
from crestron_bridge.web.api.audio.dependencies import AudioLocation

router = APIRouter()

router.include_router(deck.router, prefix="/deck", tags=["deck"])
router.include_router(AudioLocation("KITCHEN").router, prefix="/kitchen", tags=["kitchen"])
router.include_router(AudioLocation("DINING ROOM").router, prefix="/dining-room", tags=["dining-room"])
router.include_router(AudioLocation("GAME ROOM").router, prefix="/game-room", tags=["game-room"])
router.include_router(AudioLocation("JAKE OFFICE").router, prefix="/jake-office", tags=["jake-office"])
