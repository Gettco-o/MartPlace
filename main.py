import argparse
import asyncio
from getpass import getpass
import uuid

from dotenv import load_dotenv
from sqlalchemy import select

from app.domain.entities.user import User
from app.domain.exceptions import DomainError
from app.domain.value_objects.user_role import UserRole
from app.infrastructure.db import Database
from app.infrastructure.db.models import UserModel
from app.infrastructure.db.repositories import SqlAlchemyUserRepository
from app.infrastructure.web.app import create_app
from werkzeug.security import generate_password_hash


async def bootstrap_platform_admin(email: str, name: str, password: str) -> None:
    app = create_app()
    database: Database = app.extensions["db"]

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MartPlace management commands")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Run the Quart development server")
    serve_parser.add_argument("--debug", action="store_true", help="Run Quart in debug mode")

    bootstrap_parser = subparsers.add_parser(
        "bootstrap-admin",
        help="Create the initial platform admin if one does not already exist",
    )
    bootstrap_parser.add_argument("--email", help="Platform admin email")
    bootstrap_parser.add_argument("--name", help="Platform admin display name")
    bootstrap_parser.add_argument("--password", help="Platform admin password")

    args = parser.parse_args()
    if args.command is None:
        args.command = "serve"
        args.debug = False
    return args


def prompt_if_missing(value: str | None, prompt: str, *, secret: bool = False) -> str:
    if value:
        return value
    return getpass(prompt) if secret else input(prompt)


def main() -> None:
    load_dotenv()
    args = parse_args()

    if args.command == "serve":
        app = create_app()
        app.run(debug=args.debug)
        return

    if args.command == "bootstrap-admin":
        email = prompt_if_missing(args.email, "Platform admin email: ")
        name = prompt_if_missing(args.name, "Platform admin name: ")
        password = prompt_if_missing(args.password, "Platform admin password: ", secret=True)
        asyncio.run(bootstrap_platform_admin(email=email, name=name, password=password))
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
