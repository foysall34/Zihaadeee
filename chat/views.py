from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from celebrity.models import CelebrityProfile
from rest_framework import status
from django.shortcuts import get_object_or_404
from account.models import User



from celebrity.models import CelebrityProfile
from .models import ChatRoom



class CreateChatRoom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user_id = request.data.get("user_id")

        # 1) Target user exists?
        target_user = get_object_or_404(User, id=user_id)

        # 2) Target user must have a celebrity profile
        celebrity = get_object_or_404(CelebrityProfile, user=target_user)

        # 3) Create chat room (ONLY two fields exist: user + celebrity)
        room, created = ChatRoom.objects.get_or_create(
            user=request.user,
            celebrity=celebrity
        )

        return Response({
            "room_id": room.id,
            "created": created,
            "message": "Chat room ready!"
        })
    


    
class ChatHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        msgs = ChatMessage.objects.filter(room_id=room_id).order_by("timestamp")
        return Response(ChatMessageSerializer(msgs, many=True).data)