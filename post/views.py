from rest_framework import viewsets, permissions
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer


from cloudinary.uploader import upload


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        request = self.request
        
        media_file = request.FILES.get("media")
        print("Uploaded media file:", media_file)
        media_url = None

        if media_file:
            result = upload(
                media_file,
                folder="posts/",
                resource_type="auto"
            )
            media_url = result.get("secure_url")

        serializer.save(
            author=request.user,
            media=media_url
        )



class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Post
from .models import Comment  
from .models import PostReaction, CommentReaction
from .serializers import PostReactionSerializer, CommentReactionSerializer

class PostReactionToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        """
        Toggle or set reaction for a post.
        Body: {"reaction_type": "like"}
        Behavior:
          - if no existing reaction -> create
          - if existing and same reaction_type -> delete (toggle off)
          - if existing and different reaction_type -> update to new type
        """
        post = get_object_or_404(Post, id=post_id)
        reaction_type = request.data.get("reaction_type")
        if not reaction_type:
            return Response({"detail": "reaction_type is required"}, status=status.HTTP_400_BAD_REQUEST)

        obj = PostReaction.objects.filter(user=request.user, post=post).first()

        if obj is None:
            obj = PostReaction.objects.create(user=request.user, post=post, reaction_type=reaction_type)
            serializer = PostReactionSerializer(obj, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # existing reaction present
        if obj.reaction_type == reaction_type:
            # toggle off
            obj.delete()
            return Response({"detail": "reaction removed"}, status=status.HTTP_204_NO_CONTENT)
        else:
            # change reaction type
            obj.reaction_type = reaction_type
            obj.save(update_fields=["reaction_type", "created_at"])
            serializer = PostReactionSerializer(obj, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        obj = PostReaction.objects.filter(user=request.user, post=post).first()
        if not obj:
            return Response({"detail": "no reaction to delete"}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({"detail": "reaction removed"}, status=status.HTTP_204_NO_CONTENT)


class CommentReactionToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        reaction_type = request.data.get("reaction_type")
        if not reaction_type:
            return Response({"detail": "reaction_type is required"}, status=status.HTTP_400_BAD_REQUEST)

        obj = CommentReaction.objects.filter(user=request.user, comment=comment).first()

        if obj is None:
            obj = CommentReaction.objects.create(user=request.user, comment=comment, reaction_type=reaction_type)
            serializer = CommentReactionSerializer(obj, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if obj.reaction_type == reaction_type:
            obj.delete()
            return Response({"detail": "reaction removed"}, status=status.HTTP_204_NO_CONTENT)
        else:
            obj.reaction_type = reaction_type
            obj.save(update_fields=["reaction_type", "created_at"])
            serializer = CommentReactionSerializer(obj, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        obj = CommentReaction.objects.filter(user=request.user, comment=comment).first()
        if not obj:
            return Response({"detail": "no reaction to delete"}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response({"detail": "reaction removed"}, status=status.HTTP_204_NO_CONTENT)


# Lists: who reacted to a post / comment
class PostReactionsListView(generics.ListAPIView):
    serializer_class = PostReactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return PostReaction.objects.filter(post__id=post_id).select_related("user")


class CommentReactionsListView(generics.ListAPIView):
    serializer_class = CommentReactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        comment_id = self.kwargs.get("comment_id")
        return CommentReaction.objects.filter(comment__id=comment_id).select_related("user")



# For newsfeed views.py 
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from .models import Post
from User_Friend.models import Follow
from .models import Comment
from .models import PostReaction

from .serializers import PostSerializer


class NewsFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
      
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list("following_id", flat=True)


        user_ids = list(following_ids) + [request.user.id]


        posts = (
            Post.objects.filter(author__id__in=user_ids)
            .select_related("author")              # get author in single query
            .prefetch_related("comments")          # comments count faster
            .prefetch_related("reactions")         # reactions count faster
            .order_by("-created_at")               # latest first
        )

        paginator = PageNumberPagination()
        paginator.page_size = 10 
        result_page = paginator.paginate_queryset(posts, request)

     
        serializer = PostSerializer(result_page, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data)
