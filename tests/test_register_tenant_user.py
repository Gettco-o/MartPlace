import pytest
from app.domain.events.tenant_created import TenantCreated
from app.domain.events.tenant_user_registered import TenantUserRegistered
from app.domain.value_objects.user_role import UserRole
from app.use_cases.tenant.create_tenant import CreateTenant
from app.use_cases.user.register_tenant_user import RegisterTenantUser
from tests.fakes.fake_event_bus import FakeEventBus
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from app.domain.exceptions import DomainError


def test_register_tenant_user_success():
      tenant_repo = FakeTenantRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()

      create_tenant_use_case = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)

      tenant = create_tenant_use_case.execute(name="Shop A")


      register_tenant_use_case = RegisterTenantUser(
            tenant_repo=tenant_repo,
            user_repo=user_repo,
            event_bus=fake_bus,
      )

      tenant_user = register_tenant_use_case.execute(
            tenant_id=tenant.id,
            email="seller@test.com",
            name=tenant.name,
            password="secure123",
            role=UserRole.TENANT_ADMIN
      )

      assert tenant_user.tenant_id == tenant.id
      assert tenant_user.name == tenant.name
      assert tenant_user.role == UserRole.TENANT_ADMIN
      assert any(isinstance(event, TenantCreated) for event in fake_bus.published_events)
      assert any(isinstance(event, TenantUserRegistered) for event in fake_bus.published_events)


def test_register_tenant_user_invalid_tenant():
      tenant_repo = FakeTenantRepository()
      user_repo = FakeUserRepository()

      use_case = RegisterTenantUser(
            tenant_repo=tenant_repo,
            user_repo=user_repo,
            event_bus=FakeEventBus(),
      )

      with pytest.raises(DomainError):
            use_case.execute(
            tenant_id="invalid",
            email="seller@test.com",
            name="t user A",
            password="secure123",
            role=UserRole.TENANT_ADMIN
            )
