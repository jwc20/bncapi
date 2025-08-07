from django.contrib.auth import get_user_model
from django.db import IntegrityError
from ninja import Router, Schema
from ninja.errors import HttpError
from typing import List
from datetime import datetime
from knoxtokens.auth import TokenAuthentication
from django.contrib.auth import authenticate

from .models import Room

User = get_user_model()

import logging

logger = logging.getLogger(__name__)

game_router = Router(tags=["Games"])


class RoomSchema(Schema):
    name: str


# TODO: add auth
# TODO: add schemas


@game_router.get("/rooms", response=list[RoomSchema])
def list_rooms(request, *args, **kwargs):

    # user = authenticate(request)
    # if user is None:
    #     raise HttpError(401, "Unauthorized")

    return [
        {
            "name": room.name,
        }
        for room in Room.objects.all()
    ]


@game_router.post("/rooms", response=RoomSchema, summary="Create a new room")
def create_room(request, data: RoomSchema):
    try:
        room = Room.objects.create(name=data.name)
        return {
            "name": room.name,
        }
    except IntegrityError:
        raise HttpError(400, "Room with this name already exists")
    except Exception as e:
        logger.error(f"Room creation error: {e}")
        raise HttpError(400, "Room creation failed")


@game_router.get("/rooms/{room_id}", response=RoomSchema, summary="Get room by ID")
def get_room(request, room_id: int):
    try:
        room = Room.objects.get(id=room_id)
        return {
            "name": room.name,
        }
    except Room.DoesNotExist:
        raise HttpError(404, "Room not found")
    except Exception as e:
        logger.error(f"Room retrieval error: {e}")
        raise HttpError(400, "Room retrieval failed")
