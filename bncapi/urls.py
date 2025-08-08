from django.contrib import admin
from django.urls import path, include
from games.routing import websocket_urlpatterns as games_ws
from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]

urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
urlpatterns += [*games_ws]
