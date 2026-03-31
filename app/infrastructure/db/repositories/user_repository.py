from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.infrastructure.db.mappers import user_to_entity, user_to_model
from app.infrastructure.db.models import UserModel
from app.interfaces.repositories.user_repository import UserRepository


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, user: User) -> None:
        model = await self.session.get(UserModel, user.id)
        model = user_to_model(user, model)
        self.session.add(model)
        await self.session.flush()

    async def get_by_id(self, user_id: str) -> User | None:
        model = await self.session.get(UserModel, user_id)
        if model is None:
            return None
        return user_to_entity(model)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        model = await self.session.scalar(stmt)
        if model is None:
            return None
        return user_to_entity(model)

    async def list_all(self) -> list[User]:
        stmt = select(UserModel).order_by(UserModel.name.asc(), UserModel.id.asc())
        result = await self.session.scalars(stmt)
        return [user_to_entity(model) for model in result.all()]
