from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.entities.order import Order
from app.infrastructure.db.mappers import order_to_entity, order_to_model
from app.infrastructure.db.models import OrderModel
from app.interfaces.repositories.order_repository import OrderRepository


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session) -> None:
        self.session = session

    async def save(self, order: Order) -> None:
        model = await self.session.get(
            OrderModel,
            order.id,
            options=[selectinload(OrderModel.items)],
        )
        model = order_to_model(order, model)
        self.session.add(model)
        await self.session.flush()

    async def get_by_id(self, tenant_id: str, order_id: str) -> Order | None:
        stmt = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.tenant_id == tenant_id, OrderModel.id == order_id)
        )
        model = await self.session.scalar(stmt)
        if model is None:
            return None
        return order_to_entity(model)

    async def list_all(self, tenant_id: str) -> list[Order]:
        stmt = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.tenant_id == tenant_id)
            .order_by(OrderModel.created_at.desc(), OrderModel.id.desc())
        )
        result = await self.session.scalars(stmt)
        return [order_to_entity(model) for model in result.all()]
