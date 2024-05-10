import re
from crestron_bridge.services.telnet.lifetime import get_telnet_manager
from crestron_bridge.services.state.lifetime import get_server_state
from crestron_bridge.static.schema import schema

class Commander:
  def __init__(self):
    self.tm = get_telnet_manager()
    self.state = get_server_state()

  def initialize_device_states(self):
    self._initialize_light_states()
    self._initialize_media_room_state()
    self._initialize_audio_states()

  def _initialize_light_states(self):
    commands = []
    for room in schema["lights"].keys():
      command = self._construct_light_status_command(room)
      commands.append(command)
    
    responses = self.tm.send_batch_command(commands)
    self._update_light_states(responses)

  def _initialize_media_room_state(self):
    commands = [
      self._construct_media_room_power_status_command(),
      self._construct_media_room_source_status_command()
    ]
    responses = self.tm.send_batch_command(commands)
    self._update_media_room_state(responses)

  def _initialize_audio_states(self):
    commands = []
    for location in schema["audio"].keys():
      command = self._construct_audio_status_command(location)
      commands.append(command)
    
    responses = self.tm.send_batch_command(commands)
    self._update_audio_states(responses)

  def _construct_light_status_command(self, room: str) -> str:
    if room not in schema["lights"].keys():
      if room not in schema["lights"].values():
        raise ValueError(f"Room {room} not found in lights schema")
      else:
        return f"{room} LTS STATUS"
    return f"{schema['lights'][room]} LTS STATUS"

  def _construct_media_room_power_status_command(self) -> str:
    return f"{schema['media_room']} POWER STATUS"

  def _construct_media_room_source_status_command(self) -> str:
    return f"{schema['media_room']} SRC STATUS"

  def _construct_audio_status_command(self, location: str) -> str:
    if location not in schema["audio"].keys():
      if location not in schema["audio"].values():
        raise ValueError(f"Location {location} not found in audio schema")
      else:
        return f"{location} AUDIO SRC STATUS"
    return f"{schema['audio'][location]} AUDIO SRC STATUS"

  def _update_audio_states(self, responses: list[str]):
    audio_pattern = r"^([\w\s]+) AUDIO SRC STATUS (SONOS|XM|FM|OFF) OK$"
    for response in responses:
      match = re.search(audio_pattern, response)
      if match:
        location = match.group(1)
        source = match.group(2)
        state = "ON" if source != "OFF" else "OFF"
        # print(f"Updating audio state for {location} to {source}, {state}")
        self.state.update_audio_state(location=location, source=source, state=state)

  def _update_light_states(self, responses: list[str]):
    lights_pattern = r"^([\w\s]+) LTS STATUS (S[1-3]|OFF) OK$"
    for response in responses:
      match = re.search(lights_pattern, response)
      if match:
        room = match.group(1)
        status = match.group(2)
        level = 100 if status == "S1" else 66 if status == "S2" else 33 if status == "S3" else 0
        is_active = "true" if status != "OFF" else "false"
        # print(f"Updating light for {room} to {status}, {level}, {is_active}")
        self.state.update_light_state(room=room, status=status, level=level, is_active=is_active)

  def _update_media_room_state(self, responses: list[str]):
    response = "\n".join(responses)

    media_room_power_pattern = r"^MEDIA ROOM POWER STATUS (ON|OFF) OK$"
    media_room_source_pattern = r"^MEDIA ROOM SRC STATUS (APPLETV|CABLE) OK$"

    power_match = re.search(media_room_power_pattern, response, re.MULTILINE)
    source_match = re.search(media_room_source_pattern, response, re.MULTILINE)

    if power_match and source_match:
      status = power_match.group(1)
      source = source_match.group(1)
      is_active = "true" if status == "ON" else "false"
      self.state.update_media_room_state(status=status, source=source, is_active=is_active)
    elif power_match:
      status = power_match.group(1)
      self.state.update_media_room_state(status=status)
    elif source_match:
      source = source_match.group(1)
      self.state.update_media_room_state(source=source)
  
  def close(self):
    self.tm = None
    self.state = None