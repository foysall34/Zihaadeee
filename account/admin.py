# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# This class defines how the User model will be displayed in the Django admin panel.
class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the base UserAdmin to use 'email' as the primary identifier.
    ordering = ['email']
    list_display = ['email', 'full_name', 'is_verified', 'is_staff', 'is_active']
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'full_name')

    # The fields to be displayed on the user change page.
    # We remove the 'username' field which we are not using.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
        ('Security', {'fields': ('otp',)}), # Display OTP for debugging
    )

    # The fields to be used when creating a new user via the admin panel.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password', 'password2'), # Add any fields needed for user creation
        }),
    )

    # Now that we have the 'groups' and 'user_permissions' fields, we can use filter_horizontal.
    filter_horizontal = ('groups', 'user_permissions',)


# Register your custom User model with the custom UserAdmin.
admin.site.register(User, UserAdmin)