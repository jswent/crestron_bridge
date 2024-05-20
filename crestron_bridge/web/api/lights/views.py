from fastapi import APIRouter

from crestron_bridge.web.api.lights.dependencies import Room 
from crestron_bridge.web.api.lights.config import room_configs

router = APIRouter()

# Create routes dynamically based on room configurations
for floor, rooms in room_configs.items():
    for room_config in rooms:
        if "room" in room_config:
            room = room_config["room"]
        else:
            room = Room(room_config["name"])

        if "sub_lights" in room_config:
            for sub_light in room_config["sub_lights"]:
                room.create_sub_light(sub_light["room"], sub_light["prefix"])

        router.include_router(
            room.router, prefix=room_config["prefix"], tags=room_config["tags"]
        )
