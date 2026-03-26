import uuid
from datetime import datetime
from dataclasses import dataclass

from app.domain.entities.user import User
from app.domain.events.tenant_user_registered import TenantUserRegistered
from app.domain.exceptions import DomainError
from app.domain.value_objects.user_role import UserRole
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_tenant_manager
from werkzeug.security import generate_password_hash


@dataclass
class RegisterTenantUser:
    user_repo: UserRepository
    tenant_repo: TenantRepository
    event_bus: EventBus

    async def execute(
        self,
        actor_user_id: str,
        email: str,
        name: str,
        tenant_id: str,
        role: UserRole,
        password: str,
    ) -> User:

        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise DomainError("Tenant not found")

        tenant.ensure_active()
        await ensure_tenant_manager(self.user_repo, actor_user_id, tenant_id)

        if role not in (
            UserRole.TENANT_ADMIN,
            UserRole.TENANT_STAFF,
        ):
            raise DomainError("Invalid role for tenant user")

        if await self.user_repo.get_by_email(email):
            raise DomainError("Email already registered")

        user = User(
            id=str(uuid.uuid4()),
            email=email.strip().lower(),
            name=name,
            password=generate_password_hash(password),
            role=role,
            tenant_id=tenant_id,
        )

        await self.user_repo.save(user)
        user.record_event(
            TenantUserRegistered(
                user_id=user.id,
                tenant_id=user.tenant_id,
                email=user.email,
                role=user.role.value,
                occurred_at=datetime.now(),
            )
        )
        self.event_bus.publish(user.events)
        user.clear_events()
        return user
