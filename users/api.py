from django.contrib.auth import get_user_model
from django.db import IntegrityError
from ninja import Router
from ninja.errors import HttpError
from typing import List
from actstream import action
import json

from .utils import CustomerAccountHandler
from knoxtokens.models import KnoxToken
from bncapi.settings import TOKEN_KEY_LENGTH

from .schemas import (
    UserSchema,
    MeResponse,
    AuthResponse,
    UserCreate,
    UserLogin,
)

User = get_user_model()

import logging

logger = logging.getLogger(__name__)


user_router = Router(tags=["Users"])
auth_router = Router(tags=["Authentication"], auth=None)


@user_router.get("/me", response=MeResponse, summary="Get current user")
def me(request):
    user, token = request.auth
    if not user or not user.is_authenticated:
        raise HttpError(401, "Unauthorized")
    return MeResponse.from_orm(user)


@user_router.get("/", response=List[UserSchema], summary="List all users")
def list_users(request):
    return [UserSchema.from_orm(user) for user in User.objects.all()]


@user_router.get("/{user_id}", response=UserSchema, summary="Get user by ID")
def get_user(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
        return UserSchema.from_orm(user)
    except User.DoesNotExist:
        raise HttpError(404, "User not found")


@auth_router.post("/login", response=AuthResponse, summary="Login user")
def login(request, data: UserLogin):
    try:
        validated_data = data.dict()
        user, token_info = CustomerAccountHandler(**validated_data).login()
        token = token_info["token_value"]
        expiry = token_info["expiry"]

        knox_token = KnoxToken.objects.select_related("user").get(
            token_key=token[:TOKEN_KEY_LENGTH]
        )
        user_logged_in = knox_token.user

        user_dict = {
            "id": user_logged_in.id,
            "email": user_logged_in.email,
            "username": user_logged_in.username,
        }

        user_json = json.dumps(user_dict)
        request.session["user"] = user_json

        action.send(
            user_logged_in,
            verb="logged_in",
            action_object=user_logged_in,
            data=user_dict,
        )

        return AuthResponse(
            token=token,
            username=user.username,
            expiry=expiry,
        )

    except KnoxToken.DoesNotExist:
        logger.error("Invalid token during login")
        raise HttpError(400, "Invalid token")
    except User.DoesNotExist:
        logger.error("User not found during login")
        raise HttpError(400, "Invalid credentials")
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

        user_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
        }

        user_json = json.dumps(user_dict)
        request.session["user"] = user_json

        action.send(user, verb="registered", action_object=user, data=user_dict)

        return AuthResponse(
            token=token,
            username=user.username,
            expiry=expiry,
        )
    except IntegrityError:
        raise HttpError(400, "User with this email or username already exists")
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HttpError(400, "Registration failed")
