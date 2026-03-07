from dataclasses import dataclass
from typing import Optional

from app.domain.exceptions import DomainError
from app.domain.value_objects.user_role import UserRole
from app.domain.value_objects.user_status import UserStatus

@dataclass
class User:
      id: str
      email: str
      name: str
      password: str
      role: UserRole
      status: UserStatus = UserStatus.ACTIVE
      tenant_id: Optional[str] = None


      def ensure_active(self):
            if self.status != UserStatus.ACTIVE:
                  raise DomainError("User is not active")
            
      def ensure_buyer(self):
            if self.role != UserRole.BUYER:
                  raise DomainError("User is not a buyer")
            
      def ensure_tenant_user(self):
            if self.role not in (
                  UserRole.TENANT_ADMIN, 
                  UserRole.TENANT_STAFF
            ):
                  raise DomainError("User is not a tenant user")
            
      def ensure_platform_admin(self):
            if self.role != UserRole.PLATFORM_ADMIN:
                  raise DomainError("User is not a platform admin")
            
      def suspend(self):
            if self.status == UserStatus.SUSPENDED:
                  raise DomainError("User is already suspended")
            self.status = UserStatus.SUSPENDED

      def activate(self):
            if self.status == UserStatus.ACTIVE:
                  raise DomainError("User is already active")
            self.status = UserStatus.ACTIVE

      def __post_init__(self):
            if self.role == UserRole.BUYER and self.tenant_id is not None:
                  raise DomainError("Buyer cannot belong to a tenant")

            if self.role in (
                  UserRole.TENANT_ADMIN,
                  UserRole.TENANT_STAFF,
            ) and not self.tenant_id:
                  raise DomainError("Tenant user must belong to a tenant")
                  
