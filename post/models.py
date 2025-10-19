from django.db import models
from account.models import User

MEDIA_TYPES = [
    ('image', 'Image'),
    ('video', 'Video')
]

REACTION_CHOICES = [
    ('like', 'Like'),
    ('love', 'Love'),
    ('haha', 'Haha'),
    ('wow', 'Wow'),
    ('sad', 'Sad'),
    ('angry', 'Angry'),
]


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='image')
    media = models.FileField(upload_to='post_media/', blank=True, null=True)
    content = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:30] if self.content else f"{self.media_type} Post"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.email} on {self.post}"


class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='post_reactions')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='comment_reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post', 'comment')

    def __str__(self):
        target = self.post or self.comment
        return f"{self.user.email} reacted '{self.reaction_type}' to {target}"
