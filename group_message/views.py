from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Group, GroupMember, GroupMessage
from .serializers import GroupSerializer, GroupMessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class GroupCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")
        if not name:
            return Response({"detail": "Group name required"}, status=400)

        group = Group.objects.create(name=name, created_by=request.user)
        GroupMember.objects.create(group=group, user=request.user, is_admin=True)

        return Response(GroupSerializer(group).data, status=201)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from django.contrib.auth import get_user_model
from .models import Group, GroupMember
from .serializers import GroupMemberAddSerializer

User = get_user_model()

class AddGroupMemberAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = GroupMemberAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_id = serializer.validated_data["group_id"]
        user_id = serializer.validated_data["user_id"]

        # Check group exists
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found"}, status=404)

        # Check user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)

        # Check if already exists
        if GroupMember.objects.filter(group=group, user=user).exists():
            return Response({"detail": "User is already a member"}, status=400)

        # Add member
        GroupMember.objects.create(group=group, user=user)

        return Response({
            "message": "User added to group successfully",
            "group_id": group_id,
            "user_id": user_id
        }, status=201)


class RemoveGroupMemberAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = GroupMemberAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_id = serializer.validated_data["group_id"]
        user_id = serializer.validated_data["user_id"]

        # Check group member exists
        try:
            membership = GroupMember.objects.get(group_id=group_id, user_id=user_id)
        except GroupMember.DoesNotExist:
            return Response({"detail": "User is not a member"}, status=400)

        membership.delete()

        return Response({
            "message": "User removed from group",
            "group_id": group_id,
            "user_id": user_id
        }, status=200)


class GroupMessageListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        page = int(request.query_params.get("page", 1))
        size = int(request.query_params.get("page_size", 20))
        offset = (page - 1) * size

        group = get_object_or_404(Group, id=group_id)

        if not GroupMember.objects.filter(group=group, user=request.user).exists():
            return Response({"detail": "Not a member"}, status=403)

        msgs = group.messages.order_by("-timestamp")[offset:offset+size]
        return Response({
            "page": page,
            "results": GroupMessageSerializer(msgs, many=True).data
        })
