import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

User = get_user_model()


@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token.get("user_id")
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope["headers"])
        
        token = None

        # WebSocket sends token through "Sec-WebSocket-Protocol" or query param
        if b"sec-websocket-protocol" in headers:
            token = headers[b"sec-websocket-protocol"].decode()

        # Fallback: Token in Query String: ws://host/ws/chat/?token=xxx
        if not token and "query_string" in scope:
            query = scope["query_string"].decode()
            if "token=" in query:
                token = query.split("token=")[-1]

        # If no token
        if not token:
            scope["user"] = None
            return await super().__call__(scope, receive, send)

        # Decode JWT
        try:
            validated_data = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
        except Exception:
            scope["user"] = None
            return await super().__call__(scope, receive, send)

        # Attach user
        scope["user"] = await get_user(validated_data)

        return await super().__call__(scope, receive, send)
