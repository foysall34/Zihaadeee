import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()

class JWTAuthMiddleware:
    """
    Custom JWT authentication middleware for Django Channels.
    Extracts token from WebSocket query params: ?token=<JWT>
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return JWTAuthMiddlewareInstance(scope, self.inner)


class JWTAuthMiddlewareInstance:
    def __init__(self, scope, inner):
        self.scope = dict(scope)
        self.inner = inner

    async def __call__(self, receive, send):
        # Extract token from query string
        query_string = self.scope.get("query_string", b"").decode()

        token = None
        if "token=" in query_string:
            try:
                token = query_string.split("token=")[1].split("&")[0]
            except:
                token = None

        # Try to authenticate the user
        user = None
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("user_id")
                if user_id:
                    user = await get_user(user_id)
            except jwt.ExpiredSignatureError:
                print("JWT expired")
            except jwt.InvalidTokenError:
                print("Invalid JWT")

        # attach user or AnonymousUser
        self.scope["user"] = user if user else AnonymousUser()

        inner = self.inner(self.scope)
        return await inner(receive, send)


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


from django.contrib.auth.models import AnonymousUser
