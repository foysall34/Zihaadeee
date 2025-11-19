from celery import shared_task
from django.utils import timezone
from .models import Story
import cloudinary.uploader
import os

@shared_task
def delete_expired_stories():
    now = timezone.now()
    expired = Story.objects.filter(expires_at__lte=now)
    count = 0
    for story in expired:
        try:
            # Prefer using stored public_id if you store one. Here we extract from URL:
            # cloudinary storage keeps `story.media_url` e.g. https://res.cloudinary.com/<cloud>/image/upload/v12345/folder/name.jpg
            public_id = extract_public_id_from_url(story.media_url)
            if public_id:
                cloudinary.uploader.destroy(public_id, invalidate=True, resource_type="auto")
        except Exception as e:
            # log error in real app
            print("Cloudinary delete error:", e)
        story.delete()
        count += 1
    return {"deleted": count}

# helper (simple)
def extract_public_id_from_url(url):
    # naive extraction: remove extension and everything before upload/
    # e.g. https://res.cloudinary.com/<cloud>/image/upload/v12345/stories/abcd123.jpg
    try:
        # find '/upload/' and take the rest
        idx = url.find("/upload/")
        if idx == -1:
            return None
        tail = url[idx + len("/upload/"):]
        # drop version like v12345/
        parts = tail.split("/")
        if parts and parts[0].startswith("v"):
            parts = parts[1:]
        filename = "/".join(parts)
        # remove extension
        public_id = os.path.splitext(filename)[0]
        return public_id
    except Exception:
        return None
