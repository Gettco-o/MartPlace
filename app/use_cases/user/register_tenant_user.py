

import uuid
from app.domain.entities.user import User
from app.domain.exceptions import DomainError
from app.domain.value_objects.user_role import UserRole
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository


from dataclasses import dataclass


@dataclass
class RegisterTenantUser:
    user_repo: UserRepository
    tenant_repo: TenantRepository

    def execute(self, email: str, name: str, tenant_id: str, role: UserRole, password: str) -> User:

        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        if role not in (
            UserRole.TENANT_ADMIN,
            UserRole.TENANT_STAFF,
        ):
            raise DomainError("Invalid role for tenant user")

        if self.user_repo.get_by_email(email):
            raise DomainError("Email already registered")

        user = User(
            id=str(uuid.uuid4()),
            email=email.strip().lower(),
            name=name,
            password=password,
            role=role,
            tenant_id=tenant_id,
        )

        self.user_repo.save(user)
        return user