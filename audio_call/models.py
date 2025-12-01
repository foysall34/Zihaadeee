from django.db import models
from django.conf import settings

class CallLog(models.Model):
    caller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="calls_made", on_delete=models.CASCADE)
    callee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="calls_received", on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(default=False)

