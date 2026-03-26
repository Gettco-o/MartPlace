from contextlib import asynccontextmanager

from quart import Quart
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.db.config import DatabaseConfig


class Database:
    """Quart-friendly async SQLAlchemy database manager."""

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def init_app(self, app: Quart, config: DatabaseConfig | None = None) -> None:
        db_config = config or DatabaseConfig.from_env()
        self.engine = create_async_engine(
            db_config.url,
            echo=db_config.echo,
            future=True,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        app.config["DATABASE_URL"] = db_config.url
        app.config["SQLALCHEMY_ECHO"] = db_config.echo
        app.extensions["db"] = self

        @app.after_serving
        async def shutdown_database() -> None:
            await self.close()

    @asynccontextmanager
    async def session(self):
        if self.session_factory is None:
            raise RuntimeError("Database is not initialized")

        session = self.session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None
