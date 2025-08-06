from django.contrib import admin
from django.urls import path
from ninja_extra import NinjaExtraAPI

from knoxtokens.auth import TokenAuthentication
from users.api import UserAPI

api = NinjaExtraAPI(
    openapi_extra={
        "info": {
            "title": "bncapi",
            "description": "this is the bncapi",
            "public": True,
            # "version": "1.0.0",
        }
    },
    auth=TokenAuthentication(),
)
api.register_controllers(UserAPI)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
