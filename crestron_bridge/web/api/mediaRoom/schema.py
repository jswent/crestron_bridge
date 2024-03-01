from pydantic import BaseModel

class MediaRoomPost(BaseModel):
  status: str

class MediaRoomPostResponse(BaseModel):
  status: str
  response: str

class MediaRoomGetResponse(BaseModel):
  status: str
  is_active: str