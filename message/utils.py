from .models import Conversation

def get_or_create_conversation(user1, user2):
    conv = Conversation.objects.filter(
        user1__in=[user1, user2],
        user2__in=[user1, user2]
    ).first()

    if conv:
        return conv

    # Always save in sorted order (small user id first)
    if user1.id < user2.id:
        return Conversation.objects.create(user1=user1, user2=user2)
    return Conversation.objects.create(user1=user2, user2=user1)
