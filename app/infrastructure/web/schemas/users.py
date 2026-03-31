from dataclasses import dataclass

from app.domain.entities.user import User
from app.domain.value_objects.user_role import UserRole


@dataclass
class RegisterBuyerRequest:
    email: str
    name: str
    password: str


@dataclass
class RegisterTenantUserRequest:
    email: str
    name: str
    tenant_id: str
    role: UserRole
    password: str


@dataclass
class UserSchema:
    id: str
    email: str
    name: str
    role: str
    status: str
    tenant_id: str | None

    @classmethod
    def from_entity(cls, user: User) -> "UserSchema":
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role.value,
            status=user.status.value,
            tenant_id=user.tenant_id,
        )


@dataclass
class UserResponse:
    success: bool
    user: UserSchema


@dataclass
class UsersResponse:
    success: bool
    users: list[UserSchema]
