from dataclasses import dataclass

from app.domain.entities.tenant import Tenant


@dataclass
class CreateTenantRequest:
    name: str
    admin_email: str
    admin_name: str
    admin_password: str


@dataclass
class TenantSchema:
    id: str
    name: str
    status: str

    @classmethod
    def from_entity(cls, tenant: Tenant) -> "TenantSchema":
        return cls(
            id=tenant.id,
            name=tenant.name,
            status=tenant.status.value,
        )


@dataclass
class TenantResponse:
    success: bool
    tenant: TenantSchema
