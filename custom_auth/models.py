from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser): 
    groups = models.ManyToManyField(Group, related_name="custom_auth_users", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_auth_users_permissions", blank=True) # Extending Django's built-in user model
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    USERNAME_FIELD = 'email'  # Use email as the login field
    REQUIRED_FIELDS = ['username', 'full_name']  # Keep username for compatibility
     
     
    class Meta:
        swappable = 'AUTH_USER_MODEL'  # Ensure Django can swap this user model
