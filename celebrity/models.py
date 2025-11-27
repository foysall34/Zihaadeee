from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

from django.utils import timezone



class CelebrityProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    is_celebrity = models.BooleanField(default=False)
    is_paid_celeb = models.BooleanField(default=False)
    is_follower_celeb = models.BooleanField(default=False)

    bio = models.TextField(blank=True)
    profile_image = models.URLField(blank=True)

    followers_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Celebrity: {self.user}"


class CelebrityFollow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="celeb_following")
    celebrity = models.ForeignKey(CelebrityProfile, on_delete=models.CASCADE, related_name="celeb_followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'celebrity')


# ----------- Paid Chat Access (4.99$ for 10-minute chat) -------------

class PaidChatAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    celebrity = models.ForeignKey(CelebrityProfile, on_delete=models.CASCADE)
    duration_minutes = models.PositiveIntegerField(default=10)
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    expiry_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'celebrity')


# -------- Text Messages ------------

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    celebrity = models.ForeignKey(CelebrityProfile, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)










# Donation models ------------------------------

class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)