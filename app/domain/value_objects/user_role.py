from enum import Enum

class UserRole(str, Enum):
      BUYER = "buyer"
      TENANT_ADMIN = "tenant_admin"
      TENANT_STAFF = "tenant_staff"
      PLATFORM_ADMIN = "platform_admin"