from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostReactionToggleAPIView, PostReactionsListView, PostViewSet, CommentViewSet  , CommentReactionToggleAPIView, CommentReactionsListView , NewsFeedView

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    # Posts reactions
    path('posts/<int:post_id>/react/', PostReactionToggleAPIView.as_view(), name='post-react'),
    path('posts/<int:post_id>/reactions/', PostReactionsListView.as_view(), name='post-reactions-list'),

    # Comments reactions
    path('comments/<int:comment_id>/react/', CommentReactionToggleAPIView.as_view(), name='comment-react'),
    path('comments/<int:comment_id>/reactions/', CommentReactionsListView.as_view(), name='comment-reactions-list'),
    path("newsfeed/", NewsFeedView.as_view(), name="newsfeed"),

]
 