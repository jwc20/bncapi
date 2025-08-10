from channels.db import database_sync_to_async
from .models import Room
from bncpy.bnc import GameState, GameConfig
from django.contrib.auth import get_user_model


class GameService:
    @staticmethod
    @database_sync_to_async
    def handle_move(room_id, payload, player_info):
        try:
            room = Room.objects.get(id=room_id)
            action = payload.get("action")

            state = GameService._load_state(room)

            if action == "submit_guess":
                result = GameService._handle_guess(
                    state, room, payload.get("guess"), player_info
                )
            elif action == "reset_game":
                result = GameService._reset_game(state, room)
            elif action == "join_room":
                result = GameService._join_room(state, room, player_info)
            elif action == "leave_room":
                result = GameService._leave_room(state, room, player_info)
            elif action == "start_game":
                result = GameService._start_game(state, room)
            else:
                return {"error": "Unknown action"}

            return result

        except Room.DoesNotExist:
            return {"error": "Room not found"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def _load_state(room) -> GameState:
        config = GameConfig(
            code_length=room.code_length,
            num_of_colors=room.num_of_colors,
            num_of_guesses=room.num_of_guesses,
            secret_code=room.secret_code,
        )

        if room.game_state:
            return GameState.from_dict(room.game_state, config)
        else:
            # Create new state if none exists
            return GameState(config=config)

    @staticmethod
    def _save_state(state: GameState, room) -> dict:
        room.secret_code = state.config.secret_code

        state_dict = state.to_dict()
        room.game_state = state_dict
        room.save()

        return state_dict

    @staticmethod
    def _handle_guess(state: GameState, room, guess: str, player_info=None) -> dict:
        player_token = player_info.get("token") if player_info else "Anonymous"
        result = state.submit_guess(player_token, guess)

        if "error" in result:
            return result

        return GameService._save_state(state, room)

    @staticmethod
    def _reset_game(state: GameState, room) -> dict:
        state.reset()
        return GameService._save_state(state, room)

    @staticmethod
    def _start_game(state: GameState, room) -> dict:
        if not state.config.secret_code:
            state.config.secret_code = state.config.generate_secret_code()

        state.game_started = True
        return GameService._save_state(state, room)

    @staticmethod
    def _join_room(state: GameState, room, player_info) -> dict:
        if player_info and player_info.get("token"):
            # Use the token as the player identifier
            player_token = player_info["token"]
            
            # Add player to the game state using the token
            state.add_player(player_token)
            
            # Note: We're not using room.active_users since we're not using Django auth
            # But you could create a custom field to track connected players if needed

        return GameService._save_state(state, room)

    @staticmethod
    def _leave_room(state: GameState, room, player_info) -> dict:
        if player_info and player_info.get("token"):
            # Use the token as the player identifier
            player_token = player_info["token"]
            
            # Remove player from the game state using the token
            state.remove_player(player_token)

        return GameService._save_state(state, room)
