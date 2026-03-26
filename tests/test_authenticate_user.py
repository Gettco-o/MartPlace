import asyncio

import pytest
from quart import Quart
from werkzeug.security import generate_password_hash

from app.domain.exceptions import DomainError
from app.infrastructure.web.auth import (
    decode_access_token,
    issue_auth_tokens,
    refresh_auth_tokens,
    revoke_refresh_token,
)
from app.use_cases.user.authenticate_user import AuthenticateUser
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.helpers import make_buyer

run = asyncio.run


def test_authenticate_user_returns_active_user_for_valid_credentials():
    user_repo = FakeUserRepository()
    user = make_buyer()
    user.password = generate_password_hash("secure123")
    run(user_repo.save(user))

    authenticated = run(
        AuthenticateUser(user_repo=user_repo).execute(
            email=user.email,
            password="secure123",
        )
    )

    assert authenticated.id == user.id


def test_authenticate_user_rejects_invalid_credentials():
    user_repo = FakeUserRepository()
    user = make_buyer()
    user.password = generate_password_hash("secure123")
    run(user_repo.save(user))

    with pytest.raises(DomainError, match="Invalid credentials"):
        run(
            AuthenticateUser(user_repo=user_repo).execute(
                email=user.email,
                password="wrong-password",
            )
        )


def test_access_token_round_trip_uses_signed_user_id():
    app = Quart(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    app.config["AUTH_TOKEN_MAX_AGE"] = 60
    app.config["AUTH_REFRESH_TOKEN_MAX_AGE"] = 120
    app.extensions["auth_refresh_store"] = {}

    async def run_test():
        async with app.app_context():
            tokens = issue_auth_tokens("user-123")
            assert decode_access_token(tokens["access_token"]) == "user-123"

    run(run_test())


def test_refresh_token_rotation_and_logout_revocation():
    app = Quart(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    app.config["AUTH_TOKEN_MAX_AGE"] = 60
    app.config["AUTH_REFRESH_TOKEN_MAX_AGE"] = 120
    app.extensions["auth_refresh_store"] = {}

    async def run_test():
        async with app.app_context():
            first_tokens = issue_auth_tokens("user-123")
            second_tokens = refresh_auth_tokens(first_tokens["refresh_token"])

            assert second_tokens["refresh_token"] != first_tokens["refresh_token"]

            with pytest.raises(Exception):
                refresh_auth_tokens(first_tokens["refresh_token"])

            revoke_refresh_token(second_tokens["refresh_token"])

            with pytest.raises(Exception):
                refresh_auth_tokens(second_tokens["refresh_token"])

    run(run_test())
