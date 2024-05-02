from fastapi import APIRouter, Depends
from crestron_bridge.web.api.lights.schema import LightPost, LightPostResponse, LightGetResponse
from crestron_bridge.services.telnet.lifetime import get_telnet_manager

class Room:
    def __init__(self, name: str):
        self.name = name.upper()
        self.router = APIRouter()
        self.tm = get_telnet_manager()

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
            if f"{self.name} LTS {status} OK" in response_text:
                return LightPostResponse(status=status, response="OK")
            return LightPostResponse(status="ERROR", response="ERROR")

        @self.router.get("/", response_model=LightGetResponse)
        async def get_light_status() -> LightGetResponse:
            response = self.tm.send_command(f"{self.name} LTS STATUS")
            print(response)
            if f"{self.name} LTS STATUS S1 OK" in response:
                return LightGetResponse(status="SCENE 1", is_active="true")
            elif f"{self.name} LTS STATUS S2 OK" in response:
                return LightGetResponse(status="SCENE 2", is_active="true")
            elif f"{self.name} LTS STATUS S3 OK" in response:
                return LightGetResponse(status="SCENE 3", is_active="true")
            elif f"{self.name} LTS STATUS OFF OK" in response:
                return LightGetResponse(status="OFF", is_active="false")
            else:
                return LightGetResponse(status="ERROR", is_active="false")