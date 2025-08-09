# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room
from .services import GameService


class GameConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_id = None
        self.room_group_name = None
        self.room = None
        self.user = None

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        print(self.room_id)
        self.room_group_name = f"game_{self.room_id}"
        # self.user = self.scope.get("user")

        try:
            self.room = await database_sync_to_async(Room.objects.get)(id=self.room_id)

            if not self.room.game_state:
                await database_sync_to_async(self.room.initialize_game)()

            if self.user and self.user.is_authenticated:
                # game_state = await GameService.handle_move(
                #     self.room_id, {"action": "join_room"}, self.user
                # )
                pass
            else:
                game_state = await database_sync_to_async(
                    lambda: self.room.game_state
                )()

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            await self.send(
                text_data=json.dumps({"type": "update", "state": game_state})
            )

        except Room.DoesNotExist:
            await self.close(code=4004)

    async def disconnect(self, close_code):
        if self.user and self.user.is_authenticated and self.room:
            await GameService.handle_move(
                self.room_id, {"action": "leave_room"}, self.user
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

                game_state = await GameService.handle_move(
                    self.room_id, payload, self.user
                )

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

        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps({"type": "error", "message": "Invalid JSON"})
            )
        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    async def game_update(self, event):
        """Send game update to WebSocket"""
        await self.send(
            text_data=json.dumps({"type": "update", "state": event["state"]})
        )
