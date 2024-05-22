from crestron_bridge.web.api.lights.dependencies import Room, CustomRoom
from crestron_bridge.web.api.lights.config import CustomRooms

# Define room configurations
room_configs = {
    "first_floor": [
        {
            "name": "KITCHEN",
            "prefix": "/kitchen",
            "tags": ["kitchen"],
            "sub_lights": [
                {
                    "room": Room("KITCHEN ISLAND"),
                    "prefix": "island",
                }
            ],
        },
        {"name": "MEDIA ROOM", "prefix": "/media-room", "tags": ["media-room"]},
        {"name": "FOYER", "prefix": "/foyer", "tags": ["foyer"]},
        {"name": "LIVING", "prefix": "/living-room", "tags": ["living-room"]},
        {"name": "DINING", "prefix": "/dining-room", "tags": ["dining-room"]},
    ],
    "second_floor": [
        {
            "name": "JAKE OFFICE",
            "prefix": "/jake-office",
            "tags": ["jake-office"],
            "sub_lights": [{"room": Room("JAKE OFFICE DESK"), "prefix": "desk"}],
        },
        {
            "name": "JAKE BED",
            "prefix": "/jake-bedroom",
            "tags": ["jake-bedroom"],
            "sub_lights": [{"room": Room("JAKE BED READING"), "prefix": "reading"}],
        },
        {"name": "MBED", "prefix": "/master-bedroom", "tags": ["master-bedroom"]},
        {"name": "GAME ROOM", "prefix": "/game-room", "tags": ["game-room"]},
        {
            "name": "JAKE BATH",
            "room": CustomRoom(CustomRooms.jake_bath()),
            "prefix": "/jake-bathroom",
            "tags": ["jake-bathroom"],
        },
    ],
    "third_floor": [
        {"name": "JWS OFFICE", "prefix": "/jws-office", "tags": ["jws-office"]},
        {"name": "STAFF RM", "prefix": "/staff-room", "tags": ["staff-room"]},
    ],
}
