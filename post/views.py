from rest_framework import viewsets, permissions
from cloudinary.uploader import upload

from account import serializers
from .models import Post
from .serializers import PostSerializer , CommentSerializer, PostSerializerFilter, VideoPostSerializer

from rest_framework import viewsets, permissions
from cloudinary.uploader import upload
from .models import Post
from .serializers import PostSerializer


from rest_framework import status
from rest_framework.response import Response
from cloudinary.uploader import upload




from .models import Post
from .serializers import PostSerializer


from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from cloudinary.uploader import upload

from .models import Post
from .serializers import PostSerializer


from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from cloudinary.uploader import upload

from .models import Post
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # ---------------- CREATE ----------------
    def perform_create(self, serializer):
        request = self.request

        media_type = request.data.get("media_type", "image")

        if media_type not in ["image", "video"]:
            raise serializers.ValidationError({
                "media_type": "Invalid media type. Allowed: image, video."
            })

        media_urls = []

        resource_type = "video" if media_type == "video" else "image"

        # multiple files
        media_files = request.FILES.getlist("media_files")
        if media_files:
            for file in media_files:
                result = upload(
                    file,
                    folder="posts/",
                    resource_type=resource_type
                )
                url = result.get("secure_url")
                if url:
                    media_urls.append(url)

        # single file
        single_media = request.FILES.get("media")
        if single_media:
            result = upload(
                single_media,
                folder="posts/",
                resource_type=resource_type
            )
            url = result.get("secure_url")
            if url:
                media_urls = [url]

        serializer.save(
            author=request.user,
            media_type=media_type,
            media=media_urls
        )

    # ---------------- PATCH ----------------
    def partial_update(self, request, *args, **kwargs):
        post = self.get_object()

        if post.author != request.user:
            return Response(
                {"detail": "You do not have permission to edit this post"},
                status=status.HTTP_403_FORBIDDEN
            )

        media_urls = post.media or []

        # multiple files
        media_files = request.FILES.getlist("media_files")
        if media_files:
            media_urls = []
            for file in media_files:
                result = upload(
                    file,
                    folder="posts/",
                    resource_type="auto"
                )
                url = result.get("secure_url")
                if url:
                    media_urls.append(url)

        # single file
        single_media = request.FILES.get("media")
        if single_media:
            result = upload(
                single_media,
                folder="posts/",
                resource_type="auto"
            )
            url = result.get("secure_url")
            if url:
                media_urls = [url]

        serializer = self.get_serializer(
            post,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(media=media_urls)

        return Response(serializer.data, status=status.HTTP_200_OK)






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Post
from .serializers import PostSerializer


class VideoPostListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        videos = Post.objects.filter(media_type="video").order_by("-created_at")
        serializer = VideoPostSerializer(videos, many=True)
        return Response({
            "count": videos.count(),
            "results": serializer.data
        })






# post/views.py
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Post
from .serializers import RepostCreateSerializer, PostSerializer

class RepostCreateAPIView(CreateAPIView):
    serializer_class = RepostCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['post_id'] = self.kwargs['post_id']
        return ctx

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repost = serializer.save()
        data = PostSerializer(repost, context={'request': request}).data
        return Response(data, status=status.HTTP_201_CREATED)








from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Post, PostReaction
from .serializers import PostReactionSerializer
from notification.utils import create_and_push_notification
from .authentication import CsrfExemptJWTAuthentication


# @method_decorator(csrf_exempt, name='dispatch')
class PostReactionToggleAPIView(APIView):
    authentication_classes = [CsrfExemptJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        print("\n========== POST REACTION DEBUG START ==========")

        print("REQUEST USER:", request.user)
        print("USER AUTHENTICATED:", request.user.is_authenticated)
        print("POST ID FROM URL:", post_id)

        print("\nREQUEST DATA:")
        print(request.data)

        post = get_object_or_404(Post, id=post_id)
        print("POST FOUND:", post.id, "| AUTHOR:", post.author)

        reaction_type = request.data.get("reaction_type")
        print("REACTION TYPE:", reaction_type)

        if not reaction_type:
            print("ERROR: reaction_type missing")
            return Response(
                {"detail": "reaction_type is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj = PostReaction.objects.filter(
            user=request.user,
            post=post
        ).first()

        print("\nEXISTING REACTION OBJ:", obj)

        # CASE 1: FIRST REACTION
        if obj is None:
            print("CASE 1 → FIRST REACTION")

            obj = PostReaction.objects.create(
                user=request.user,
                post=post,
                reaction_type=reaction_type
            )

            print("REACTION CREATED:", obj.id, "| TYPE:", obj.reaction_type)

            if post.author != request.user:
                print("SENDING NOTIFICATION → POST AUTHOR")

                create_and_push_notification(
                    receiver=post.author,
                    sender=request.user,
                    action_type="post_reaction",
                    message=f"{request.user.full_name} reacted '{reaction_type}' to your post",
                    target_type="post",
                    target_id=post.id,
                )

            serializer = PostReactionSerializer(
                obj, context={"request": request}
            )

            print("RESPONSE STATUS: 201 CREATED")
            print("========== POST REACTION DEBUG END ==========\n")

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # CASE 2: SAME REACTION → REMOVE
        if obj.reaction_type == reaction_type:
            print("CASE 2 → SAME REACTION, REMOVING")

            obj.delete()
            print("REACTION REMOVED")

            print("RESPONSE STATUS: 204 NO CONTENT")
            print("========== POST REACTION DEBUG END ==========\n")

            return Response(
                {"detail": "reaction removed"},
                status=status.HTTP_204_NO_CONTENT
            )

        # CASE 3: UPDATE REACTION
        print("CASE 3 → UPDATE REACTION")
        print("OLD REACTION:", obj.reaction_type)
        print("NEW REACTION:", reaction_type)

        obj.reaction_type = reaction_type
        obj.save(update_fields=["reaction_type", "created_at"])

        print("REACTION UPDATED")

        if post.author != request.user:
            print("SENDING UPDATE NOTIFICATION → POST AUTHOR")

            create_and_push_notification(
                receiver=post.author,
                sender=request.user,
                action_type="post_reaction_update",
                message=f"{request.user.full_name} changed reaction to '{reaction_type}'",
                target_type="post",
                target_id=post.id,
            )

        serializer = PostReactionSerializer(
            obj, context={"request": request}
        )

        print("RESPONSE STATUS: 200 OK")
        print("========== POST REACTION DEBUG END ==========\n")

        return Response(serializer.data, status=status.HTTP_200_OK)




from notification.utils import create_and_push_notification
from .models import CommentReaction
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

from .models import Comment
from .serializers import CommentSerializer
from rest_framework import viewsets, permissions
from rest_framework import status, generics
from .serializers import PostReactionSerializer, CommentReactionSerializer
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch

from .models import Comment
from .serializers import CommentSerializer
from notification.utils import create_and_push_notification


from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Prefetch

from .models import Comment
from .serializers import CommentSerializer
from notification.utils import create_and_push_notification


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

 
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        """
        GET /comments/?post=<post_id>

        - only root comments (parent=None)
        - replies handled by serializer
        - reactions prefetched
        """
        queryset = (
            Comment.objects
            .select_related("user", "post")
            .prefetch_related(
                "replies",
                "reactions",
            )
            .order_by("-created_at")
        )

        post_id = self.request.query_params.get("post")
        if post_id:
            queryset = queryset.filter(
                post_id=post_id,
                parent__isnull=True
            )

        return queryset

    # -------- POST --------
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
                        "post_id": comment.post.id,
                    }
                )
            return

        # CASE 2: Normal comment → notify post owner
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
                    "image": comment.post.media[0] if comment.post.media else None,
                }
            )

    # -------- GET (single comment) --------
    def retrieve(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)










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


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Post
from .serializers import PostSerializer


