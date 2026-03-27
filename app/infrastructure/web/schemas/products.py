from dataclasses import dataclass

from app.domain.entities.product import Product


@dataclass
class CreateProductRequest:
    tenant_id: str
    name: str
    price_amount: int
    stock: int


@dataclass
class ProductSchema:
    id: str
    tenant_id: str
    name: str
    price_amount: int
    stock: int

    @classmethod
    def from_entity(cls, product: Product) -> "ProductSchema":
        return cls(
            id=product.id,
            tenant_id=product.tenant_id,
            name=product.name,
            price_amount=product.price.amount,
            stock=product.stock,
        )


@dataclass
class ProductResponse:
    success: bool
    product: ProductSchema

@dataclass
class ProductUpdateRequest:
    name: str | None = None
    price_amount: int | None = None
    stock: int | None = None
