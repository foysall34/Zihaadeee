from rest_framework import serializers
from .models import Donation


from .models import CelebrityProfile, Message, PaidChatAccess


class CelebrityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CelebrityProfile
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.email", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender", "sender_name", "celebrity", "text", "created_at"]


class PaidChatAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaidChatAccess
        fields = "__all__"




class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = "__all__"


