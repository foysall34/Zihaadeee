import random, re
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import serializers
from .models import User , UserProfile



# ------------------- REGISTER SERIALIZER -------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name',  'password']

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        otp = str(random.randint(1000, 9999))
        user = User.objects.create(**validated_data, otp=otp)
        user.set_password(password)
        user.is_active = False
        user.save()

        # Send OTP to user email
        send_mail(
            subject="Verify your email",
            message=f"Your verification OTP is: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user


# ------------------- OTP VERIFY SERIALIZER -------------------
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")
        return data

    def save(self, **kwargs):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        user.is_active = True
        user.is_verified = True
        user.otp = None
        user.save()
        return user


# ------------------- RESEND OTP SERIALIZER -------------------
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.save()
        send_mail(
            subject="Resend OTP",
            message=f"Your new OTP is: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return user









# ------------------- FORGOT PASSWORD REQUEST SERIALIZER -------------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.save()

        send_mail(
            subject="Password Reset OTP",
            message=f"Your password reset OTP is: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return user


# ------------------- VERIFY FORGOT PASSWORD OTP SERIALIZER -------------------
class VerifyForgotOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if user.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP.")
        return data

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.otp = None 
        user.save()
        return user


# ------------------- RESET PASSWORD SERIALIZER -------------------
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        user.set_password(new_password)
        user.save()
        return user




class UserProfileSerializer(serializers.ModelSerializer):
    profile_photo = serializers.CharField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user_email', 'bio', 'cover_photo' , 'work', 'education', 'web_link' , 'home_town' , 'profile_photo', 'profile_link']

        read_only_fields = ['user', 'profile_photo']
