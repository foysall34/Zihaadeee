from django.shortcuts import render

import uuid

def generate_room_id():
    return str(uuid.uuid4())

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class CreateCallRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        room_id = str(uuid.uuid4())
        return Response({"room_id": room_id})
