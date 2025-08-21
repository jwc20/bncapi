from actstream import action
from actstream.models import Action
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from bncapi.settings import TOKEN_KEY_LENGTH
from knoxtokens.models import KnoxToken
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

actions_to_send_directly = ["joined_room", "left_room", "won_game", "guessed_code"]


async def log_user_action(token: str, room, user_action: str) -> bool:
    user = None

    try:
        token_obj = await database_sync_to_async(
            KnoxToken.objects.select_related("user").get
        )(token_key=token[:TOKEN_KEY_LENGTH])
        user = token_obj.user

        if not user:
            logger.warning("Knox token exists but user not found")
            return False

    except KnoxToken.DoesNotExist:
        logger.debug("Anonymous connection attempted")
        return False
    except Exception as e:
        logger.error(
            f"Error authenticating user for action logging: {type(e).__name__}: {e}",
            exc_info=True,
        )
        return False

    description = None
    if "won" in user_action:
        description = f"Room {room.id} won by {user.username}"

    action_sent = False
    for keyword in actions_to_send_directly:
        if keyword in user_action:
            try:
                await database_sync_to_async(action.send)(
                    user,
                    verb=user_action,
                    action_object=room,
                    description=description,
                )
                action_sent = True
                break
            except Exception as e:
                logger.error(
                    f"Error sending direct action '{user_action}': {type(e).__name__}: {e}",
                    exc_info=True,
                )
                return False

    try:
        action_exists = await database_sync_to_async(
            Action.objects.filter(
                actor_object_id=user.id,
                verb=user_action,
                action_object_object_id=room.id,
            ).exists
        )()

        if not action_exists and not action_sent:
            await database_sync_to_async(action.send)(
                user,
                verb=user_action,
                action_object=room,
                description=description,
            )
            logger.debug(f"Action '{user_action}' logged for user {user.id}")

    except Exception as e:
        logger.error(
            f"Error checking/logging action '{user_action}': {type(e).__name__}: {e}",
            exc_info=True,
        )
        return False

    return True
