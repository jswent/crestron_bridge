from fastapi import APIRouter

from crestron_bridge.web.api.mediaRoom.schema import MediaRoomPost, MediaRoomPostResponse, MediaRoomGetResponse
from crestron_bridge.services.telnet.lifetime import get_telnet_manager

router = APIRouter()
tm = get_telnet_manager()

@router.post("/", response_model=MediaRoomPost)
async def update_media_room_status(
    media_room_status: MediaRoomPost,
):
  status = media_room_status.status.upper()
  response = tm.send_command(f"MEDIA ROOM {status}")
  print(response)

  response_text = response.upper()
  switch_response = {
    "MEDIA ROOM ON": MediaRoomPostResponse(status="POWERING UP", response="OK"),
    "MEDIA ROOM OFF": MediaRoomPostResponse(status="POWERING DOWN", response="OK")
  }
  for key in switch_response:
    if key in response_text:
      return switch_response[key]
  return MediaRoomPostResponse(status="ERROR", response="ERROR")

@router.get("/", response_model=MediaRoomGetResponse)
async def get_media_room_status() -> MediaRoomGetResponse:
  response = tm.send_command("MEDIA ROOM STATUS")
  print(response)
  
  if response.__contains__("MEDIA ROOM STATUS ON"):
    return MediaRoomGetResponse(status="ON", is_active="true")
  elif response.__contains__("MEDIA ROOM STATUS POWERING UP"):
    return MediaRoomGetResponse(status="ON", is_active="true")
  else:
    return MediaRoomGetResponse(status="OFF", is_active="false")