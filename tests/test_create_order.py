from app.use_cases.order.create_order import CreateOrder
from tests.fakes.fake_order_repository import FakeOrderRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository

def test_create_order():
      wallet_repo = FakeWalletRepository()
      order_repo = FakeOrderRepository()
      product_repo = FakeProductRepository()

      use_case = CreateOrder(
            product_repo=product_repo,
            wallet_repo=wallet_repo,
            order_repo=order_repo,
      )

      order = use_case.execute(
            tenant_id='tenant_1',
            user_id='user_1',
            products={'product_1': 2, 'product_2': 10},
      )


      assert order.products == {'product_1': 2, 'product_2': 10}
      