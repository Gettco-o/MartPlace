from dataclasses import dataclass
from datetime import datetime
import uuid

from app.domain.entities.tenant import Tenant
from app.domain.entities.user import User
from app.domain.events.tenant_created import TenantCreated
from app.domain.events.tenant_user_registered import TenantUserRegistered
from app.domain.value_objects.user_role import UserRole
from app.interfaces.repositories.tenant_repository import TenantRepository
from app.domain.exceptions import DomainError
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.user_repository import UserRepository
from werkzeug.security import generate_password_hash


@dataclass
class CreateTenant:
    tenant_repo: TenantRepository
    event_bus: EventBus
    user_repo: UserRepository | None = None

    async def execute(
        self,
        name: str,
        admin_email: str | None = None,
        admin_name: str | None = None,
        admin_password: str | None = None,
    ) -> Tenant:

        if not name or not name.strip():
            raise DomainError("Tenant name cannot be empty")
        if await self.tenant_repo.get_by_name(name):
                  raise DomainError("Name already in use")

        provided_admin_fields = [
            admin_email is not None,
            admin_name is not None,
            admin_password is not None,
        ]
        if any(provided_admin_fields):
            if not all(provided_admin_fields):
                raise DomainError("Initial tenant admin details are incomplete")
            if self.user_repo is None:
                raise DomainError("User repository is required to create the initial tenant admin")

        tenant = Tenant(
            id=str(uuid.uuid4()),
            name=name.strip()
        )

        await self.tenant_repo.save(tenant)
        events = []
        tenant.record_event(
            TenantCreated(
                tenant_id=tenant.id,
                name=tenant.name,
                occurred_at=datetime.now(),
            )
        )
        events.extend(tenant.events)
        tenant.clear_events()

        if admin_email is not None and admin_name is not None and admin_password is not None:
            normalized_email = admin_email.strip().lower()
            if await self.user_repo.get_by_email(normalized_email):
                raise DomainError("Email already registered")

            admin_user = User(
                id=str(uuid.uuid4()),
                email=normalized_email,
                name=admin_name,
                password=generate_password_hash(admin_password),
                role=UserRole.TENANT_ADMIN,
                tenant_id=tenant.id,
            )
            await self.user_repo.save(admin_user)
            admin_user.record_event(
                TenantUserRegistered(
                    user_id=admin_user.id,
                    tenant_id=tenant.id,
                    email=admin_user.email,
                    role=admin_user.role.value,
                    occurred_at=datetime.now(),
                )
            )
            events.extend(admin_user.events)
            admin_user.clear_events()

        self.event_bus.publish(events)
        return tenant
