from dataclasses import dataclass

from app.domain.value_objects.user_role import UserRole
from app.domain.value_objects.user_status import UserStatus

@dataclass
class RegisterTenantUserIn:
      actor_user_id: str
      email: str
      name: str
      tenant_id: str
      role: UserRole
      password: str

@dataclass
class RegisterTenantUserOut:
      id: str
      email: str
      name: str
      password: str
      role: UserRole
      status: UserStatus
      tenant_id: str