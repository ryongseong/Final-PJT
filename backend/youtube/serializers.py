from rest_framework import serializers
from .models import YouTubeVideo, SavedVideo
from django.contrib.auth import get_user_model

User = get_user_model()


class YouTubeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeVideo
        fields = "__all__"
        read_only_fields = ("created_at",)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class SavedVideoSerializer(serializers.ModelSerializer):
    video = YouTubeVideoSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = SavedVideo
        fields = ("id", "user", "video", "saved_at", "notes")
        read_only_fields = ("saved_at",)


class SavedVideoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedVideo
        fields = ("id", "video", "notes")
