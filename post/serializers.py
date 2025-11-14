from rest_framework import serializers
from .models import Post, Comment




class CommentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    replies = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'user_email',
            'parent',
            'text',
            'created_at',
            'replies',
            'reactions_count',
        ]
        read_only_fields = ['user_email', 'created_at']

    def get_replies(self, obj):
        replies = obj.replies.all().order_by('-created_at')
        return CommentSerializer(replies, many=True).data

    def get_reactions_count(self, obj):
        return obj.comment_reactions.count()

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_photo = serializers.ImageField(source='author.profile_photo', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    reactions_count = serializers.IntegerField(source='reactions.count', read_only=True)
    my_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_name', 'author_photo', 'content', 'media_type', 'media',
            'created_at', 'comments_count', 'reactions_count', 'my_reaction',
        ]

    def get_my_reaction(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        pr = PostReaction.objects.filter(post=obj, user=request.user).first()
        return pr.reaction_type if pr else None






from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PostReaction, CommentReaction

User = get_user_model()

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "full_name", "email", "profile_photo")

class PostReactionSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = PostReaction
        fields = ("id", "user", "post", "reaction_type", "created_at")
        read_only_fields = ("id", "user", "created_at", "post")

class CommentReactionSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = CommentReaction
        fields = ("id", "user", "comment", "reaction_type", "created_at")
        read_only_fields = ("id", "user", "created_at", "comment")





from rest_framework import serializers
from .models import Post
from .models import PostReaction

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_photo = serializers.ImageField(source='author.profile_photo', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    reactions_count = serializers.IntegerField(source='reactions.count', read_only=True)
    my_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'author_name',
            'author_photo',
            'content',
            'media_type',
            'media',
            'created_at',
            'comments_count',
            'reactions_count',
            'my_reaction',
        ]

    def get_my_reaction(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        reaction = PostReaction.objects.filter(post=obj, user=request.user).first()
        return reaction.reaction_type if reaction else None
