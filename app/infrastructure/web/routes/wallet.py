from dataclasses import asdict

from quart import Blueprint
from quart_schema import tag_blueprint, validate_request, validate_response

from app.domain.value_objects.money import Money
from app.infrastructure.web.auth import auth_required, get_current_actor_id
from app.infrastructure.web.dependencies import request_services
from app.infrastructure.web.schemas import (
    WalletAmountRequest,
    WalletResponse,
    WalletSchema,
)
from app.infrastructure.web.utils import success

wallet = Blueprint('wallet', __name__, url_prefix='/wallet')
tag_blueprint(wallet, ["wallet"])


@wallet.post("/credit")
@validate_request(WalletAmountRequest)
@auth_required
@validate_response(WalletResponse, 201)
async def credit_wallet(data: WalletAmountRequest):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        wallet_entity = await services["credit_wallet"].execute(
            actor_user_id=actor_user_id,
            user_id=actor_user_id,
            amount=Money(data.amount),
            reference_id=data.reference_id,
        )
        await services["session"].commit()

    return success({"wallet": asdict(WalletSchema.from_entity(wallet_entity))}, status_code=201)


@wallet.post("/debit")
@validate_request(WalletAmountRequest)
@auth_required
@validate_response(WalletResponse)
async def debit_wallet(data: WalletAmountRequest):
    actor_user_id = get_current_actor_id()

    async with request_services() as services:
        wallet_entity = await services["debit_wallet"].execute(
            actor_user_id=actor_user_id,
            user_id=actor_user_id,
            amount=Money(data.amount),
            reference_id=data.reference_id,
        )
        await services["session"].commit()

    return success({"wallet": asdict(WalletSchema.from_entity(wallet_entity))})
