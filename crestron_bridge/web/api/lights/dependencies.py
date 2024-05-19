from typing import Callable
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

        self.router.add_api_route("/", self.update_light_status, methods=["POST"], response_model=LightPostResponse)
        self.router.add_api_route("/", self.get_light_status, methods=["GET"], response_model=LightGetResponse)
        self.router.add_api_route("/turn-on", self.turn_on, methods=["POST"], response_model=LightPostResponse)
        self.router.add_api_route("/turn-off", self.turn_off, methods=["POST"], response_model=LightPostResponse)
        self.router.add_api_route("/set-level", self.set_level, methods=["POST"], response_model=LightPostResponse)

    def create_sub_light(self, sub_light_name: str, sub_light_endpoint: str):
        sub_light = Room(sub_light_name)
        self.router.include_router(sub_light.router, prefix=f"/{sub_light_endpoint}")

    # @router.post("/", response_model=LightPostResponse)
    async def update_light_status(self, body: LightPost):
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

    # @router.get("/", response_model=LightGetResponse)
    async def get_light_status(self) -> LightGetResponse:
        print(f"Getting light status of {self.name} from state")
        light_state = self.state.get_light_state(self.name)
        return LightGetResponse(status=light_state.status, level=light_state.level, is_active=light_state.is_active)

    # @router.post("/turn-on", response_model=LightPostResponse)
    async def turn_on(self):
        response = self.tm.send_command(f"{self.name} LTS S1")
        print(response)
        response_text = response.upper()
        if f"{self.name} LTS S1 OK" in response_text:
            self.state.update_light_state(self.name, "S1", 100, "true")
            return LightPostResponse(status="S1", level=100, response="OK")
        return LightPostResponse(status="ERROR", level=-1, response="ERROR")

    # @router.post("/turn-off", response_model=LightPostResponse)
    async def turn_off(self):
        response = self.tm.send_command(f"{self.name} LTS OFF")
        print(response)
        response_text = response.upper()
        if f"{self.name} LTS OFF OK" in response_text:
            self.state.update_light_state(self.name, "OFF", 0, "false")
            return LightPostResponse(status="OFF", level=0, response="OK")
        return LightPostResponse(status="ERROR", level=-1, response="ERROR")

    # @router.post("/set-level", response_model=LightPostResponse)
    async def set_level(self, body: LightSetLevelPost):
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


class CustomRoomConfig:
    def __init__(
        self, 
        name: str, 
        update_light_status: Callable[[object, LightPost], LightPostResponse] = None,
        get_light_status: Callable[[object], LightGetResponse] = None,
        turn_on: Callable[[object], LightPostResponse] = None,
        turn_off: Callable[[object], LightPostResponse] = None,
        set_level: Callable[[object, LightSetLevelPost], LightPostResponse] = None
    ):
        self.name = name.upper()
        self.update_light_status = update_light_status
        self.get_light_status = get_light_status
        self.turn_on = turn_on
        self.turn_off = turn_off
        self.set_level = set_level

class CustomRoom(Room):
    def __init__(self, config: CustomRoomConfig):
        super().__init__(config.name)
        self.config = config

        # Override the router endpoints
        self.router.routes = [
            route for route in self.router.routes
            if route.path not in ["/", "/turn-on", "/turn-off", "/set-level"]
        ]

        self.router.add_api_route("/", self.update_light_status, methods=["POST"], response_model=LightPostResponse)
        self.router.add_api_route("/", self.get_light_status, methods=["GET"], response_model=LightGetResponse)
        self.router.add_api_route("/turn-on", self.turn_on, methods=["POST"], response_model=LightPostResponse)
        self.router.add_api_route("/turn-off", self.turn_off, methods=["POST"], response_model=LightPostResponse)
        self.router.add_api_route("/set-level", self.set_level, methods=["POST"], response_model=LightPostResponse)

    async def update_light_status(self, body: LightPost):
        if self.config.update_light_status:
            return await self.config.update_light_status(self, body)
        return await super().update_light_status(body)

    async def get_light_status(self):
        if self.config.get_light_status:
            return await self.config.get_light_status(self)
        return await super().get_light_status()

    async def turn_on(self):
        if self.config.turn_on:
            return await self.config.turn_on(self)
        return await super().turn_on()

    async def turn_off(self):
        if self.config.turn_off:
            return await self.config.turn_off(self)
        return await super().turn_off()

    async def set_level(self, body: LightSetLevelPost):
        if self.config.set_level:
            return await self.config.set_level(self, body)
        return await super().set_level(body)