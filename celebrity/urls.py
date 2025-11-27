from django.urls import path
from .views import *

urlpatterns = [

    path("donation/create/", CreateDonationPayment.as_view()),
    path("celebrity/upgrade/", CelebrityUpgradePayment.as_view()),
    path("celebrity/follow/", FollowCelebrity.as_view()),
    path("celebrity/chat-access/", ChatAccessPayment.as_view()),
    path("celebrity/message/send/", SendMessage.as_view()),
    path("stripe/webhook/", StripeWebhookView.as_view()),

  

  
]
