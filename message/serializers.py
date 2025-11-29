from rest_framework import serializers
from .models import Message, Conversation

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "user1", "user2", "updated_at", "last_message"]

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by("-timestamp").first()
        return MessageSerializer(last_msg).data if last_msg else None
