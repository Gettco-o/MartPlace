from app.domain.value_objects.order_item import OrderItem
from app.use_cases.order.create_order import CreateOrder
from app.use_cases.tenant.create_tenant import CreateTenant
from tests.fakes.fake_event_bus import FakeEventBus
from app.use_cases.wallet.credit_wallet import CreditWallet
from tests.fakes.fake_order_repository import FakeOrderRepository
from tests.fakes.fake_product_repository import FakeProductRepository
from tests.fakes.fake_tenant_repository import FakeTenantRepository
from tests.fakes.fake_wallet_repository import FakeWalletRepository
from tests.fakes.fake_idempotency_repository import FakeIdempotencyRepository
from app.domain.entities.product import Product
from app.domain.value_objects.money import Money
from app.domain.events.order_created import OrderCreated


def test_create_order_idempotent():
      wallet_repo = FakeWalletRepository()
      product_repo = FakeProductRepository()
      order_repo = FakeOrderRepository()
      idem_repo = FakeIdempotencyRepository()
      tenant_repo = FakeTenantRepository()
      fake_bus = FakeEventBus()

      credit_uc = CreditWallet(wallet_repo, tenant_repo, fake_bus)
      create_order_uc = CreateOrder(
            order_repo=order_repo,
            product_repo=product_repo,
            wallet_repo=wallet_repo,
            idempotency_repo=idem_repo,
            tenant_repo=tenant_repo,
            event_bus=fake_bus,
      )

      t_use_case = CreateTenant(tenant_repo, fake_bus)

      tenant = t_use_case.execute(name="Shop A")

      product = Product(
            id="prod_1",
            tenant_id=tenant.id,
            name="Plaster Powder",
            price=Money(50),
            stock=100,
      )
      product_repo.save(product)

      credit_uc.execute(tenant.id, "user_1", Money(150))

      order1 = create_order_uc.execute(
            tenant_id=tenant.id,
            user_id="user_1",
            items=[
                  OrderItem(
                        product_id="prod_1",
                        quantity=2,
                        unit_price=Money(50)
                  )
            ],
            idempotency_key="abc-123",
      )

      order2 = create_order_uc.execute(
            tenant_id=tenant.id,
            user_id="user_1",
            items=[
                  OrderItem(
                        product_id="prod_1",
                        quantity=2,
                        unit_price=Money(50)
                  )
            ],
            idempotency_key="abc-123",
      )

      assert order1.id == order2.id
      # ensure the OrderCreated event was published
      assert any(isinstance(e, OrderCreated) for e in fake_bus.published_events)
      assert wallet_repo.get_wallet(tenant.id, "user_1").balance.amount == 50
