from app.use_cases.order.create_order import CreateOrder
from app.use_cases.wallet.credit_wallet import CreditWallet
from tests.fakes.fake_order_repository import FakeOrderRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from tests.fakes.fake_idempotency_repository import FakeIdempotencyRepository
from app.domain.entities.product import Product
from app.domain.value_objects.money import Money

"""
def test_create_order():
      wallet_repo = FakeWalletRepository()
      order_repo = FakeOrderRepository()
      product_repo = FakeProductRepository()

      create_order_use_case = CreateOrder(
            product_repo=product_repo,
            wallet_repo=wallet_repo,
            order_repo=order_repo,
      )

      credit_wallet_use_case = CreditWallet(
            wallet_repository=wallet_repo
      )

      product_1 = Product(
            id="product_1",
            tenant_id="tenant_1",
            name="Nunex",
            price=Money(500),
            stock=200,
      )

      product_2 = Product(
            id="product_2",
            tenant_id="tenant_1",
            name="Plaster Powder",
            price=Money(300),
            stock=100,
      )

      product_repo.save(product_1)
      product_repo.save(product_2)

      credit_wallet_use_case.execute(
            tenant_id="tenant_1",
            user_id="user_1",
            amount=Money(200000)
      )

      order = create_order_use_case.execute(
            tenant_id='tenant_1',
            user_id='user_1',
            products={'product_1': 2, 'product_2': 10},
      )


      assert order.amount == Money(4000)
      assert len(order_repo.orders) == 1
"""

def test_create_order_idempotent():
      wallet_repo = FakeWalletRepository()
      product_repo = FakeProductRepository()
      order_repo = FakeOrderRepository()
      idem_repo = FakeIdempotencyRepository()

      credit_uc = CreditWallet(wallet_repo)
      create_order_uc = CreateOrder(
            order_repo,
            product_repo,
            wallet_repo,
            idem_repo,
      )

      product = Product(
            id="prod_1",
            tenant_id="tenant_1",
            name="Plaster Powder",
            price=Money(50),
            stock=100,
      )
      product_repo.save(product)

      credit_uc.execute("tenant_1", "user_1", Money(100))

      order1 = create_order_uc.execute(
            tenant_id="tenant_1",
            user_id="user_1",
            products={"prod_1": 1},
            idempotency_key="abc-123",
      )

      order2 = create_order_uc.execute(
            tenant_id="tenant_1",
            user_id="user_1",
            products={"prod_1": 1},
            idempotency_key="abc-123",
      )

      assert order1.id == order2.id
      assert wallet_repo.get_wallet("tenant_1", "user_1").balance.amount == 50
