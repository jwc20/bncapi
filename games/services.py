from asgiref.sync import sync_to_async
from .models import GameRoom

class GameService:
    @staticmethod
    @sync_to_async
    def handle_move(room_code, move_data):
        room = GameRoom.objects.get(code=room_code)
        
        state = room.state
        state["moves"].append(move_data)
        room.state = state
        room.save()

        return state
