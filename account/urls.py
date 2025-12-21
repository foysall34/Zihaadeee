# accounts/urls.py

from django.urls import path

from .views import register_user, verify_otp, login_user, resend_otp , UserProfileView , forgot_password , verify_forgot_otp , reset_password
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', register_user, name='register'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('login/', login_user, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('resend-otp/', resend_otp, name='resend_otp'),
     # Forgot Password Flow
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-forgot-otp/', verify_forgot_otp, name='verify_forgot_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]


