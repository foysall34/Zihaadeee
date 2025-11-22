import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.urls import reverse
from .models import Notification

def build_notification_payload(notification: Notification):
    # Compose payload sent to client
    return {
        "id": notification.id,
        "sender_id": notification.sender.id,
        "sender_name": getattr(notification.sender, "full_name", str(notification.sender)),
        "action_type": notification.action_type,
        "message": notification.message,
        "target_type": notification.target_type,
        "target_id": notification.target_id,
        "extra_data": notification.extra_data,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat(),
    }

def create_and_push_notification(receiver, sender, action_type, message,
                                 target_type=None, target_id=None, extra_data=None):
    """
    1) Save Notification in DB
    2) Push to receiver via Channels group `notifications_{user_id}`
    Returns notification instance.
    """
    notification = Notification.objects.create(
        receiver=receiver,
        sender=sender,
        action_type=action_type,
        message=message,
        target_type=target_type,
        target_id=target_id,
        extra_data=extra_data or {}
    )

    payload = build_notification_payload(notification)

    # Channels push (sync wrapper)
    channel_layer = get_channel_layer()
    group_name = f"notifications_{receiver.id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send.notification",   # maps to method send_notification in consumer (dots -> underscores)
            "data": payload
        }
    )

    return notification
