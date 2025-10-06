# accounts/utils.py

import random
from django.core.mail import EmailMessage
from django.conf import settings

def generate_otp():
    """
    Generates a 4-digit random OTP.
    """
    return str(random.randint(1000, 9999))

def send_otp_email(email, otp):
    """
    Sends a verification OTP to the user's email address.
    """
    try:
        subject = 'Your Account Verification OTP'
        message = f'Hello,\n\nYour One-Time Password (OTP) for verification is: {otp}\n\nThank you.'
        
        email_message = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_message.send()
        
        print(f"OTP email sent successfully to {email}")

    except Exception as e:
        # Log the error in a real application
        print(f"Failed to send OTP email to {email}: {e}")
        # You might want to raise an exception or handle the failure gracefully