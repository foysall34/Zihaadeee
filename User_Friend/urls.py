from django.urls import path

from User_Friend.models import UnblockUserView
from .views import (
    FriendRequestViewSet, FriendListView, FriendSuggestionView, IncomingFriendRequestViewSet, UnfriendView, 
    BlockUserView, BlockedListView, FriendDetailView ,FriendRequestViewSet , FollowView , FollowerListView , FollowingListView
)


friend_request_list = FriendRequestViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

friend_request_detail = FriendRequestViewSet.as_view({
    'put': 'update',
    'delete': 'destroy',
})


urlpatterns = [
    # Friend Request
    path('friend-requests/', friend_request_list, name='friend-requests-list'),
    path('friend-requests/<int:pk>/', friend_request_detail, name='friend-request-detail'),# put , delete , get 
    path("friend-requests/incoming/",IncomingFriendRequestViewSet.as_view({"get": "list"}),name="incoming-friend-requests"),
    # Friends
    path('all_friends/', FriendListView.as_view(), name='friend-list'),
    path('friends/<int:friend_id>/', FriendDetailView.as_view(), name='friend-detail'),
    path('unfriend/', UnfriendView.as_view(), name='unfriend'),
    path('suggestion-list/', FriendSuggestionView.as_view(), name='send-suggestion-request'),
    
    # Block
    path('block/', BlockUserView.as_view(), name='block-user'),
    path('blocked/', BlockedListView.as_view(), name='blocked-list'),
    path('unblock/<int:blocked_user_id>/', UnblockUserView.as_view(), name='unblock-user'),

    # Follow
    path('follow/', FollowView.as_view(), name='follow-unfollow'),

   #Followers and Following list
    path('followers/', FollowerListView.as_view(), name='followers'),
    path('following/', FollowingListView.as_view(), name='following'),


]



