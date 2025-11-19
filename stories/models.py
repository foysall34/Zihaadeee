from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

User = settings.AUTH_USER_MODEL

MEDIA_TYPES = [
    ('image', 'Image'),
    ('video', 'Video'),
]

class Story(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stories")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    media_url = models.URLField(max_length=1000)   
    caption = models.CharField(max_length=400, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.author} story #{self.pk}"


class StoryView(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="story_views")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("story", "user")
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user} viewed {self.story}"
