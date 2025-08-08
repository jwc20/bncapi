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

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # must use database_sync_to_async for database operations for async
        self.room = await database_sync_to_async(Room.objects.get)(id=self.room_id)
        print(self.room)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None):
        data = json.loads(text_data)
        event_type = data.get("type")
        payload = data.get("payload", {})

        if event_type == "make_move":
            game_state = await GameService.handle_move(self.room_id, payload)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "game_update",
                    "state": game_state,
                },
            )

    async def game_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "update",
                    "state": event["state"],
                }
            )
        )
