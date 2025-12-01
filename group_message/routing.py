from django.urls import path
from .consumers import GroupChatConsumer

websocket_urlpatterns = [
    path("ws/group/", GroupChatConsumer.as_asgi()),
]
