from rest_framework import serializers
from .models import Post, Comment



class CommentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    replies = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()
    reaction_type = serializers.SerializerMethodField() 

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
            'reaction_type',
        ]
        read_only_fields = ['user_email', 'created_at']

    def get_replies(self, obj):
        replies = obj.replies.all().order_by('-created_at')
        return CommentSerializer(
            replies,
            many=True,
            context=self.context   
        ).data

    def get_reactions_count(self, obj):
        return obj.reactions.count()

    def get_reaction_type(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        reaction = obj.reactions.filter(user=request.user).first()
        return reaction.reaction_type if reaction else None



# class PostSerializer(serializers.ModelSerializer):
#     author_name = serializers.CharField(source='author.full_name', read_only=True)
#     author_photo = serializers.ImageField(source='author.profile_photo', read_only=True)
#     comments_count = serializers.IntegerField(source='comments.count', read_only=True)
#     reactions_count = serializers.IntegerField(source='reactions.count', read_only=True)
#     my_reaction = serializers.SerializerMethodField()

#     class Meta:
#         model = Post
#         fields = [
#             'id', 'author', 'author_name', 'author_photo', 'content', 'media_type', 'media',
#             'created_at', 'comments_count', 'reactions_count', 'my_reaction',
#         ]

#     def get_my_reaction(self, obj):
#         request = self.context.get('request')
#         if not request or not request.user.is_authenticated:
#             return None
#         pr = PostReaction.objects.filter(post=obj, user=request.user).first()
#         return pr.reaction_type if pr else None






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




#####Final Post Serializer with Repost and Follow Logic #####
from rest_framework import serializers
from .models import Post, PostReaction
from User_Friend.models import Follow


class PostSerializer(serializers.ModelSerializer):
    content = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    author_name = serializers.CharField(
        source="author.full_name",
        read_only=True
    )

    author_photo = serializers.SerializerMethodField()

    comments_count = serializers.IntegerField(
        source="comments.count",
        read_only=True
    )

    reactions_count = serializers.IntegerField(
        source="reactions.count",
        read_only=True
    )

    my_reaction = serializers.SerializerMethodField()
    is_user = serializers.SerializerMethodField()
    is_follow = serializers.SerializerMethodField()

    # ✅ ALWAYS list
    media = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )

    is_repost = serializers.BooleanField(read_only=True)
    shares_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_name",
            "author_photo",
            "content",
            "media_type",
            "media",
            "created_at",
            "comments_count",
            "reactions_count",
            "my_reaction",
            "is_user",
            "is_follow",
            "is_repost",
            "shares_count",
        ]
        read_only_fields = ["author"]

    # -------------------------
    # Author photo
    # -------------------------
    def get_author_photo(self, obj):
        return obj.author.profile_photo

    # -------------------------
    # My reaction
    # -------------------------
    def get_my_reaction(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        reaction = PostReaction.objects.filter(
            post=obj,
            user=request.user
        ).first()

        return reaction.reaction_type if reaction else None

    # -------------------------
    # Is my post?
    # -------------------------
    def get_is_user(self, obj):
        request = self.context.get("request")
        return bool(
            request and request.user.is_authenticated and obj.author == request.user
        )

    # -------------------------
    # Follow check
    # -------------------------
    def get_is_follow(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        if obj.author == request.user:
            return False

        return Follow.objects.filter(
            follower=request.user,
            following=obj.author
        ).exists()

    # -------------------------
    # FORCE media=[]
    # -------------------------
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("media") is None:
            data["media"] = []
        return data













# serializers.py
from rest_framework import serializers
from .models import Post

class VideoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"





# post/serializers.py
from rest_framework import serializers
from django.db import transaction
from django.db.models import F
from .models import Post

class RepostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['content']

    def create(self, validated_data):
        request = self.context['request']
        post_id = self.context.get('post_id')

        with transaction.atomic():
            original = Post.objects.select_for_update().get(id=post_id)

            repost = Post.objects.create(
                author=request.user,
                content=validated_data.get('content', ''),
                media=None,  
                media_type=original.media_type,
                original=original,
                is_repost=True,
            )

           
            Post.objects.filter(id=original.id).update(shares_count=F('shares_count') + 1)

        return repost





from rest_framework import serializers
from .models import Post

class PostSerializerFilter(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = "__all__"




from rest_framework import serializers
from .models import Post, PostReaction
from User_Friend.models import Follow


class UserPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    author_photo = serializers.CharField(source="author.profile_photo", read_only=True)

    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    reactions_count = serializers.IntegerField(source="reactions.count", read_only=True)

    my_reaction = serializers.SerializerMethodField()
    is_user = serializers.SerializerMethodField()
    is_follow = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_name",
            "author_photo",
            "content",
            "media_type",
            "media",
            "created_at",

            "comments_count",
            "reactions_count",
            "my_reaction",

            "is_user",
            "is_follow",

            "is_repost",
            "shares_count",
        ]
        read_only_fields = ["author"]

    # ---------- METHODS ----------

    def get_my_reaction(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        reaction = obj.reactions.filter(user=request.user).first()
        return reaction.reaction_type if reaction else None

    def get_is_user(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        return obj.author == request.user

    def get_is_follow(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        return Follow.objects.filter(
            follower=request.user,
            following=obj.author
        ).exists()
