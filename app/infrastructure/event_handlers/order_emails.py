from app.domain.events.order_created import OrderCreated
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


def register_order_email_handlers(event_bus: EventBus, email_service: EmailService) -> None:
    event_bus.register(
        OrderCreated,
        lambda event: handle_order_created_email(event, email_service),
    )
