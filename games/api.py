from django.contrib.auth import get_user_model
from django.db import IntegrityError
from ninja import Router, Schema
from ninja.errors import HttpError
from .models import Room

User = get_user_model()

import logging

logger = logging.getLogger(__name__)

game_router = Router(tags=["Games"])


class RoomSchema(Schema):
    id: int
    name: str
    game_type: int
    code_length: int | None
    num_of_colors: int | None
    num_of_guesses: int | None
    secret_code: str | None


class CreateRoomRequest(Schema):
    name: str
    game_type: int
    code_length: int | None = 4
    num_of_colors: int | None = 6
    num_of_guesses: int | None = 10
    secret_code: str | None


class CreateRandomSingleplayerRoomRequest(Schema):
    code_length: int | None = 4
    num_of_colors: int | None = 6
    num_of_guesses: int | None = 10
    game_type: int = 0


class CheckBullsCowsRequest(Schema):
    room_id: int
    guess: str


class CheckBullsCowsResponse(Schema):
    bulls: int
    cows: int


@game_router.get("/rooms", response=list[RoomSchema], summary="List all rooms")
def list_rooms(request):
    return [
        {
            "id": room.id,
            "name": room.name,
            "game_type": room.game_type,
            "code_length": room.code_length,
            "num_of_colors": room.num_of_colors,
            "num_of_guesses": room.num_of_guesses,
            "secret_code": room.secret_code,
        }
        for room in Room.objects.all().order_by("id").reverse()
    ]


@game_router.post("/rooms", response=RoomSchema, summary="Create a new room")
def create_room(request, data: CreateRoomRequest):
    from bncpy.bnc.utils import get_random_number

    validated_data = data.dict()
    validated_data["secret_code"] = get_random_number(
        length=validated_data["code_length"],
        max_value=validated_data["num_of_colors"],
    )
    try:
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
    except Exception as e:
        logger.error(f"Room creation error: {e}")
        raise HttpError(400, "Room creation failed")


@game_router.get("/rooms/{room_id}", response=RoomSchema, summary="Get room by ID")
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
def create_random_singleplayer_room(request, data: CreateRandomSingleplayerRoomRequest):
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
        return RoomSchema(id=room.id, name=room.name, game_type=room.game_type)
    except IntegrityError:
        raise HttpError(400, "Room with this name already exists")
    except Exception as e:
        logger.error(f"Room creation error: {e}")
        raise HttpError(400, "Room creation failed")


# deprecated
@game_router.post(
    "/check",
    response=CheckBullsCowsResponse,
    summary="Check guess for bulls and cows",
    deprecated=True,
)
def check_game(request, data: CheckBullsCowsRequest):
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
        return CheckBullsCowsResponse(bulls=bulls, cows=cows)
    except Exception as e:
        logger.error(f"Game check error: {e}")
        raise HttpError(400, "Game check failed")
