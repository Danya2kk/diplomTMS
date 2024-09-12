import os
import sys

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from .routing import websocket_urlpatterns

# Debugging lines
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socnet.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)

print(f"ASGI application loaded")
