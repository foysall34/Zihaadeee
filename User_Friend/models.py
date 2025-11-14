from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user') 

    def __str__(self):
        return f"{self.from_user} → {self.to_user} ({self.status})"


class BlockedUser(models.Model):
    blocker = models.ForeignKey(User, related_name='blocking', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import BlockedUser

class UnblockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, blocked_user_id):
        """
        Unblock a previously blocked user.
        """
        try:
            # Check if blocked relationship exists
            blocked_relation = BlockedUser.objects.filter(
                blocker=request.user, blocked_id=blocked_user_id
            ).first()

            if not blocked_relation:
                return Response(
                    {"detail": "This user is not blocked."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            blocked_relation.delete()
            return Response(
                {"detail": "User unblocked successfully."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"detail": f"Error while unblocking: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )  


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} → {self.following}"