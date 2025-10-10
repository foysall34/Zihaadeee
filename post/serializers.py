from rest_framework import serializers
from .models import Post, Comment, Reaction


class ReactionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 
                  'user_email', 
                  'post', 
                  'comment', 
                  'reaction_type', 
                  'created_at'
                ]
        read_only_fields = ['user_email', 'created_at']

        def get_reacted_on(self, obj):
            if obj.post:
                return {"type": "post", "id": obj.post.id, "content": obj.post.content[:30]}
            elif obj.comment:
                return {"type": "comment", "id": obj.comment.id, "text": obj.comment.text[:30]}
            return None


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
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_photo = serializers.ImageField(source='author.profile_photo', read_only=True)
    comments = serializers.SerializerMethodField()
    reactions_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author_name',
            'author_email',
            'author_photo',
            'media_type',
            'media',
            'content',
            'created_at',
            'comments',
            'reactions_count',
        ]
        read_only_fields = ['author_name', 'author_email', 'author_photo', 'created_at']

    def get_comments(self, obj):
        comments = obj.comments.filter(parent__isnull=True).order_by('-created_at')
        return CommentSerializer(comments, many=True).data

    def get_reactions_count(self, obj):
        return obj.post_reactions.count()

    def validate(self, data):
        media_type = data.get('media_type')
        media = data.get('media')

        if media:
            if media_type == 'image' and not media.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise serializers.ValidationError("Only image files are allowed for 'Image' type.")
            elif media_type == 'video' and not media.name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                raise serializers.ValidationError("Only video files are allowed for 'Video' type.")
        return data
