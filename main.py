# app/main.py
from flask import Flask, request, jsonify
from app.interfaces.repositories.order_repository import OrderRepository
from app.interfaces.repositories.product_repository import ProductRepository
from app.interfaces.repositories.wallet_repository import WalletRepository
from app.use_cases.order.create_order import CreateOrder

app = Flask(__name__)

# Temporary fake repositories for demonstration purposes
class FakeProductRepo(ProductRepository):
      def get_product_by_id(self, tenant_id: str, product_id: str):
            # Return a fake product
            from app.domain.entities.product import Product
            from app.domain.value_objects.money import Money
            return Product(
                  id=product_id,
                  tenant_id=tenant_id,
                  name="Sample Product",
                  price=Money(100),
                  stock=10
            )
class FakeWalletRepo(WalletRepository):
      def get_wallet(self, tenant_id: str, user_id: str):
            # Return a fake wallet
            from app.domain.entities.wallet import Wallet
            from app.domain.value_objects.money import Money
            return Wallet(
                  tenant_id=tenant_id,
                  user_id=user_id,
                  balance=Money(1000)
            )
      def save(self, wallet):
            pass  # Fake save method

class FakeOrderRepo(OrderRepository):
      def save(self, order):
            pass  # Fake save method
      def get_order_by_id(self, tenant_id: str, order_id: str):
            pass  # Fake get method
            

@app.route("/orders", methods=["POST"])
def create_order():
      data = request.json

      # temporary fake repositories
      use_case = CreateOrder(
            product_repo=FakeProductRepo(),
            wallet_repo=FakeWalletRepo(),
            order_repo=FakeOrderRepo(),
      )

      order = use_case.execute(
            tenant_id=data["tenant_id"],
            user_id=data["user_id"],
            products=data["products"],
      )
      
      return jsonify({
        "order_id": order.id,
        "status": order.status,
        "total": order.total.amount
    }), 201

if __name__ == "__main__":
    app.run(debug=True)
