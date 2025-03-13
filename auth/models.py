from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    
    USERNAME_FIELD = 'email'  # Use email as the login field
    REQUIRED_FIELDS = ['username', 'full_name']  # Keep username for compatibility

    def __str__(self):
        return self.email
