from app.domain.entities.user import User
from app.domain.exceptions import DomainError
from app.interfaces.repositories.user_repository import UserRepository


async def get_active_user(user_repo: UserRepository, user_id: str) -> User:
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise DomainError("User not found")

    user.ensure_active()
    return user


async def ensure_active_buyer(user_repo: UserRepository, actor_user_id: str, target_user_id: str) -> User:
    actor = await get_active_user(user_repo, actor_user_id)
    actor.ensure_buyer()

    if actor.id != target_user_id:
        raise DomainError("Buyer cannot act on behalf of another user")

    return actor


async def ensure_tenant_manager(
    user_repo: UserRepository,
    actor_user_id: str,
    tenant_id: str,
) -> User:
    actor = await get_active_user(user_repo, actor_user_id)
    actor.ensure_tenant_user()

    if actor.tenant_id != tenant_id:
        raise DomainError("User does not belong to this tenant")

    return actor


async def ensure_platform_admin(user_repo: UserRepository, actor_user_id: str) -> User:
    actor = await get_active_user(user_repo, actor_user_id)
    actor.ensure_platform_admin()
    return actor
