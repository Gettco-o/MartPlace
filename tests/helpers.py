import uuid

from app.domain.entities.user import User
from app.domain.value_objects.user_role import UserRole


def make_buyer(email: str = "buyer@test.com", name: str = "Buyer") -> User:
    return User(
        id=str(uuid.uuid4()),
        email=email,
        name=name,
        password="secure123",
        role=UserRole.BUYER,
    )


def make_tenant_user(tenant_id: str, email: str = "seller@test.com", name: str = "Seller") -> User:
    return User(
        id=str(uuid.uuid4()),
        email=email,
        name=name,
        password="secure123",
        role=UserRole.TENANT_ADMIN,
        tenant_id=tenant_id,
    )


def make_platform_admin(email: str = "admin@test.com", name: str = "Admin") -> User:
    return User(
        id=str(uuid.uuid4()),
        email=email,
        name=name,
        password="secure123",
        role=UserRole.PLATFORM_ADMIN,
    )
