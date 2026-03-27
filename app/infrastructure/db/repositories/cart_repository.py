from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.entities.cart import Cart
from app.infrastructure.db.mappers import cart_to_entity, cart_to_model
from app.infrastructure.db.models import CartModel
from app.interfaces.repositories.cart_repository import CartRepository


class SqlAlchemyCartRepository(CartRepository):
    def __init__(self, session) -> None:
        self.session = session

    async def get_by_user(self, user_id: str) -> Cart | None:
        stmt = (
            select(CartModel)
            .options(selectinload(CartModel.items))
            .where(CartModel.user_id == user_id)
        )
        model = await self.session.scalar(stmt)
        if model is None:
            return None
        return cart_to_entity(model)

    async def save(self, cart: Cart) -> None:
        stmt = (
            select(CartModel)
            .options(selectinload(CartModel.items))
            .where(CartModel.user_id == cart.user_id)
        )
        existing = await self.session.scalar(stmt)
        if existing is not None and existing.id != cart.id:
            await self.session.delete(existing)
            await self.session.flush()
            existing = None

        model = cart_to_model(cart, existing)
        self.session.add(model)
        await self.session.flush()

    async def delete(self, cart_id: str) -> None:
        model = await self.session.get(CartModel, cart_id)
        if model is not None:
            await self.session.delete(model)
            await self.session.flush()

    async def list_all(self) -> list[Cart]:
        stmt = select(CartModel).options(selectinload(CartModel.items))
        result = await self.session.scalars(stmt)
        return [cart_to_entity(model) for model in result.all()]
