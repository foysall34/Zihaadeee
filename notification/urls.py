from django.urls import path
from .views import NotificationListView, MarkAllReadView, MarkReadView

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notifications-list"),
    path("notifications/mark-all-read/", MarkAllReadView.as_view(), name="notifications-mark-all"),
    path("notifications/<int:notif_id>/read/", MarkReadView.as_view(), name="notifications-mark-read"),
]
