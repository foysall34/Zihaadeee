import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

from .models import Message
from .utils import get_or_create_conversation

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope.get("user")

        # If user is anonymous / invalid token
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        # Create unique room
        self.room_group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        # Protect from missing group name
        if hasattr(self, "room_group_name"):
            try:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
            except:
                pass


    async def receive(self, text_data):
        """
        Receive data from WebSocket
        """
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "action": "error",
                "message": "Invalid JSON format"
            }))
            return
        
        action = data.get("action")

        if action == "send_message":
            await self.handle_send_message(data)
        else:
            await self.send(text_data=json.dumps({
                "action": "error",
                "message": "Invalid action"
            }))


    @database_sync_to_async
    def save_message(self, sender, receiver, text):
        conv = get_or_create_conversation(sender, receiver)
        msg = Message.objects.create(
            conversation=conv,
            sender=sender,
            receiver=receiver,
            text=text
        )
        conv.save()
        return msg


    async def handle_send_message(self, data):

        if "receiver_id" not in data or "text" not in data:
            await self.send(text_data=json.dumps({
                "action": "error",
                "message": "receiver_id and text are required"
            }))
            return

        receiver_id = data["receiver_id"]
        text = data["text"]

   
        try:
            receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
        except User.DoesNotExist:
            await self.send(text_data=json.dumps({
                "action": "error",
                "message": f"Receiver with id {receiver_id} does not exist"
            }))
            return

        msg = await self.save_message(self.user, receiver, text)

        message_payload = {
            "action": "new_message",
            "message": {
                "id": msg.id,
                "sender_id": msg.sender.id,
                "receiver_id": msg.receiver.id,
                "text": msg.text,
                "timestamp": str(msg.timestamp),
                "is_seen": msg.is_seen,
            }
        }

        # Send to receiver
        await self.channel_layer.group_send(
            f"user_{receiver.id}",
            {"type": "chat_message", "message": message_payload}
        )

        
        await self.channel_layer.group_send(
            f"user_{self.user.id}",
            {"type": "chat_message", "message": message_payload}
        )


    async def chat_message(self, event):
        """
        Receive message from room group
        """
        await self.send(text_data=json.dumps(event["message"]))
