from app.domain.events.order_cancelled import OrderCancelled
from app.domain.events.order_created import OrderCreated
from app.domain.events.order_delivered import OrderDelivered
from app.domain.events.order_failed import OrderFailed
from app.domain.events.order_fulfilled import OrderFulfilled
from app.domain.events.order_processing_started import OrderProcessingStarted
from app.domain.events.order_refunded import OrderRefunded
from app.interfaces.email_service import EmailService
from app.interfaces.event_bus import EventBus


def handle_order_created_email(event: OrderCreated, email_service: EmailService) -> None:
    subject = f"Order {event.order_id} created successfully"
    body = (
        f"Hi,\n\n"
        f"Your order has been created successfully.\n"
        f"Order ID: {event.order_id}\n"
        f"Tenant ID: {event.tenant_id}\n\n"
        f"We'll notify you again as your order progresses."
    )
    email_service.send(
        to=event.user_email,
        subject=subject,
        body=body,
    )


def _send_order_status_email(
    *,
    to: str,
    order_id: str,
    tenant_id: str,
    status_label: str,
    body_message: str,
    email_service: EmailService,
) -> None:
    email_service.send(
        to=to,
        subject=f"Order {order_id} {status_label}",
        body=(
            f"Hi,\n\n"
            f"{body_message}\n"
            f"Order ID: {order_id}\n"
            f"Tenant ID: {tenant_id}"
        ),
    )


def handle_order_processing_started_email(
    event: OrderProcessingStarted,
    email_service: EmailService,
) -> None:
    _send_order_status_email(
        to=event.user_email,
        order_id=event.order_id,
        tenant_id=event.tenant_id,
        status_label="is now processing",
        body_message="Your order is now being processed.",
        email_service=email_service,
    )


def handle_order_fulfilled_email(event: OrderFulfilled, email_service: EmailService) -> None:
    _send_order_status_email(
        to=event.user_email,
        order_id=event.order_id,
        tenant_id=event.tenant_id,
        status_label="has been fulfilled",
        body_message="Your order has been fulfilled and is getting ready for delivery.",
        email_service=email_service,
    )


def handle_order_delivered_email(event: OrderDelivered, email_service: EmailService) -> None:
    _send_order_status_email(
        to=event.user_email,
        order_id=event.order_id,
        tenant_id=event.tenant_id,
        status_label="has been delivered",
        body_message="Your order has been marked as delivered.",
        email_service=email_service,
    )


def handle_order_cancelled_email(event: OrderCancelled, email_service: EmailService) -> None:
    _send_order_status_email(
        to=event.user_email,
        order_id=event.order_id,
        tenant_id=event.tenant_id,
        status_label="has been cancelled",
        body_message="Your order has been cancelled and any eligible refund has been initiated.",
        email_service=email_service,
    )


def handle_order_refunded_email(event: OrderRefunded, email_service: EmailService) -> None:
    _send_order_status_email(
        to=event.user_email,
        order_id=event.order_id,
        tenant_id=event.tenant_id,
        status_label="has been refunded",
        body_message="Your order has been refunded successfully.",
        email_service=email_service,
    )


def handle_order_failed_email(event: OrderFailed, email_service: EmailService) -> None:
    _send_order_status_email(
        to=event.user_email,
        order_id=event.order_id,
        tenant_id=event.tenant_id,
        status_label="could not be completed",
        body_message="We could not complete your order. Please try again or contact support.",
        email_service=email_service,
    )


def register_buyer_order_email_handlers(event_bus: EventBus, email_service: EmailService) -> None:
    event_bus.register(
        OrderCreated,
        lambda event: handle_order_created_email(event, email_service),
    )
    event_bus.register(
        OrderProcessingStarted,
        lambda event: handle_order_processing_started_email(event, email_service),
    )
    event_bus.register(
        OrderFulfilled,
        lambda event: handle_order_fulfilled_email(event, email_service),
    )
    event_bus.register(
        OrderDelivered,
        lambda event: handle_order_delivered_email(event, email_service),
    )
    event_bus.register(
        OrderCancelled,
        lambda event: handle_order_cancelled_email(event, email_service),
    )
    event_bus.register(
        OrderRefunded,
        lambda event: handle_order_refunded_email(event, email_service),
    )
    event_bus.register(
        OrderFailed,
        lambda event: handle_order_failed_email(event, email_service),
    )
