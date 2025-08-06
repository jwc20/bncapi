from django.contrib.auth import get_user_model
from django.db import IntegrityError
from ninja import Schema
from ninja.errors import HttpError
from ninja_extra import (
    api_controller,
    route,
)

from .utils import CustomerAccountHandler

User = get_user_model()

import logging

logger = logging.getLogger(__name__)


class UserSchema(Schema):
    # username: str | None = None
    email: str


class UserCreate(UserSchema):
    password: str


class UserLogin(UserSchema):
    password: str


class UserResponse(Schema):
    id: int
    email: str
    # Add other fields you want to return
    # username: str | None = None


@api_controller(auth=None, permissions=[])
class UserAPI:
    @route.get("/me")
    def me(self, request):
        return request.user

    @route.get("/users")
    def users(self, request):
        return User.objects.all()

    @route.get("/users/{user_id}")
    def user(self, request, user_id):
        return User.objects.get(id=user_id)

    @route.post("/user/login")
    def login_email(self, request, data: UserLogin):
        print(data)
        print(request)
        try:
            validated_data = data.dict()
            user, token_info = CustomerAccountHandler(**validated_data).login()
            token = token_info["token_value"]
            expiry = token_info["expiry"]

            return {
                "token": token,
                "expiry": expiry,
            }
        except Exception as e:
            logging.error(e)
            raise HttpError(400, "Invalid email or password")

    @route.post("/user/signup", response=UserResponse)
    def signup(self, request, data: UserCreate):
        validated_data = data.dict()
        try:
            user = User.objects.create_user(
                email=validated_data["email"], password=validated_data["password"]
            )
        except IntegrityError as e:
            logging.error(e)
            raise HttpError(400, "User with this email already exists")

        return user
