from dataclasses import asdict

from quart import Blueprint, current_app, make_response, request
from quart_schema import security_scheme, security_scheme_blueprint, tag_blueprint, validate_request

from app.infrastructure.web.auth import (
    AuthenticationError,
    issue_auth_tokens,
    refresh_auth_tokens,
    revoke_refresh_token,
)
from app.infrastructure.web.dependencies import request_services
from app.infrastructure.web.schemas import (
    LoginRequest,
    UserSchema,
)
from app.infrastructure.web.utils import success

auth = Blueprint("auth", __name__, url_prefix="/auth")
tag_blueprint(auth, ["auth"])
security_scheme_blueprint(auth, [])

#@security_scheme([])
@auth.post("/login")
@validate_request(LoginRequest)
async def login(data: LoginRequest):
    async with request_services() as services:
        user = await services["authenticate_user"].execute(
            email=data.email,
            password=data.password,
        )

    tokens = await issue_auth_tokens(user.id)
    response = await make_response(success(
        {
            "access_token": tokens["access_token"],
            "user": asdict(UserSchema.from_entity(user)),
        }
    ))
    _set_refresh_cookie(response, tokens["refresh_token"])
    return response


@auth.post("/refresh")
async def refresh_tokens():
    refresh_token = request.cookies.get(_refresh_cookie_name())
    if not refresh_token:
        raise AuthenticationError("Missing refresh-token cookie")

    tokens = await refresh_auth_tokens(refresh_token)
    response = await make_response(success({"access_token": tokens["access_token"]}))
    _set_refresh_cookie(response, tokens["refresh_token"])
    return response


@auth.post("/logout")
async def logout():
    refresh_token = request.cookies.get(_refresh_cookie_name())
    if refresh_token:
        try:
            await revoke_refresh_token(refresh_token)
        except AuthenticationError:
            # An expired or already-rotated cookie is still safe to clear.
            pass

    response = await make_response(success({"message": "Logged out"}))
    response.delete_cookie(_refresh_cookie_name(), path="/auth")
    return response


def _refresh_cookie_name() -> str:
    return current_app.config["AUTH_REFRESH_COOKIE_NAME"]


def _set_refresh_cookie(response, refresh_token: str) -> None:
    response.set_cookie(
        _refresh_cookie_name(),
        refresh_token,
        max_age=current_app.config["AUTH_REFRESH_TOKEN_MAX_AGE"],
        httponly=True,
        secure=current_app.config["AUTH_REFRESH_COOKIE_SECURE"],
        samesite=current_app.config["AUTH_REFRESH_COOKIE_SAMESITE"],
        path="/auth",
    )
