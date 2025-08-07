from urllib.parse import parse_qs

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from channels.auth import AuthMiddleware
from channels.db import database_sync_to_async
from channels.sessions import CookieMiddleware, SessionMiddleware
from knoxtokens.auth import TokenAuthentication  # Changed from JWT

from users.utils import CustomerAccountHandler

User = get_user_model()


# @database_sync_to_async
# def get_user(scope):
#     close_old_connections()
#     query_string = parse_qs(scope["query_string"].decode())
#     token = query_string.get("token")
#
#     # if not token:
#     #     return AnonymousUser()
#
#     try:
#         user, token = TokenAuthentication().authenticate(token[0].encode())
#
#         if not user or not user.is_active:
#             return AnonymousUser()
#
#         return user
#
#     except Exception:
#         return AnonymousUser()

import logging

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user(scope):
    close_old_connections()
    query_string = parse_qs(scope["query_string"].decode())
    token = query_string.get("token")

    if not token:
        logger.warning(
            f"WebSocket connection attempt without token from {scope.get('client', ['unknown'])[0]}"
        )
        return AnonymousUser()

    try:
        knox_auth = TokenAuthentication()
        user, auth_token = knox_auth.authenticate(token[0].encode())

        if not user or not user.is_active:
            logger.warning(
                f"WebSocket connection attempt with invalid user from {scope.get('client', ['unknown'])[0]}"
            )
            return AnonymousUser()

        # Check token expiry (Knox handles this, but you can add custom logic)
        if auth_token.expiry and auth_token.expiry < timezone.now():
            logger.warning(
                f"WebSocket connection attempt with expired token for user {user.id}"
            )
            return AnonymousUser()

        logger.info(f"Successful WebSocket authentication for user {user.id}")
        return user

    except Exception as e:
        logger.error(f"WebSocket authentication error: {str(e)}")
        return AnonymousUser()


class TokenAuthMiddleware(AuthMiddleware):
    async def resolve_scope(self, scope):
        scope["user"]._wrapped = await get_user(scope)


def TokenAuthMiddlewareStack(inner):
    return CookieMiddleware(SessionMiddleware(TokenAuthMiddleware(inner)))
