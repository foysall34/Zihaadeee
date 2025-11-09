from django.contrib import admin
from .models import FriendRequest, BlockedUser


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'blocker', 'blocked', 'created_at')
    search_fields = ('blocker__username', 'blocked__username')
