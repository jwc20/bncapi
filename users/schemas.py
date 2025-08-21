from actstream.models import Action
from ninja import ModelSchema, Schema, FilterSchema
from django.contrib.auth import get_user_model
from pydantic import EmailStr
from datetime import datetime

User = get_user_model()


class ActivityFilterSchema(FilterSchema):
    actor_object_id: int | None = None
    verb: str | None = None
    action_object_object_id: int | None = None
    timestamp: datetime | None = None


class ActivityResponseSchema(Schema):
    id: int
    verb: str
    timestamp: datetime
    actor_object_id: int | None
    action_object_object_id: int | None
    target_object_id: int | None


class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = ["id", "email", "username"]


class UserResponse(UserSchema):
    pass


class MeResponse(UserSchema):
    activities: list[ActivityResponseSchema]

    class Meta:
        fields = UserSchema.Meta.fields + ["activities"]


class UserCreate(Schema):
    email: EmailStr
    username: str
    password: str


class UserLogin(Schema):
    email: EmailStr
    password: str


class AuthResponse(Schema):
    token: str
    username: str
    expiry: datetime
