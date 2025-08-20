from ninja import ModelSchema, Schema
from django.contrib.auth import get_user_model
from pydantic import EmailStr
from datetime import datetime

User = get_user_model()


class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = ["id", "email", "username"]


class UserResponse(UserSchema):
    pass


class MeResponse(UserSchema):
    pass


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
