from django.urls import re_path

from .consumers import ChatConsumer

# формируем паттерн для url для ччата
websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>[^/]+)/$", ChatConsumer.as_asgi()),
]
