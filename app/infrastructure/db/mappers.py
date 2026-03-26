from app.domain.entities.product import Product
from app.domain.entities.tenant import Tenant
from app.domain.entities.user import User
from app.domain.value_objects.money import Money
from app.infrastructure.db.models import ProductModel, TenantModel, UserModel


def tenant_to_model(entity: Tenant, model: TenantModel | None = None) -> TenantModel:
    model = model or TenantModel(id=entity.id, name=entity.name, status=entity.status)
    model.name = entity.name
    model.status = entity.status
    return model


def tenant_to_entity(model: TenantModel) -> Tenant:
    return Tenant(
        id=model.id,
        name=model.name,
        status=model.status,
    )


def user_to_model(entity: User, model: UserModel | None = None) -> UserModel:
    model = model or UserModel(
        id=entity.id,
        email=entity.email,
        name=entity.name,
        password=entity.password,
        role=entity.role,
        status=entity.status,
        tenant_id=entity.tenant_id,
    )
    model.email = entity.email
    model.name = entity.name
    model.password = entity.password
    model.role = entity.role
    model.status = entity.status
    model.tenant_id = entity.tenant_id
    return model


def user_to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        name=model.name,
        password=model.password,
        role=model.role,
        status=model.status,
        tenant_id=model.tenant_id,
    )


def product_to_model(entity: Product, model: ProductModel | None = None) -> ProductModel:
    model = model or ProductModel(
        id=entity.id,
        tenant_id=entity.tenant_id,
        name=entity.name,
        price_amount=entity.price.amount,
        stock=entity.stock,
    )
    model.tenant_id = entity.tenant_id
    model.name = entity.name
    model.price_amount = entity.price.amount
    model.stock = entity.stock
    return model


def product_to_entity(model: ProductModel) -> Product:
    return Product(
        id=model.id,
        tenant_id=model.tenant_id,
        name=model.name,
        price=Money(model.price_amount),
        stock=model.stock,
    )
