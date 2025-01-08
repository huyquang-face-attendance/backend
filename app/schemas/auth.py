from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    client_id: str
    client_secret: str
    user_name: str
    password: str


class RefreshTokenRequest(BaseModel):
    client_id: str
    client_secret: str
    refresh_token: str


class TokenResponse(BaseModel):
    accessToken: str
    accessTokenExpires: datetime
    refreshToken: str
    refreshTokenExpires: datetime
    fullName: str
    userName: str
    unitId: int
    userId: int


class TokenData(BaseModel):
    sub: str
    username: Optional[str] = None
    client_id: Optional[str] = None


class LogoutResponse(BaseModel):
    message: str
