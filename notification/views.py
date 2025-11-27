from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.db import transaction
from .models import Notification
from .serializers import NotificationSerializer

import logging

logger = logging.getLogger("notifications_debug")


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print("User:", user)
        logger.info(f"[NotificationList] User: {user.id} -> Fetching notifications")

        qs = Notification.objects.filter(receiver=user).order_by("-created_at")
        print(qs)
        logger.info(f"[NotificationList] Total notifications found: {qs.count()}")
        return qs


class MarkAllReadView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        logger.info(f"[MarkAllRead] User: {user.id} requested to mark all as read")

        qs = Notification.objects.filter(receiver=user, is_read=False)
        count = qs.count()
        logger.info(f"[MarkAllRead] Unread notifications: {count}")

        updated = qs.update(is_read=True)
        logger.info(f"[MarkAllRead] Successfully marked {updated} notifications")

        return Response({"marked": updated}, status=status.HTTP_200_OK)


class MarkReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "notif_id"

    def get_queryset(self):
        qs = Notification.objects.filter(receiver=self.request.user)
        logger.info(f"[MarkRead] QuerySet count: {qs.count()}")
        return qs

    def patch(self, request, *args, **kwargs):
        notif_id = kwargs.get("notif_id")
        logger.info(f"[MarkRead] Request to mark notification {notif_id} as read")

        obj = self.get_object()
        logger.info(f"[MarkRead] Notification owner: {obj.receiver.id}, Request user: {request.user.id}")

        obj.is_read = True
        obj.save(update_fields=["is_read"])

        logger.info(f"[MarkRead] Notification {notif_id} marked as read")

        return Response({"id": obj.id, "is_read": obj.is_read})



