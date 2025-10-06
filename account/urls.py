# accounts/urls.py

from django.urls import path
from .views import (
    UserRegisterView, VerifyOTPView, ResendOTPView, LoginView,
    ForgotPasswordView, ResetPasswordView
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]