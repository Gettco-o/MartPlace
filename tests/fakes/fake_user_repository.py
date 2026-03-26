from app.domain.entities.user import User
from app.interfaces.repositories.user_repository import UserRepository


class FakeUserRepository(UserRepository):

    def __init__(self):
        self.users: dict[str, User] = {}

    async def save(self, user: User):
        self.users[user.id] = user

    async def get_by_id(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        for user in self.users.values():
            if user.email == email:
                return user
        return None
