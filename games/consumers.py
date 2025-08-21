from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .utils import log_user_action_async

User = get_user_model()

from .models import Room
from .services import GameService
import uuid
import json
import logging
from django.conf import settings
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

TOKEN_KEY_LENGTH = getattr(settings, "TOKEN_KEY_LENGTH", 8)
logger = logging.getLogger(__name__)


class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = None
        self.room_group_name = None
        self.room = None
        self.token = None

    async def connect(self):
        try:
            self.room_id = int(self.scope["url_route"]["kwargs"]["room_id"])
        except (KeyError, ValueError, TypeError):
            logger.error(f"Invalid room_id in URL route")
            await self.close(code=4004)
            return

        self.room_group_name = f"game_{self.room_id}"

        query_string = self.scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        self.token = query_params.get("token", [None])[0][:TOKEN_KEY_LENGTH]

        if not self.token or len(self.token) < TOKEN_KEY_LENGTH:
            self.token = str(uuid.uuid4())
            logger.info(f"Generated new token for connection: {self.token[:8]}...")

        try:
            self.room = await database_sync_to_async(Room.objects.select_related().get)(
                id=self.room_id
            )

            if not self.room.game_state:
                await database_sync_to_async(self.room.initialize_game)()
                logger.info(f"Initialized game state for room {self.room_id}")

            game_state = await GameService.handle_move(
                self.room_id,
                {
                    "action": "join_room",
                    "token": self.token,
                },
                {"token": self.token},
            )

            if "error" in game_state:
                logger.error(
                    f"GameService error for room {self.room_id}, "
                    f"token {self.token[:8]}...: {game_state.get('error')}"
                )
                await self.close(code=4000)
                return

            await self.accept()

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            logger.info(f"Player {self.token[:8]}... connected to room {self.room_id}")

            await log_user_action_async(
                token=self.token, room=self.room, user_action="joined_room"
            )

            await self.send(
                text_data=json.dumps({"type": "update", "state": game_state})
            )

        except Room.DoesNotExist:
            logger.warning(f"Room {self.room_id} not found")
            await self.close(code=4004)
        except Exception as e:
            logger.error(
                f"Unexpected error connecting to room {self.room_id}: "
                f"{type(e).__name__}: {e}",
                exc_info=True,
            )
            await self.close(code=1011)

    async def disconnect(self, close_code):
        if self.room:
            logger.info(f"Player {self.token} disconnecting from room {self.room_id}")
            await GameService.handle_move(
                self.room_id,
                {
                    "action": "leave_room",
                    "token": self.token,
                },
                {"token": self.token},
            )

            await log_user_action_async(
                token=self.token, room=self.room, user_action="left_room"
            )

        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data=None):
        try:
            data = json.loads(text_data)
            event_type = data.get("type")
            payload = data.get("payload", {})

            if event_type == "make_move":
                payload["token"] = self.token

                game_state = await GameService.handle_move(
                    self.room_id,
                    payload,
                    {"token": self.token},
                )

                await log_user_action_async(
                    token=self.token,
                    room=self.room,
                    user_action="guessed_code",
                    data=payload,
                )

                if game_state.get("game_won"):
                    await log_user_action_async(
                        token=self.token, room=self.room, user_action="won_game"
                    )

                if "error" in game_state:
                    await self.send(
                        text_data=json.dumps(
                            {"type": "error", "message": game_state["error"]}
                        )
                    )
                    return

                # broadcast updated state to all players in room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_update",
                        "state": game_state,
                    },
                )
            elif event_type == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))

            # TODO: add chat
            elif event_type == "chat_message":
                pass
            else:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "error",
                            "message": f"Unknown event type: {event_type}",
                        }
                    )
                )

        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps({"type": "error", "message": "Invalid JSON"})
            )
        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def game_update(self, event):
        # use from the client
        await self.send(
            text_data=json.dumps({"type": "update", "state": event["state"]})
        )
