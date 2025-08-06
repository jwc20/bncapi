from ninja import NinjaAPI
from knoxtokens.auth import TokenAuthentication

from users.api import user_router, auth_router

api = NinjaAPI(auth=TokenAuthentication())

api.add_router("/users", user_router)
api.add_router("/auth", auth_router)
