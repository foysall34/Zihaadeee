from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Q
from django.contrib.auth import get_user_model
from urllib3 import request
from .models import FriendRequest, BlockedUser
from account.models import UserProfile
from .serializers import FriendRequestSerializer, UserProfileSerializer, BlockedUserSerializer

User = get_user_model()




class FriendRequestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # Get all friend requests (sent or received)
    def list(self, request):
        friend_requests = FriendRequest.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user)
        ).order_by('-id')
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Send a friend request
    def create(self, request):
        to_user_id = request.data.get('to_user')

        # validation: field required
        if not to_user_id:
            return Response(
                {'detail': 'to_user field is required!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # prevent self request
        if request.user.id == int(to_user_id):
            return Response(
                {'detail': 'You cannot send a request to yourself!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # check if blocked
        if BlockedUser.objects.filter(
            Q(blocker=request.user, blocked_id=to_user_id) |
            Q(blocker_id=to_user_id, blocked=request.user)
        ).exists():
            return Response(
                {'detail': 'Cannot send request. User blocked!'},
                status=status.HTTP_403_FORBIDDEN
            )

        # already sent
        if FriendRequest.objects.filter(
            from_user=request.user, to_user_id=to_user_id
        ).exists():
            return Response(
                {'detail': 'Request already sent!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # create request
        friend_request = FriendRequest.objects.create(
            from_user=request.user,
            to_user_id=to_user_id
        )
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Accept or reject request
    def update(self, request, pk=None):
        try:
            friend_request = FriendRequest.objects.get(id=pk)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Request not found!'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status', 'accepted')

        if new_status not in ['accepted', 'rejected']:
            return Response({'detail': 'Invalid status provided!'}, status=status.HTTP_400_BAD_REQUEST)

        # Only recipient can accept, both can reject
        if new_status == 'accepted':
            if friend_request.to_user != request.user:
                return Response({'detail': 'Only recipient can accept the request!'}, status=status.HTTP_403_FORBIDDEN)
        elif new_status == 'rejected':
            if friend_request.to_user != request.user and friend_request.from_user != request.user:
                return Response({'detail': 'Permission denied!'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.status = new_status
        friend_request.save()
        return Response({'detail': f'Friend request {new_status}.'}, status=status.HTTP_200_OK)

    # ✅ Delete (cancel or remove) friend request
    def destroy(self, request, pk=None):
        try:
            friend_request = FriendRequest.objects.get(id=pk)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Request not found!'}, status=status.HTTP_404_NOT_FOUND)

        if friend_request.from_user != request.user and friend_request.to_user != request.user:
            return Response({'detail': 'Permission denied!'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.delete()
        return Response({'detail': 'Friend request removed.'}, status=status.HTTP_204_NO_CONTENT)







class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friends = FriendRequest.objects.filter(
            Q(from_user=request.user, status='accepted') | 
            Q(to_user=request.user, status='accepted')
        )
        data = []
        for fr in friends:
            friend = fr.to_user if fr.from_user == request.user else fr.from_user
            data.append({
                'id': friend.id,
                'email': friend.email,
                # আরো field যোগ করতে পারেন
            })
        return Response(data)


class UnfriendView(APIView):

    permission_classes = [IsAuthenticated]


    def post(self, request):
        friend_id = request.data.get('friend_id')
        print("friend_id",friend_id)
        if not friend_id:
            return Response({'detail': 'friend_id field is required!'}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            friend_request = FriendRequest.objects.get(
                Q(from_user=request.user, to_user_id=friend_id, status='accepted') |
                Q(to_user=request.user, from_user_id=friend_id, status='accepted')
            )
            friend_request.delete()
            return Response({'detail': 'Unfriended successfully!'}, status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Friendship not found!'}, status=status.HTTP_404_NOT_FOUND)

                                               


    







class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        blocked_user_id = request.data.get('user_id')

        if not blocked_user_id:
            return Response({'detail': 'user_id field is required!'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.id == int(blocked_user_id):
            return Response({'detail': 'You cannot block yourself!'}, status=status.HTTP_400_BAD_REQUEST)

   
        if BlockedUser.objects.filter(blocker=request.user, blocked_id=blocked_user_id).exists():
            return Response({'detail': 'User already blocked!'}, status=status.HTTP_400_BAD_REQUEST)


        BlockedUser.objects.create(blocker=request.user, blocked_id=blocked_user_id)

        FriendRequest.objects.filter(
            Q(from_user=request.user, to_user_id=blocked_user_id) |
            Q(to_user=request.user, from_user_id=blocked_user_id)
        ).delete()

        return Response({'detail': 'User blocked successfully!'}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        """Unblock a user"""
        blocked_user_id = request.data.get('user_id')

        if not blocked_user_id:
            return Response({'detail': 'user_id field is required!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            blocked = BlockedUser.objects.get(blocker=request.user, blocked_id=blocked_user_id)
            blocked.delete()
            return Response({'detail': 'User unblocked!'}, status=status.HTTP_200_OK)
        except BlockedUser.DoesNotExist:
            return Response({'detail': 'Block record not found!'}, status=status.HTTP_404_NOT_FOUND)







class BlockedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        blocked_users = BlockedUser.objects.filter(blocker=request.user).select_related('blocked')
        data = [{
            'id': b.blocked.id,
            'username': b.blocked.id,
            'blocked_at': b.created_at
        } for b in blocked_users]
        return Response(data)


class FriendDetailView(APIView):
    def get(self, request, friend_id):
        try:
            is_friend = FriendRequest.objects.filter(
                Q(from_user=request.user, to_user_id=friend_id, status='accepted') |
                Q(to_user=request.user, from_user_id=friend_id, status='accepted')
            ).exists()
            
            if not is_friend:
                return Response({'detail': 'You are not friends with this user!'}, status=status.HTTP_403_FORBIDDEN)
            
            friend_profile = UserProfile.objects.get(user_id=friend_id)
            serializer = UserProfileSerializer(friend_profile)
            return Response(serializer.data)
            
        except UserProfile.DoesNotExist:
            return Response({'detail': 'User profile not found!'}, status=status.HTTP_404_NOT_FOUND)