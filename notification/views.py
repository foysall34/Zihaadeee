from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.db import transaction
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by("-created_at")

class MarkAllReadView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        qs = Notification.objects.filter(receiver=request.user, is_read=False)
        count = qs.update(is_read=True)
        return Response({"marked": count}, status=status.HTTP_200_OK)

class MarkReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "notif_id"

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user)

    def patch(self, request, *args, **kwargs):
        # Only mark is_read true
        obj = self.get_object()
        obj.is_read = True
        obj.save(update_fields=["is_read"])
        return Response({"id": obj.id, "is_read": obj.is_read})
