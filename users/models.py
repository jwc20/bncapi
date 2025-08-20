# import uuid
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email, ValidationError
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        if not password:
            raise ValueError("The given password must be set")

        email = email.lower()
        username = username.lower()
        try:
            validate_email(email)
        except ValidationError as e:
            raise ValueError(f"Invalid email address: {e}")

        return User.objects.create(
            email=email,
            username=username,
            password=make_password(password),
            **extra_fields,
        )

    def create_superuser(self, login_id, password=None):
        extra_fields = {
            "is_superuser": True,
            "is_staff": True,
        }
        return self.create_user(login_id, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True, max_length=100, db_index=True)
    disabled = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(auto_now=True)
    password_changed_at = models.DateTimeField(default=timezone.now)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self) -> str:
        return super().__str__()