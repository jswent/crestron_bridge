from crestron_bridge.web.api.lights.dependencies import CustomRoomConfig, CustomRoom
from crestron_bridge.web.api.lights.schema import LightPost, LightPostResponse, LightGetResponse, LightSetLevelPost, LightSetLevelPostResponse

class CustomRooms:
    @staticmethod
    def jake_bath():
        room_name = "JAKE BATHROOM"

        async def custom_update_light_status(self, body: LightPost) -> LightPostResponse:
            print("Executing custom update light status handler")
            status = body.status.upper()

            if not status in ["S1", "OFF"]:
                return LightPostResponse(status="ERROR", level=-1, response="ERROR")

            if status == "ON":
                status = "S1"

            response = self.tm.send_command(f"{room_name} LTS {status}")
            print(response)
            response_text = response.upper()

            level = 100 if status == "S1" else 0
            is_active = "true" if status != "OFF" else "false"

            if f"{room_name} LTS {status} OK" in response_text:
                self.state.update_light_state(room_name, status, level, is_active)
                return LightPostResponse(status=status, level=level, response="OK")
            return LightPostResponse(status="ERROR", level=-1, response="ERROR")

        async def custom_set_level(self, body: LightSetLevelPost) -> LightPostResponse:
            level = body.level
            status = "S1" if level > 0 else "OFF"

            command = f"{room_name} LTS {status}"

            response = self.tm.send_command(command)
            print(response)

            scene_level = 100 if status == "S1" else 0
            is_active = "true" if status != "OFF" else "false"

            if f"{command} OK" in response.upper():
                self.state.update_light_state(room_name, status, scene_level, is_active)
                return LightPostResponse(status=status, level=scene_level, response="OK")
            return LightPostResponse(status="ERROR", level=-1, response="ERROR")
        
        return CustomRoomConfig(
            name=room_name, 
            update_light_status=custom_update_light_status, 
            set_level=custom_set_level
        )

    @staticmethod
    def on_off(room: str):
        room_name = room.upper()

        async def custom_update_light_status(self, body: LightPost) -> LightPostResponse:
            print("Executing custom update light status handler")
            status = body.status.upper()

            if not status in ["S1", "OFF"]:
                return LightPostResponse(status="ERROR", level=-1, response="ERROR")

            if status == "ON":
                status = "S1"

            response = self.tm.send_command(f"{room_name} LTS {status}")
            print(response)
            response_text = response.upper()

            level = 100 if status == "S1" else 0
            is_active = "true" if status != "OFF" else "false"

            if f"{room_name} LTS {status} OK" in response_text:
                self.state.update_light_state(room_name, status, level, is_active)
                return LightPostResponse(status=status, level=level, response="OK")
            return LightPostResponse(status="ERROR", level=-1, response="ERROR")

        async def custom_set_level(self, body: LightSetLevelPost) -> LightPostResponse:
            level = body.level
            status = "S1" if level > 0 else "OFF"

            command = f"{room_name} LTS {status}"

            response = self.tm.send_command(command)
            print(response)

            scene_level = 100 if status == "S1" else 0
            is_active = "true" if status != "OFF" else "false"

            if f"{command} OK" in response.upper():
                self.state.update_light_state(room_name, status, scene_level, is_active)
                return LightPostResponse(status=status, level=scene_level, response="OK")
            return LightPostResponse(status="ERROR", level=-1, response="ERROR")

        return CustomRoomConfig(
            name=room_name, 
            update_light_status=custom_update_light_status,
            set_level=custom_set_level
        )