from app.domain.events.buyer_registered import BuyerRegistered
from app.domain.events.tenant_user_registered import TenantUserRegistered
from app.interfaces.email_service import EmailService
from app.interfaces.event_bus import EventBus


def handle_buyer_registered_email(event: BuyerRegistered, email_service: EmailService) -> None:
    email_service.send(
        to=event.email,
        subject="Welcome to MartPlace",
        body=(
            f"Hi {event.name},\n\n"
            f"Your buyer account has been created successfully.\n"
            f"You can now browse stores and place orders on MartPlace."
        ),
    )


def handle_tenant_user_registered_email(
    event: TenantUserRegistered,
    email_service: EmailService,
) -> None:
    email_service.send(
        to=event.email,
        subject="Your MartPlace tenant account is ready",
        body=(
            f"Hi,\n\n"
            f"You've been added to tenant {event.tenant_id} as {event.role}.\n"
            f"You can now sign in and start working from your dashboard."
        ),
    )


def register_user_email_handlers(event_bus: EventBus, email_service: EmailService) -> None:
    event_bus.register(
        BuyerRegistered,
        lambda event: handle_buyer_registered_email(event, email_service),
    )
    event_bus.register(
        TenantUserRegistered,
        lambda event: handle_tenant_user_registered_email(event, email_service),
    )
