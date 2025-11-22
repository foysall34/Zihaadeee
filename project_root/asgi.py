

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import notification.routing as project_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            project_routing.websocket_urlpatterns
        )
    ),
})
