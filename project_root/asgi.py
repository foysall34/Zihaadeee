import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_root.settings")

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from notification.middleware import JWTAuthMiddleware
# from audio_call.middleware import JWTAuthMiddleware

from notification.routing import websocket_urlpatterns as notification_ws
from chat.routing import websocket_urlpatterns as chat_ws
from message.routing import websocket_urlpatterns as message_chat
from group_message.routing import websocket_urlpatterns as grp_ws
from audio_call.routing import websocket_urlpatterns as audio_call

combined_websocket_routes = notification_ws + chat_ws  + message_chat + grp_ws + audio_call

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(combined_websocket_routes)
    ),
})
