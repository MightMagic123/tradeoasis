from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """
    Custom admin panel for managing users.
    """
    model = CustomUser

admin.site.register(CustomUser, CustomUserAdmin)