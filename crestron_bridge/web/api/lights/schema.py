from pydantic import BaseModel

class LightPost(BaseModel):
  status: str

class LightPostResponse(BaseModel):
  status: str
  response: str

class LightGetResponse(BaseModel):
  status: str
  is_active: str