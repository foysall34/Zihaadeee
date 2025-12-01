import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class CallSignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"call_{self.room_name}"

        # optional: enforce authentication
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        # join group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # leave group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Expected message JSON shape:
        {
          "type": "offer" | "answer" | "ice-candidate" | "call" | "end_call" | "reject",
          "to": "room_or_user",           # optional
          "payload": { ... }             # SDP or candidate or metadata
        }
        """
        try:
            data = json.loads(text_data)
        except:
            return

        msg_type = data.get("type")
        payload = data.get("payload")
        to = data.get("to")  

    
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "signaling.message",
                "sender_channel": self.channel_name,
                "sender_user_id": getattr(self.scope["user"], "id", None),
                "msg_type": msg_type,
                "payload": payload,
            }
        )

    async def signaling_message(self, event):
        # Don't echo back to sender
        if event.get("sender_channel") == self.channel_name:
            return

        await self.send(text_data=json.dumps({
            "type": event.get("msg_type"),
            "from_user": event.get("sender_user_id"),
            "payload": event.get("payload"),
        }))









