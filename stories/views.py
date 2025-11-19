from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import IntegrityError, transaction
from .models import Story, StoryView
from .serializers import StorySerializer, StoryListSerializer, StoryViewSerializer
from User_Friend.models import Follow
from django.db.models import F
from stories import models 


class StoryCreateView(generics.CreateAPIView):
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx.update({"request": self.request})
        return ctx



class StoryListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        following_ids = Follow.objects.filter(follower=request.user).values_list("following_id", flat=True)
        user_ids = list(following_ids) + [request.user.id]
        qs = Story.objects.filter(author__id__in=user_ids, expires_at__gt=now).select_related("author").order_by("-created_at")
        serializer = StoryListSerializer(qs, many=True, context={"request": request})
  
        return Response(serializer.data)



class StoriesByAuthorView(generics.ListAPIView):
    serializer_class = StoryListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        author_id = self.kwargs.get("author_id")
        return Story.objects.filter(author__id=author_id, expires_at__gt=timezone.now()).order_by("-created_at")


class StoryMarkViewedAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, story_id):
        
        story = get_object_or_404(
            Story, 
            id=story_id, 
            expires_at__gt=timezone.now()
        )

        try:
            with transaction.atomic():
                sv, created = StoryView.objects.get_or_create(
                    story=story, 
                    user=request.user
                )

              
                if created:
                    Story.objects.filter(id=story.id).update(
                        views_count=F("views_count") + 1
                    )

        except IntegrityError:
            created = False

        serializer = StoryViewSerializer(sv, context={"request": request})

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )



class StoryViewersListView(generics.ListAPIView):
    serializer_class = StoryViewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        story_id = self.kwargs.get("story_id")
        story = get_object_or_404(Story, id=story_id)
    
        if self.request.user != story.author and not self.request.user.is_staff:
            return StoryView.objects.none()
        return StoryView.objects.filter(story=story).select_related("user").order_by("-viewed_at")



from rest_framework.exceptions import PermissionDenied

class StoryDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Story.objects.all()
    lookup_url_kwarg = "story_id"

    def perform_destroy(self, instance):
     
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You can't delete this story.")
        
     
        instance.delete()

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return Response(
            {"message": "your story is deleted"},
            status=status.HTTP_200_OK
        )
    



