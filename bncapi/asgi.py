import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import URLRouter

# from games.api import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bncapi.settings")

django_asgi_app = get_asgi_application()

import games.routing

from games.middleware import TokenAuthMiddlewareStack
from games.consumers import GameConsumer

# from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(games.routing.websocket_urlpatterns),
            ),
        ),
    }
)
