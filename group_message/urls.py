

from django.urls import path 
from .views import * 

urlpatterns = [

    path('create-group/', GroupCreateAPIView.as_view(), name='conversation-user'),
    path("group/add-member/", AddGroupMemberAPIView.as_view()),
    path("group/remove-member/", RemoveGroupMemberAPIView.as_view()),

     


   
   
]
