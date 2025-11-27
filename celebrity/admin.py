from django.contrib import admin


# Register your models here.
from .models import CelebrityProfile , CelebrityFollow ,PaidChatAccess ,Message


@admin.register(CelebrityProfile)
class CelebrityFollowAdmin(admin.ModelAdmin):
    list_display = ( 'id', 'user' ,'is_celebrity', 'followers_count' )


admin.site.register(CelebrityFollow)
admin.site.register(Message)
admin.site.register(PaidChatAccess)