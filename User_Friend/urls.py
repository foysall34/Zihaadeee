from django.urls import path
from .views import (
    FriendRequestViewSet, FriendListView, UnfriendView, 
    BlockUserView, BlockedListView, FriendDetailView
)

friend_request_list = FriendRequestViewSet.as_view({
    'post': 'create',
})

friend_request_detail = FriendRequestViewSet.as_view({
    'put': 'update',
    'delete': 'destroy',
})

urlpatterns = [
    # Friend Request
    path('friend-requests/', friend_request_list, name='friend-request-list'),
    path('friend-requests/<int:pk>/', friend_request_detail, name='friend-request-detail'),
    
    # Friends
    path('all_friends/', FriendListView.as_view(), name='friend-list'),
    path('friends/<int:friend_id>/', FriendDetailView.as_view(), name='friend-detail'),
    path('unfriend/', UnfriendView.as_view(), name='unfriend'),
    
    # Block
    path('block/', BlockUserView.as_view(), name='block-user'),
    path('blocked/', BlockedListView.as_view(), name='blocked-list'),
]