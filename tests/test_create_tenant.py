import pytest
from app.use_cases.tenant.create_tenant import CreateTenant
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from app.domain.exceptions import DomainError


def test_create_tenant_success():
    repo = FakeTenantRepository()
    use_case = CreateTenant(repo)

    tenant = use_case.execute(name="Shop A")

    assert tenant.name == "Shop A"
    assert tenant.id is not None
    assert repo.get_by_id(tenant.id) == tenant


def test_create_tenant_duplicate_name_raises():
    repo = FakeTenantRepository()
    use_case = CreateTenant(repo)

    use_case.execute(name="Shop A")

    with pytest.raises(DomainError):
        use_case.execute(name="Shop A")