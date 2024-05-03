from pydantic import BaseModel

class AudioPost(BaseModel):
  source: str

class AudioPostResponse(BaseModel):
  source: str
  state: str
  response: str

class AudioGetResponse(BaseModel):
  source: str
  state: str