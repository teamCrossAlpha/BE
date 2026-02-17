from pydantic import BaseModel

class LoginResponse(BaseModel):
    accessToken: str
    refreshToken: str
    userId: int
    isNewUser: bool

class RefreshTokenRequest(BaseModel):
    refreshToken: str

class RefreshTokenResponse(BaseModel):
    accessToken: str

class DevTokenRequest(BaseModel):
    email: str

class DevTokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    userId: int
