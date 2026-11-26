import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django first
django_asgi_app = get_asgi_application()

# Import Channels routing and consumers after initialization
from channels.routing import ProtocolTypeRouter, URLRouter
from chats.routing import websocket_urlpatterns
from chats.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})