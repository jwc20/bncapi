from ninja import ModelSchema
from .models import Room


class RoomSchema(ModelSchema):
    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "game_type",
            "code_length",
            "num_of_colors",
            "num_of_guesses",
            "secret_code",
        ]


class CreateRoomSchema(ModelSchema):
    class Meta:
        model = Room
        fields = [
            "name",
            "game_type",
            "code_length",
            "num_of_colors",
            "num_of_guesses",
            "created_by",
        ]
