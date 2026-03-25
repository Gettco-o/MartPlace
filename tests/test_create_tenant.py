import pytest
from app.domain.events.tenant_created import TenantCreated
from app.use_cases.tenant.create_tenant import CreateTenant
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_event_bus import FakeEventBus
from app.domain.exceptions import DomainError


def test_create_tenant_success():
    repo = FakeTenantRepository()
    fake_bus = FakeEventBus()
    use_case = CreateTenant(repo, fake_bus)

    tenant = use_case.execute(name="Shop A")

    assert tenant.name == "Shop A"
    assert tenant.id is not None
    assert repo.get_by_id(tenant.id) == tenant
    assert any(isinstance(event, TenantCreated) for event in fake_bus.published_events)


def test_create_tenant_duplicate_name_raises():
    repo = FakeTenantRepository()
    use_case = CreateTenant(repo, FakeEventBus())

    use_case.execute(name="Shop A")

    with pytest.raises(DomainError):
        use_case.execute(name="Shop A")
