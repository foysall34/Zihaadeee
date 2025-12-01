from rest_framework import serializers
from .models import Group, GroupMember, GroupMessage
from django.contrib.auth import get_user_model

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "created_by", "created_at", "members"]

    def get_members(self, group):
        users = group.members.all()
        return [{"id": m.user.id, "email": m.user.email, "is_admin": m.is_admin} for m in users]


class GroupMessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = GroupMessage
        fields = ["id", "group", "sender_id", "text", "attachment", "attachment_url", "timestamp"]

    def get_attachment_url(self, obj):
        if obj.attachment:
            try:
                return obj.attachment.url
            except:
                return None
        return None





from rest_framework import serializers
from .models import GroupMember

class GroupMemberAddSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
