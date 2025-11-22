import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return
        self.group_name = f"notifications_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Called by group_send above: "type": "send.notification" -> method name send_notification
    async def send_notification(self, event):
        data = event.get("data", {})
        # you can add server time or transform payload here
        await self.send_json({
            "type": "notification",
            "payload": data
        })

    # For consistency with dotted type (if you used "send.notification")
    async def send_notification(self, event):
        data = event.get("data", {})
        await self.send_json({"type":"notification", "payload": data})
