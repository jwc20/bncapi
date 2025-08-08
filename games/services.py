# from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from .models import Room


class GameService:
    @staticmethod
    @database_sync_to_async
    def handle_move(room_id, payload, user=None):
        try:
            room = Room.objects.get(id=room_id)
            action = payload.get("action")

            if action == "submit_guess":
                return GameService._handle_guess(room, payload.get("guess"), user)
            elif action == "reset_game":
                return GameService._reset_game(room)
            elif action == "join_room":
                return GameService._join_room(room, user)
            elif action == "leave_room":
                return GameService._leave_room(room, user)
            else:
                return {"error": "Unknown action"}

        except Room.DoesNotExist:
            return {"error": "Room not found"}
        except Exception as e:
            return {"error": str(e)}


    # def _validate_guess(guess, secret_code):
    #     from bncpy.bnc.utils import validate_code_input

    #     guess_list = validate_code_input(guess, room.code_length, room.num_of_colors)
    #     secret_code_list = validate_code_input(
    #         secret_code, room.code_length, room.num_of_colors
    #     )
    #     return

    @staticmethod
    def _handle_guess(room, guess, user=None):
        state = room.game_state
        if state.get("gameOver", False):
            return {**state, "error": "Game is already over"}

        if not guess or len(guess) != room.code_length:
            return {**state, "error": f"Guess must be {room.code_length} digits"}

        bulls, cows = GameService._calculate_feedback(guess, room.secret_code)

        # add to history
        guess_entry = {
            "guess": guess,
            "bulls": bulls,
            "cows": cows,
            "player": user.username if user else "Anonymous",
        }


        # TODO use game class instead to handle state
        state["guesses"].append(guess_entry)        
        state["currentRow"] += 1
        state["remainingGuesses"] = room.num_of_guesses - state["currentRow"]
        
        if bulls == room.code_length:
            state["gameOver"] = True
            state["gameWon"] = True
            state["secretCode"] = room.secret_code
        elif state["currentRow"] >= room.num_of_guesses:
            state["gameOver"] = True
            state["gameWon"] = False
            state["secretCode"] = room.secret_code

        
        room.game_state = state
        room.save()

        return state

    @staticmethod
    def _calculate_feedback(guess, secret):
        from bncpy.bnc.utils import calculate_bulls_and_cows

        bulls, cows = calculate_bulls_and_cows(guess, secret)
        return bulls, cows

    @staticmethod
    def _reset_game(room):
        # from bnc.utils import get_random_number
        from bncpy.bnc.utils import get_random_number

        # room.secret_code = get_random_number(
        #     number=room.code_length, maximum=room.num_of_colors
        # )

        room.game_state = {
            "guesses": [],
            "currentRow": 0,
            "gameOver": False,
            "gameWon": False,
            "remainingGuesses": room.num_of_guesses,
            # "secretCode": None,
            "players": room.game_state.get("players", []),
        }
        room.save()

        return room.game_state

    @staticmethod
    def _join_room(room, user):
        if user and user.is_authenticated:
            room.active_users.add(user)
            state = room.game_state
            players = state.get("players", [])
            username = user.username
            if username not in players:
                players.append(username)
            state["players"] = players
            room.game_state = state
            room.save()
        return room.game_state

    @staticmethod
    def _leave_room(room, user):
        if user and user.is_authenticated:
            room.active_users.remove(user)
            state = room.game_state
            players = state.get("players", [])
            username = user.username
            if username in players:
                players.remove(username)
            state["players"] = players
            room.game_state = state
            room.save()
        return room.game_state
