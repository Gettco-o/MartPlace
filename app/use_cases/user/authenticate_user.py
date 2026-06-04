from dataclasses import dataclass

from app.domain.entities.user import User
from app.domain.exceptions import DomainError
from app.interfaces.repositories.user_repository import UserRepository
from werkzeug.security import check_password_hash, generate_password_hash


@dataclass
class AuthenticateUser:
    user_repo: UserRepository

    async def execute(self, email: str, password: str) -> User:
        normalized_email = email.strip().lower()
        user = await self.user_repo.get_by_email(normalized_email)
        if user is None:
            raise DomainError("Invalid credentials")

        password_matches = check_password_hash(user.password, password)
        if not password_matches and user.password == password:
            user.password = generate_password_hash(password)
            await self.user_repo.save(user)
            password_matches = True

        if not password_matches:
            raise DomainError("Invalid credentials")

        user.ensure_active()
        return user
