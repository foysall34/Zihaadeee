
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/' ,  include('account.urls')),
    path('content/' ,  include('post.urls')),
    path('friend/' ,  include('User_Friend.urls')),
    path('stories/' ,  include('stories.urls')),
    path('notification/' ,  include('notification.urls')),
    path('celebrity/' , include('celebrity.urls')) ,
    path('chat/' , include('chat.urls')), 
    path('message/' , include('message.urls')),
    path('group-message/' , include('group_message.urls')),
    path('audio-call/', include('audio_call.urls'))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)