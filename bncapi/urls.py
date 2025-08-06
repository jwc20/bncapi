from django.contrib import admin
from django.urls import path
from ninja_extra import NinjaExtraAPI

from knoxtokens.auth import TokenAuthentication
from users.api import UserAPI

api = NinjaExtraAPI(auth=TokenAuthentication())
api.register_controllers(UserAPI)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
