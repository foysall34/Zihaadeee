import jwt
from django.conf import settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser  # safe import inside

        query_params = parse_qs(scope["query_string"].decode())
        token = query_params.get("token", [None])[0]

        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = await self.get_user(payload["user_id"])
                scope["user"] = user
            except Exception as e:
                print("JWT ERROR:", e)
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        from django.contrib.auth.models import AnonymousUser
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()
