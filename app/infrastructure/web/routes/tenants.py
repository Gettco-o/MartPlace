from dataclasses import asdict

from quart import Blueprint
from quart_schema import tag_blueprint, validate_request, validate_response

from app.infrastructure.web.dependencies import request_services
from app.infrastructure.web.schemas import (
    CreateTenantRequest,
    TenantResponse,
    TenantSchema,
)
from app.infrastructure.web.utils import success

tenants = Blueprint('tenants', __name__, url_prefix='/tenants')
tag_blueprint(tenants, ["tenants"])


@tenants.post("/")
@validate_request(CreateTenantRequest)
@validate_response(TenantResponse, 201)
async def create_tenant(data: CreateTenantRequest):
    async with request_services() as services:
        tenant = await services["create_tenant"].execute(
            name=data.name,
            admin_email=data.admin_email,
            admin_name=data.admin_name,
            admin_password=data.admin_password,
        )
        await services["session"].commit()

    return success({"tenant": asdict(TenantSchema.from_entity(tenant))}, status_code=201)


@tenants.get("/<tenant_id>")
@validate_response(TenantResponse)
async def get_tenant(tenant_id: str):
    async with request_services() as services:
        tenant = await services["get_tenant"].execute(tenant_id)

    return success({"tenant": asdict(TenantSchema.from_entity(tenant))})
