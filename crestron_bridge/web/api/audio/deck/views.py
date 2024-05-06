from fastapi import APIRouter

from crestron_bridge.web.api.audio.schema import AudioGetResponse, AudioPost, AudioPostResponse
from crestron_bridge.services.telnet.lifetime import get_telnet_manager
from crestron_bridge.services.state.lifetime import get_server_state

router = APIRouter()
tm = get_telnet_manager()
state = get_server_state()

@router.get("/", response_model=AudioGetResponse)
async def get_deck_audio_status() -> AudioGetResponse:
  print(f"Getting deck audio status from state")
  audio_state = state.get_audio_state("DECK")
  return AudioGetResponse(source=audio_state.source, state=audio_state.state)

@router.post("/turn-on", response_model=AudioPostResponse)
async def turn_on_deck_audio():
  response = tm.send_command("DECK AUDIO SRC SONOS")
  print(response)

  response_text = response.upper()
  if "DECK AUDIO SRC SONOS OK" in response_text:
    return AudioPostResponse(source="SONOS", state="ON", response="OK")

  return AudioPostResponse(source="ERROR", state="ERROR", response="ERROR")

@router.post("/turn-off", response_model=AudioPostResponse)
async def turn_off_deck_audio():
  response = tm.send_command("DECK AUDIO SRC OFF")
  print(response)

  response_text = response.upper()
  if "DECK AUDIO SRC OFF OK" in response_text:
    return AudioPostResponse(source="OFF", state="OFF", response="OK")

  return AudioPostResponse(source="ERROR", state="ERROR", response="ERROR")

@router.post("/select-source", response_model=AudioPostResponse)
async def update_deck_audio_source(
    body: AudioPost,
):
  source = body.source.upper()
  if not source in ["SONOS", "XM", "FM"]:
    return AudioPostResponse(status="ERROR", response="SOURCE NOT FOUND")
  response = tm.send_command(f"DECK AUDIO SRC {source}")
  print(response)

  response_text = response.upper()
  if f"DECK AUDIO SRC {source} OK" in response_text:
    return AudioPostResponse(source=source, state="ON", response="OK")

  return AudioPostResponse(source="ERROR", state="ERROR", response="ERROR")