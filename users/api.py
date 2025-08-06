from django.contrib.auth import get_user_model
from django.db import IntegrityError
from ninja import Router, Schema
from ninja.errors import HttpError
from typing import List

from .utils import CustomerAccountHandler
from pydantic import EmailStr

User = get_user_model()

import logging

logger = logging.getLogger(__name__)


class UserSchema(Schema):
    email: EmailStr


class UserCreate(UserSchema):
    username: str
    password: str


class UserLogin(UserSchema):
    password: str


class UserResponse(Schema):
    id: int
    email: str
    username: str


class AuthResponse(Schema):
    token: str
    expiry: str


class MeResponse(Schema):
    id: int
    email: str
    username: str


user_router = Router(tags=["Users"], auth=None)
auth_router = Router(tags=["Authentication"], auth=None)


@user_router.get("/me", response=MeResponse, summary="Get current user")
def me(request):
    user = request.user
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
    }


@user_router.get("/", response=List[UserResponse], summary="List all users")
def list_users(request):
    return [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }
        for user in User.objects.all()
    ]


@user_router.get("/{user_id}", response=UserResponse, summary="Get user by ID")
def get_user(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }
    except User.DoesNotExist:
        raise HttpError(404, "User not found")


@auth_router.post("/login", response=AuthResponse, summary="Login user")
def login(request, data: UserLogin):
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
        logger.error(f"Login error: {e}")
        raise HttpError(400, "Invalid email or password")


@auth_router.post("/signup", response=AuthResponse, summary="Register user")
def signup(request, data: UserCreate):
    try:
        validated_data = data.dict()
        user, token_info = CustomerAccountHandler(**validated_data).email_signup()
        token = token_info["token_value"]
        expiry = token_info["expiry"]

        return {
            "token": token,
            "expiry": expiry,
        }
    except IntegrityError:
        raise HttpError(400, "User with this email or username already exists")
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HttpError(400, "Registration failed")
