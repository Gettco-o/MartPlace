from app.domain.events.order_cancelled import OrderCancelled
from app.domain.events.order_created import OrderCreated
from app.domain.events.order_delivered import OrderDelivered
from app.domain.events.order_refunded import OrderRefunded
from app.interfaces.email_service import EmailService
from app.interfaces.event_bus import EventBus


def _send_tenant_order_email(
    *,
    recipients: tuple[str, ...],
    subject: str,
    body: str,
    email_service: EmailService,
) -> None:
    for recipient in recipients:
        email_service.send(
            to=recipient,
            subject=subject,
            body=body,
        )


def handle_tenant_order_created_email(event: OrderCreated, email_service: EmailService) -> None:
    _send_tenant_order_email(
        recipients=event.tenant_admin_emails,
        subject=f"New order {event.order_id} received",
        body=(
            f"Hi,\n\n"
            f"A new order has been placed for tenant {event.tenant_id}.\n"
            f"Order ID: {event.order_id}\n"
            f"Buyer ID: {event.user_id}"
        ),
        email_service=email_service,
    )


def handle_tenant_order_cancelled_email(
    event: OrderCancelled,
    email_service: EmailService,
) -> None:
    _send_tenant_order_email(
        recipients=event.tenant_admin_emails,
        subject=f"Order {event.order_id} was cancelled",
        body=(
            f"Hi,\n\n"
            f"Order {event.order_id} for tenant {event.tenant_id} has been cancelled.\n"
            f"Buyer ID: {event.user_id}"
        ),
        email_service=email_service,
    )


def handle_tenant_order_refunded_email(event: OrderRefunded, email_service: EmailService) -> None:
    _send_tenant_order_email(
        recipients=event.tenant_admin_emails,
        subject=f"Order {event.order_id} was refunded",
        body=(
            f"Hi,\n\n"
            f"Order {event.order_id} for tenant {event.tenant_id} has been refunded.\n"
            f"Buyer ID: {event.user_id}"
        ),
        email_service=email_service,
    )


def handle_tenant_order_delivered_email(event: OrderDelivered, email_service: EmailService) -> None:
    _send_tenant_order_email(
        recipients=event.tenant_admin_emails,
        subject=f"Order {event.order_id} was delivered",
        body=(
            f"Hi,\n\n"
            f"Order {event.order_id} for tenant {event.tenant_id} has been delivered.\n"
            f"Buyer ID: {event.user_id}"
        ),
        email_service=email_service,
    )


def register_tenant_order_email_handlers(event_bus: EventBus, email_service: EmailService) -> None:
    event_bus.register(
        OrderCreated,
        lambda event: handle_tenant_order_created_email(event, email_service),
    )
    event_bus.register(
        OrderCancelled,
        lambda event: handle_tenant_order_cancelled_email(event, email_service),
    )
    event_bus.register(
        OrderRefunded,
        lambda event: handle_tenant_order_refunded_email(event, email_service),
    )
    event_bus.register(
        OrderDelivered,
        lambda event: handle_tenant_order_delivered_email(event, email_service),
    )
