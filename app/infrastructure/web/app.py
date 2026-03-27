import os

from dotenv import load_dotenv
from quart import Quart, jsonify
from quart_schema import tag

from app.domain.exceptions import DomainError
from app.infrastructure.web.auth import AuthenticationError
from app.infrastructure.web.extensions import db, event_bus, qs


def create_app():
      load_dotenv()
      app = Quart(__name__)
      app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
      app.config["AUTH_TOKEN_MAX_AGE"] = int(os.getenv("AUTH_TOKEN_MAX_AGE", "900"))
      app.config["AUTH_REFRESH_TOKEN_MAX_AGE"] = int(os.getenv("AUTH_REFRESH_TOKEN_MAX_AGE", "604800"))

      db.init_app(app)
      qs.init_app(app)
      app.extensions["event_bus"] = event_bus
      app.extensions["auth_refresh_store"] = {}

      @app.errorhandler(DomainError)
      async def handle_domain_error(error: DomainError):
            return jsonify({"success": False, "error": str(error)}), 400

      @app.errorhandler(ValueError)
      async def handle_value_error(error: ValueError):
            return jsonify({"success": False, "error": str(error)}), 400

      @app.errorhandler(AuthenticationError)
      async def handle_authentication_error(error: AuthenticationError):
            return jsonify({"success": False, "error": str(error)}), 401

      @app.errorhandler(422)
      def unprocessable(error):
            return jsonify({
                  "success": False,
                  "error": str(error)
            }), 422


      @app.errorhandler(404)
      def resource_not_found(error):
            return jsonify(
                  {
                  "success": False,
                  "error": str(error)
                  }
            ), 404

      @app.errorhandler(400)
      def bad_request(error):
            return jsonify(
                  {
                  "success": False,
                  "error": str(error)
                  }
            ), 400


      @app.errorhandler(401)
      def unauthorized(error):
            return jsonify(
                  {
                  "success": False,
                  "error": str(error)
                  }
            )

      @app.errorhandler(405)
      def method_not_allowed(error):
            return jsonify(
                  {
                  "success": False,
                  "error": str(error)
                  }
            ), 405
      
      @app.errorhandler(500)
      def internal_server_error(error):
            return jsonify(
                  {
                        "success": False,
                        "error": str(error)
                  }
            )

      @app.get("/health")
      @tag(["system"])
      async def health():
            return jsonify(
                  {
                        "success": True,
                        "service": "martplace-api",
                        "database_url": app.config.get("DATABASE_URL"),
                  }
            )

      from app.infrastructure.web.routes.auth import auth
      from app.infrastructure.web.routes.orders import orders
      from app.infrastructure.web.routes.tenants import tenants
      from app.infrastructure.web.routes.users import users
      from app.infrastructure.web.routes.products import products
      from app.infrastructure.web.routes.cart import cart
      from app.infrastructure.web.routes.wallet import wallet
      app.register_blueprint(auth)
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
