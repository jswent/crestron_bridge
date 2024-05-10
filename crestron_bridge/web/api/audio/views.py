from fastapi import APIRouter

from crestron_bridge.web.api.audio import deck
from crestron_bridge.web.api.audio.dependencies import AudioLocation

router = APIRouter()

router.include_router(deck.router, prefix="/deck", tags=["deck"])
router.include_router(AudioLocation("KITCHEN").router, prefix="/kitchen", tags=["kitchen"])
