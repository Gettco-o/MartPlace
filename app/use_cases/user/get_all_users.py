from dataclasses import dataclass

from app.domain.entities.user import User
from app.interfaces.repositories.user_repository import UserRepository
from app.use_cases.auth import ensure_platform_admin


@dataclass
class GetAllUsers:
    user_repo: UserRepository

    async def execute(self, actor_user_id: str) -> list[User]:
        await ensure_platform_admin(self.user_repo, actor_user_id)
        return await self.user_repo.list_all()
