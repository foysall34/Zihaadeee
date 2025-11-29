
from django.contrib import admin
from django.urls import path 
from .views import * 

urlpatterns = [
    path('conversation/', ConversationListAPIView.as_view(), name='conversation-user'),
   
]
