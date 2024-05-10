from pydantic import BaseModel

class MediaRoomPost(BaseModel):
  status: str

class MediaRoomSelectSourcePost(BaseModel):
  source: str

class MediaRoomPostResponse(BaseModel):
  status: str
  source: str | None
  response: str

class MediaRoomGetResponse(BaseModel):
  status: str
  source: str
  is_active: str