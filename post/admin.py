from django.contrib import admin
from .models import Post, Comment , PostReaction, CommentReaction 




admin.site.register(PostReaction)
admin.site.register(CommentReaction)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'created_at')
    search_fields = ('content', 'author__email')
    list_filter = ('created_at', 'media_type')
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
    search_fields = ('text', 'user__email', 'post__content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
