from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.product import Product
from app.infrastructure.db.mappers import product_to_entity, product_to_model
from app.infrastructure.db.models import ProductModel
from app.interfaces.repositories.product_repository import ProductRepository


class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, product: Product) -> None:
        model = await self.session.get(ProductModel, product.id)
        model = product_to_model(product, model)
        self.session.add(model)
        await self.session.flush()

    async def get_by_id(self, tenant_id: str, product_id: str) -> Product | None:
        stmt = select(ProductModel).where(
            ProductModel.tenant_id == tenant_id,
            ProductModel.id == product_id,
        )
        model = await self.session.scalar(stmt)
        if model is None:
            return None
        return product_to_entity(model)

    async def exists_by_name(self, tenant_id: str, name: str) -> bool:
        stmt = select(ProductModel.id).where(
            ProductModel.tenant_id == tenant_id,
            ProductModel.name == name,
        )
        result = await self.session.scalar(stmt)
        return result is not None
