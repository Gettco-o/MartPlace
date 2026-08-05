import os

from dotenv import load_dotenv
from quart import Quart, jsonify
from quart_schema import security_scheme, tag
from quart_cors import cors
from app.domain.exceptions import DomainError
from app.bootstrap import create_app_runtime
from app.infrastructure.services.cache_service import RedisCacheService
from app.infrastructure.web.auth import AuthenticationError
from app.infrastructure.web.extensions import db, qs


def create_app():
      load_dotenv()
      app = Quart(__name__)
      app = cors(app, allow_origin="*")
      app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
      app.config["AUTH_TOKEN_MAX_AGE"] = int(os.getenv("AUTH_TOKEN_MAX_AGE", "900"))
      app.config["AUTH_REFRESH_TOKEN_MAX_AGE"] = int(
            os.getenv("AUTH_REFRESH_TOKEN_MAX_AGE", "604800")
      )
      app.config["AUTH_REFRESH_COOKIE_NAME"] = os.getenv(
            "AUTH_REFRESH_COOKIE_NAME", "refresh_token"
      )
      app.config["AUTH_REFRESH_COOKIE_SECURE"] = os.getenv(
            "AUTH_REFRESH_COOKIE_SECURE", "true"
      ).lower() == "true"
      app.config["AUTH_REFRESH_COOKIE_SAMESITE"] = os.getenv(
            "AUTH_REFRESH_COOKIE_SAMESITE", "Lax"
      )
      app.config["EVENT_LOG_PATH"] = os.getenv("EVENT_LOG_PATH", "logs/events.log")
      app.config["EMAIL_LOG_PATH"] = os.getenv("EMAIL_LOG_PATH", "logs/emails.log")
      app.config["REDIS_URL"] = os.getenv("REDIS_URL", "redis://localhost:6379/0")

      db_config = db.init()
      app.config["DATABASE_URL"] = db_config.url
      app.config["SQLALCHEMY_ECHO"] = db_config.echo
      app.extensions["db"] = db

      cache = RedisCacheService(redis_url=app.config["REDIS_URL"])
      app.extensions["cache"] = cache

      @app.before_serving
      async def startup_services() -> None:
            await cache.connect()

      @app.after_serving
      async def shutdown_services() -> None:
            await db.close()
            await cache.close()


      qs.init_app(app)
      runtime = create_app_runtime(
            event_log_path=app.config["EVENT_LOG_PATH"],
            email_log_path=app.config["EMAIL_LOG_PATH"],
      )
      app.extensions["event_bus"] = runtime.event_bus
      app.extensions["email_service"] = runtime.email_service

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

      @security_scheme([])
      @app.get("/health")
      @tag(["system"])
      async def health():
            return jsonify(
                  {
                        "success": True,
                        "service": "martplace-api",
                        "database_url": app.config.get("DATABASE_URL"),
                        "redis_connected": cache.is_connected,
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
