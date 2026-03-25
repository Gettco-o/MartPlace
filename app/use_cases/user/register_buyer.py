from dataclasses import dataclass
from datetime import datetime
import uuid

from app.domain.entities.user import User
from app.domain.events.buyer_registered import BuyerRegistered
from app.domain.exceptions import DomainError
from app.domain.value_objects.user_role import UserRole
from app.interfaces.event_bus import EventBus
from app.interfaces.repositories.user_repository import UserRepository

@dataclass
class RegisterBuyer:
      user_repo: UserRepository
      event_bus: EventBus

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
            user.record_event(
                  BuyerRegistered(
                        user_id=user.id,
                        email=user.email,
                        name=user.name,
                        occurred_at=datetime.now(),
                  )
            )
            self.event_bus.publish(user.events)
            user.clear_events()
            return user
