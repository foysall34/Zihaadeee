from rest_framework import serializers
from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']
        read_only_fields = fields


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)
    receiver = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "receiver",
            "action_type",
            "message",
            "target_id",
            "target_type",
            "extra_data",
            "is_read",
            "created_at",
        ]
