# serializers.py
from rest_framework import serializers
from .models import BlockedUser, FriendRequest
from account.models import UserProfile

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'
        read_only_fields = ['from_user', 'status']



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'



class BlockedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedUser
        fields = '__all__'
        read_only_fields = ['blocker']