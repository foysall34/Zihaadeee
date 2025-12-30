# serializers.py
from rest_framework import serializers
from .models import BlockedUser, FriendRequest , Follow
from account.models import UserProfile



from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "profile_photo",
        ]

    def get_profile_photo(self, obj):
        return obj.profile_photo



class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = SimpleUserSerializer(read_only=True)
    # to_user = SimpleUserSerializer(read_only=True)
    class Meta:
        model = FriendRequest
        fields = [
            "id",
            "from_user",
            # "to_user",
            "status",
            "created_at",
        ]
        read_only_fields = [ 'from_user', 'status']



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'



class BlockedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedUser
        fields = '__all__'
        read_only_fields = ['blocker']



class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'follower', 'created_at']