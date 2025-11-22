from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Notification(models.Model):
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_notifications"
    )

    action_type = models.CharField(max_length=50)  
    # like, comment, reply, follow, story_view, message

    message = models.CharField(max_length=255)

    target_id = models.PositiveIntegerField(null=True, blank=True)  
    target_type = models.CharField(max_length=50, null=True, blank=True)  
    # post, comment, story, message, friend

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.action_type})"
