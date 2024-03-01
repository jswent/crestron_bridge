from pydantic import BaseModel

class MediaRoomLightPost(BaseModel):
  status: str

class MediaRoomLightPostResponse(BaseModel):
  status: str
  response: str

class MediaRoomLightGetResponse(BaseModel):
  status: str
  is_active: str