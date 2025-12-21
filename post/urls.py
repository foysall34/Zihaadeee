from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FilterPostView, PostReactionToggleAPIView, PostReactionsListView, PostViewSet, CommentViewSet  , CommentReactionToggleAPIView, CommentReactionsListView , NewsFeedView, RepostCreateAPIView, UserPostListAPIView

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'comments/<int:post_id>/', CommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
    # Posts reactions
    path('posts/<int:post_id>/react/', PostReactionToggleAPIView.as_view(), name='post-react'),
    path('posts/<int:post_id>/reactions/', PostReactionsListView.as_view(), name='post-reactions-list'),
    path("users/<int:user_id>/posts/",UserPostListAPIView.as_view(),name="user-post-list" ),
    # Comments reactions
    path('comments/<int:comment_id>/react/', CommentReactionToggleAPIView.as_view(), name='comment-react'),
    path('comments/<int:comment_id>/reactions/', CommentReactionsListView.as_view(), name='comment-reactions-list'),
    path("posts/<int:post_id>/repost/", RepostCreateAPIView.as_view(), name="post-repost"), #shared repost API


    path("newsfeed/", NewsFeedView.as_view(), name="newsfeed"),
    path("filter/", FilterPostView.as_view(), name="filter-posts"),
]












