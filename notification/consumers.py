import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope.get("user")
        print(f"[DEBUG CONNECT] Scope user = {user}")

        if user.is_anonymous:
            print("[DEBUG CONNECT BLOCKED] Anonymous user detected.")
            await self.close()
            return

        self.group_name = f"notifications_{user.id}"
        print(f"[DEBUG CONNECT SUCCESS] Group created = {self.group_name}")

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        print(f"[DEBUG GROUP ADD] Channel added: {self.channel_name}")

        await self.accept()
        print("[DEBUG ACCEPT] WebSocket connection accepted.")

    async def disconnect(self, close_code):
        print(f"[DEBUG DISCONNECT] Code = {close_code}")

        if hasattr(self, "group_name"):
            print(f"[DEBUG GROUP DISCARD] Removing {self.channel_name} from {self.group_name}")
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        else:
            print("[DEBUG DISCONNECT WARNING] group_name does not exist (connect failed earlier).")

    async def send_notification(self, event):
        print(f"[DEBUG EVENT RECEIVED] Event = {event}")

        data = event.get("data")
        if not data:
            print("[DEBUG ERROR] Event has no 'data' key!")
            return

        try:
            await self.send(text_data=json.dumps(data))
            print(f"[DEBUG SEND OK] Notification sent: {data}")
        except Exception as e:
            print(f"[DEBUG SEND ERROR] {e}")
