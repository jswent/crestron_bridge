from fastapi import APIRouter, Depends
from crestron_bridge.web.api.lights.schema import LightPost, LightPostResponse, LightGetResponse, LightSetLevelPost
from crestron_bridge.services.telnet.lifetime import get_telnet_manager
from crestron_bridge.services.state.lifetime import get_server_state

class Room:
    def __init__(self, name: str):
        self.name = name.upper()
        self.router = APIRouter()
        self.tm = get_telnet_manager()
        self.state = get_server_state()

        @self.router.post("/", response_model=LightPostResponse)
        async def update_light_status(body: LightPost):
            status = body.status.upper()
            if status == "ON":
                status = "S1"
            elif status.startswith("SCENE"):
                scene_number = status.split(" ")[1]
                status = f"S{scene_number}"

            response = self.tm.send_command(f"{self.name} LTS {status}")
            print(response)
            response_text = response.upper()

            level = 100 if status == "S1" else 66 if status == "S2" else 33 if status == "S3" else 0
            is_active = "true" if status != "OFF" else "false"

            if f"{self.name} LTS {status} OK" in response_text:
                self.state.update_light_state(self.name, status, level, is_active)
                return LightPostResponse(status=status, level=level, response="OK")
            return LightPostResponse(status="ERROR", level=-1, response="ERROR")

        @self.router.get("/", response_model=LightGetResponse)
        async def get_light_status() -> LightGetResponse:
          print(f"Getting light status of {self.name} from state")
          light_state = self.state.get_light_state(self.name)
          return LightGetResponse(status=light_state.status, level=light_state.level, is_active=light_state.is_active)

        @self.router.post("/turn-on", response_model=LightPostResponse)
        async def turn_on():
            response = self.tm.send_command(f"{self.name} LTS S1")
            print(response)
            response_text = response.upper()
            if f"{self.name} LTS S1 OK" in response_text:
                self.state.update_light_state(self.name, "S1", 100, "true")
                return LightPostResponse(status="S1", level=100, response="OK")
            return LightPostResponse(status="ERROR", level=-1, response="ERROR")

        @self.router.post("/turn-off", response_model=LightPostResponse)
        async def turn_off():
            response = self.tm.send_command(f"{self.name} LTS OFF")
            print(response)
            response_text = response.upper()
            if f"{self.name} LTS OFF OK" in response_text:
                self.state.update_light_state(self.name, "OFF", 0, "false")
                return LightPostResponse(status="OFF", level=0, response="OK")
            return LightPostResponse(status="ERROR", level=-1, response="ERROR")

        @self.router.post("/set-level", response_model=LightPostResponse)
        async def set_level(body: LightSetLevelPost):
            level = body.level;
            status = "OFF" if level == 0 else "S1" if level > 66 else "S2" if level > 33 else "S3"

            command = f"{self.name} LTS {status}"
            
            response = self.tm.send_command(command)
            print(response)

            scene_level = 100 if status == "S1" else 66 if status == "S2" else 33 if status == "S3" else 0
            is_active = "true" if status != "OFF" else "false"

            if f"{command} OK" in response.upper():
                self.state.update_light_state(self.name, status, scene_level, is_active)
                return LightPostResponse(status=status, level=scene_level, response="OK")
            return LightPostResponse(status="ERROR", level=-1, response="ERROR")

