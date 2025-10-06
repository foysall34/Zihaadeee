# accounts/serializers.py

from rest_framework import serializers
from .models import User
from .utils import generate_otp, send_otp_email

class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    # Make the photo field required for registration
    photo = serializers.ImageField(required=True)

    class Meta:
        model = User
        # Add 'photo' to the fields list
        fields = ['email', 'full_name', 'photo', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        """
        Check if an already verified user with this email exists.
        """
        if User.objects.filter(email=value, is_verified=True).exists():
            raise serializers.ValidationError("An active account with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        email = validated_data['email']

        # Data to be used for creating or updating the user
        user_defaults = {
            'full_name': validated_data.get('full_name'),
            'photo': validated_data.get('photo'),
        }

        # Creates a new user or updates an existing unverified one
        user, created = User.objects.update_or_create(
            email=email, defaults=user_defaults
        )

        # Always set/reset the password and send a new OTP for verification
        otp = generate_otp()
        user.otp = otp
        user.set_password(validated_data['password'])
        user.save()
        
        send_otp_email(user.email, otp)

        return user

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs