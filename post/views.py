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








from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post
from .models import Comment  
from .models import PostReaction, CommentReaction
from .serializers import PostReactionSerializer, CommentReactionSerializer



from notification.utils import create_and_push_notification


class PostReactionToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        reaction_type = request.data.get("reaction_type")

        if not reaction_type:
            return Response({"detail": "reaction_type is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        obj = PostReaction.objects.filter(user=request.user, post=post).first()

        # ---------------------------------------------
        # CASE 1: FIRST TIME REACTION (create)
        # ---------------------------------------------
        if obj is None:
            obj = PostReaction.objects.create(
                user=request.user,
                post=post,
                reaction_type=reaction_type
            )

            #  Notification (ONLY for new reaction)
            if post.author != request.user:
                print(">>> Creating notification for post reaction **")
                create_and_push_notification(
                    receiver=post.author,
                    sender=request.user,
                    action_type="post_reaction",
                    message=f"{request.user.full_name} reacted '{reaction_type}' to your post",
                    target_type="post",
                    target_id=post.id,
                   
                )
                print(">>> Notification created for post reaction **")

            serializer = PostReactionSerializer(obj, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # ---------------------------------------------
        # CASE 2: SAME reaction → REMOVE (toggle off)
        # ---------------------------------------------
        if obj.reaction_type == reaction_type:
            obj.delete()
            return Response({"detail": "reaction removed"},
                            status=status.HTTP_204_NO_CONTENT)

        # ---------------------------------------------
        # CASE 3: DIFFERENT reaction → UPDATE
        # ---------------------------------------------
        obj.reaction_type = reaction_type
        obj.save(update_fields=["reaction_type", "created_at"])

        # 🔔 Notification (reaction changed)
        if post.author != request.user:
            create_and_push_notification(
                receiver=post.author,
                sender=request.user,
                action_type="post_reaction_update",
                message=f"{request.user.full_name} changed reaction to '{reaction_type}'",
                target_type="post",
                target_id=post.id,
                extra_data={
                    "post_id": post.id,
                    "image": post.media.url if post.media else None
                }
            )

        serializer = PostReactionSerializer(obj, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)










from notification.utils import create_and_push_notification

class CommentReactionToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        reaction_type = request.data.get("reaction_type")
        if not reaction_type:
            return Response({"detail": "reaction_type is required"}, status=status.HTTP_400_BAD_REQUEST)

        obj = CommentReaction.objects.filter(user=request.user, comment=comment).first()

        # -------------------------------
        # CASE 1: NEW reaction create
        # -------------------------------
        if obj is None:
            obj = CommentReaction.objects.create(
                user=request.user,
                comment=comment,
                reaction_type=reaction_type
            )

            #  Send Notification
            if comment.user != request.user:
                create_and_push_notification(
                    receiver=comment.user,
                    sender=request.user,
                    action_type="comment_reaction",
                    message=f"{request.user.full_name} reacted '{reaction_type}' on your comment",
                    target_type="comment",
                    target_id=comment.id,
                    extra_data={
                        "comment_id": comment.id,
                        "post_id": comment.post.id,
                    }
                )

            serializer = CommentReactionSerializer(obj, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # -------------------------------
        # CASE 2: SAME reaction → REMOVE
        # -------------------------------
        if obj.reaction_type == reaction_type:
            obj.delete()
            return Response({"detail": "reaction removed"}, status=status.HTTP_204_NO_CONTENT)

        # -------------------------------
        # CASE 3: UPDATE reaction
        # -------------------------------
        obj.reaction_type = reaction_type
        obj.save(update_fields=["reaction_type", "created_at"])

        #  Notification for reaction changed
        if comment.user != request.user:
            create_and_push_notification(
                receiver=comment.user,
                sender=request.user,
                action_type="comment_reaction_update",
                message=f"{request.user.full_name} changed reaction to '{reaction_type}' on your comment",
                target_type="comment",
                target_id=comment.id,
                extra_data={
                    "comment_id": comment.id,
                    "post_id": comment.post.id,
                    "image": comment.post.media.url if comment.post.media else None
                }
            )

        serializer = CommentReactionSerializer(obj, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)





from notification.utils import create_and_push_notification

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)

        # CASE 1: Reply comment
        if comment.parent:
            parent_user = comment.parent.user
            if parent_user != self.request.user:
                create_and_push_notification(
                    receiver=parent_user,
                    sender=self.request.user,
                    action_type="comment_reply",
                    message=f"{self.request.user.full_name} replied to your comment",
                    target_type="comment",
                    target_id=comment.parent.id,
                    extra_data={
                        "comment_id": comment.id,
                        "post_id": comment.post.id
                    }
                )
            return

        # CASE 2: Normal comment → send to post author
        post_owner = comment.post.author
        if post_owner != self.request.user:
            create_and_push_notification(
                receiver=post_owner,
                sender=self.request.user,
                action_type="comment",
                message=f"{self.request.user.full_name} commented on your post",
                target_type="post",
                target_id=comment.post.id,
                extra_data={
                    "comment_id": comment.id,
                    "post_id": comment.post.id,
                    "image": comment.post.media.url if comment.post.media else None
                }
            )






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



# --------------------------------------- For newsfeed views.py -----------------------------------------------------


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







