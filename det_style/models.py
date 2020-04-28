from django.db import models
from django.conf import settings


class Paintings(models.Model):
    name = models.CharField(max_length=45)
    author = models.CharField(max_length=50, default='Author')
    image_path = models.CharField(max_length=200)
    model_path = models.CharField(max_length=200)


class UserStyling(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_image = models.FileField(upload_to='user_uploads')
    selected_painting = models.ForeignKey(Paintings, on_delete=models.DO_NOTHING)
    selected_mode = models.CharField(max_length=10)
    resulted_image = models.TextField(max_length=255)
