from fastapi import APIRouter
from typing import Callable

from crestron_bridge.web.api.audio.schema import AudioGetResponse, AudioPost, AudioPostResponse
from crestron_bridge.services.telnet.lifetime import get_telnet_manager
from crestron_bridge.services.state.lifetime import get_server_state

class AudioLocation:
    def __init__(self, location: str):
        self.location = location.upper()
        self.router = APIRouter()
        self.tm = get_telnet_manager()
        self.state = get_server_state()

        self.router.add_api_route("/", self.get_audio_status, methods=["GET"], response_model=AudioGetResponse)
        self.router.add_api_route("/turn-on", self.turn_on_audio, methods=["POST"], response_model=AudioPostResponse)
        self.router.add_api_route("/turn-off", self.turn_off_audio, methods=["POST"], response_model=AudioPostResponse)
        self.router.add_api_route("/select-source", self.select_source, methods=["POST"], response_model=AudioPostResponse)

    async def get_audio_status(self) -> AudioGetResponse:
        print(f"Getting {self.location} audio status from state")
        audio_state = self.state.get_audio_state(self.location)
        return AudioGetResponse(source=audio_state.source, state=audio_state.state)
    
    async def turn_on_audio(self):
        response = self.tm.send_command(f"{self.location} AUDIO SRC SONOS")
        print(response)
        if f"{self.location} AUDIO SRC SONOS OK" in response.upper():
            self.state.update_audio_state(self.location, "SONOS", "ON")
            return AudioPostResponse(source="SONOS", state="ON", response="OK")
        return AudioPostResponse(source="ERROR", state="ERROR", response="ERROR")
    
    async def turn_off_audio(self):
        response = self.tm.send_command(f"{self.location} AUDIO SRC OFF")
        print(response)
        if f"{self.location} AUDIO SRC OFF OK" in response.upper():
            self.state.update_audio_state(self.location, "OFF", "OFF")
            return AudioPostResponse(source="OFF", state="OFF", response="OK")
        return AudioPostResponse(source="ERROR", state="ERROR", response="ERROR")
    
    async def select_source(self, body: AudioPost):
        source = body.source.upper()
        if not source in ["SONOS", "XM", "FM"]:
            return AudioPostResponse(status="ERROR", response="SOURCE NOT FOUND")
        response = self.tm.send_command(f"{self.location} AUDIO SRC {source}")
        print(response)
        if f"{self.location} AUDIO SRC {source} OK" in response.upper():
            self.state.update_audio_state(self.location, source, "ON")
            return AudioPostResponse(source=source, state="ON", response="OK")
        return AudioPostResponse(source="ERROR", state="ERROR", response="ERROR")


class CustomAudioLocationConfig:
    def __init__(
        self,
        location: str,
        get_audio_status: Callable[[object], AudioGetResponse] = None,
        turn_on: Callable[[object], AudioPostResponse] = None,
        turn_off: Callable[[object], AudioPostResponse] = None,
        select_source: Callable[[object], AudioPostResponse] = None,
    ):
        self.location = location.upper()
        self.get_audio_status = get_audio_status
        self.turn_on = turn_on
        self.turn_off = turn_off
        self.select_source = select_source

class CustomAudioLocation(AudioLocation):
    def __init__(self, config: CustomAudioLocationConfig):
        self.location = config.location
        self.router = APIRouter()
        self.get_audio_status = config.get_audio_status
        self.turn_on_audio = config.turn_on
        self.turn_off_audio = config.turn_off
        self.select_source = config.select_source

        self.router.add_api_route("/", self.get_audio_status, methods=["GET"], response_model=AudioGetResponse)
        self.router.add_api_route("/turn-on", self.turn_on_audio, methods=["POST"], response_model=AudioPostResponse)
        self.router.add_api_route("/turn-off", self.turn_off_audio, methods=["POST"], response_model=AudioPostResponse)
        self.router.add_api_route("/select-source", self.select_source, methods=["POST"], response_model=AudioPostResponse)

    async def get_audio_status(self):
        if self.get_audio_status:
            return await self.get_audio_status(self)
        return await super().get_audio_status()
    
    async def turn_on_audio(self):
        if self.turn_on:
            return await self.turn_on(self)
        return await super().turn_on_audio()
    
    async def turn_off_audio(self):
        if self.turn_off:
            return await self.turn_off(self)
        return await super().turn_off_audio()
    
