from dataclasses import asdict

from quart import Blueprint
from quart_schema import validate_request, validate_response

from app.infrastructure.web.auth import issue_auth_tokens, refresh_auth_tokens, revoke_refresh_token
from app.infrastructure.web.dependencies import request_services
from app.infrastructure.web.schemas import (
    AuthTokens,
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokensResponse,
    UserSchema,
)
from app.infrastructure.web.utils import success

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.post("/login")
@validate_request(LoginRequest)
@validate_response(AuthTokens)
async def login(data: LoginRequest):
    async with request_services() as services:
        user = await services["authenticate_user"].execute(
            email=data.email,
            password=data.password,
        )

    tokens = issue_auth_tokens(user.id)
    return success(
        {
            **tokens,
            "user": asdict(UserSchema.from_entity(user)),
        }
    )


@auth.post("/refresh")
@validate_request(RefreshTokenRequest)
@validate_response(RefreshTokensResponse)
async def refresh_tokens(data: RefreshTokenRequest):
    return success(refresh_auth_tokens(data.refresh_token))


@auth.post("/logout")
@validate_request(RefreshTokenRequest)
@validate_response(LogoutResponse)
async def logout(data: RefreshTokenRequest):
    revoke_refresh_token(data.refresh_token)
    return success({"message": "Logged out"})
