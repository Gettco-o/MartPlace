import argparse
from datetime import datetime
import os
import uuid

from dotenv import load_dotenv

from app.bootstrap import create_app_runtime
from app.domain.events.buyer_registered import BuyerRegistered
from app.infrastructure.web.app import create_app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MartPlace management commands")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Run the Quart development server")
    serve_parser.add_argument("--debug", action="store_true", help="Run Quart in debug mode")
    serve_parser.add_argument(
        "--host",
        default=os.getenv("HOST", "0.0.0.0"),
        help="Host interface to bind the server to",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "50055")),
        help="Port to bind the server to",
    )

    emit_parser = subparsers.add_parser(
        "emit-test-event",
        help="Publish a test domain event without starting the web server",
    )
    emit_parser.add_argument("--email", default="buyer@example.com", help="Buyer email")
    emit_parser.add_argument("--name", default="Test Buyer", help="Buyer display name")

    args = parser.parse_args()
    if args.command is None:
        args.command = "serve"
        args.debug = False
        args.host = os.getenv("HOST", "0.0.0.0")
        args.port = int(os.getenv("PORT", "50055"))
    return args


def main() -> None:
    load_dotenv()
    args = parse_args()

    if args.command == "serve":
        app = create_app()
        app.run(host=args.host, port=args.port, debug=args.debug)
        return

    if args.command == "emit-test-event":
        event_log_path = os.getenv("EVENT_LOG_PATH", "logs/events.log")
        email_log_path = os.getenv("EMAIL_LOG_PATH", "logs/emails.log")
        runtime = create_app_runtime(
            event_log_path=event_log_path,
            email_log_path=email_log_path,
        )
        runtime.event_bus.publish(
            [
                BuyerRegistered(
                    user_id=str(uuid.uuid4()),
                    email=args.email.strip().lower(),
                    name=args.name.strip(),
                    occurred_at=datetime.now(),
                )
            ]
        )
        print(f"Published BuyerRegistered event for {args.email.strip().lower()}")
        print(f"Event log: {event_log_path}")
        print(f"Email log: {email_log_path}")
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
