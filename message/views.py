from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Conversation
from .serializers import ConversationSerializer

class ConversationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conv = Conversation.objects.filter(
            user1=request.user
        ) | Conversation.objects.filter(
            user2=request.user
        )

        conv = conv.order_by("-updated_at")
        serializer = ConversationSerializer(conv, many=True)
        return Response(serializer.data)




from .models import Message

class MarkAsSeenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        try:
            msg = Message.objects.get(id=message_id, receiver=request.user)
            msg.is_seen = True
            msg.save()
            return Response({"detail": "seen updated"}, status=200)
        except Message.DoesNotExist:
            return Response({"detail": "message not found"}, status=404)
