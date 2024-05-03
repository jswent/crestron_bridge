from fastapi import APIRouter

from crestron_bridge.web.api.audio import deck

router = APIRouter()

router.include_router(deck.router, prefix="/deck", tags=["deck"])
