import json
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from ninja import Router, Schema
from ninja.errors import HttpError
from .models import Room
from .schemas import RoomSchema

User = get_user_model()

import logging

logger = logging.getLogger(__name__)
game_router = Router(tags=["Games"])


@game_router.get("/rooms", response=list[RoomSchema], summary="List all rooms")
def list_rooms(request):
    return [RoomSchema.from_orm(room) for room in Room.objects.all()]


@game_router.post("/rooms", response=RoomSchema, summary="Create a new room")
def create_room(request, data: RoomSchema):
    from bncpy.bnc.utils import get_random_number
    from actstream import action
    from django.core.exceptions import ValidationError
    from django.db import IntegrityError

    if not request.auth or len(request.auth) < 1:
        raise HttpError(401, "Authentication required")

    _user = request.auth[0]
    validated_data = data.dict()

    validated_data["secret_code"] = get_random_number(
        length=validated_data["code_length"],
        max_value=validated_data["num_of_colors"],
    )
    try:
        room = Room.objects.create(**validated_data)
        if hasattr(request, "session"):
            request.session["user"] = {
                "id": _user.id,
                "email": _user.email,
                "username": _user.username,
            }
        log_data = {
            "id": room.id,
            "name": room.name,
            "game_type": room.game_type,
        }
        action.send(_user, verb="created room", target=room, data=json.dumps(log_data))
        return RoomSchema.from_orm(room)
    except ValidationError as e:
        logger.error(f"Room creation validation error: {e}")
        raise HttpError(400, "Invalid room configuration")
    except IntegrityError as e:
        logger.error(f"Room creation integrity error: {e}")
        raise HttpError(409, "Room with this configuration already exists")
    except Exception as e:
        logger.error(f"Unexpected room creation error: {e}")
        raise HttpError(500, "Internal server error")


######################################################################################
## deprecated ########################################################################
######################################################################################


# deprecated
@game_router.get(
    "/rooms/{room_id}",
    response=RoomSchema,
    summary="Get room by ID",
    deprecated=True,
)
def get_room(request, room_id: int):
    try:
        room = Room.objects.get(id=room_id)
        return RoomSchema(
            id=room.id,
            name=room.name,
            game_type=room.game_type,
            code_length=room.code_length,
            num_of_colors=room.num_of_colors,
            num_of_guesses=room.num_of_guesses,
            secret_code=room.secret_code,
        )
    except Room.DoesNotExist:
        raise HttpError(404, "Room not found")
    except Exception as e:
        logger.error(f"Room retrieval error: {e}")
        raise HttpError(400, "Room retrieval failed")


# deprecated
@game_router.post(
    "/quick-play",
    response=RoomSchema,
    summary="Create a new singleplayer room with random secret code",
    deprecated=True,
)
def create_random_singleplayer_room(request, data):
    try:
        # from bnc.utils import get_random_number
        from bncpy.bnc.utils import get_random_number

        validated_data = data.dict()

        # generate random number as room name
        # validated_data["name"] = f"singleplayer_room_{}"

        validated_data["secret_code"] = get_random_number(
            length=validated_data["code_length"],
            max_value=validated_data["num_of_colors"],
        )
        room = Room.objects.create(**validated_data)
        return {
            "id": room.id,
            "name": room.name,
            "game_type": room.game_type,
            "code_length": room.code_length,
            "num_of_colors": room.num_of_colors,
            "num_of_guesses": room.num_of_guesses,
            "secret_code": room.secret_code,
        }
    except IntegrityError:
        raise HttpError(400, "Room with this name already exists")
    except Exception as e:
        logger.error(f"Room creation error: {e}")
        raise HttpError(400, "Room creation failed")


# deprecated
@game_router.post(
    "/check",
    summary="Check guess for bulls and cows",
    deprecated=True,
)
def check_game(request, data):
    # TODO: replace naive solution, use Game, Player, Board classes
    try:
        # from bnc.utils import calculate_bulls_and_cows
        from bncpy.bnc.utils import calculate_bulls_and_cows, validate_code_input

        validated_data = data.dict()

        room = Room.objects.get(id=validated_data["room_id"])
        _secret_code = room.secret_code

        _secret_code_list = validate_code_input(
            _secret_code, room.code_length, room.num_of_colors
        )
        _guess_list = validate_code_input(
            validated_data["guess"], room.code_length, room.num_of_colors
        )
        bulls, cows = calculate_bulls_and_cows(_secret_code_list, _guess_list)
        return {
            "bulls": bulls,
            "cows": cows,
        }
    except Exception as e:
        logger.error(f"Game check error: {e}")
        raise HttpError(400, "Game check failed")
