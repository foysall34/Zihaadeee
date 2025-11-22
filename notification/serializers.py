from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id","sender","sender_name","action_type","message",
            "target_type","target_id","extra_data","is_read","created_at"
        ]
