from dataclasses import dataclass

from app.domain.entities.user import User
from app.domain.exceptions import DomainError
from app.interfaces.repositories.user_repository import UserRepository


@dataclass
class GetUser:
    user_repo: UserRepository

    async def execute(self, user_id: str) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise DomainError("User not found")
        return user
