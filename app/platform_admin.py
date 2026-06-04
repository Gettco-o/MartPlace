import uuid

from sqlalchemy import select
from werkzeug.security import generate_password_hash

from app.domain.entities.user import User
from app.domain.exceptions import DomainError
from app.domain.value_objects.user_role import UserRole
from app.infrastructure.db import Database
from app.infrastructure.db.models import UserModel
from app.infrastructure.db.repositories import SqlAlchemyUserRepository


async def bootstrap_platform_admin(email: str, name: str, password: str) -> None:
    database = Database()
    database.init()

    try:
        async with database.session() as session:
            existing_platform_admin = await session.scalar(
                select(UserModel.id).where(UserModel.role == UserRole.PLATFORM_ADMIN)
            )
            if existing_platform_admin is not None:
                raise DomainError("A platform admin already exists")

            user_repo = SqlAlchemyUserRepository(session)
            normalized_email = email.strip().lower()
            if await user_repo.get_by_email(normalized_email):
                raise DomainError("Email already registered")

            admin_user = User(
                id=str(uuid.uuid4()),
                email=normalized_email,
                name=name.strip(),
                password=generate_password_hash(password),
                role=UserRole.PLATFORM_ADMIN,
            )
            await user_repo.save(admin_user)
            await session.commit()

        print(f"Platform admin created for {normalized_email}")
    finally:
        await database.close()
