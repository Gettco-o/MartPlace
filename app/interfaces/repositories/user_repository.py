from abc import ABC, abstractmethod
from app.domain.entities.user import User


class UserRepository(ABC):

      @abstractmethod
      async def save(self, user: User) -> None:
            pass

      @abstractmethod
      async def get_by_id(self, user_id: str) -> User | None:
            pass

      @abstractmethod
      async def get_by_email(self, email: str) -> User | None:
            pass

      @abstractmethod
      async def list_all(self) -> list[User]:
            pass

      @abstractmethod
      async def list_by_tenant(self, tenant_id: str) -> list[User]:
            pass
