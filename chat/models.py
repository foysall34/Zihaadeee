from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL

# Create your models here.
class ChatRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    celebrity = models.ForeignKey('celebrity.CelebrityProfile', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'celebrity')

    def __str__(self):
        return f"Room {self.id} ({self.user} ↔ {self.celebrity.user})"





class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)

    text = models.TextField(blank=True, null=True)

    message_type = models.CharField(
        max_length=20,
        choices=[("text", "Text"), ("image", "Image"), ("audio", "Audio"), ("video", "Video")],
        default="text"
    )

    file_url = models.URLField(blank=True, null=True)

    is_seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.text}"