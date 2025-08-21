from typing import Optional
from enum import Enum

from actstream import action
from actstream.models import Action
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from asgiref.sync import async_to_sync

from bncapi.settings import TOKEN_KEY_LENGTH
from knoxtokens.models import KnoxToken
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class UserAction(Enum):
    JOINED_ROOM = "joined_room"
    LEFT_ROOM = "left_room"
    WON_GAME = "won_game"
    GUESSED_CODE = "guessed_code"


def _validate_token(token: str) -> bool:
    if not token or len(token) < TOKEN_KEY_LENGTH:
        logger.warning("Invalid token format: token is None or too short")
        return False
    return True


def _get_action_description(user_action: str, room, user) -> Optional[str]:
    descriptions = {
        UserAction.WON_GAME.value: f"Room {room.id} won by {user.username}",
        UserAction.JOINED_ROOM.value: f"{user.username} joined room {room.id}",
        UserAction.LEFT_ROOM.value: f"{user.username} left room {room.id}",
        UserAction.GUESSED_CODE.value: f"{user.username} guessed code in room {room.id}",
    }
    return descriptions.get(user_action)


async def _authenticate_user_async(token: str) -> Optional[User]:
    if not _validate_token(token):
        return None

    try:
        token_key = token[:TOKEN_KEY_LENGTH]
        token_obj = await database_sync_to_async(
            KnoxToken.objects.select_related("user").get
        )(token_key=token_key)

        if not token_obj.user:
            logger.warning(
                f"Knox token exists but user not found for token_key: {token_key[:8]}..."
            )
            return None

        return token_obj.user

    except KnoxToken.DoesNotExist:
        logger.debug("Anonymous connection attempted - token not found")
        return None
    except Exception as e:
        logger.error(
            f"Error authenticating user: {type(e).__name__}: {e}",
            exc_info=True,
        )
        return None


def _authenticate_user_sync(token: str) -> Optional[User]:
    if not _validate_token(token):
        return None

    try:
        token_key = token[:TOKEN_KEY_LENGTH]
        token_obj = KnoxToken.objects.select_related("user").get(token_key=token_key)

        if not token_obj.user:
            logger.warning(
                f"Knox token exists but user not found for token_key: {token_key[:8]}..."
            )
            return None

        return token_obj.user

    except KnoxToken.DoesNotExist:
        logger.debug("Anonymous connection attempted - token not found")
        return None
    except Exception as e:
        logger.error(
            f"Error authenticating user: {type(e).__name__}: {e}",
            exc_info=True,
        )
        return None


async def _send_action_async(
    user: User, user_action: str, room, description: Optional[str] = None
) -> bool:
    try:
        await database_sync_to_async(action.send)(
            user,
            verb=user_action,
            action_object=room,
            description=description,
        )
        logger.debug(
            f"Action '{user_action}' sent for user {user.id} in room {room.id}"
        )
        return True
    except Exception as e:
        logger.error(
            f"Error sending action '{user_action}': {type(e).__name__}: {e}",
            exc_info=True,
        )
        return False


def _send_action_sync(
    user: User, user_action: str, room, description: Optional[str] = None
) -> bool:
    try:
        action.send(
            user,
            verb=user_action,
            target=room,
            description=description,
        )
        logger.debug(
            f"Action '{user_action}' sent for user {user.id} in room {room.id}"
        )
        return True
    except Exception as e:
        logger.error(
            f"Error sending action '{user_action}': {type(e).__name__}: {e}",
            exc_info=True,
        )
        return False


async def log_user_action(token: str, room, user_action: str) -> bool:
    if not room or not user_action:
        logger.error("Invalid parameters: room or user_action is None")
        return False

    user = await _authenticate_user_async(token)
    if not user:
        return False

    description = _get_action_description(user_action, room, user)
    return await _send_action_async(user, user_action, room, description)
