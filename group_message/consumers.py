import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Group, GroupMember, GroupMessage

User = get_user_model()

class GroupChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("\n\n========= GROUP CONNECT DEBUG =========")
        print("👤 User:", self.scope.get("user"))
        print("📦 Query String:", self.scope["query_string"])

        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            print("❌ Reject: Not authenticated")
            await self.close(code=4001)
            return
        
        params = parse_qs(self.scope.get("query_string", b"").decode())
        group_ids = params.get("group_id") or params.get("id")

        if not group_ids:
            print("❌ Reject: group_id missing")
            await self.close(code=4002)
            return
        
        try:
            self.group_id = int(group_ids[0])
        except:
            print("❌ Reject: invalid group_id")
            await self.close(code=4003)
            return
        
        print("🟢 GROUP ID:", self.group_id)

        # Group membership check
        is_member = await self.is_group_member(self.group_id, self.user.id)
        print("🔍 Group Member Check:", is_member)

        if not is_member:
            print("❌ Reject: user NOT member of this group")
            await self.close(code=4004)
            return
        
        # JOIN group
        self.room_group_name = f"group_{self.group_id}"
        print("🟢 ROOM:", self.room_group_name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print("🟢 CONNECT SUCCESS!")

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "send_message":
            await self.handle_send_message(data)
        elif action == "typing":
            await self.handle_typing(data)

    @database_sync_to_async
    def is_group_member(self, group_id, user_id):
        return GroupMember.objects.filter(group_id=group_id, user_id=user_id).exists()

    @database_sync_to_async
    def save_group_message(self, group_id, sender, text):
        group = Group.objects.get(id=group_id)
        return GroupMessage.objects.create(group=group, sender=sender, text=text)

    async def handle_send_message(self, data):
        text = data.get("text", "")
        msg = await self.save_group_message(self.group_id, self.user, text)

        payload = {
            "action": "new_group_message",
            "message": {
                "id": msg.id,
                "group_id": msg.group.id,
                "sender_id": msg.sender.id,
                "text": msg.text,
                "timestamp": str(msg.timestamp)
            }
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "group_message", "message": payload}
        )

    async def group_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    async def handle_typing(self, data):
        payload = {
            "action": "group_typing",
            "group_id": self.group_id,
            "user_id": self.user.id,
            "is_typing": data.get("is_typing", True)
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "group_typing_event", "message": payload}
        )

    async def group_typing_event(self, event):
        await self.send(text_data=json.dumps(event["message"]))
