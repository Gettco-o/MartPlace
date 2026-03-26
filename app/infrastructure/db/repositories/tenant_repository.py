from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.tenant import Tenant
from app.infrastructure.db.mappers import tenant_to_entity, tenant_to_model
from app.infrastructure.db.models import TenantModel


class SqlAlchemyTenantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, tenant: Tenant) -> None:
        model = await self.session.get(TenantModel, tenant.id)
        model = tenant_to_model(tenant, model)
        self.session.add(model)
        await self.session.flush()

    async def get_by_id(self, tenant_id: str) -> Tenant | None:
        model = await self.session.get(TenantModel, tenant_id)
        if model is None:
            return None
        return tenant_to_entity(model)

    async def get_by_name(self, tenant_name: str) -> Tenant | None:
        stmt = select(TenantModel).where(TenantModel.name == tenant_name)
        model = await self.session.scalar(stmt)
        if model is None:
            return None
        return tenant_to_entity(model)
