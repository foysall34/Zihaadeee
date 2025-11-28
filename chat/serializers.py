from .models import ChatRoom, ChatMessage
from rest_framework import serializers

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ["id", "user", "celebrity", "created_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.email", read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "room",
            "sender",
            "sender_name",
            "text",
            "message_type",
            "file_url",
            "is_seen",
            "timestamp"
        ]


