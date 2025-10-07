from django.contrib import admin
from .models import FriendRequest
# Register your models here.
admin.site.register(FriendRequest)

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('from_user__username', 'to_user__username')
