from fastapi import APIRouter

from crestron_bridge.web.api.audio.schema import AudioGetResponse, AudioPost, AudioPostResponse
from crestron_bridge.services.telnet.lifetime import get_telnet_manager

router = APIRouter()
tm = get_telnet_manager()

@router.get("/", response_model=AudioGetResponse)
async def get_deck_audio_status() -> AudioGetResponse:
  response = tm.send_command("DECK AUDIO SRC STATUS")
  print(response)

  response_text = response.upper()
  if "DECK AUDIO SRC STATUS SONOS OK" in response_text:
    return AudioGetResponse(source="SONOS", state="ON")
  elif "DECK AUDIO SRC STATUS XM OK" in response_text:
    return AudioGetResponse(source="XM", state="ON")
  elif "DECK AUDIO SRC STATUS FM OK" in response_text:
    return AudioGetResponse(source="FM", state="ON")
  elif "DECK AUDIO SRC STATUS OFF OK" in response_text:
    return AudioGetResponse(source="OFF", state="OFF")
  else:
    return AudioGetResponse(source="ERROR", state="ERROR")

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