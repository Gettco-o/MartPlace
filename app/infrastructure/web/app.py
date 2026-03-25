from app.infrastructure.web.extensions import qs
from quart import Quart

def create_app():
      app = Quart(__name__)

      qs.init_app(app)

      from app.infrastructure.web.routes.orders import orders
      from app.infrastructure.web.routes.tenants import tenants
      from app.infrastructure.web.routes.users import users
      from app.infrastructure.web.routes.products import products
      from app.infrastructure.web.routes.cart import cart
      from app.infrastructure.web.routes.wallet import wallet
      app.register_blueprint(orders)
      app.register_blueprint(tenants)
      app.register_blueprint(users)
      app.register_blueprint(products)
      app.register_blueprint(cart)
      app.register_blueprint(wallet)

      return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)