from ninja import NinjaAPI, Swagger
from knoxtokens.auth import TokenAuthentication

from users.api import user_router, auth_router
from games.api import game_router

api = NinjaAPI(
    auth=TokenAuthentication(), docs=Swagger(settings={"persistAuthorization": True})
)

api.add_router("/users", user_router)
api.add_router("/auth", auth_router)
api.add_router("/games", game_router)
