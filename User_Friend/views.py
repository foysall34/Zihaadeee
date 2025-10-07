# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import FriendRequest
from .serializers import FriendRequestSerializer

class FriendRequestViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # ✅ 1. Send friend request
    def create(self, request):
        to_user_id = request.data.get('to_user')
        if FriendRequest.objects.filter(from_user=request.user, to_user_id=to_user_id).exists():
            return Response({'detail': 'Request already sent!'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.id == int(to_user_id):
            return Response({'detail': 'You cannot send a request to yourself!'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.create(from_user=request.user, to_user_id=to_user_id)
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ✅ 2. Accept friend request
    def update(self, request, pk=None):
        try:
            # নিশ্চিত করুন যে রিকোয়েস্টটি বর্তমান ব্যবহারকারীর জন্যই পাঠানো হয়েছে
            friend_request = FriendRequest.objects.get(id=pk, to_user=request.user)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Request not found or not sent to you!'}, status=status.HTTP_404_NOT_FOUND)
    
        new_status = request.data.get('status', 'accepted') # ডিফল্ট হিসেবে 'accepted'
    
        if new_status not in ['accepted', 'rejected']:
             return Response({'detail': 'Invalid status provided!'}, status=status.HTTP_400_BAD_REQUEST)
    
        friend_request.status = new_status
        friend_request.save()
        return Response({'detail': f'Friend request {new_status} '}, status=status.HTTP_200_OK)

    # ✅ 3. Reject or Remove friend request
    def destroy(self, request, pk=None):
        try:
            friend_request = FriendRequest.objects.get(id=pk)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Request not found!'}, status=status.HTTP_404_NOT_FOUND)

        # অনুমতি: কেবল sender বা receiver মুছতে পারবে
        if friend_request.from_user != request.user and friend_request.to_user != request.user:
            return Response({'detail': 'Permission denied!'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.delete()
        return Response({'detail': 'Friend request removed ❌'}, status=status.HTTP_204_NO_CONTENT)



from django.db.models import Q

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
            data.append({'id': friend.id})
        return Response(data)
