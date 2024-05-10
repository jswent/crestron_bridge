from fastapi import APIRouter

from crestron_bridge.web.api.mediaRoom.schema import MediaRoomPost, MediaRoomSelectSourcePost, MediaRoomPostResponse, MediaRoomGetResponse
from crestron_bridge.services.telnet.lifetime import get_telnet_manager
from crestron_bridge.services.state.lifetime import get_server_state

router = APIRouter()
tm = get_telnet_manager()
state = get_server_state()

@router.post("/", response_model=MediaRoomPost)
async def update_media_room_status(
    media_room_status: MediaRoomPost,
):
  status = media_room_status.status.upper()
  response = tm.send_command(f"MEDIA ROOM POWER {status}")
  print(response)

  response_text = response.upper()
  switch_response = {
    "MEDIA ROOM POWER ON": MediaRoomPostResponse(status="POWERING UP", response="OK"),
    "MEDIA ROOM POWER OFF": MediaRoomPostResponse(status="POWERING DOWN", response="OK")
  }
  for key in switch_response:
    if key in response_text:
      return switch_response[key]
  return MediaRoomPostResponse(status="ERROR", response="ERROR")

@router.get("/", response_model=MediaRoomGetResponse)
async def get_media_room_status() -> MediaRoomGetResponse:
  print(f"Getting media room status from state")
  media_state = state.get_media_room_state()
  return MediaRoomGetResponse(status=media_state.status, source=media_state.source, is_active=media_state.is_active)

@router.post("/turn-on", response_model=MediaRoomPostResponse)
async def turn_on():
  response = tm.send_command("MEDIA ROOM POWER ON")
  print(response)

  response_text = response.upper()
  if "MEDIA ROOM POWER ON OK" in response_text:
    state.update_media_room_state(status="ON", is_active="true")
    return MediaRoomPostResponse(status="POWERING UP", response="OK")
  return MediaRoomPostResponse(status="ERROR", response="ERROR")

@router.post("/turn-off", response_model=MediaRoomPostResponse)
async def turn_off():
  response = tm.send_command("MEDIA ROOM POWER OFF")
  print(response)

  response_text = response.upper()
  if "MEDIA ROOM POWER OFF OK" in response_text:
    state.update_media_room_state(status="OFF", is_active="false")
    return MediaRoomPostResponse(status="POWERING DOWN", response="OK")
  return MediaRoomPostResponse(status="ERROR", response="ERROR")

@router.post("/select-source", response_model=MediaRoomPostResponse)
async def select_source(
    body: MediaRoomSelectSourcePost,
):
  response = tm.send_command(f"MEDIA ROOM SRC {body.source}")
  print(response)

  response_text = response.upper()
  if f"MEDIA ROOM SRC {body.source} OK" in response_text:
    state.update_media_room_state(source=body.source)
    media_state = state.get_media_room_state()
    return MediaRoomPostResponse(status=media_state.status, source=body.source, response="OK")
  return MediaRoomPostResponse(status="ERROR", source="ERROR", response="ERROR")