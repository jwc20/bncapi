from django.contrib import admin
from django.urls import path

# from ninja import NinjaAPI
from ninja_extra import NinjaExtraAPI, api_controller, http_get

from knoxtokens.auth import TokenAuthentication
from users.api import UserAPI

# api = NinjaExtraAPI()
api = NinjaExtraAPI(auth=TokenAuthentication())


# Class-based controller example
@api_controller("/math", tags=["Math"])
class MathController:
    @http_get("/add")
    def add(self, a: int, b: int):
        """Add two numbers"""
        return {"result": a + b}

    @http_get("/multiply")
    def multiply(self, a: int, b: int):
        """Multiply two numbers"""
        return {"result": a * b}


api.register_controllers(MathController)
api.register_controllers(UserAPI)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
