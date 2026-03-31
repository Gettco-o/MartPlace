from dataclasses import asdict

from quart import Blueprint
from quart_schema import tag_blueprint, validate_request, validate_response

from app.infrastructure.web.auth import auth_required, get_current_actor_id
from app.infrastructure.web.dependencies import request_services
from app.infrastructure.web.schemas import (
    RegisterBuyerRequest,
    RegisterTenantUserRequest,
    UserSchema,
    UserResponse,
    UsersResponse,
)
from app.infrastructure.web.utils import success

users = Blueprint('users', __name__, url_prefix='/users')
tag_blueprint(users, ["users"])


@users.post("/buyers")
@validate_request(RegisterBuyerRequest)
@validate_response(UserResponse, 201)
async def register_buyer(data: RegisterBuyerRequest):
    async with request_services() as services:
        user = await services["register_buyer"].execute(
            email=data.email,
            name=data.name,
            password=data.password,
        )
        await services["session"].commit()

    return success({"user": asdict(UserSchema.from_entity(user))}, status_code=201)


@users.post("/tenant-users")
@validate_request(RegisterTenantUserRequest)
@auth_required
@validate_response(UserResponse, 201)
async def register_tenant_user(data: RegisterTenantUserRequest):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        user = await services["register_tenant_user"].execute(
            actor_user_id=actor_user_id,
            email=data.email,
            name=data.name,
            tenant_id=data.tenant_id,
            role=data.role,
            password=data.password,
        )
        await services["session"].commit()

    return success({"user": asdict(UserSchema.from_entity(user))}, status_code=201)


@users.get("/<user_id>")
@validate_response(UserResponse)
async def get_user(user_id: str):
    async with request_services() as services:
        user = await services["get_user"].execute(user_id)

    return success({"user": asdict(UserSchema.from_entity(user))})


@users.get("/")
@auth_required
@validate_response(UsersResponse)
async def get_all_users():
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        users_list = await services["get_all_users"].execute(actor_user_id)

    return success({"users": [asdict(UserSchema.from_entity(user)) for user in users_list]})
