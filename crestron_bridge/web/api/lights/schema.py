from pydantic import BaseModel

class LightPost(BaseModel):
  status: str

class LightPostResponse(BaseModel):
  status: str
  level: int
  response: str

class LightGetResponse(BaseModel):
  status: str
  level: int
  is_active: str

class LightSetLevelPost(BaseModel):
  level: int

class LightSetLevelPostResponse(BaseModel):
  level: int
  response: str