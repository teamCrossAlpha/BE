from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    email: str | None
    provider: str
    provider_id: str
    nickname: str | None
    profile_image: str | None

    class Config:
        from_attributes = True