class NewsFeedView(APIView):
    authentication_classes = [JWTAuthentication]   #  token
    permission_classes = [IsAuthenticated]          # login required

    def get(self, request):

        posts = (
            Post.objects
            .select_related("author")
            .prefetch_related("comments")
            .prefetch_related("reactions")
            .order_by("-created_at")
        )


        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(posts, request)

        serializer = PostSerializer(
            result_page,
            many=True,
            context={'request': request}  
        )
        return paginator.get_paginated_response(serializer.data)










# for filter api 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q

from .models import Post
from .serializers import PostSerializer

class FilterPostView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        print("88888888888888888888888888")
        content = request.query_params.get("content", None)
        print(">>> content filter:", content)
        author = request.query_params.get("author", None)
        print(">>> author filter:", author)

        queryset = Post.objects.all()

        # Filter by content
        if content:
            queryset = queryset.filter(content__icontains=content)

        # Filter by author (username OR email)
        if author:
            queryset = queryset.filter(
                # Q(author__username__icontains=author) |
                Q(author__email__icontains=author)
            )

        serializer = PostSerializerFilter(queryset, many=True, context={"request": request})
        return Response({"results": serializer.data})




from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model
from .models import Post
from .serializers import UserPostSerializer

User = get_user_model()


class UserPostListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        posts = Post.objects.filter(
            author=user
        ).order_by("-created_at")

        serializer = UserPostSerializer(posts, many=True)

        response_data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            },
            "total_posts": posts.count(),
            "posts": serializer.data
        }

        return Response(response_data)
