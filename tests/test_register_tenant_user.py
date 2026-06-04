import asyncio
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
from tests.helpers import make_buyer, make_tenant_user

run = asyncio.run


def test_register_tenant_user_success():
      tenant_repo = FakeTenantRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()

      create_tenant_use_case = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)

      tenant = run(create_tenant_use_case.execute(name="Shop A"))
      actor = make_tenant_user(tenant.id, email="admin@test.com", name="Tenant Admin")
      run(user_repo.save(actor))


      register_tenant_use_case = RegisterTenantUser(
            tenant_repo=tenant_repo,
            user_repo=user_repo,
            event_bus=fake_bus,
      )

      tenant_user = run(register_tenant_use_case.execute(
            actor_user_id=actor.id,
            tenant_id=tenant.id,
            email="seller@test.com",
            name=tenant.name,
            password="secure123",
            role=UserRole.TENANT_ADMIN
      ))

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
      actor = make_tenant_user("tenant-x", email="admin@test.com", name="Tenant Admin")
      run(user_repo.save(actor))

      with pytest.raises(DomainError):
            run(use_case.execute(
            actor_user_id=actor.id,
            tenant_id="invalid",
            email="seller@test.com",
            name="t user A",
            password="secure123",
            role=UserRole.TENANT_ADMIN
            ))


def test_register_tenant_user_rejects_actor_from_another_tenant():
      tenant_repo = FakeTenantRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()

      create_tenant_use_case = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
      tenant = run(create_tenant_use_case.execute(name="Shop A"))
      other_tenant = run(create_tenant_use_case.execute(name="Shop B"))
      actor = make_tenant_user(other_tenant.id, email="admin2@test.com", name="Other Admin")
      run(user_repo.save(actor))

      use_case = RegisterTenantUser(
            tenant_repo=tenant_repo,
            user_repo=user_repo,
            event_bus=fake_bus,
      )

      with pytest.raises(DomainError, match="User does not belong to this tenant"):
            run(use_case.execute(
                  actor_user_id=actor.id,
                  tenant_id=tenant.id,
                  email="seller@test.com",
                  name="Shop A Seller",
                  password="secure123",
                  role=UserRole.TENANT_STAFF
            ))


def test_register_tenant_user_rejects_non_tenant_actor():
      tenant_repo = FakeTenantRepository()
      user_repo = FakeUserRepository()
      fake_bus = FakeEventBus()

      create_tenant_use_case = CreateTenant(tenant_repo=tenant_repo, event_bus=fake_bus)
      tenant = run(create_tenant_use_case.execute(name="Shop A"))
      buyer = make_buyer()
      run(user_repo.save(buyer))

      use_case = RegisterTenantUser(
            tenant_repo=tenant_repo,
            user_repo=user_repo,
            event_bus=fake_bus,
      )

      with pytest.raises(DomainError, match="User is not a tenant user"):
            run(use_case.execute(
                  actor_user_id=buyer.id,
                  tenant_id=tenant.id,
                  email="seller@test.com",
                  name="Shop A Seller",
                  password="secure123",
                  role=UserRole.TENANT_STAFF
            ))
