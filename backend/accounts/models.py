from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    nickname = models.CharField(max_length=15, unique=True)
    profile_img = models.ImageField(
        upload_to="profile_images/",
        null=True,
        blank=True,
        default="profile_images/default.jpeg",
    )
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=[("M", "Male"), ("F", "Female")], null=True, blank=True
    )
    money = models.IntegerField(default=0, blank=True)
    salary = models.IntegerField(null=True, blank=True)
    join_date = models.DateTimeField(default=timezone.now)
    is_admin = models.BooleanField(default=False)

    # Social authentication fields
    google_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    kakao_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    social_avatar = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.username
