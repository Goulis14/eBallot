from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email']

    # Add the 'role' field to the user creation and change forms
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),  # Add the 'role' field
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),  # Add the 'role' field
    )


admin.site.register(CustomUser, CustomUserAdmin)
