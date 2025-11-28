import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, ChatMessage
from celebrity.models import CelebrityProfile
from account.models import User


class ChatConsumer(AsyncWebsocketConsumer):

    # -----------------------------------
    # CONNECT
    # -----------------------------------
    async def connect(self):

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope["user"]

        # user must be authenticated
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Broadcast: user online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status",
                "event": "online",
                "user_id": self.user.id,
                "user": self.user.email
            }
        )

    # -----------------------------------
    # DISCONNECT
    # -----------------------------------
    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Broadcast offline status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status",
                "event": "offline",
                "user_id": self.user.id,
                
            }
        )

    # -----------------------------------
    # RECEIVE FROM CLIENT
    # -----------------------------------
    async def receive(self, text_data):

        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "message":
            await self.handle_message(data)

        elif event_type == "typing":
            await self.handle_typing(data)

        elif event_type == "seen":
            await self.handle_seen(data)

    # -----------------------------------
    # HANDLE MESSAGE
    # -----------------------------------
    async def handle_message(self, data):

        message_text = data.get("text")

        message_obj = await self.save_message(
            sender=self.user,
            room_id=self.room_id,
            text=message_text
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": message_obj.id,
                "sender": self.user.email,
                "sender_id": self.user.id,
                "text": message_text,
                "timestamp": str(message_obj.timestamp),
            }
        )

    # -----------------------------------
    # HANDLE TYPING
    # -----------------------------------
    async def handle_typing(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_event",
                "user": self.user.email,
                "event": "typing"
            }
        )

    # -----------------------------------
    # HANDLE SEEN
    # -----------------------------------
    async def handle_seen(self, data):

        msg_id = data.get("message_id")

        await self.mark_seen(msg_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "seen_event",
                "message_id": msg_id,
                "user": self.user.email
            }
        )

    # -----------------------------------
    # BROADCAST - MESSAGE
    # -----------------------------------
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "id": event["id"],
            "sender": event["sender"],
            "sender_id": event["sender_id"],
            "text": event["text"],
            "timestamp": event["timestamp"]
        }))

    # -----------------------------------
    # BROADCAST - TYPING
    # -----------------------------------
    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user": event["user"]
        }))

    # -----------------------------------
    # BROADCAST - SEEN
    # -----------------------------------
    async def seen_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "seen",
            "message_id": event["message_id"],
            "user": event["user"]
        }))

    # -----------------------------------
    # BROADCAST - USER STATUS
    # -----------------------------------
    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "status",
            "event": event["event"],
            "user_id": event["user_id"],
            # "user": event["user"]
        }))

    # -----------------------------------
    # DB: SAVE MESSAGE
    # -----------------------------------
    @database_sync_to_async
    def save_message(self, sender, room_id, text):

        room = ChatRoom.objects.get(id=room_id)

        # Validate: only these 2 users can chat
        if sender != room.user and sender != room.celebrity.user:
            raise ValueError("User not allowed in this room")

        return ChatMessage.objects.create(
            room=room,
            sender=sender,
            text=text
        )

    # -----------------------------------
    # DB: MARK SEEN
    # -----------------------------------
    @database_sync_to_async
    def mark_seen(self, message_id):
        msg = ChatMessage.objects.get(id=message_id)
        msg.is_seen = True
        msg.save()
        return msg
