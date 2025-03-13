from django.urls import path
from .views import register_user, login_user, ocr_image

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('ocr/', ocr_image, name='ocr'),  # Protected endpoint
]
