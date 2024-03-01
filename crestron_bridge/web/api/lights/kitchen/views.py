from fastapi import APIRouter

from crestron_bridge.web.api.lights.schema import LightPost, LightPostResponse, LightGetResponse
from crestron_bridge.services.telnet.lifetime import get_telnet_manager

ROOM = "KITCHEN"

router = APIRouter()
tm = get_telnet_manager()

@router.post("/", response_model=LightPost)
async def update_media_room_light_status(
    body: LightPost,
):
  status = body.status.upper()
  if not status in ["S1", "S2", "S3", "OFF"]:
    if status == "ON":
      status = "S1"
    elif status.startswith("SCENE"):
      scene_number = status.split(" ")[1]
      if scene_number == "1":
        status = "S1"
      elif scene_number == "2":
        status = "S2"
      elif scene_number == "3":
        status = "S3"
  response = tm.send_command(f"{ROOM} LTS {status}")
  print(response)

  response_text = response.upper()
  if f"{ROOM} LTS {status} OK" in response_text:
    return LightPostResponse(status=status, response="OK")
  return LightPostResponse(status="ERROR", response="ERROR")

@router.get("/", response_model=LightGetResponse)
async def get_media_room_light_status() -> LightGetResponse:
  response = tm.send_command(f"{ROOM} LTS STATUS")
  print(response)

  if f"{ROOM} LTS S1 OK" in response:
    return LightGetResponse(status="SCENE 1", is_active="true")
  elif f"{ROOM} LTS S2 OK" in response:
    return LightGetResponse(status="SCENE 2", is_active="true")
  elif f"{ROOM} LTS S3 OK" in response:
    return LightGetResponse(status="SCENE 3", is_active="true")
  elif f"{ROOM} LTS OFF OK" in response:
    return LightGetResponse(status="OFF", is_active="false")
  else:
    return LightGetResponse(status="ERROR", is_active="false")