from dataclasses import dataclass

from app.infrastructure.event_bus import SimpleEventBus
from app.infrastructure.event_handlers import (
    register_audit_log_handlers,
    register_email_handlers,
    register_event_file_handlers,
)
from app.infrastructure.services import FileEmailService
from app.interfaces.email_service import EmailService
from app.interfaces.event_bus import EventBus


@dataclass(frozen=True)
class AppRuntime:
    event_bus: EventBus
    email_service: EmailService


def create_app_runtime(*, event_log_path: str, email_log_path: str) -> AppRuntime:
    event_bus = SimpleEventBus()
    email_service = FileEmailService(email_log_path)

    register_event_handlers(
        event_bus=event_bus,
        email_service=email_service,
        event_log_path=event_log_path,
    )

    return AppRuntime(
        event_bus=event_bus,
        email_service=email_service,
    )


def register_event_handlers(
    *,
    event_bus: EventBus,
    email_service: EmailService,
    event_log_path: str,
) -> None:
    register_audit_log_handlers(event_bus)
    register_event_file_handlers(event_bus, event_log_path)
    register_email_handlers(event_bus, email_service)
