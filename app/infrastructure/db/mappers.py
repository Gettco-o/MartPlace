from app.domain.entities.cart import Cart
from app.domain.entities.idempotency import IdempotencyRecord
from app.domain.entities.ledger_entry import LedgerEntry
from app.domain.entities.order import Order
from app.domain.entities.product import Product
from app.domain.entities.tenant import Tenant
from app.domain.entities.user import User
from app.domain.value_objects.cart_item import CartItem
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_item import OrderItem
from app.infrastructure.db.models import (
    CartItemModel,
    CartModel,
    IdempotencyRecordModel,
    LedgerEntryModel,
    OrderItemModel,
    OrderModel,
    ProductModel,
    TenantModel,
    UserModel,
)


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


def cart_to_model(entity: Cart, model: CartModel | None = None) -> CartModel:
    model = model or CartModel(id=entity.id, user_id=entity.user_id, status=entity.status)
    model.user_id = entity.user_id
    model.status = entity.status
    model.items = [
        CartItemModel(
            product_id=item.product_id,
            tenant_id=item.tenant_id,
            quantity=item.quantity,
            unit_price_amount=item.unit_price.amount,
        )
        for item in entity.items
    ]
    return model


def cart_to_entity(model: CartModel) -> Cart:
    return Cart(
        id=model.id,
        user_id=model.user_id,
        items=[
            CartItem(
                product_id=item.product_id,
                tenant_id=item.tenant_id,
                quantity=item.quantity,
                unit_price=Money(item.unit_price_amount),
            )
            for item in model.items
        ],
        status=model.status,
        created_at=model.created_at,
    )


def order_to_model(entity: Order, model: OrderModel | None = None) -> OrderModel:
    model = model or OrderModel(
        id=entity.id,
        tenant_id=entity.tenant_id,
        user_id=entity.user_id,
        amount=entity.amount.amount,
        status=entity.status,
    )
    model.tenant_id = entity.tenant_id
    model.user_id = entity.user_id
    model.amount = entity.amount.amount
    model.status = entity.status
    model.items = [
        OrderItemModel(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price_amount=item.unit_price.amount,
        )
        for item in entity.items
    ]
    return model


def order_to_entity(model: OrderModel) -> Order:
    return Order(
        id=model.id,
        tenant_id=model.tenant_id,
        user_id=model.user_id,
        items=[
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=Money(item.unit_price_amount),
            )
            for item in model.items
        ],
        amount=Money(model.amount),
        status=model.status,
        created_at=model.created_at,
    )


def ledger_entry_to_model(entity: LedgerEntry, model: LedgerEntryModel | None = None) -> LedgerEntryModel:
    model = model or LedgerEntryModel(
        id=entity.id,
        tenant_id=entity.tenant_id,
        user_id=entity.user_id,
        amount=entity.amount.amount,
        entry_type=entity.entry_type,
        reference_id=entity.reference_id,
    )
    model.tenant_id = entity.tenant_id
    model.user_id = entity.user_id
    model.amount = entity.amount.amount
    model.entry_type = entity.entry_type
    model.reference_id = entity.reference_id
    return model


def ledger_entry_to_entity(model: LedgerEntryModel) -> LedgerEntry:
    return LedgerEntry(
        id=model.id,
        tenant_id=model.tenant_id,
        user_id=model.user_id,
        amount=Money(model.amount),
        entry_type=model.entry_type,
        reference_id=model.reference_id,
        created_at=model.created_at,
    )


def idempotency_to_model(
    entity: IdempotencyRecord,
    model: IdempotencyRecordModel | None = None,
) -> IdempotencyRecordModel:
    model = model or IdempotencyRecordModel(
        key=entity.key,
        operation=entity.operation,
        result_id=entity.result_id,
    )
    model.result_id = entity.result_id
    return model


def idempotency_to_entity(model: IdempotencyRecordModel) -> IdempotencyRecord:
    return IdempotencyRecord(
        key=model.key,
        operation=model.operation,
        result_id=model.result_id,
    )
