from app.domain.entities.product import Product
from app.domain.value_objects.money import Money
from app.domain.value_objects.order_status import OrderStatus
from app.use_cases.order.create_order import CreateOrder
from app.use_cases.order.refund_order import RefundOrder
from app.use_cases.wallet.credit_wallet import CreditWallet
from tests.fakes.fake_idempotency_repository import FakeIdempotencyRepository
from tests.fakes.fake_order_repository import FakeOrderRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository


def test_refund_order_idempotent():
    # repositories
    wallet_repo = FakeWalletRepository()
    product_repo = FakeProductRepository()
    order_repo = FakeOrderRepository()
    idem_repo = FakeIdempotencyRepository()

    # use cases
    credit_wallet = CreditWallet(wallet_repo)
    create_order = CreateOrder(
        order_repo,
        product_repo,
        wallet_repo,
        idem_repo,
    )
    refund_order = RefundOrder(
        order_repo,
        product_repo,
        wallet_repo,
        idem_repo,
    )

    # setup product
    product = Product(
        id="prod_1",
        tenant_id="tenant_1",
        name="Nunex",
        price=Money(50),
        stock=10,
    )
    product_repo.save(product)

    # setup wallet
    credit_wallet.execute("tenant_1", "user_1", Money(100))

    # create order
    order = create_order.execute(
        tenant_id="tenant_1",
        user_id="user_1",
        products={"prod_1": 1},
        idempotency_key="order-123",
    )

    # refund (first call)
    refunded_1 = refund_order.execute(
        tenant_id="tenant_1",
        order_id=order.id,
        idempotency_key="refund-123",
    )

    # refund (retry)
    refunded_2 = refund_order.execute(
        tenant_id="tenant_1",
        order_id=order.id,
        idempotency_key="refund-123",
    )

    # assertions
    assert refunded_1.id == refunded_2.id
    assert refunded_1.status == OrderStatus.REFUNDED

    wallet = wallet_repo.get_wallet("tenant_1", "user_1")
    assert wallet.balance.amount == 100  # refunded

    product = product_repo.get_by_id("tenant_1", "prod_1")
    assert product.stock == 10  # stock restored
