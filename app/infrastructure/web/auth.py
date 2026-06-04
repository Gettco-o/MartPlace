from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar
import uuid

from itsdangerous import BadSignature, BadTimeSignature, URLSafeTimedSerializer
from quart import current_app, g, request


P = ParamSpec("P")
R = TypeVar("R")


class AuthenticationError(Exception):
    pass


def _serializer() -> URLSafeTimedSerializer:
    secret_key = current_app.config.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY is not configured")
    return URLSafeTimedSerializer(secret_key=secret_key, salt="martplace-auth")


def _refresh_store() -> dict[str, str]:
    return current_app.extensions.setdefault("auth_refresh_store", {})


def _issue_token(user_id: str, token_type: str, refresh_id: str | None = None) -> str:
    payload = {
        "sub": user_id,
        "type": token_type,
    }
    if refresh_id is not None:
        payload["rid"] = refresh_id
    return _serializer().dumps(payload)


def _decode_token(token: str, expected_type: str, max_age: int) -> dict:
    try:
        payload = _serializer().loads(token, max_age=max_age)
    except (BadSignature, BadTimeSignature):
        raise AuthenticationError("Invalid or expired token") from None

    user_id = payload.get("sub")
    token_type = payload.get("type")
    if not user_id or token_type != expected_type:
        raise AuthenticationError("Invalid token payload")
    return payload


def issue_auth_tokens(user_id: str) -> dict[str, str]:
    refresh_id = str(uuid.uuid4())
    _refresh_store()[user_id] = refresh_id
    return {
        "access_token": _issue_token(user_id, "access"),
        "refresh_token": _issue_token(user_id, "refresh", refresh_id=refresh_id),
    }


def decode_access_token(token: str) -> str:
    max_age = current_app.config.get("AUTH_TOKEN_MAX_AGE", 900)
    payload = _decode_token(token, expected_type="access", max_age=max_age)
    return payload["sub"]


def refresh_auth_tokens(refresh_token: str) -> dict[str, str]:
    max_age = current_app.config.get("AUTH_REFRESH_TOKEN_MAX_AGE", 604800)
    payload = _decode_token(refresh_token, expected_type="refresh", max_age=max_age)

    user_id = payload["sub"]
    refresh_id = payload.get("rid")
    if not refresh_id or _refresh_store().get(user_id) != refresh_id:
        raise AuthenticationError("Refresh token has been revoked")

    return issue_auth_tokens(user_id)


def revoke_refresh_token(refresh_token: str) -> None:
    max_age = current_app.config.get("AUTH_REFRESH_TOKEN_MAX_AGE", 604800)
    payload = _decode_token(refresh_token, expected_type="refresh", max_age=max_age)

    user_id = payload["sub"]
    refresh_id = payload.get("rid")
    if _refresh_store().get(user_id) == refresh_id:
        del _refresh_store()[user_id]


def get_current_actor_id() -> str:
    actor_user_id = getattr(g, "current_actor_id", None)
    if not actor_user_id:
        raise AuthenticationError("Authentication required")
    return actor_user_id


def auth_required(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise AuthenticationError("Missing bearer token")

        g.current_actor_id = decode_access_token(token)
        return await func(*args, **kwargs)

    return wrapper
