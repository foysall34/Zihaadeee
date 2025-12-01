
from django.contrib import admin
from django.urls import path 
from .views import * 

urlpatterns = [
    path('create-audio-room/', CreateCallRoomAPIView.as_view(), name='audio-room'),
   
]
