from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) 

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    ROLE_CHOICES = (
        ('user', 'User'),
        ('celebrity', 'Celebrity'),
     
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    profile_photo = models.URLField(blank=True, null=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    otp = models.CharField(max_length=4, blank=True, null=True)
    is_celebrity = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)
    work = models.TextField(default='write work-place')
    education = models.TextField(default='institue-name')
    home_town = models.CharField(max_length=100 , null= True , blank=True)
    web_link = models.CharField(max_length=1500 , null= True , blank= True)
    profile_link =models.CharField(max_length=2000 , null= True , blank=True)
        




    def __str__(self):
        return f"{self.user.email}'s profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    When a new user is created, automatically create a related UserProfile
    and generate profile_link like: https://yourdomain.com/user/<user_id>/
    """
    if created:
        domain = "https://yourdomain.com"  
        profile = UserProfile.objects.create(
            user=instance,
            work='write work-place',
            education='institue-name',
            home_town='',
            web_link='',
        )
        profile.profile_link = f"{domain}/user/{instance.id}/"
        profile.save()