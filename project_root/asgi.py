import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_root.settings")

# IMPORTANT: Load Django first (no routing before this line)
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from notification.middleware import JWTAuthMiddleware

# NOW safe to import routing
from notification.routing import websocket_urlpatterns as notification_ws
from chat.routing import websocket_urlpatterns as chat_ws
from message.routing import websocket_urlpatterns as message_chat

combined_websocket_routes = notification_ws + chat_ws  + message_chat

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(combined_websocket_routes)
    ),
})
