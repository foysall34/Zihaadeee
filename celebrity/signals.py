from django.db.models.signals import post_save
from django.dispatch import receiver
from account.models import User
from celebrity.models import CelebrityProfile

@receiver(post_save, sender=User)
def create_celebrity_profile(sender, instance, created, **kwargs):
    if created:
        CelebrityProfile.objects.create(user=instance)
