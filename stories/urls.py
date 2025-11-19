from django.urls import path
from .views import (
    StoryCreateView, StoryListView, StoriesByAuthorView,
    StoryMarkViewedAPIView, StoryViewersListView, StoryDeleteView
)

urlpatterns = [
    path("stories/create/", StoryCreateView.as_view(), name="stories-create"),
    path("stories/", StoryListView.as_view(), name="stories-list"),
    path("stories/author/<int:author_id>/", StoriesByAuthorView.as_view(), name="stories-by-author"),
    path("stories/<int:story_id>/view/", StoryMarkViewedAPIView.as_view(), name="story-mark-view"),
    path("stories/<int:story_id>/viewers/", StoryViewersListView.as_view(), name="story-viewers"),
    path("stories/<int:story_id>/", StoryDeleteView.as_view(), name="story-delete"),
]
