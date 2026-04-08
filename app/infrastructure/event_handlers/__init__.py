from app.infrastructure.event_handlers.audit_logger import register_audit_log_handlers
from app.infrastructure.event_handlers.buyer_order_emails import (
    register_buyer_order_email_handlers,
)
from app.infrastructure.event_handlers.file_logger import register_event_file_handlers
from app.infrastructure.event_handlers.tenant_order_emails import (
    register_tenant_order_email_handlers,
)
from app.infrastructure.event_handlers.user_emails import register_user_email_handlers
from app.interfaces.email_service import EmailService
from app.interfaces.event_bus import EventBus


def register_email_handlers(event_bus: EventBus, email_service: EmailService) -> None:
    register_user_email_handlers(event_bus, email_service)
    register_buyer_order_email_handlers(event_bus, email_service)
    register_tenant_order_email_handlers(event_bus, email_service)

__all__ = [
    "register_audit_log_handlers",
    "register_buyer_order_email_handlers",
    "register_event_file_handlers",
    "register_email_handlers",
    "register_tenant_order_email_handlers",
    "register_user_email_handlers",
]
