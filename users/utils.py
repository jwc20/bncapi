import logging

# from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction, IntegrityError
from django.utils import timezone

from knoxtokens.utils import CreateToken
from .models import User


# import random
# from knoxtokens.auth import TokenAuthentication


class CustomerAccountHandler:

    def __init__(self, **kwargs):
        # self.user = kwargs.get("user", None)
        self.email = kwargs.get("email", None)
        self.password = kwargs.get("password", None)
        self.username = kwargs.get("username", None)

    def login(self):
        user = self._authenticate()
        token_value, expiry = CreateToken(user=user).create()
        return user, {"token_value": token_value, "expiry": expiry}

    def _authenticate(self):
        # Ensure email is lowercase for authentication
        email = self.email.lower() if self.email else None

        # TODO: authenticate using username
        data = {"email": email, "password": self.password}

        user = authenticate(
            username=email,
            password=self.password,
        )

        if not user:
            try:
                potential_user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise Exception("User does not exist")
            if potential_user.check_password(self.password):
                self.user = potential_user
                # self.recover_account()  # can raise RecoveryPeriodExpired exception
                return potential_user
            raise Exception("Incorrect password or email")
        else:
            User.objects.filter(id=user.id).update(
                last_login=timezone.now(),
            )
            return user

    @transaction.atomic
    def email_signup(self):
        try:
            user = User.objects.create_user(
                email=self.email,
                password=self.password,
            )
            return user
        except IntegrityError as e:
            logging.error(e)
            return
