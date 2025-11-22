import cloudinary.uploader
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Story, StoryView

class StorySerializer(serializers.ModelSerializer):
    # accept file upload from frontend, but save URL in media_url
    media = serializers.FileField(write_only=True, required=True)
    media_url = serializers.CharField(read_only=True)

    class Meta:
        model = Story
        fields = [
            "id", "author", "media_type", "media", "media_url",
            "caption", "created_at", "expires_at", "views_count"
        ]
        read_only_fields = ("author", "media_url", "created_at", "expires_at", "views_count")

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        media_file = validated_data.pop("media", None)
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            media_file,
            folder="stories",
            resource_type="auto"  # support image/video
        )
        media_url = upload_result.get("secure_url")
        # set defaults
        expires = timezone.now() + timedelta(hours=24)
        story = Story.objects.create(
            author=user,
            media_type=validated_data.get("media_type"),
            media_url=media_url,
            caption=validated_data.get("caption", ""),
            expires_at=expires
        )
        return story






class StoryListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    author_photo = serializers.ImageField(source="author.profile_photo", read_only=True)

    class Meta:
        model = Story
        fields = [
            "id", "author", "author_name", "author_photo",
            "media_type", "media_url", "caption",
            "created_at", "expires_at", "views_count"
        ]


class StoryViewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = StoryView
        fields = ("id", "story", "user", "user_name", "viewed_at")
        read_only_fields = ("story", "user", "viewed_at")
