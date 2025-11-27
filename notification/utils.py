import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification


def create_and_push_notification(receiver, sender, action_type, message,
                                 target_type=None, target_id=None, extra_data=None):


    
    print("=== DEBUG: create_and_push_notification CALLED ===")
    print("Receiver:", receiver)
    print("Sender:", sender)
    print("Action:", action_type)

    # Save
    notification = Notification.objects.create(
        receiver=receiver,
        sender=sender,
        action_type=action_type,
        message=message,
        target_type=target_type,
        target_id=target_id,
        extra_data=extra_data or {}
    )

    print("=== Notification Saved ID:", notification.id)

    payload = {
        "id": notification.id,
        "message": notification.message,
        "receiver": receiver.id,
        "sender": sender.id,
    }

    channel_layer = get_channel_layer()
    print("=== CHANNEL LAYER:", channel_layer)

    group_name = f"notifications_{receiver.id}"
    print("=== Sending to group:", group_name)

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send.notification",
            "data": payload
        }
    )

    print("=== PUSH DONE ===")
    return notification
