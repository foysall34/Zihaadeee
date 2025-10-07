from django.urls import path
from .views import FriendRequestViewSet, FriendListView

friend_request_list = FriendRequestViewSet.as_view({
    'post': 'create',      # URL: friend-requests/
})

friend_request_detail = FriendRequestViewSet.as_view({
    'put': 'update',        # URL: friend-requests/<int:pk>/
    'delete': 'destroy',    # URL: friend-requests/<int:pk>/
})

urlpatterns = [
    path('friend-requests/', friend_request_list, name='friend-request-list'),
    path('friend-requests/<int:pk>/', friend_request_detail, name='friend-request-detail'),
    path('all_friends/', FriendListView.as_view(), name='friend-list'),
]