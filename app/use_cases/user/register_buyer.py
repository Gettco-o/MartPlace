from dataclasses import dataclass
import uuid

from app.domain.entities.user import User
from app.domain.exceptions import DomainError
from app.domain.value_objects.user_role import UserRole
from app.interfaces.repositories.user_repository import UserRepository

@dataclass
class RegisterBuyer:
      user_repo: UserRepository

      def execute(self, email: str, name: str, password: str) -> User:

            if self.user_repo.get_by_email(email):
                  raise DomainError("Email already in use")
            
            user = User(
                  id=str(uuid.uuid4()),
                  email=email.strip().lower(),
                  name=name,
                  password=password,
                  role=UserRole.BUYER
            )

            self.user_repo.save(user)
            return user
