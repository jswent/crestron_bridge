
class LightState:
  def __init__(self, status: str, level: int, is_active: str):
    self.status = status
    self.level = level
    self.is_active = is_active

class MediaRoomState:
  def __init__(self, status: str, source: str, is_active: str):
    self.status = status
    self.source = source
    self.is_active = is_active

class AudioState:
  def __init__(self, source: str, state: str):
    self.source = source
    self.state = state

class ServerState:
  def __init__(self):
    self.lights_state: dict[str, LightState] = {}
    self.media_room_state: MediaRoomState | None = None
    self.audio_state: dict[str, AudioState] = {}


  def update_light_state(self, room: str, status: str | None, level: int | None, is_active: str | None):
    if room not in self.lights_state:
      if status and level is not None and is_active is not None:
        print(f"Initializing new light state for {room}: ({status}, {level}, {is_active})")
        self.lights_state[room] = LightState(status, level, is_active)
      else:
        raise ValueError("status, level, and is_active must be provided when initializing a new light state")
    else:
      if status:
        self.lights_state[room].status = status
      if level:
        self.lights_state[room].level = level
      if is_active:
        self.lights_state[room].is_active = is_active

  def get_light_state(self, room: str) -> LightState:
    return self.lights_state[room]
  
  def update_media_room_state(self, status: str | None, source: str | None, is_active: str | None):
    if self.media_room_state is None:
      if status and source and is_active:
        print(f"Initializing new media room state: ({status}, {source}, {is_active})")
        self.media_room_state = MediaRoomState(status, source, is_active)
      else:
        raise ValueError("status, source, and is_active must be provided when initializing a new media room state")
    else:
      if status:
        self.media_room_state.status = status
      if source:
        self.media_room_state.source = source
      if is_active:
        self.media_room_state.is_active = is_active

  def get_media_room_state(self) -> MediaRoomState:
    return self.media_room_state
  
  def update_audio_state(self, location: str, source: str | None, state: str | None):
    if location not in self.audio_state:
      if source and state:
        print(f"Initializing new audio state for {location}")
        self.audio_state[location] = AudioState(source, state)
      else:
        raise ValueError("source and state must be provided when initializing a new audio state")
    else:
      if source:
        self.audio_state[location].source = source
      if state:
        self.audio_state[location].state = state

  def get_audio_state(self, location: str) -> AudioState:
    return self.audio_state[location]
