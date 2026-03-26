from dataclasses import dataclass

from app.infrastructure.web.schemas.users import UserSchema


@dataclass
class LoginRequest:
    email: str
    password: str


@dataclass
class AuthTokens:
    success: bool
    access_token: str
    refresh_token: str
    user: UserSchema


@dataclass
class RefreshTokenRequest:
    refresh_token: str


@dataclass
class RefreshTokensResponse:
    success: bool
    access_token: str
    refresh_token: str


@dataclass
class LogoutResponse:
    success: bool
    message: str
