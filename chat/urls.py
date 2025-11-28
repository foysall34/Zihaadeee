from django.urls import path
from .views import *

urlpatterns = [

 
    path("room/create/", CreateChatRoom.as_view()),
    path("history/<int:room_id>/", ChatHistory.as_view()),

  

  
]
