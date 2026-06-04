import asyncio
import pytest
from app.domain.events.tenant_created import TenantCreated
from app.domain.events.tenant_user_registered import TenantUserRegistered
from app.use_cases.tenant.create_tenant import CreateTenant
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_event_bus import FakeEventBus
from app.domain.exceptions import DomainError
from tests.fakes.fake_user_repository import FakeUserRepository
from werkzeug.security import check_password_hash

run = asyncio.run


def test_create_tenant_success():
    repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()
    use_case = CreateTenant(repo, fake_bus, user_repo=user_repo)

    tenant = run(
        use_case.execute(
            name="Shop A",
            admin_email="owner@shopa.com",
            admin_name="Shop Owner",
            admin_password="secure123",
        )
    )

    assert tenant.name == "Shop A"
    assert tenant.id is not None
    assert run(repo.get_by_id(tenant.id)) == tenant
    admin_user = run(user_repo.get_by_email("owner@shopa.com"))
    assert admin_user is not None
    assert admin_user.tenant_id == tenant.id
    assert admin_user.role.value == "tenant_admin"
    assert check_password_hash(admin_user.password, "secure123")
    assert any(isinstance(event, TenantCreated) for event in fake_bus.published_events)
    assert any(isinstance(event, TenantUserRegistered) for event in fake_bus.published_events)


def test_create_tenant_duplicate_name_raises():
    repo = FakeTenantRepository()
    use_case = CreateTenant(repo, FakeEventBus())

    run(use_case.execute(name="Shop A"))

    with pytest.raises(DomainError):
        run(use_case.execute(name="Shop A"))


def test_create_tenant_rejects_duplicate_initial_admin_email():
    repo = FakeTenantRepository()
    user_repo = FakeUserRepository()
    fake_bus = FakeEventBus()
    use_case = CreateTenant(repo, fake_bus, user_repo=user_repo)

    run(
        use_case.execute(
            name="Shop A",
            admin_email="owner@test.com",
            admin_name="Owner One",
            admin_password="secure123",
        )
    )

    with pytest.raises(DomainError, match="Email already registered"):
        run(
            use_case.execute(
                name="Shop B",
                admin_email="owner@test.com",
                admin_name="Owner Two",
                admin_password="secure456",
            )
        )
