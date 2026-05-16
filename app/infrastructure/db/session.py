from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.db.config import DatabaseConfig


class Database:
    """Async SQLAlchemy database manager."""

    def __init__(self) -> None:
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None

    def init(self, config: DatabaseConfig | None = None) -> DatabaseConfig:
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

        return db_config

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
