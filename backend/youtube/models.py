from django.db import models
from django.conf import settings


class YouTubeVideo(models.Model):
    youtube_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail_url = models.URLField()
    published_at = models.DateTimeField()
    channel_title = models.CharField(max_length=255)
    search_query = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SavedVideo(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_videos"
    )
    video = models.ForeignKey(
        YouTubeVideo, on_delete=models.CASCADE, related_name="saved_by"
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "video")

    def __str__(self):
        return f"{self.user.username} - {self.video.title}"
