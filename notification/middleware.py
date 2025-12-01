import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

User = get_user_model()


@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token.get("user_id")
        print("🟢 USER ID from token:", user_id)
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        print("🔴 User does not exist in DB")
        return None


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):

        print("\n\n==============================")
        print("🔍 NEW WEBSOCKET REQUEST")
        print("==============================")

        print("📦 RAW QUERY_STRING:", scope.get("query_string"))
        print("📦 RAW HEADERS:", dict(scope["headers"]))

        headers = dict(scope["headers"])
        token = None

        # 1️⃣ Check Sec-WebSocket-Protocol Header
        if b"sec-websocket-protocol" in headers:
            token = headers[b"sec-websocket-protocol"].decode()
            print("🟢 Token found in header:", token)
        else:
            print("🔴 No token in Sec-WebSocket-Protocol header")

        # 2️⃣ Fallback: token from ?token= in query params
        if not token:
            qs = parse_qs(scope.get("query_string", b"").decode())
            print("📦 Parsed Query Params:", qs)

            token_list = qs.get("token")
            if token_list:
                token = token_list[0]
                print("🟢 Token found in query param:", token)
            else:
                print("🔴 No token in query params")

        # 3️⃣ If still missing
        if not token:
            print("❌ FINAL: NO TOKEN FOUND → Anonymous user")
            scope["user"] = None
            return await super().__call__(scope, receive, send)

        # 4️⃣ Decode JWT Token
        print("🔧 Decoding JWT token...")
        try:
            validated_data = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            print("🟢 JWT DECODE SUCCESS:", validated_data)
        except Exception as e:
            print("❌ JWT DECODE FAILED:", str(e))
            scope["user"] = None
            return await super().__call__(scope, receive, send)

        # 5️⃣ Attach user
        user = await get_user(validated_data)

        if user:
            print("🟢 AUTHENTICATED USER:", user.email if hasattr(user, "email") else user.id)
        else:
            print("🔴 NO USER ATTACHED → INVALID TOKEN")

        scope["user"] = user

        print("==============================\n")

        return await super().__call__(scope, receive, send)
